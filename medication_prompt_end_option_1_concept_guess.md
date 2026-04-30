Whenever you return a result, also include up to three synonyms or similar terms for both the event (medication/device name) and the concept.

## 9. Output contract

For each event, respond with a JSON object:

```json
{
  "event": "<input event name>",
  "concept": "<chosen dm+d concept long name, or null>",
  "event_similar_terms": ["<event synonym 1>", "<event synonym 2>", "<event synonym 3>"],
  "concept_similar_terms": ["<concept synonym 1>", "<concept synonym 2>", "<concept synonym 3>"],
}
```

Do not invent dm+d long names: reproduce them exactly as they appear in the
vocabulary / retrieval context supplied to you.


Don't include any notes or reasoning. Just return the contracted JSON object.


Review the following events
