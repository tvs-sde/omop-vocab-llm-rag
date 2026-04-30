"""Domain-specific configuration for lab tests."""
from __future__ import annotations

from pathlib import Path

from .config import ROOT

DATA_DIR = ROOT / "data" / "lab"

# Inputs
CONCEPTS_CSV = DATA_DIR / "lab_concepts.csv"
EVENTS_CSV = DATA_DIR / "lab_events_random_100.csv"

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
