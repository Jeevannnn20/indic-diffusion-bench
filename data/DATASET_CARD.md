# Dataset Card: IndicDiffusionBench Pilot

## Summary

The pilot contains ten deterministic reasoning items, each represented in
Devanagari Hindi, Romanized Hindi, Hinglish, and English. It is designed to test
benchmark infrastructure before a larger native-authored dataset is created.

## Current review status

`reviewed` (primary review only)

The items were reviewed on 2026-07-16 by the project owner, a fluent Hindi
speaker who studied Hindi through Grade 10. They have not been independently
reviewed by a second bilingual annotator. They should not yet be used to make
claims about a model or language community.

## Fields

- `id`: stable item identifier
- `category`: reasoning category
- `difficulty`: pilot difficulty label
- `original_language`: language in which the item was first drafted
- `review_status`: annotation review state
- `variants`: mapping from language form to chat messages
- `accepted_answers`: acceptable exact answers for each variant
- `canonical_answer`: language-neutral answer label for analysis
- `split`: dataset split
- `notes`: annotation or ambiguity notes

## Intended use

- Pipeline development
- Prompt-format testing
- Model-adapter development
- Preliminary error-taxonomy design

## Out-of-scope use

- Ranking models publicly
- Claiming broad Hindi or Indic reasoning capability
- Training on pilot questions and evaluating on the same questions
- Treating Romanized Hindi or Hinglish as a single standardized dialect

## Known limitations

- Only ten items and one primary Indic language
- Limited cultural and linguistic diversity
- Exact-match scoring rewards answer compliance as well as reasoning
- The pilot does not yet capture diffusion trajectories
- Romanization choices may not reflect all common spellings
- No inter-annotator agreement measurement yet

## Licensing

The original pilot items are released under the repository's MIT License. Model
outputs retain any restrictions imposed by the corresponding model license or
service terms.
