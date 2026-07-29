from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from tarps_ai.core.models import RunResult

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))


def render_html(run: RunResult) -> str:
    template = _env.get_template("report.html")
    return template.render(run=run)


def render_pdf(html: str, base_url: str) -> bytes:
    return HTML(string=html, base_url=base_url).write_pdf()


def build_dtc_waypoints(run: RunResult) -> dict:
    return {"waypoints": [wp.model_dump() for wp in run.waypoints]}
