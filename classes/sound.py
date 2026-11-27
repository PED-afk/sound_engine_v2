
import sounddevice as sd
import soundfile as sf
import numpy as np
import threading


class Sound:
    def __init__(self, soundFiles: dict):
        """
        soundFiles: {
            "sound_name": "path/to/file.wav"
        }
        """

        self.sounds={}
        self.active_streams={}
        self.lock=threading.Lock()

        # Cache all audio files in memory
        for sound_name, file_path in soundFiles.items():
            audio, sample_rate=sf.read(
                file_path,
                dtype="float32",
                always_2d=True
            )

            self.sounds[sound_name]={
                "audio": audio,
                "sample_rate": sample_rate,
                "channels": audio.shape[1]
            }

    def play(self, sound_name: str):
        """Play a cached sound. Multiple sounds can play simultaneously."""

        if sound_name not in self.sounds:
            raise ValueError(f"Unknown sound: {sound_name}")

        sound=self.sounds[sound_name]

        with self.lock:
            # Stop an existing instance with the same name
            if sound_name in self.active_streams:
                self._stop_locked(sound_name)

            stream=sd.OutputStream(
                samplerate=sound["sample_rate"],
                channels=sound["channels"],
                dtype="float32"
            )

            stream.start()

            self.active_streams[sound_name]=stream

            def playback():
                try:
                    stream.write(sound["audio"])
                except sd.PortAudioError:
                    pass
                finally:
                    with self.lock:
                        if self.active_streams.get(sound_name) is stream:
                            del self.active_streams[sound_name]

                    try:
                        stream.stop()
                        stream.close()
                    except sd.PortAudioError:
                        pass

            thread=threading.Thread(
                target=playback,
                daemon=True
            )
            thread.start()

    def _stop_locked(self, sound_name: str):
        stream=self.active_streams.pop(sound_name, None)
        if stream is not None:
            try:
                stream.abort()
                stream.close()
            except sd.PortAudioError:
                pass

    def stop(self, sound_name: str):
        """Stop a specific sound."""
        with self.lock:
            self._stop_locked(sound_name)

    def stop_all(self):
        """Stop all currently playing sounds."""
        with self.lock:
            for sound_name in list(self.active_streams):
                self._stop_locked(sound_name)
