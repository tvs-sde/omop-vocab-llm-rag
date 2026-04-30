# omop-vocab-llm-rag

Map free-text UK hospital lab event names to OMOP/LOINC concepts using
**Claude Opus 4.7** + a RAG index built with the
[`abhinand/MedEmbed-large-v0.1`](https://huggingface.co/abhinand/MedEmbed-large-v0.1)
embedding model.

## Pipeline

1. **Guess** — Claude proposes a concept name + synonyms for each event.
2. **Retrieve** — bulk vector search over `lab_concepts.csv` collects candidates.
3. **Review** — Claude picks the best candidate per event under the rules in
   `lab_test_prompt_beginning.md`.
4. **Verify** — resolve each reviewed concept name to a real `concept_id` by
   matching against the RAG corpus (exact name match, with a semantic top-1
   fallback). `NO_MATCH` rows from Stage 3 are preserved with a null id.

## Install

```bash
pip install -e .
```

GPU is used automatically when CUDA is available; otherwise it falls back to CPU.
The Claude API key is read from `claude_api_key.txt` (or `ANTHROPIC_API_KEY`).

## Usage

```bash
# 1. Build the RAG index (required once, prerequisite for retrieve)
omop-map build-rag

# 2. Run the full pipeline
omop-map run-all

# Or step-by-step:
omop-map guess
omop-map retrieve
omop-map review
omop-map verify

# Ad-hoc RAG query for debugging
omop-map rag-query "potassium" --k 5
```

Outputs land in `data/lab/`:

- `rag_index/index.faiss`, `rag_index/concepts.parquet`
- `stage1_guesses.jsonl`
- `stage2_candidates.jsonl`
- `stage3_reviews.jsonl`
- `stage4_verified.json` — final array of `{event, status, review_concept,
  rationale, concept_id, matched_concept_name, match_method, match_score}`.

## Config

Override the Claude model with `OMOP_CLAUDE_MODEL` (default `claude-opus-4-7`).
Other constants (batch sizes, top-k) live in `omop_vocab_llm_rag/config.py`.
