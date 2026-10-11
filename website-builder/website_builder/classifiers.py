"""Explicit choices by default; optional lazy-loaded research classifiers."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from website_builder.config import DATA_DIR, Settings

ZERO_SHOT_MODEL = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"


class AnswerError(ValueError):
    """The response needs clarification before the interview can advance."""


@lru_cache(maxsize=2)
def _intent_pipeline(model_path: Path):
    """Load the trained classifier once, when it is first needed."""
    if not (model_path / "model.safetensors").is_file():
        raise RuntimeError("Local classifier not found. Follow docs/models.md or disable ML mode.")
    from transformers import pipeline

    return pipeline("text-classification", model=str(model_path), tokenizer=str(model_path))


@lru_cache(maxsize=1)
def _zero_shot_pipeline():
    """Load and reuse the model that chooses between candidate answers."""
    from transformers import pipeline

    return pipeline("zero-shot-classification", model=ZERO_SHOT_MODEL)


def predict_intent(text: str, settings: Settings) -> str:
    """Translate a trained model output, such as LABEL_6, into its meaning."""
    model = _intent_pipeline(settings.intent_model_path)
    prediction = model(text, truncation=True)[0]
    labels = json.loads((DATA_DIR / "intent_labels.json").read_text(encoding="utf-8"))
    label_id = prediction["label"].removeprefix("LABEL_")
    if label_id not in labels:
        raise RuntimeError("Classifier output does not match the documented label map.")
    return labels[label_id]


def choose_answer(text: str, candidates: list[str], settings: Settings) -> str:
    """Match a listed choice; use the optional model for other wording."""
    normalized = text.casefold().rstrip(".!?")
    aliases = {"y": "yes", "yeah": "yes", "sure": "yes", "n": "no", "nope": "no"}
    normalized = aliases.get(normalized, normalized)
    for choice in candidates:
        if normalized == choice.casefold():
            return choice
    if settings.use_ml:
        result = _zero_shot_pipeline()(text, candidate_labels=candidates)
        return result["labels"][0]
    raise AnswerError("Choose one of: " + ", ".join(candidates) + ".")


def classify_answer(text: str, model_type: str, candidates: list[str], settings: Settings) -> str:
    """Validate an answer and select the handling for its question type."""
    text = text.strip()
    if not text:
        raise AnswerError("Please enter an answer.")
    if len(text) > 4000:
        raise AnswerError("Please keep each answer under 4,000 characters.")

    if model_type == "text":
        return text
    if model_type == "intent":
        return predict_intent(text, settings) if settings.use_ml else text
    if model_type == "choice" and candidates:
        return choose_answer(text, candidates, settings)
    raise ValueError("Unknown answer type or missing choices.")
