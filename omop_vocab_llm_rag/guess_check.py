"""Stage 1.5 (guess_check): re-run the guess prompt for any stage-1 records
whose `concept` is null, in case the first pass produced an invalid response."""
from __future__ import annotations

import json
from pathlib import Path
from types import ModuleType

from tqdm import tqdm

from . import claude_client, prompts
from .config import BATCH_GUESS, MAX_TOKENS_GUESS
from .io_utils import extract_json_objects, read_jsonl


def _is_null(value) -> bool:
    return value in (None, "", "null")


def _retry_chunk(chunk: list[dict], cfg: ModuleType) -> dict[int, dict]:
    prompt = prompts.build_guess_prompt([r["event"] for r in chunk], cfg)
    text = claude_client.complete(prompt, max_tokens=MAX_TOKENS_GUESS)
    objs = extract_json_objects(text)
    by_event = {o.get("event"): o for o in objs if isinstance(o, dict)}

    updated: dict[int, dict] = {}
    for r in chunk:
        idx = r["event_concept_id"]
        o = by_event.get(r["event"])
        if o is None:
            updated[idx] = r
            continue
        o["event_concept_id"] = idx
        o.setdefault("event_similar_terms", [])
        o.setdefault("concept_similar_terms", [])
        updated[idx] = o
    return updated


def run(in_out_path: Path, cfg: ModuleType) -> None:
    records = read_jsonl(in_out_path)
    if not records:
        raise SystemExit(f"No stage-1 records found at {in_out_path}")

    null_records = [r for r in records if _is_null(r.get("concept"))]
    if not null_records:
        print(f"Guess-check: nothing to do (0 null concepts in {in_out_path})")
        return

    print(
        f"Guess-check: re-running {len(null_records)}/{len(records)} null-concept "
        f"records (model={claude_client.MODEL_CLAUDE})"
    )

    updated_by_id: dict[int, dict] = {}
    for start in tqdm(range(0, len(null_records), BATCH_GUESS)):
        chunk = null_records[start : start + BATCH_GUESS]
        updated_by_id.update(_retry_chunk(chunk, cfg))

    new_records = [updated_by_id.get(r["event_concept_id"], r) for r in records]

    with in_out_path.open("w") as f:
        for r in new_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    fixed = sum(
        1
        for r in new_records
        if r["event_concept_id"] in updated_by_id and not _is_null(r.get("concept"))
    )
    print(f"Guess-check done -> {in_out_path} ({fixed} now have a concept)")
