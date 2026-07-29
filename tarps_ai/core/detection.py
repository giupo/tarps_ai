from functools import lru_cache
from pathlib import Path

from ultralytics import YOLO

from tarps_ai.core.config import get_settings, load_hostile_classes
from tarps_ai.core.models import Detection


@lru_cache
def get_model() -> YOLO:
    return YOLO(str(get_settings().model_path))


def detect(image_path: Path | str) -> list[Detection]:
    """Run the YOLO model on an image and return only hostile-class detections."""
    hostile_classes = set(load_hostile_classes())
    model = get_model()
    results = model(str(image_path))

    detections = []
    for r in results:
        for box in r.boxes:
            cls_name = model.names[int(box.cls)]
            if cls_name in hostile_classes:
                detections.append(
                    Detection(cls_name=cls_name, confidence=float(box.conf))
                )
    return detections
