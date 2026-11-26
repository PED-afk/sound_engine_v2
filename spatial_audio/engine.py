"""Four-channel quadraphonic spatial audio mixer.

Coordinate convention:
    x: right is positive
    y: front is positive
    direction: degrees clockwise from front (0=front, 90=right)
    distance: 0..100, where 0 is at the listener and 100 is very quiet.

Output channel order is configurable; default is:
    front-left, front-right, rear-left, rear-right
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from threading import RLock
from typing import Optional, Union
import itertools
import math
import time

import numpy as np
import sounddevice as sd
import soundfile as sf


@dataclass(frozen=True)
class SoundAsset:
    """Audio samples already loaded into memory, converted to mono float32."""
    samples: np.ndarray
    sample_rate: int
    source: str = "<memory>"

    @classmethod
    def load(cls, filepath: Union[str, Path], target_sample_rate: int) -> "SoundAsset":
        path = str(Path(filepath).expanduser().resolve())
        samples, source_rate = sf.read(path, dtype="float32", always_2d=True)
        # Spatial panning is performed on a mono source. Stereo files are downmixed.
        mono = samples.mean(axis=1).astype(np.float32, copy=False)
        if len(mono) == 0:
            raise ValueError(f"Audio file is empty: {path}")
        if source_rate != target_sample_rate:
            mono = _resample_linear(mono, source_rate, target_sample_rate)
        mono = np.ascontiguousarray(mono, dtype=np.float32)
        mono.setflags(write=False)
        return cls(mono, target_sample_rate, path)


def _resample_linear(data: np.ndarray, source_rate: int, target_rate: int) -> np.ndarray:
    """Dependency-free linear resampler; adequate for effects and general playback."""
    if source_rate == target_rate:
        return data.astype(np.float32, copy=False)
    new_length = max(1, int(round(len(data) * target_rate / source_rate)))
    old_positions = np.arange(len(data), dtype=np.float64)
    new_positions = np.arange(new_length, dtype=np.float64) * source_rate / target_rate
    new_positions = np.minimum(new_positions, len(data) - 1)
    result = np.interp(new_positions, old_positions, data).astype(np.float32)
    return result


@dataclass
class _Voice:
    sound_id: int
    asset: SoundAsset
    start_frame: int
    volume: float
    initial_xy: tuple[float, float]
    final_xy: Optional[tuple[float, float]] = None
    move_after_frames: int = 0
    move_duration_frames: int = 0
    cursor: int = 0
    stopped: bool = False

    def position_at(self, absolute_frame: int) -> tuple[float, float]:
        if self.final_xy is None:
            return self.initial_xy
        move_start = self.start_frame + self.move_after_frames
        if absolute_frame <= move_start:
            return self.initial_xy
        if self.move_duration_frames <= 0:
            return self.final_xy
        fraction = min(1.0, (absolute_frame - move_start) / self.move_duration_frames)
        x = self.initial_xy[0] + (self.final_xy[0] - self.initial_xy[0]) * fraction
        y = self.initial_xy[1] + (self.final_xy[1] - self.initial_xy[1]) * fraction
        return x, y


class SpatialAudioEngine:
    """Realtime four-speaker mixer supporting many simultaneous sound voices."""

    # Speaker positions clockwise from front; output channel indices:
    # FL=0, FR=1, RL=2, RR=3.
    _speaker_angles = np.array([45.0, 135.0, 225.0, 315.0], dtype=np.float64)
    _speaker_channels = np.array([1, 3, 2, 0], dtype=np.int64)

    def __init__(
        self,
        device=None,
        sample_rate: Optional[int] = None,
        block_size: int = 512,
        output_channels: int = 4,
        distance_attenuation_db: float = 30.0,
    ):
        if output_channels != 4:
            raise ValueError("This engine currently requires exactly 4 output channels.")
        self.device = device
        self.block_size = block_size
        self.output_channels = output_channels
        self.distance_attenuation_db = float(distance_attenuation_db)

        if sample_rate is None:
            info = sd.query_devices(device, "output")
            sample_rate = int(info["default_samplerate"])
        self.sample_rate = int(sample_rate)

        sd.check_output_settings(
            device=self.device,
            channels=4,
            samplerate=self.sample_rate,
            dtype="float32",
        )

        self._lock = RLock()
        self._voices: dict[int, _Voice] = {}
        self._asset_cache: dict[str, SoundAsset] = {}
        self._id_counter = itertools.count(1)
        self._rendered_frames = 0
        self._stream = None
        self._started = False

    def start(self):
        """Start the output stream. Safe to call more than once."""
        with self._lock:
            if self._started:
                return
            self._stream = sd.OutputStream(
                device=self.device,
                samplerate=self.sample_rate,
                channels=4,
                dtype="float32",
                blocksize=self.block_size,
                callback=self._audio_callback,
            )
            self._stream.start()
            self._started = True

    def close(self):
        """Stop audio output and clear active voices."""
        with self._lock:
            stream = self._stream
            self._stream = None
            self._started = False
            self._voices.clear()
        if stream is not None:
            stream.stop()
            stream.close()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def load_sound(self, filepath: Union[str, Path]) -> SoundAsset:
        """Load and cache a sound once; reuse the returned asset for many voices."""
        path = str(Path(filepath).expanduser().resolve())
        with self._lock:
            cached = self._asset_cache.get(path)
            if cached is not None:
                return cached
        asset = SoundAsset.load(path, self.sample_rate)
        with self._lock:
            # If another thread loaded it in the meantime, keep the first cached object.
            return self._asset_cache.setdefault(path, asset)

    def add_sound(
        self,
        sound: Union[str, Path, SoundAsset],
        *,
        direction: Optional[float] = None,
        distance: float = 0.0,
        x: Optional[float] = None,
        y: Optional[float] = None,
        start: Optional[tuple[float, float]] = None,
        end: Optional[tuple[float, float]] = None,
        speed: Optional[float] = None,
        volume: float = 1.0,
        wait: float = 0.0,
        wait_before_move: float = 0.0,
    ) -> int:
        """Add a sound and return its ID.

        Supply exactly one position mode:
          * direction + distance
          * x + y coordinates
          * start + end + speed for linear movement

        `wait` delays playback after this method is called.
        `wait_before_move` delays movement after playback begins.
        `volume` is a linear multiplier (1.0 = original loaded amplitude).
        """
        if isinstance(sound, SoundAsset):
            asset = sound
            if asset.sample_rate != self.sample_rate:
                raise ValueError("SoundAsset sample rate does not match engine sample rate.")
        else:
            asset = self.load_sound(sound)

        if volume < 0:
            raise ValueError("volume must be >= 0")
        if wait < 0 or wait_before_move < 0:
            raise ValueError("wait and wait_before_move must be >= 0")

        modes = int(direction is not None) + int(x is not None or y is not None) + int(start is not None or end is not None or speed is not None)
        if modes != 1:
            raise ValueError("Choose exactly one position mode: direction/distance, x/y, or start/end/speed.")

        final_xy = None
        move_after_frames = 0
        move_duration_frames = 0

        if direction is not None:
            if not 0 <= distance <= 100:
                raise ValueError("distance must be between 0 and 100")
            angle = math.radians(float(direction) % 360.0)
            initial_xy = (math.sin(angle) * distance, math.cos(angle) * distance)
        elif x is not None or y is not None:
            if x is None or y is None:
                raise ValueError("Both x and y must be provided.")
            initial_xy = (float(x), float(y))
            if math.hypot(*initial_xy) > 100:
                raise ValueError("The (x, y) position must be within distance 100.")
        else:
            if start is None or end is None or speed is None:
                raise ValueError("Movement requires start, end, and speed.")
            if speed <= 0:
                raise ValueError("speed must be > 0 (coordinate units per second).")
            initial_xy = (float(start[0]), float(start[1]))
            final_xy = (float(end[0]), float(end[1]))
            if math.hypot(*initial_xy) > 100 or math.hypot(*final_xy) > 100:
                raise ValueError("Start and end positions must be within distance 100.")
            move_after_frames = int(round(wait_before_move * self.sample_rate))
            travel_distance = math.dist(initial_xy, final_xy)
            move_duration_frames = int(round((travel_distance / speed) * self.sample_rate))

        with self._lock:
            sound_id = next(self._id_counter)
            start_frame = self._rendered_frames + int(round(wait * self.sample_rate))
            self._voices[sound_id] = _Voice(
                sound_id=sound_id,
                asset=asset,
                start_frame=start_frame,
                volume=float(volume),
                initial_xy=initial_xy,
                final_xy=final_xy,
                move_after_frames=move_after_frames,
                move_duration_frames=move_duration_frames,
            )
        return sound_id

    def remove_sound(self, sound_id: int) -> bool:
        """Remove a voice immediately. Returns False if the ID is not active."""
        with self._lock:
            return self._voices.pop(int(sound_id), None) is not None

    def remove_all_sounds(self):
        """Stop all active and scheduled sounds."""
        with self._lock:
            self._voices.clear()

    def active_sounds(self) -> list[dict]:
        """Return a snapshot of active/scheduled sound IDs and source paths."""
        with self._lock:
            return [
                {"id": v.sound_id, "source": v.asset.source, "scheduled": v.cursor == 0}
                for v in self._voices.values()
            ]

    @staticmethod
    def _speaker_gains(x: float, y: float) -> tuple[np.ndarray, float]:
        distance = min(100.0, math.hypot(x, y))
        # Angle is clockwise from front (+Y), with +X to the right.
        angle = math.degrees(math.atan2(x, y)) % 360.0
        angles = SpatialAudioEngine._speaker_angles
        adjusted = angle if angle >= angles[0] else angle + 360.0
        extended = np.append(angles, angles[0] + 360.0)
        segment = int(np.searchsorted(extended, adjusted, side="right") - 1)
        next_segment = (segment + 1) % 4
        fraction = (adjusted - extended[segment]) / (extended[segment + 1] - extended[segment])
        gain_a = math.cos(fraction * math.pi / 2.0)
        gain_b = math.sin(fraction * math.pi / 2.0)
        gains = np.zeros(4, dtype=np.float32)
        gains[SpatialAudioEngine._speaker_channels[segment]] = gain_a
        gains[SpatialAudioEngine._speaker_channels[next_segment]] = gain_b

        # 0 -> 1.0 gain; 100 -> -30 dB (0.0316), deliberately very quiet.
        attenuation = 10.0 ** (
            -SpatialAudioEngine._distance_db(distance) / 20.0
        )
        return gains, attenuation

    @staticmethod
    def _distance_db(distance: float) -> float:
        # Smooth 0..30 dB attenuation over the 0..100 distance range.
        return 30.0 * min(100.0, max(0.0, distance)) / 100.0

    def _audio_callback(self, outdata, frames, time_info, status):
        outdata.fill(0.0)
        block_start = self._rendered_frames
        block_end = block_start + frames

        # The callback owns voice cursors. API mutations are protected by the same lock.
        with self._lock:
            finished = []
            for sound_id, voice in list(self._voices.items()):
                playback_start = max(block_start, voice.start_frame)
                if playback_start >= block_end:
                    continue

                source_offset = voice.cursor
                # If scheduled playback starts part-way through this block, skip silence.
                if block_start < voice.start_frame:
                    source_offset = 0
                output_offset = playback_start - block_start
                available = min(
                    frames - output_offset,
                    len(voice.asset.samples) - source_offset,
                )
                if available <= 0:
                    finished.append(sound_id)
                    continue

                source = voice.asset.samples[source_offset:source_offset + available]
                # Apply spatial gain per sample so movement is smooth.
                for j in range(available):
                    absolute_frame = playback_start + j
                    px, py = voice.position_at(absolute_frame)
                    gains, attenuation = self._speaker_gains(px, py)
                    outdata[output_offset + j, :] += (
                        source[j] * voice.volume * attenuation * gains
                    )

                voice.cursor = source_offset + available
                if voice.cursor >= len(voice.asset.samples):
                    finished.append(sound_id)

            for sound_id in finished:
                self._voices.pop(sound_id, None)

            self._rendered_frames = block_end

        # A modest safety limiter prevents summed voices from clipping.
        peak = float(np.max(np.abs(outdata))) if outdata.size else 0.0
        if peak > 0.98:
            outdata *= 0.98 / peak
