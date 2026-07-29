from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from tarps_ai.core.config import get_settings
from tarps_ai.web.routes import router


def create_app() -> FastAPI:
    settings = get_settings()
    settings.runs_folder.mkdir(parents=True, exist_ok=True)

    fastapi_app = FastAPI(title="TARPS AI")
    fastapi_app.include_router(router)
    # Serves report.html / report.pdf / waypoints.json / images/* directly,
    # so relative image paths inside report.html resolve correctly.
    fastapi_app.mount(
        "/runs", StaticFiles(directory=settings.runs_folder), name="runs"
    )
    return fastapi_app


app = create_app()
