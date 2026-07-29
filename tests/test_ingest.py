import json
from pathlib import Path

from tarps_ai.core.ingest import parse_folder, parse_record


def _write_pair(folder: Path, json_name: str, image_name: str, **data):
    (folder / image_name).write_bytes(b"fake-image-bytes")
    payload = {"file": image_name, **data}
    (folder / json_name).write_text(json.dumps(payload))


def test_parse_record_reads_fields(tmp_path):
    _write_pair(
        tmp_path, "a.json", "a.png",
        targetName="Radar", lat=1.5, lon=2.5, alt=100.0, heading=45.0,
    )

    record = parse_record(tmp_path / "a.json", tmp_path)

    assert record is not None
    assert record.name == "Radar"
    assert record.lat == 1.5
    assert record.lon == 2.5
    assert record.alt == 100.0
    assert record.hdg == 45.0
    assert record.image_name == "a.png"


def test_parse_record_skips_missing_image(tmp_path):
    (tmp_path / "b.json").write_text(json.dumps({"file": "missing.png"}))

    assert parse_record(tmp_path / "b.json", tmp_path) is None


def test_parse_folder_collects_all_valid_pairs(tmp_path):
    _write_pair(tmp_path, "a.json", "a.png", targetName="Radar")
    _write_pair(tmp_path, "b.json", "b.png", targetName="SAM")
    (tmp_path / "c.json").write_text(json.dumps({"file": "missing.png"}))

    records = parse_folder(tmp_path)

    assert {r.name for r in records} == {"Radar", "SAM"}
