"""Stage 1: ask Claude to guess concept + synonyms for each event."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from tqdm import tqdm

from . import claude_client, prompts
from .config import BATCH_GUESS, MAX_TOKENS_GUESS
from .io_utils import append_jsonl, extract_json_objects


def run(events_csv: Path, out_path: Path) -> None:
    df = pd.read_csv(events_csv)
    col = df.columns[0]
    events = [str(e).strip() for e in df[col].tolist() if str(e).strip()]

    if out_path.exists():
        out_path.unlink()
    pending = list(enumerate(events))

    print(f"Stage 1: {len(pending)} events to guess (model={claude_client.MODEL_CLAUDE})")
    for start in tqdm(range(0, len(pending), BATCH_GUESS)):
        chunk = pending[start : start + BATCH_GUESS]
        prompt = prompts.build_guess_prompt([e for _, e in chunk])
        text = claude_client.complete(prompt, max_tokens=MAX_TOKENS_GUESS)
        objs = extract_json_objects(text)
        by_event = {o.get("event"): o for o in objs if isinstance(o, dict)}

        out_records = []
        for idx, event in chunk:
            o = by_event.get(event) or {"event": event, "concept": None}
            o["event_concept_id"] = idx
            o.setdefault("event_similar_terms", [])
            o.setdefault("concept_similar_terms", [])
            out_records.append(o)
        append_jsonl(out_path, out_records)

    print(f"Stage 1 done -> {out_path}")
