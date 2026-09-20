import hashlib
import json
from pathlib import Path

MONITORED_DIR = Path("Monitored")
BASELINE_FILE = Path("baseline.json")


def calculate_hash(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while chunk := file.read(4096):
            sha256.update(chunk)

    return sha256.hexdigest()


def get_file_hashes():
    file_hashes = {}

    for file_path in MONITORED_DIR.rglob("*"):
        if file_path.is_file():
            relative_path = str(file_path.relative_to(MONITORED_DIR))
            file_hashes[relative_path] = calculate_hash(file_path)

    return file_hashes


def save_baseline(file_hashes):
    with open(BASELINE_FILE, "w") as file:
        json.dump(file_hashes, file, indent=4)


def load_baseline():
    with open(BASELINE_FILE, "r") as file:
        return json.load(file)


def create_baseline():
    file_hashes = get_file_hashes()
    save_baseline(file_hashes)

    print("✅ Baseline created successfully.")
    print(f"Files monitored: {len(file_hashes)}")


def check_integrity():
    old_hashes = load_baseline()
    current_hashes = get_file_hashes()

    for file_path in old_hashes:
        if file_path not in current_hashes:
            print(f"🔴 DELETED: {file_path}")

    for file_path in current_hashes:
        if file_path not in old_hashes:
            print(f"🟢 NEW: {file_path}")

        elif current_hashes[file_path] != old_hashes[file_path]:
            print(f"🟠 MODIFIED: {file_path}")

    if old_hashes == current_hashes:
        print("✅ No changes detected.")


def main():
    if not MONITORED_DIR.exists():
        MONITORED_DIR.mkdir()

    if not BASELINE_FILE.exists():
        print("No baseline found.")
        print("Creating baseline...")
        create_baseline()
    else:
        print("Checking file integrity...")
        check_integrity()


if __name__ == "__main__":
    main()
