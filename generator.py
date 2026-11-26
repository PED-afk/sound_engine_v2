
from pathlib import Path
import json
import math

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly


# ============================================================
# CONFIGURATION
# ============================================================

ROOTPATH = Path(__file__).resolve().parent

DEFINITIONS_DIR = ROOTPATH / "sounds" / "sound_defs"
REDEFINITIONS_DIR = ROOTPATH / "sounds" / "sound_defs" / "old_redone"
PLAYABLES_DIR = ROOTPATH / "sounds" / "playables"

SAMPLE_RATE = 48000
CHUNK_SIZE = 1024

# Distance at which attenuation becomes very strong
DISTANCE_REFERENCE = 15.0

# Around 100 units away, sound is faint (~2.2% amplitude)
# Gain = 1 / (1 + (distance / DISTANCE_REFERENCE)^2)

# Speaker positions, square layout around listener (0, 0)
# Channel order in the exported WAV:
# FL, FR, RL, RR, LFE
SPEAKERS = [
    (-1,  1),  # Front Left  (FL)
    ( 1,  1),  # Front Right (FR)
    (-1, -1),  # Rear Left  (RL)
    ( 1, -1),  # Rear Right (RR)
]

LFE_CHANNEL = 4  # Fifth channel, left empty


# ============================================================
# PATH / AUDIO HELPERS
# ============================================================

def resolve_path(path_string: str) -> Path:
    """Resolve an audio path relative to ROOTPATH."""
    # Support Windows-style paths even when running on Linux.
    normalized = path_string.replace("\\", "/")
    path = Path(normalized)

    if not path.is_absolute():
        path = ROOTPATH / path

    return path.resolve()

def load_audio(path: Path) -> np.ndarray:
    """Load audio and convert to mono float32 at SAMPLE_RATE."""
    audio, sr = sf.read(path, dtype="float32", always_2d=True)

    # Convert stereo/multichannel input to mono for positional panning.
    audio = audio.mean(axis=1)

    if sr != SAMPLE_RATE:
        gcd = math.gcd(sr, SAMPLE_RATE)
        audio = resample_poly(
            audio,
            SAMPLE_RATE // gcd,
            sr // gcd
        ).astype(np.float32)

    return audio


# ============================================================
# POSITION / SPATIAL AUDIO
# ============================================================
def get_position(
        t,
        start,
        end,
        speed,
        move_start,
        orbit_mode=False,
        orbit_distance=0
    ):
    """
    Linear movement or circular orbit.

    Linear mode:
        SPEED = units per second

    Orbit mode:
        SPEED = degrees per second
        DIST = orbit radius
    """

    if t <= move_start:
        if orbit_mode:
            return np.array([orbit_distance, 0.0])

        return np.asarray(start, dtype=float)

    elapsed = t - move_start

    if orbit_mode:
        angle = math.radians(speed * elapsed)

        x = orbit_distance * math.cos(angle)
        y = orbit_distance * math.sin(angle)

        return np.array([x, y])

    start = np.asarray(start, dtype=float)
    end = np.asarray(end, dtype=float)

    direction = end - start
    distance = np.linalg.norm(direction)

    if distance == 0 or speed <= 0:
        return start

    travel_time = distance / speed
    progress = min(elapsed / travel_time, 1.0)

    return start + direction * progress

def spatial_gains(position):
    """
    Bilinear panning between the four square speakers.

    Position x/y is mapped to [-1, 1].
    Outside the speaker square, position is clamped.
    """
    x, y = position

    x = float(np.clip(x / 100.0, -1.0, 1.0))
    y = float(np.clip(y / 100.0, -1.0, 1.0))

    # Convert to 0..1 coordinates
    right = (x + 1.0) / 2.0
    front = (y + 1.0) / 2.0

    # FL, FR, RL, RR
    gains = np.array([
        (1 - right) * front,        # FL
        right * front,              # FR
        (1 - right) * (1 - front),  # RL
        right * (1 - front),        # RR
    ], dtype=np.float32)

    return gains

def distance_gain(position):
    """Distance attenuation, with a faint sound at 100 units."""
    distance = np.linalg.norm(position)

    return 1.0 / (
        1.0 + (distance / DISTANCE_REFERENCE) ** 2
    )


# ============================================================
# JSON PROCESSING / MIXING
# ============================================================
def generate_sound(definition_path: Path, lang:str="eng"):
    with open(definition_path, "r", encoding="utf-8") as f:
        definition = json.load(f)

    name = definition["NAME"]
    subtitle = definition.get("SUBTITLE", "")

    speed = float(definition.get("SPEED", 0))
    movement_delay = float(definition.get("WAIT_BEFORE_MOVE", 0))

    orbit_mode = "START" not in definition

    if orbit_mode:
        if "DIST" not in definition or "SPEED" not in definition:
            raise ValueError("Orbit mode requires DIST and SPEED")

        orbit_distance = float(definition["DIST"])

        if orbit_distance < 0:
            raise ValueError("DIST cannot be negative")

        start = None
        end = None

    else:
        start = definition["START"]
        end = definition["END"]
        orbit_distance = None
        master_volume = float(definition.get("VOLUME", 1.0))

        sounds = definition.get("SOUNDS", [])

    # Load all source audio
    loaded_sounds = []

    for sound in sounds:
        source_path = resolve_path(sound["PATH"])

        if not source_path.exists():
            print(f"[WARNING] Missing audio file: {source_path}")
            continue

        if lang=="eng":
            audio=load_audio(source_path)
        else:
            audio=load_audio(Path(str(source_path).replace("eng", lang)))

        times = max(1, int(sound.get("TIMES", 1)))
        wait = max(0.0, float(sound.get("WAIT", 0)))
        wait_before = max(0.0, float(sound.get("WAIT_BEFORE", 0)))
        volume = float(sound.get("VOLUME", 1.0))

        loaded_sounds.append({
            "audio": audio,
            "times": times,
            "wait": wait,
            "wait_before": wait_before,
            "volume": volume,
        })

    if not loaded_sounds:
        print(f"[SKIP] No valid sounds in {definition_path.name}")
        return

    # Calculate when each subsound should play
    scheduled = []
    total_duration = 0.0

    for sound in loaded_sounds:
        audio = sound["audio"]
        sound_duration = len(audio) / SAMPLE_RATE

        play_time = sound["wait_before"]

        for repeat in range(sound["times"]):
            scheduled.append({
                "audio": audio,
                "start_time": play_time,
                "volume": sound["volume"],
            })

            total_duration = max(
                total_duration,
                play_time + sound_duration
            )

            play_time += sound_duration + sound["wait"]

    if total_duration <= 0:
        print(f"[SKIP] Empty sound: {name}")
        return

    total_frames = int(math.ceil(total_duration * SAMPLE_RATE))

    # Check whether the sound has enough time to reach END
    travel_distance = np.linalg.norm(
        np.asarray(end, dtype=float) - np.asarray(start, dtype=float)
    )
    travel_time = travel_distance / speed if speed > 0 else float("inf")
    arrival_time = movement_delay + travel_time
    if total_duration >= arrival_time:
        pass
        #print(f"[REACHED END] {name}: {end} (at {arrival_time:.2f}s)")
    else:
        print(
            f"[DID NOT REACH END] {name}: "
            f"stopped at {get_position(total_duration, start, end, speed, movement_delay).tolist()} "
            f"(END: {end})"
        )



    # Output channels: FL, FR, RL, RR, LFE
    output = np.zeros((total_frames, 5), dtype=np.float32)

    # Mix each sound into the output
    for item in scheduled:
        audio = item["audio"]
        sound_start = int(item["start_time"] * SAMPLE_RATE)
        sound_volume = item["volume"]

        audio_frames = len(audio)

        for offset in range(0, audio_frames, CHUNK_SIZE):
            chunk = audio[offset:offset + CHUNK_SIZE]

            if len(chunk) == 0:
                continue

            absolute_start = sound_start + offset
            absolute_end = min(absolute_start + len(chunk), total_frames)

            if absolute_start >= total_frames:
                break

            chunk = chunk[:absolute_end - absolute_start]
            frames = len(chunk)

            # Absolute time of every sample in this chunk
            times = (
                np.arange(absolute_start, absolute_start + frames)
                / SAMPLE_RATE
            )

            # Get position over time
            positions = np.array([
                get_position(
                    t,
                    start,
                    end,
                    speed,
                    movement_delay,
                    orbit_mode,
                    orbit_distance if orbit_mode else 0
                )
                for t in times
            ])

            # Per-sample attenuation and speaker panning
            distances = np.linalg.norm(positions, axis=1)

            attenuations = 1.0 / (
                1.0 + (distances / DISTANCE_REFERENCE) ** 2
            )

            x = np.clip(positions[:, 0] / 100.0, -1, 1)
            y = np.clip(positions[:, 1] / 100.0, -1, 1)

            right = (x + 1.0) / 2.0
            front = (y + 1.0) / 2.0

            # Speaker gains: FL, FR, RL, RR
            gains = np.column_stack([
                (1 - right) * front,
                right * front,
                (1 - right) * (1 - front),
                right * (1 - front),
            ])

            mixed = (
                chunk[:, None]
                * gains
                * attenuations[:, None]
                * sound_volume
                * master_volume
            )

            # Add to corresponding channels
            output[absolute_start:absolute_end, :4] += mixed

    # LFE remains silent

    # Prevent clipping without distorting relative mix
    peak = np.max(np.abs(output))

    if peak > 1.0:
        output /= peak

    # Save WAV
    PLAYABLES_DIR.mkdir(parents=True, exist_ok=True)

    output_path = (PLAYABLES_DIR / f"{name}.wav").resolve()

    sf.write(
        output_path,
        output,
        SAMPLE_RATE,
        subtype="PCM_24"
    )

    # Save metadata
    metadata = {
        "NAME": name,
        "PATH": str(output_path),
        "SUBTITLE": subtitle,
    }

    metadata_path = PLAYABLES_DIR / f"{name}.json"

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)

    print(f"[OK] {name}")
    print(f"     Audio: {output_path}")
    print(f"     Duration: {total_duration:.2f}s")


# ============================================================
# MAIN
# ============================================================

def main(lang):
    PLAYABLES_DIR.mkdir(parents=True, exist_ok=True)

    if not DEFINITIONS_DIR.exists():
        print(f"[ERROR] Folder not found: {DEFINITIONS_DIR}")
        return

    # Only JSON files in this folder; ignore subdirectories.
    definition_files = sorted(DEFINITIONS_DIR.glob("*.json"))

    #redone old files
    definition_files += sorted(REDEFINITIONS_DIR.glob("*.json"))

    print(f"Found {len(definition_files)} sound definitions.")
    for definition_path in definition_files:
        try:
            generate_sound(definition_path, lang)
        except Exception as e:
            print(f"[ERROR] {definition_path.name}: {e}")
        print("")

    print("Finished generating playables.")


if __name__ == "__main__":
    doEng=False
    if doEng:
        main(lang="eng")
    else:
        main(lang="hun")



