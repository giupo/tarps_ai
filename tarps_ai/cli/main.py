import os
from pathlib import Path

import typer

app = typer.Typer(
    help="TARPS AI - classifica bersagli ostili dalle immagini TARPS del pod F14 DCS"
)


@app.command()
def scan(
    folder: Path | None = typer.Option(
        None, help="Cartella TARPS da scansionare (default: ~/Saved Games/DCS_F14/TARPS)"
    ),
    output: Path | None = typer.Option(
        None, help="Cartella di output per i run generati"
    ),
    model: Path | None = typer.Option(None, help="Path del modello YOLO (.pt)"),
    classes: Path | None = typer.Option(
        None, help="Path del classes.yaml con le classi ostili"
    ),
) -> None:
    """Scansiona una cartella TARPS, filtra i bersagli ostili e genera report HTML/PDF + waypoint DTC."""
    if folder is not None:
        os.environ["TARPS_TARPS_FOLDER_OVERRIDE"] = str(folder)
    if output is not None:
        os.environ["TARPS_OUTPUT_FOLDER"] = str(output)
    if model is not None:
        os.environ["TARPS_MODEL_PATH"] = str(model)
    if classes is not None:
        os.environ["TARPS_CLASSES_PATH"] = str(classes)

    from tarps_ai.core.config import get_settings

    settings = get_settings()
    tarps_folder = settings.tarps_folder

    if not tarps_folder.is_dir():
        typer.echo(f"Cartella TARPS non trovata: {tarps_folder}", err=True)
        raise typer.Exit(code=1)

    from tarps_ai.core.pipeline import process_folder
    from tarps_ai.core.runs import create_run

    entries = process_folder(tarps_folder)
    meta = create_run(source="scan", entries=entries, image_source_dir=tarps_folder)

    run_directory = settings.runs_folder / meta.run_id
    typer.echo(f"Bersagli ostili rilevati: {meta.count}")
    typer.echo(f"Report HTML generato: {run_directory / 'report.html'}")
    typer.echo(f"Report PDF generato: {run_directory / 'report.pdf'}")
    typer.echo(f"Waypoints DTC generati: {run_directory / 'waypoints.json'}")


def _default_port() -> int:
    raw = os.environ.get("PORT")
    if raw is None:
        return 8000
    try:
        return int(raw)
    except ValueError:
        typer.echo(f"Valore di $PORT non valido: {raw!r}, uso 8000", err=True)
        return 8000


@app.command()
def serve(
    host: str = typer.Option(
        "0.0.0.0" if "PORT" in os.environ else "127.0.0.1", help="Host di binding"
    ),
    port: int = typer.Option(
        _default_port(),
        help="Porta di ascolto (default: variabile d'ambiente $PORT, altrimenti 8000)",
    ),
    reload: bool = typer.Option(False, help="Ricarica automatica in sviluppo"),
) -> None:
    """Avvia la webapp FastAPI."""
    import uvicorn

    uvicorn.run("tarps_ai.web.app:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    app()
