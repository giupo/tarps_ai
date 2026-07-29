import json
import re
import shutil
import uuid
from datetime import datetime
from pathlib import Path

from tarps_ai.core.config import get_settings
from tarps_ai.core.models import ReportEntry, RunMeta, RunResult
from tarps_ai.core.report import build_dtc_waypoints, render_html, render_pdf

_RUN_ID_RE = re.compile(r"^[0-9A-Za-z_-]+$")


def _new_run_id() -> str:
    return f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"


def _index_path() -> Path:
    return get_settings().runs_folder / "index.json"


def _read_index() -> list[dict]:
    path = _index_path()
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f)


def _write_index(rows: list[dict]) -> None:
    path = _index_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(rows, f, indent=2, default=str)


def run_dir(run_id: str) -> Path:
    if not _RUN_ID_RE.fullmatch(run_id):
        raise ValueError(f"invalid run_id: {run_id!r}")
    return get_settings().runs_folder / run_id


def run_exists(run_id: str) -> bool:
    try:
        return run_dir(run_id).is_dir()
    except ValueError:
        return False


def create_run(
    source: str, entries: list[ReportEntry], image_source_dir: Path
) -> RunMeta:
    """Persist a run to disk: copy surviving images, render html/pdf/waypoints, index it."""
    run_id = _new_run_id()
    directory = run_dir(run_id)
    images_dir = directory / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    for entry in entries:
        shutil.copy2(image_source_dir / entry.image_name, images_dir / entry.image_name)

    run = RunResult(
        run_id=run_id, created_at=datetime.now(), source=source, entries=entries
    )

    html = render_html(run)
    (directory / "report.html").write_text(html, encoding="utf-8")
    (directory / "report.pdf").write_bytes(render_pdf(html, base_url=str(directory)))
    (directory / "waypoints.json").write_text(
        json.dumps(build_dtc_waypoints(run), indent=2), encoding="utf-8"
    )

    meta = RunMeta(run_id=run_id, created_at=run.created_at, source=source, count=len(entries))
    rows = _read_index()
    rows.append(meta.model_dump())
    _write_index(rows)
    return meta


def list_runs() -> list[RunMeta]:
    metas = [RunMeta(**row) for row in _read_index()]
    return sorted(metas, key=lambda m: m.created_at, reverse=True)
