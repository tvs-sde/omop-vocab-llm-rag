"""IO helpers: JSONL append/read, robust JSON extraction from LLM text."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable, Iterator


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def append_jsonl(path: Path, records: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def append_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(text)
        if not text.endswith("\n"):
            f.write("\n")


_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def extract_json_objects(text: str) -> list[dict]:
    """Pull JSON objects out of LLM text. Accepts a top-level array, NDJSON,
    or fenced code blocks. Returns empty list if nothing parses."""
    candidates: list[str] = []
    for m in _FENCE_RE.finditer(text):
        candidates.append(m.group(1).strip())
    candidates.append(text.strip())

    for blob in candidates:
        # Try array
        try:
            parsed = json.loads(blob)
            if isinstance(parsed, list):
                return [x for x in parsed if isinstance(x, dict)]
            if isinstance(parsed, dict):
                return [parsed]
        except json.JSONDecodeError:
            pass
        # Try NDJSON
        rows = []
        ok = True
        for line in blob.splitlines():
            line = line.strip().rstrip(",")
            if not line:
                continue
            try:
                obj = json.loads(line)
                if isinstance(obj, dict):
                    rows.append(obj)
                else:
                    ok = False
                    break
            except json.JSONDecodeError:
                ok = False
                break
        if ok and rows:
            return rows

    # Last resort: find balanced { ... } objects
    return list(_iter_balanced_objects(text))


def _iter_balanced_objects(text: str) -> Iterator[dict]:
    depth = 0
    start = -1
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start >= 0:
                blob = text[start : i + 1]
                try:
                    obj = json.loads(blob)
                    if isinstance(obj, dict):
                        yield obj
                except json.JSONDecodeError:
                    pass
                start = -1
