from datetime import datetime

from pydantic import BaseModel


class TarpsRecord(BaseModel):
    """One TARPS json + image pair, before detection has run."""

    name: str
    lat: float
    lon: float
    alt: float
    hdg: float
    image_path: str
    image_name: str


class Detection(BaseModel):
    cls_name: str
    confidence: float


class ReportEntry(BaseModel):
    """A TarpsRecord that survived the hostile-detection filter."""

    name: str
    lat: float
    lon: float
    alt: float
    hdg: float
    image_name: str
    detections: list[Detection]


class Waypoint(BaseModel):
    type: str = "TARGET"
    name: str
    lat: float
    lon: float
    alt: float


class RunResult(BaseModel):
    run_id: str
    created_at: datetime
    source: str
    entries: list[ReportEntry]

    @property
    def waypoints(self) -> list[Waypoint]:
        return [
            Waypoint(name=e.name, lat=e.lat, lon=e.lon, alt=e.alt)
            for e in self.entries
        ]


class RunMeta(BaseModel):
    """Lightweight index record for a past run (see core/runs.py)."""

    run_id: str
    created_at: datetime
    source: str
    count: int
