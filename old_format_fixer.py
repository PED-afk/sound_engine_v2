
from pathlib import Path
import json
import sys


ROOTPATH = Path(__file__).resolve().parent

OLD_DIR = ROOTPATH / "sounds" / "sound_defs" / "old"
NEW_DIR = ROOTPATH / "sounds" / "sound_defs" / "old_redone"


def convert_path_entry(entry, filename):
    """
    Convert one old PATH entry to the new SOUNDS format.

    Old formats supported:
        "filepath"

        ["filepath"]

        ["filepath", TIMES]

        ["filepath", TIMES, WAIT]

        ["filepath", TIMES, WAIT, WAIT_BEFORE]

    Missing values are filled with defaults.
    """

    # Old format: path is just a string
    if isinstance(entry, str):
        filepath = entry
        times = 1
        wait = 0
        wait_before = 0

    # Old format: path is a list
    elif isinstance(entry, list):
        if len(entry) == 0:
            raise ValueError(f"Empty PATH entry in {filename}")

        filepath = entry[0]
        times = entry[1] if len(entry) > 1 else 1
        wait = entry[2] if len(entry) > 2 else 0
        wait_before = entry[3] if len(entry) > 3 else 0

    else:
        raise ValueError(
            f"Unsupported PATH entry type in {filename}: "
            f"{type(entry).__name__}"
        )

    if not isinstance(filepath, str):
        raise ValueError(f"Invalid filepath in {filename}: {filepath!r}")

    # Random-play folder paths are currently unsupported.
    # Old format indicates these with a trailing slash/backslash.
    if filepath.endswith("\\") or filepath.endswith("/"):
        raise ValueError(
            f"Random-folder playback is unsupported: {filepath}"
        )

    return {
        "PATH": filepath,
        "TIMES": times,
        "WAIT": wait,
        "WAIT_BEFORE": wait_before,
        "VOLUME": 1.0,
    }


def convert_old_json(data, filename):
    """Convert one legacy JSON object to the new format."""

    if "PATH" not in data:
        raise ValueError(f"Missing PATH field in {filename}")

    old_paths = data["PATH"]

    # A single string or a single sound's parameter list
    # should be treated as one entry.
    if isinstance(old_paths, str):
        entries = [old_paths]

    elif isinstance(old_paths, list):
        if not old_paths:
            entries = []

        # A single entry like:
        # ["filepath", 1, 0, 2]
        elif isinstance(old_paths[0], str):
            entries = [old_paths]

        # A collection of entries like:
        # [
        #   "filepath",
        #   ["filepath", 1, 0, 2]
        # ]
        else:
            entries = old_paths

    else:
        raise ValueError(f"Invalid PATH format in {filename}")

    sounds = [
        convert_path_entry(entry, filename)
        for entry in entries
    ]

    return {
        "NAME": data.get("NAME", Path(filename).stem),
        "SUBTITLE": data.get("SUBTITLE", ""),
        "SOUNDS": sounds,
        "START": [0, 0],
        "END": [0, 0],
        "SPEED": 0,
        "WAIT_BEFORE_MOVE": 0,
        "VOLUME": 1.0,
    }


def convert_old_sounds_folder():
    """Convert all JSON files in OLD_DIR. Stop on first failure."""

    NEW_DIR.mkdir(parents=True, exist_ok=True)

    if not OLD_DIR.exists():
        print(f"Folder not found: {OLD_DIR}")
        return

    # Only scan this folder, not subfolders.
    files = sorted(OLD_DIR.glob("*.json"))

    print(f"Found {len(files)} old JSON files.")

    for old_file in files:
        try:
            with open(old_file, "r", encoding="utf-8") as f:
                old_data = json.load(f)

            new_data = convert_old_json(old_data, old_file.name)

            new_file = NEW_DIR / old_file.name

            with open(new_file, "w", encoding="utf-8") as f:
                json.dump(
                    new_data,
                    f,
                    indent=4,
                    ensure_ascii=False
                )

            print(f"[OK] {old_file.name}")

        except Exception as e:
            print(f"\n[STOP] Failed to convert: {old_file.name}")
            print(f"Reason: {e}")
            #sys.exit(1)

    print("\nConversion finished successfully.")


if __name__ == "__main__":
    convert_old_sounds_folder()
