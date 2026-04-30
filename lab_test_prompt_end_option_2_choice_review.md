Apply the rules below in order. If after applying them no candidate is defensible, return
**NO_MATCH** rather than guessing.

Your aim is to select the bast candidate for any given event. Do not pick another concept. It must be a concept from the candidates collection.

Input data

```json
{
    "event": "Haemoglobin levels in blood",
    "candidates": [
        {
            "concept_id": 3000963,
            "concept_name": "Hemoglobin [Mass/volume] in Blood",
            "score": 1.0
        },
        {
            "concept_id": 3002173,
            "concept_name": "Hemoglobin [Mass/volume] in Arterial blood",
            "score": 0.9705100655555725
        },
        ......
    ]
}
```

## 9. Output contract

For each event, respond with a JSON object:

```json
{
  "concept": "<matching candidate>"
  "event": "<input event name>",
  "status": "OK | modified | NO_MATCH | uncertain",
}
```

- `status = OK` → candidate was already correct.
- `status = modified` → candidate was wrong; `concept` is the corrected LOINC.
- `status = NO_MATCH` → event is a comment / header / unmappable row (§7), or no
  candidate passes §8 step 1.
- `status = uncertain` → multiple defensible mappings (e.g. presence vs
  moles/volume dipstick, INR vs PT, blood vs venous blood); state the ambiguity
  briefly in `rationale`.

Do not invent LOINC long names: reproduce them exactly as they appear in the
vocabulary / retrieval context supplied to you.
