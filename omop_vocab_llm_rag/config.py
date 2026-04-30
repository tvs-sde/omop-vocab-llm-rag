"""Static configuration constants and default paths."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "lab"

# Inputs
CONCEPTS_CSV = DATA_DIR / "lab_concepts.csv"
EVENTS_CSV = DATA_DIR / "lab_events.csv"
API_KEY_FILE = ROOT / "claude_api_key.txt"

# Prompt fragments
PROMPT_BEGIN = ROOT / "lab_test_prompt_beginning.md"
PROMPT_GUESS_END = ROOT / "lab_test_prompt_end_option_1_concept_guess.md"
PROMPT_REVIEW_END = ROOT / "lab_test_prompt_end_option_2_choice_review.md"

# Outputs
RAG_DIR = DATA_DIR / "rag_index"
STAGE1_OUT = DATA_DIR / "stage1_guesses.jsonl"
STAGE2_OUT = DATA_DIR / "stage2_candidates.jsonl"
STAGE3_OUT = DATA_DIR / "stage3_reviews.jsonl"
STAGE4_OUT = DATA_DIR / "stage4_verified.json"

# Models
MODEL_CLAUDE = os.environ.get("OMOP_CLAUDE_MODEL", "claude-haiku-4-5-20251001")#"claude-opus-4-7")
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
