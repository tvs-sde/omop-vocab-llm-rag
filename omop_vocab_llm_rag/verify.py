"""Stage 4: resolve each reviewed concept name to a concept_id by exact name
match against the RAG corpus, falling back to the top RAG candidate. Records
with status NO_MATCH are emitted with no concept_id but are not dropped."""
from __future__ import annotations

import json
from pathlib import Path

from tqdm import tqdm

from . import rag
from .io_utils import read_jsonl


def run(in_path: Path, rag_dir: Path, out_path: Path) -> None:
    stage3 = read_jsonl(in_path)
    if not stage3:
        raise SystemExit(f"No stage-3 records found at {in_path}")

    index = rag.load(rag_dir)
    name_to_id = dict(zip(index.df["concept_name"].astype(str), index.df["concept_id"].astype(int)))

    # Collect names needing semantic lookup (not in exact map and not NO_MATCH)
    to_lookup: list[tuple[int, str]] = []
    for i, r in enumerate(stage3):
        if (r.get("status") or "").upper() == "NO_MATCH":
            continue
        name = r.get("concept")
        if not name or not isinstance(name, str):
            continue
        if name not in name_to_id:
            to_lookup.append((i, name))

    print(f"Stage 4: {len(stage3)} records, {len(to_lookup)} need semantic lookup")
    semantic: dict[int, dict] = {}
    if to_lookup:
        results = index.query([name for _, name in to_lookup], k=1)
        for (i, _), res in zip(to_lookup, results):
            semantic[i] = res[0] if res else {}

    out: list[dict] = []
    for i, r in enumerate(tqdm(stage3, desc="verify")):
        status = (r.get("status") or "").upper()
        name = r.get("concept")
        rec = {
            "event": r.get("event"),
            "status": r.get("status"),
            "review_concept": name,
            "rationale": r.get("rationale"),
            "concept_id": None,
            "matched_concept_name": None,
            "match_method": None,
            "match_score": None,
        }
        if status == "NO_MATCH" or not name or not isinstance(name, str):
            out.append(rec)
            continue
        if name in name_to_id:
            rec["concept_id"] = int(name_to_id[name])
            rec["matched_concept_name"] = name
            rec["match_method"] = "exact"
            rec["match_score"] = 1.0
        else:
            cand = semantic.get(i, {})
            if cand:
                rec["concept_id"] = cand.get("concept_id")
                rec["matched_concept_name"] = cand.get("concept_name")
                rec["match_method"] = "semantic"
                rec["match_score"] = cand.get("score")
        out.append(rec)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"Stage 4 done -> {out_path}")
