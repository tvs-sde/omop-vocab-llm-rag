"""Anthropic Claude client with minimal backoff."""
from __future__ import annotations

import os
import time
from functools import lru_cache

import anthropic

from .config import API_KEY_FILE, MODEL_CLAUDE


def _load_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return key.strip()
    if API_KEY_FILE.exists():
        return API_KEY_FILE.read_text().strip()
    raise SystemExit("No Claude API key found (ANTHROPIC_API_KEY or claude_api_key.txt)")


@lru_cache(maxsize=1)
def _client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=_load_key())


def complete(prompt: str, max_tokens: int, model: str = MODEL_CLAUDE) -> str:
    client = _client()
    last_err: Exception | None = None
    for attempt in range(4):
        try:
            resp = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            parts = []
            for block in resp.content:
                if getattr(block, "type", None) == "text":
                    parts.append(block.text)
            return "".join(parts)
        except (anthropic.RateLimitError, anthropic.APIStatusError, anthropic.APIConnectionError) as e:
            last_err = e
            status = getattr(e, "status_code", None)
            if status and status < 500 and not isinstance(e, anthropic.RateLimitError):
                raise
            time.sleep(2 ** attempt)
    raise SystemExit(f"Claude call failed after retries: {last_err}")
