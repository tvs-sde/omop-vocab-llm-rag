"""Stage 3: ask Claude to pick the best candidate per event. Output JSONL."""
from __future__ import annotations

import time
from pathlib import Path
from types import ModuleType

from tqdm import tqdm

from . import claude_client, prompts
from .config import BATCH_REVIEW, MAX_TOKENS_REVIEW, REQUEST_DELAY_SECONDS
from .io_utils import append_jsonl, extract_json_objects, read_jsonl


def run(in_path: Path, out_path: Path, cfg: ModuleType) -> None:
    stage2 = read_jsonl(in_path)
    if not stage2:
        raise SystemExit(f"No stage-2 records found at {in_path}")

    if out_path.exists():
        out_path.unlink()

    print(f"Stage 3: {len(stage2)} records, batch={BATCH_REVIEW} (model={claude_client.MODEL_CLAUDE})")
    for start in tqdm(range(0, len(stage2), BATCH_REVIEW)):
        chunk = stage2[start : start + BATCH_REVIEW]
        payload = [
            {
                "event": r.get("event"),
                "candidates": [c["concept_name"] for c in r.get("candidates", [])],
            }
            for r in chunk
        ]
        prompt = prompts.build_review_prompt(payload, cfg)
        text = claude_client.complete(prompt, max_tokens=MAX_TOKENS_REVIEW)
        time.sleep(REQUEST_DELAY_SECONDS)
        objs = extract_json_objects(text)
        append_jsonl(out_path, [o for o in objs if isinstance(o, dict)])

    print(f"Stage 3 done -> {out_path}")

