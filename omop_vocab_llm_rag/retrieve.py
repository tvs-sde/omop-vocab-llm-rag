"""Stage 2: bulk RAG retrieval per stage-1 record."""
from __future__ import annotations

from pathlib import Path

from tqdm import tqdm

from . import rag
from .config import TOPK_CONCEPT, TOPK_EVENT, TOPK_TERM
from .io_utils import append_jsonl, read_jsonl


def _as_list(v) -> list[str]:
    if not v:
        return []
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    return [str(v).strip()]


def run(in_path: Path, rag_dir: Path, out_path: Path) -> None:
    stage1 = read_jsonl(in_path)
    if not stage1:
        raise SystemExit(f"No stage-1 records found at {in_path}")

    if out_path.exists():
        out_path.unlink()
    pending = stage1

    # Build one big batch of (record_idx, kind, k, text)
    queries: list[tuple[int, int]] = []  # (record_idx, k)
    texts: list[str] = []
    record_query_ranges: list[list[tuple[int, int]]] = []  # per record: list of (start, end) into texts

    for rec_idx, rec in enumerate(pending):
        ranges: list[tuple[int, int]] = []
        # event
        event = (rec.get("event") or "").strip()
        if event:
            s = len(texts); texts.append(event); queries.append((rec_idx, TOPK_EVENT))
            ranges.append((s, s + 1))
        else:
            ranges.append((-1, -1))
        # concept
        concept = (rec.get("concept") or "")
        concept = concept.strip() if isinstance(concept, str) else ""
        if concept:
            s = len(texts); texts.append(concept); queries.append((rec_idx, TOPK_CONCEPT))
            ranges.append((s, s + 1))
        else:
            ranges.append((-1, -1))
        # event_similar_terms (sic)
        ets = _as_list(rec.get("event_similar_terms"))
        if ets:
            s = len(texts)
            for t in ets:
                texts.append(t); queries.append((rec_idx, TOPK_TERM))
            ranges.append((s, len(texts)))
        else:
            ranges.append((-1, -1))
        # concept_similar_terms
        cts = _as_list(rec.get("concept_similar_terms"))
        if cts:
            s = len(texts)
            for t in cts:
                texts.append(t); queries.append((rec_idx, TOPK_TERM))
            ranges.append((s, len(texts)))
        else:
            ranges.append((-1, -1))
        record_query_ranges.append(ranges)

    print(f"Stage 2: {len(pending)} records, {len(texts)} bulk queries")
    index = rag.load(rag_dir)

    # Run searches in two groups by k (FAISS search expects single k per call).
    results_by_qidx: list[list[dict]] = [[] for _ in range(len(texts))]
    for k in {q[1] for q in queries}:
        sub_idxs = [i for i, q in enumerate(queries) if q[1] == k]
        sub_texts = [texts[i] for i in sub_idxs]
        sub_results = index.query(sub_texts, k=k)
        for i, res in zip(sub_idxs, sub_results):
            results_by_qidx[i] = res

    out_records = []
    for rec_idx, rec in enumerate(tqdm(pending, desc="merge")):
        ranges = record_query_ranges[rec_idx]
        merged: dict[int, dict] = {}
        for start, end in ranges:
            if start < 0:
                continue
            for qi in range(start, end):
                for cand in results_by_qidx[qi]:
                    cid = cand["concept_id"]
                    prev = merged.get(cid)
                    if prev is None or cand["score"] > prev["score"]:
                        merged[cid] = cand
        candidates = sorted(merged.values(), key=lambda x: x["score"], reverse=True)
        out_records.append(
            {
                "event": rec.get("event"),
                "candidates": candidates,
            }
        )

    append_jsonl(out_path, out_records)
    print(f"Stage 2 done -> {out_path}")
