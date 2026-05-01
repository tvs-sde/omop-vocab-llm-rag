"""Shared configuration constants and domain-config loader."""
from __future__ import annotations

import importlib
import os
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parent.parent

# Shared inputs
API_KEY_FILE = ROOT / "claude_api_key.txt"

# Models
MODEL_CLAUDE = os.environ.get("OMOP_CLAUDE_MODEL", "claude-haiku-4-5-20251001")
MODEL_EMBED = "abhinand/MedEmbed-large-v0.1"
MODEL_EMBED_DIR = ROOT / "models" / "MedEmbed-large-v0.1"

# Batch / retrieval sizes
BATCH_GUESS = 50
BATCH_REVIEW = 50
TOPK_EVENT = 10
TOPK_CONCEPT = 5
TOPK_TERM = 3

# Claude
MAX_TOKENS_GUESS = 16000
MAX_TOKENS_REVIEW = 16000


# Request rate limiting
REQUEST_DELAY_SECONDS = 30

# Domains
_VALID_DOMAINS = ("labs", "meds")


def get_domain_config(domain: str) -> ModuleType:
    if domain not in _VALID_DOMAINS:
        raise SystemExit(f"Unknown domain {domain!r}. Choose from: {', '.join(_VALID_DOMAINS)}")
    return importlib.import_module(f".config_{domain}", package=__package__)
