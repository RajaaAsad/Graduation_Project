"""Configuration with no network requests or filesystem writes at import time."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(__file__).resolve().parent / "data"
ASSETS_DIR = PROJECT_ROOT / "assets"


@dataclass(frozen=True)
class Settings:
    """Runtime settings. Credentials stay on the server."""

    api_key: str = ""
    model: str = "gpt-4.1-mini"
    intent_model_path: Path = PROJECT_ROOT / "models" / "intent-classifier"
    use_ml: bool = False


def load_settings(env_file: Path | None = None) -> Settings:
    """Read the project .env; existing environment variables take precedence."""
    from dotenv import dotenv_values

    values = dict(dotenv_values(env_file or PROJECT_ROOT / ".env"))
    # Values set in the terminal or hosting service override the local file.
    values.update(os.environ)
    key = (values.get("OPENAI_API_KEY") or "").strip()
    if key.startswith("your-"):
        key = ""
    model_path = Path(values.get("INTENT_MODEL_PATH") or "models/intent-classifier")
    if not model_path.is_absolute():
        model_path = PROJECT_ROOT / model_path
    return Settings(
        api_key=key,
        model=(values.get("OPENAI_MODEL") or "gpt-4.1-mini").strip(),
        intent_model_path=model_path.resolve(),
        use_ml=(values.get("USE_ML_CLASSIFIERS") or "false").lower() == "true",
    )
