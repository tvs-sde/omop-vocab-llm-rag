"""MedEmbed wrapper. CUDA when available. Model is snapshotted into the repo
under `models/<name>/` so subsequent runs do not call the HF Hub."""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import torch
from huggingface_hub import snapshot_download
from sentence_transformers import SentenceTransformer

from .config import MODEL_EMBED, MODEL_EMBED_DIR


def _ensure_local_model() -> str:
    target = MODEL_EMBED_DIR
    # Heuristic: a populated snapshot has a config.json at the root.
    if not (target / "config.json").exists():
        target.mkdir(parents=True, exist_ok=True)
        snapshot_download(
            repo_id=MODEL_EMBED,
            local_dir=str(target),
        )
    return str(target)


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    device = "cuda" if torch.cuda.is_available() else "mps" if torch.mps.is_available() else "cpu"
    local_path = _ensure_local_model()
    return SentenceTransformer(local_path, device=device)


def encode(texts: list[str], batch_size: int = 64) -> np.ndarray:
    model = get_model()
    vecs = model.encode(
        texts,
        batch_size=batch_size,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=len(texts) > 256,
    )
    return vecs.astype("float32", copy=False)
