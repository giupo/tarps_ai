import json

from tarps_ai.core.models import Detection, TarpsRecord
from tarps_ai.core.pipeline import build_entries, process_folder


def _record(name: str, image_name: str = "x.png") -> TarpsRecord:
    return TarpsRecord(
        name=name, lat=0, lon=0, alt=0, hdg=0, image_path=image_name, image_name=image_name
    )


def test_build_entries_keeps_only_hits_with_detections():
    def fake_detect(path):
        return [Detection(cls_name="radar", confidence=0.9)] if "Radar" in str(path) else []

    entries = build_entries(
        [_record("Radar", image_name="Radar.png"), _record("Farmhouse", image_name="Farmhouse.png")],
        detect_fn=fake_detect,
    )

    assert [e.name for e in entries] == ["Radar"]
    assert entries[0].detections[0].cls_name == "radar"


def test_process_folder_uses_real_ingest_and_injected_detector(tmp_path):
    (tmp_path / "img.png").write_bytes(b"data")
    (tmp_path / "rec.json").write_text(json.dumps({"file": "img.png", "targetName": "Tank"}))

    entries = process_folder(
        tmp_path, detect_fn=lambda p: [Detection(cls_name="tank", confidence=0.5)]
    )

    assert len(entries) == 1
    assert entries[0].name == "Tank"


def test_process_folder_empty_when_nothing_detected(tmp_path):
    (tmp_path / "img.png").write_bytes(b"data")
    (tmp_path / "rec.json").write_text(json.dumps({"file": "img.png", "targetName": "Farmhouse"}))

    entries = process_folder(tmp_path, detect_fn=lambda p: [])

    assert entries == []
