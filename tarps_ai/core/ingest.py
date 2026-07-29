import json
from pathlib import Path

from tarps_ai.core.models import TarpsRecord


def parse_record(json_path: Path, image_dir: Path) -> TarpsRecord | None:
    """Parse a single TARPS json file and locate its associated image.

    Returns None if the json has no matching image on disk, mirroring the
    "skip if missing" behaviour of the original script.
    """
    with open(json_path) as f:
        data = json.load(f)

    image_name = data.get("file")
    if not image_name:
        return None

    image_path = image_dir / image_name
    if not image_path.exists():
        return None

    return TarpsRecord(
        name=data.get("targetName", "Ostile rilevato"),
        lat=data.get("lat", 0),
        lon=data.get("lon", 0),
        alt=data.get("alt", 0),
        hdg=data.get("heading", 0),
        image_path=str(image_path),
        image_name=image_name,
    )


def parse_folder(folder: Path) -> list[TarpsRecord]:
    """Parse every *.json in a folder into TarpsRecords, skipping unmatched images."""
    records = []
    for json_path in sorted(folder.glob("*.json")):
        record = parse_record(json_path, folder)
        if record is not None:
            records.append(record)
    return records
