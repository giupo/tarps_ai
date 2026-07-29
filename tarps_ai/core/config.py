import os
from functools import lru_cache
from pathlib import Path

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TARPS_")

    dcs_folder: Path = Path(os.path.expanduser("~/Saved Games/DCS"))
    tarps_subfolder: str = "TARPS"
    tarps_folder_override: Path | None = None
    output_folder: Path = REPO_ROOT / "output"
    model_path: Path = REPO_ROOT / "model" / "best.pt"
    classes_path: Path = REPO_ROOT / "classes.yaml"

    @property
    def tarps_folder(self) -> Path:
        return self.tarps_folder_override or (self.dcs_folder / self.tarps_subfolder)

    @property
    def runs_folder(self) -> Path:
        return self.output_folder / "runs"


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def load_hostile_classes(classes_path: Path | None = None) -> list[str]:
    path = classes_path or get_settings().classes_path
    with open(path) as f:
        data = yaml.safe_load(f)
    return list(data["names"])
