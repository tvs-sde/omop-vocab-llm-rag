"""Build prompts from the .md fragments + dynamic content."""
from __future__ import annotations

import json
from functools import lru_cache

from .config import PROMPT_BEGIN, PROMPT_GUESS_END, PROMPT_REVIEW_END


@lru_cache(maxsize=1)
def _begin() -> str:
    return PROMPT_BEGIN.read_text()


@lru_cache(maxsize=1)
def _guess_end() -> str:
    return PROMPT_GUESS_END.read_text()


@lru_cache(maxsize=1)
def _review_end() -> str:
    return PROMPT_REVIEW_END.read_text()


def build_guess_prompt(events: list[str]) -> str:
    bullets = "\n".join(f"- {e}" for e in events)
    return f"{_begin()}\n\n{_guess_end()}\n\n{bullets}\n"


def build_review_prompt(records: list[dict]) -> str:
    """`records` items: {event_concept_id, event, candidates: [name,...]}."""
    payload = json.dumps(records, ensure_ascii=False, indent=2)
    return (
        f"{_begin()}\n\n{_review_end()}\n\n"
        "Each event below is supplied with a list of candidate LOINC concept long names "
        "retrieved from the OMOP vocabulary. Pick the best concept for each event under "
        "the rules above. Respond with one JSON object per event (NDJSON or a JSON array) "
        "matching the §9 contract.\n\n"
        f"```json\n{payload}\n```\n"
    )
