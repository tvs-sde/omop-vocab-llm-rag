Apply the rules below in order. If after applying them no candidate is defensible, return
**NO_MATCH** rather than guessing.

Your aim is to select the best candidate for any given event. Do not pick another concept. It must be a concept from the candidates collection.

Input data

```json
{
    "event": "paracetamol",
    "candidates": [
        {
            "concept_id": 873059,
            "concept_name": "Paracetamol",
            "score": 1.0
        },
        ......
    ]
}
```

## 9. Output contract

For each event, respond with a JSON object:

```json
{
  "concept": "<matching candidate>",
  "event": "<input event name>",
  "status": "OK | modified | NO_MATCH | uncertain",
  "rationale": "<one-sentence reason>"
}
```

- `status = OK` → candidate was already correct.
- `status = modified` → candidate was wrong; `concept` is the corrected dm+d.
- `status = NO_MATCH` → event is a comment / header / unmappable row, or there is no suitable candidate
- `status = uncertain` → multiple defensible mappings; state the ambiguity briefly in `rationale`.

Do not invent dm+d long names: reproduce them exactly as they appear in the
vocabulary / retrieval context supplied to you.
