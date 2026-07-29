from collections.abc import Callable, Iterable
from pathlib import Path

from tarps_ai.core.detection import detect as default_detect
from tarps_ai.core.ingest import parse_folder
from tarps_ai.core.models import Detection, ReportEntry, TarpsRecord

DetectFn = Callable[[Path | str], list[Detection]]


def build_entries(
    records: Iterable[TarpsRecord], detect_fn: DetectFn = default_detect
) -> list[ReportEntry]:
    """Run detection on each record and keep only the ones with a hostile hit."""
    entries = []
    for record in records:
        detections = detect_fn(record.image_path)
        if not detections:
            continue
        entries.append(
            ReportEntry(
                name=record.name,
                lat=record.lat,
                lon=record.lon,
                alt=record.alt,
                hdg=record.hdg,
                image_name=record.image_name,
                detections=detections,
            )
        )
    return entries


def process_folder(folder: Path, detect_fn: DetectFn = default_detect) -> list[ReportEntry]:
    """Parse every TARPS json+image pair in `folder` and filter down to hostile hits.

    Used both for scanning the local DCS TARPS folder and for uploaded files
    (which the caller first writes into a temp folder of the same shape).
    """
    records = parse_folder(folder)
    return build_entries(records, detect_fn=detect_fn)
