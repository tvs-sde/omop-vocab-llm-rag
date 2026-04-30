"""Build prompts from the .md fragments + dynamic content."""
from __future__ import annotations

import json
from types import ModuleType


def build_guess_prompt(events: list[str], cfg: ModuleType) -> str:
    bullets = "\n".join(f"- {e}" for e in events)
    begin = cfg.PROMPT_BEGIN.read_text()
    guess_end = cfg.PROMPT_GUESS_END.read_text()
    return f"{begin}\n\n{guess_end}\n\n{bullets}\n"


def build_review_prompt(records: list[dict], cfg: ModuleType) -> str:
    """`records` items: {event_concept_id, event, candidates: [name,...]}."""
    payload = json.dumps(records, ensure_ascii=False, indent=2)
    begin = cfg.PROMPT_BEGIN.read_text()
    review_end = cfg.PROMPT_REVIEW_END.read_text()
    return (
        f"{begin}\n\n{review_end}\n\n"
        "Each event below is supplied with a list of candidate LOINC concept long names "
        "retrieved from the OMOP vocabulary. Pick the best concept for each event under "
        "the rules above. Respond with one JSON object per event (NDJSON or a JSON array) "
        "matching the §9 contract.\n\n"
        f"```json\n{payload}\n```\n"
    )
