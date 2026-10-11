"""Interview data and a UI-independent state machine."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache

from website_builder.classifiers import classify_answer
from website_builder.config import DATA_DIR, Settings

PAGE_TYPES = {
    "landing": "Landing page",
    "signin": "Sign-in page",
    "signup": "Sign-up page",
    "event": "Event page",
    "soon": "Coming soon page",
    "contact": "Contact page",
    "blog": "Blog",
    "restaurant": "Restaurant page",
}


@dataclass(frozen=True)
class Step:
    """One question, its answer type, and the condition for asking it."""

    question: str
    dependencies: str
    model_type: str
    candidate_labels: tuple[str, ...]


@lru_cache(maxsize=1)
def load_flows() -> dict[str, tuple[Step, ...]]:
    """Load and validate all interview definitions before presenting questions."""
    flow_file = DATA_DIR / "question_flows.json"
    raw = json.loads(flow_file.read_text(encoding="utf-8"))
    if set(raw) != set(PAGE_TYPES):
        raise ValueError("Interview definitions do not match the supported page types.")
    result = {}
    for name, entries in raw.items():
        if not entries:
            raise ValueError(f"Empty interview: {name}")
        steps = []
        for entry in entries:
            step = Step(
                question=entry["question"],
                dependencies=entry["dependencies"],
                model_type=entry["model_type"],
                candidate_labels=tuple(str(label) for label in entry["candidate_labels"]),
            )
            if step.dependencies not in {"always", "yes", "no", "color", "image"}:
                raise ValueError(f"Invalid dependency in {name}")
            if step.model_type not in {"text", "intent", "choice"}:
                raise ValueError(f"Invalid answer type in {name}")
            if step.model_type == "choice" and not step.candidate_labels:
                raise ValueError(f"Missing choices in {name}")
            steps.append(step)
        result[name] = tuple(steps)
    return result


@dataclass
class Interview:
    """Independent state per Streamlit session; failed answers do not advance it."""

    page_type: str
    index: int = 0
    answers: list[dict[str, str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.page_type not in PAGE_TYPES:
            raise ValueError("Unsupported page type.")

    @property
    def steps(self) -> tuple[Step, ...]:
        return load_flows()[self.page_type]

    @property
    def complete(self) -> bool:
        return self.index >= len(self.steps)

    @property
    def current(self) -> Step:
        if self.complete:
            raise ValueError("This interview is already complete.")
        return self.steps[self.index]

    def answer(self, text: str, settings: Settings) -> str:
        """Check the answer, save it, and move to the next relevant question."""
        step = self.current
        answer = classify_answer(text, step.model_type, list(step.candidate_labels), settings)
        self.answers.append({"question": step.question, "answer": answer})
        self.index += 1
        # Example: choosing "color" means the image question should be skipped.
        while not self.complete:
            dependency = self.current.dependencies
            if dependency == "always" or dependency == answer.casefold():
                break
            self.index += 1
        return answer

    def design_brief(self) -> str:
        if not self.complete:
            raise ValueError("Finish the interview before generating a design.")
        return json.dumps(
            {"page_type": PAGE_TYPES[self.page_type], "requirements": self.answers},
            ensure_ascii=False,
        )
