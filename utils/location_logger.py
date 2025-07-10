# utils/location_logger.py
from pathlib import Path

FILE = Path("unknown_locations.txt")

def log(location: str):
    """
    Appends location string to unknown_locations.txt
    (only if not logged already).
    """
    if not FILE.exists():
        FILE.touch()
    location = location.strip()
    if not location:
        return
    lines = {line.strip() for line in FILE.read_text(encoding="utf-8").splitlines()}
    if location not in lines:
        with FILE.open("a", encoding="utf-8") as f:
            f.write(location + "\n")
