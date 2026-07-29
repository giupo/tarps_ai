# TARPS AI

Classifica automaticamente le immagini TARPS del pod ricognitivo dell'F14 di
DCS World: legge le coppie immagine + JSON esportate dal pod, individua
tramite un modello YOLO gli eventuali bersagli ostili, e genera un report
HTML/PDF con posizione, rotta e classi rilevate per ogni bersaglio, più un
file di waypoint pronto per il DTC.

Disponibile sia come **CLI** (`tarps`) sia come **webapp** (FastAPI), entrambe
basate sulla stessa libreria core — nessuna logica duplicata tra i due front
end.

## Requisiti

- Python >= 3.14
- [uv](https://docs.astral.sh/uv/) per gestire dipendenze e ambiente virtuale
- Un modello YOLO addestrato sulle classi ostili in `model/best.pt`
  (già incluso nel repo)

## Installazione

```bash
uv sync
```

Questo crea il virtualenv in `.venv/` e installa tutte le dipendenze
(FastAPI, Typer, Ultralytics, WeasyPrint, ecc.) più il pacchetto `tarps_ai`
stesso in modalità editabile.

## Configurazione

La cartella TARPS di default è `~/Saved Games/DCS/TARPS` (quella usata da
DCS). Tutte le impostazioni sono sovrascrivibili con variabili d'ambiente
con prefisso `TARPS_` (vedi `tarps_ai/core/config.py`):

| Variabile | Default | Significato |
|---|---|---|
| `TARPS_DCS_FOLDER` | `~/Saved Games/DCS` | cartella base di DCS |
| `TARPS_TARPS_SUBFOLDER` | `TARPS` | sottocartella con json+immagini |
| `TARPS_OUTPUT_FOLDER` | `./output` | dove finiscono i run generati |
| `TARPS_MODEL_PATH` | `./model/best.pt` | path del modello YOLO |
| `TARPS_CLASSES_PATH` | `./classes.yaml` | elenco classi considerate ostili |

`classes.yaml` è la fonte unica delle classi ostili: qualunque nome elencato
sotto `names:` viene usato per filtrare le rilevazioni del modello YOLO.

## Uso da CLI

```bash
# Scansiona la cartella TARPS di default e genera report + waypoint
uv run tarps scan

# Con override espliciti
uv run tarps scan --folder /path/a/cartella/TARPS --output /path/output

# Avvia la webapp
uv run tarps serve --host 0.0.0.0 --port 8000
```

`uv run python main.py` continua a funzionare esattamente come lo script
originale (equivalente a `tarps scan` senza argomenti), per compatibilità.

Ogni `scan` crea un run in `output/runs/<run_id>/` con:

```
output/runs/<run_id>/
  report.html       # report HTML (card per ogni bersaglio ostile)
  report.pdf        # stesso report in PDF (via WeasyPrint)
  waypoints.json    # waypoint DTC nel formato {"waypoints": [...]}
  images/           # solo le immagini dei bersagli rilevati come ostili
```

e viene aggiunto a `output/runs/index.json`, l'indice usato dalla webapp per
elencare i run passati.

## Uso da webapp

```bash
uv run tarps serve
```

Poi apri `http://127.0.0.1:8000/`. La pagina permette di:

- **Scansionare una cartella locale**: indica un path sul filesystem del
  server (default: la cartella TARPS configurata) e avvia lo stesso
  pipeline della CLI.
- **Caricare file**: seleziona manualmente immagini + json TARPS dal
  browser (utile se il server non gira sulla stessa macchina di DCS).
- **Consultare i run precedenti**: elenco con link a HTML, PDF e waypoint
  JSON di ogni run già generato.

Ogni scan/upload reindirizza al report HTML appena creato
(`/runs/<run_id>/report.html`); PDF e waypoint sono raggiungibili con lo
stesso `run_id` (`/runs/<run_id>/report.pdf`, `/runs/<run_id>/waypoints.json`).

## Struttura del progetto

```
tarps_ai/
  core/
    config.py     # Settings (env-configurabile) + caricamento classes.yaml
    models.py     # modelli pydantic (TarpsRecord, Detection, ReportEntry, ...)
    detection.py  # modello YOLO caricato una sola volta + filtro classi ostili
    ingest.py     # parsing delle coppie json+immagine TARPS
    pipeline.py   # orchestrazione: ingest -> detection -> filtro ostili
    runs.py       # persistenza dei run su filesystem (output/runs/, index.json)
    report.py     # rendering HTML/PDF/waypoints dal template condiviso
  templates/
    report.html   # template Jinja2 del report (usato da CLI, PDF e webapp)
  cli/
    main.py       # comandi Typer: scan, serve
  web/
    app.py        # app FastAPI (mount statico di output/runs su /runs)
    routes.py      # rotte: /, /scan, /upload
    templates/
      index.html  # pagina di upload/scan + elenco run

main.py            # shim: richiama `tarps scan` per compatibilità con l'uso originale
classes.yaml       # elenco classi ostili (sam, radar, aaa, tank, apc, artillery, shilka, launcher)
model/best.pt      # pesi del modello YOLO
tests/             # test pytest per ingest, pipeline e report
```

## Test

```bash
uv run pytest
```

I test coprono il parsing delle coppie json+immagine, il filtro dei
bersagli ostili (con un detector finto, senza serve il modello YOLO reale)
e il rendering del report HTML/waypoints.
