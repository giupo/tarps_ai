from datetime import datetime

from tarps_ai.core.models import Detection, ReportEntry, RunResult
from tarps_ai.core.report import build_dtc_waypoints, render_html


def _run() -> RunResult:
    entry = ReportEntry(
        name="SAM Site",
        lat=41.9,
        lon=12.5,
        alt=100.0,
        hdg=90.0,
        image_name="sam.png",
        detections=[Detection(cls_name="sam", confidence=0.8)],
    )
    return RunResult(
        run_id="test-run",
        created_at=datetime(2026, 1, 1, 12, 0, 0),
        source="scan",
        entries=[entry],
    )


def test_render_html_includes_entry_data():
    html = render_html(_run())

    assert "SAM Site" in html
    assert "images/sam.png" in html
    assert "sam" in html and "80%" in html


def test_build_dtc_waypoints_matches_entries():
    waypoints = build_dtc_waypoints(_run())

    assert waypoints == {
        "waypoints": [
            {"type": "TARGET", "name": "SAM Site", "lat": 41.9, "lon": 12.5, "alt": 100.0}
        ]
    }
