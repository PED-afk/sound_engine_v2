"""Example: play three sounds at once, including a moving sound."""
import time
from spatial_audio import SpatialAudioEngine

engine = SpatialAudioEngine(device=None)
engine.start()

try:
    # Load once, then reuse the in-memory asset efficiently.
    engine.start()  # Safe to call repeatedly.
    whoosh = engine.load_sound("sounds/whoosh.wav")
    beep = engine.load_sound("sounds/beep.wav")

    # Static sound: 45 degrees right, distance 20, original volume.
    right_id = engine.add_sound(
        beep, direction=45, distance=20
    )

    # Coordinate sound: x=0, y=0 is exactly at the listener.
    center_id = engine.add_sound(
        beep, x=0, y=0, volume=0.5, wait=1.0
    )

    # Moving sound: starts behind-left, waits 0.5s after playback begins,
    # then moves to front-right at 12 coordinate units per second.
    moving_id = engine.add_sound(
        whoosh,
        start=(-30, -20),
        end=(35, 25),
        speed=12,
        volume=0.8,
        wait=2.0,
        wait_before_move=0.5,
    )

    print("Playing IDs:", right_id, center_id, moving_id)
    print("Active:", engine.active_sounds())

    time.sleep(8)

    # Remove one sound before it naturally finishes.
    engine.remove_sound(center_id)
    print("After removal:", engine.active_sounds())

    time.sleep(10)
finally:
    engine.close()
