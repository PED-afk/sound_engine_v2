
from pathlib import Path
import json
import sys


# ============================================================
# CONFIG
# ============================================================

ROOTPATH = Path(__file__).resolve().parent

OLD_DIR = ROOTPATH / "sounds" / "sound_defs" / "old"
NEW_DIR = ROOTPATH / "sounds" / "sound_defs" / "old_redone"


# ============================================================
# PARSING OLD PATH FORMAT
# ============================================================

def parse_old_path_entry(entry):
    """
    Converts one old PATH entry into a new SOUNDS entry.

    Supported formats:
        "filepath"

        ["filepath"]

        ["filepath", TIMES]

        ["filepath", TIMES, WAIT]

        ["filepath", TIMES, WAIT, WAIT_BEFORE]
    """

    if isinstance(entry, str):
        path = entry
        times = 1
        wait = 0
        wait_before = 0

    elif isinstance(entry, list):
        if not entry or not isinstance(entry[0], str):
            raise ValueError(f"Invalid PATH entry: {entry!r}")

        path = entry[0]

        # Defaults for all optional fields
        times = 1
        wait = 0
        wait_before = 0

        if len(entry) >= 2:
            times = entry[1]

        if len(entry) >= 3:
            wait = entry[2]

        if len(entry) >= 4:
            wait_before = entry[3]

        if len(entry) > 4:
            raise ValueError(f"Too many values in PATH entry: {entry!r}")

    else:
        raise ValueError(f"Unsupported PATH entry: {entry!r}")

    # Detect unsupported random-folder playback
    normalized_path = path.replace("/", "\\")
    if normalized_path.endswith("\\"):
        raise RuntimeError(f"Random folder playback is unsupported: {path}")

    return {
        "PATH": path,
        "TIMES": times,
        "WAIT": wait,
        "WAIT_BEFORE": wait_before,
        "VOLUME": 1.0,
    }


def parse_old_path(path_data):
    """
    Converts the old PATH field into a list of new SOUNDS entries.

    Supports:
        PATH = "filepath"

        PATH = ["filepath1", "filepath2"]

        PATH = [["filepath1", 2, 0.5], ["filepath2", 1, 0, 3]]

        PATH = ["filepath1", ["filepath2", 2, 0.5, 3]]

        PATH = ["filepath", 2, 0.5, 3]  # Single entry
    """

    if isinstance(path_data, str):
        return [parse_old_path_entry(path_data)]

    if not isinstance(path_data, list):
        raise ValueError(f"Unsupported PATH format: {path_data!r}")

    if not path_data:
        return []

    # Detect a single entry formatted as:
    # ["filepath", TIMES, WAIT, WAIT_BEFORE]
    #
    # If all items after the path are numbers, this is one sound entry,
    # not a list of separate sounds.
    if (
        isinstance(path_data[0], str)
        and all(
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            for value in path_data[1:]
        )
    ):
        return [parse_old_path_entry(path_data)]

    # Otherwise treat the list as a collection of sound entries.
    sounds = []

    for entry in path_data:
        sounds.append(parse_old_path_entry(entry))

    return sounds


# ============================================================
# CONVERSION
# ============================================================

def convert_file(old_file: Path):
    with open(old_file, "r", encoding="utf-8") as f:
        old_data = json.load(f)

    name = old_data.get("NAME", old_file.stem)

    # Convert the old PATH field
    sounds = parse_old_path(old_data.get("PATH", []))

    new_data = {
        "NAME": name,
        "SUBTITLE": old_data.get("SUBTITLE", ""),
        "SOUNDS": sounds,
        "START": [0, 0],
        "END": [0, 0],
        "SPEED": 0,
        "WAIT_BEFORE_MOVE": 0,
        "VOLUME": 1.0
    }

    output_file = NEW_DIR / f"{old_file.stem}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=4, ensure_ascii=False)

    print(f"[OK] {old_file.name} -> {output_file.name}")


# ============================================================
# MAIN
# ============================================================

def main():
    print("Don't run this again or save the already fixed files")
    return
    if not OLD_DIR.exists():
        print(f"[ERROR] Folder not found: {OLD_DIR}")
        return

    NEW_DIR.mkdir(parents=True, exist_ok=True)

    # Only files in this folder, no subfolders
    json_files = sorted(OLD_DIR.glob("*.json"))

    print(f"Found {len(json_files)} old sound definitions.\n")

    for old_file in json_files:
        try:
            convert_file(old_file)

        except RuntimeError as e:
            # Unsupported folder/random playback:
            # Stop the entire migration immediately.
            print("\n[MIGRATION STOPPED]")
            print(f"File: {old_file.name}")
            print(f"Reason: {e}")
            #sys.exit(1)

        except Exception as e:
            # Stop on other conversion errors as well,
            # to avoid silently skipping problematic definitions.
            print("\n[MIGRATION STOPPED]")
            print(f"File: {old_file.name}")
            print(f"Reason: {e}")
            #sys.exit(1)

    print("\nMigration completed successfully.")


print("Don't run this again or save the already fixed files")
exit()
if __name__ == "__main__":
    print("Don't run this again or save the already fixed files")
    exit()
    main()
