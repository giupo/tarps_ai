import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, Form, Request, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from tarps_ai.core.config import get_settings
from tarps_ai.core.pipeline import process_folder
from tarps_ai.core.runs import create_run, list_runs

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "templates")


@router.get("/")
def index(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "runs": list_runs(),
            "default_folder": str(get_settings().tarps_folder),
        },
    )


@router.post("/scan")
def scan(folder: str = Form("")):
    settings = get_settings()
    tarps_folder = Path(folder) if folder.strip() else settings.tarps_folder

    if not tarps_folder.is_dir():
        return RedirectResponse(
            url=f"/?error=Cartella+non+trovata:+{tarps_folder}", status_code=303
        )

    entries = process_folder(tarps_folder)
    meta = create_run(source="scan", entries=entries, image_source_dir=tarps_folder)
    return RedirectResponse(url=f"/runs/{meta.run_id}/report.html", status_code=303)


@router.post("/upload")
async def upload(files: list[UploadFile]):
    tmp_dir = Path(tempfile.mkdtemp(prefix="tarps-upload-"))
    try:
        for f in files:
            if not f.filename:
                continue
            content = await f.read()
            (tmp_dir / Path(f.filename).name).write_bytes(content)

        entries = process_folder(tmp_dir)
        meta = create_run(source="upload", entries=entries, image_source_dir=tmp_dir)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    return RedirectResponse(url=f"/runs/{meta.run_id}/report.html", status_code=303)
