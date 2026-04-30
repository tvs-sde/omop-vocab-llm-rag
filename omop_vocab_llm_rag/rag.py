"""FAISS-backed RAG over lab_concepts.csv."""
from __future__ import annotations

from pathlib import Path

import faiss
import numpy as np
import pandas as pd

from . import embedder


def build(concepts_csv: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(concepts_csv)
    if not {"concept_id", "concept_name"}.issubset(df.columns):
        raise SystemExit(f"{concepts_csv} must have concept_id, concept_name columns")
    df = df.dropna(subset=["concept_name"]).reset_index(drop=True)

    vecs = embedder.encode(df["concept_name"].tolist())
    index = faiss.IndexFlatIP(vecs.shape[1])
    index.add(vecs)

    faiss.write_index(index, str(out_dir / "index.faiss"))
    df[["concept_id", "concept_name"]].to_parquet(out_dir / "concepts.parquet")
    print(f"Built RAG: {len(df)} concepts -> {out_dir}")


class RagIndex:
    def __init__(self, out_dir: Path):
        self.index = faiss.read_index(str(out_dir / "index.faiss"))
        self.df = pd.read_parquet(out_dir / "concepts.parquet").reset_index(drop=True)

    def query(self, texts: list[str], k: int) -> list[list[dict]]:
        if not texts:
            return []
        vecs = embedder.encode(texts)
        scores, idxs = self.index.search(vecs, k)
        results: list[list[dict]] = []
        for row_scores, row_idxs in zip(scores, idxs):
            row = []
            for score, idx in zip(row_scores, row_idxs):
                if idx < 0:
                    continue
                rec = self.df.iloc[int(idx)]
                row.append(
                    {
                        "concept_id": int(rec["concept_id"]),
                        "concept_name": str(rec["concept_name"]),
                        "score": float(score),
                    }
                )
            results.append(row)
        return results


def load(out_dir: Path) -> RagIndex:
    return RagIndex(out_dir)
