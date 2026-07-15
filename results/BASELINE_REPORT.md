# Qwen3 1.7B Pilot Baseline

## Status

Preliminary pipeline-validation result. The benchmark has only ten items and
has not received an independent second-language review. These numbers must not
be presented as general evidence about Hindi or any model family.

## Run configuration

| Field | Value |
|---|---|
| Date | 2026-07-16 |
| Model | `qwen3:1.7b` |
| Ollama model ID | `8f68893c685c` |
| Reported parameters | 2.0B |
| Quantization | Q4_K_M |
| Local package size | 1.4 GB; 1.5 GB loaded |
| Runtime | Ollama 0.32.0 |
| Hardware | Apple M2 MacBook Air, 8 GB unified memory |
| Processor during run | 100% Apple Metal GPU |
| Runtime context | 4096 tokens |
| Prompt version | `answer-only-v1` |
| Thinking | Disabled |
| Temperature | 0 |
| Seed | 42 |
| Maximum generated tokens | 64 |

## Automated results

| Metric | Result |
|---|---:|
| Evaluations | 40 |
| Strict exact accuracy | 22.5% (9/40) |
| Answer-mention rate | 40.0% (16/40) |
| Mean wall-clock latency | 0.535 seconds |
| Total wall-clock latency | 21.413 seconds |

### Strict exact accuracy by language form

| Variant | Accuracy |
|---|---:|
| English | 60% |
| Hindi (Devanagari) | 0% |
| Romanized Hindi | 10% |
| Hinglish | 20% |

The English-minus-variant gaps were 60 points for Devanagari Hindi, 50 for
Romanized Hindi, and 40 for Hinglish. With ten items per variant, one answer
changes a score by ten points; these gaps are descriptive, not estimates.

### Strict exact accuracy by category

| Category | Accuracy |
|---|---:|
| Arithmetic and time | 0.0% |
| Family relationships | 12.5% |
| Spatial reasoning | 12.5% |
| Logical constraints | 62.5% |
| Multi-turn correction | 25.0% |

## Manual semantic adjudication

Strict exact match intentionally penalizes responses that ignore the
answer-only instruction. A manual review found five additional responses whose
answer was semantically correct but verbose or cross-script. This produces
14/40, or **35% manually adjudicated semantic accuracy**.

| Variant | Semantic accuracy | Correct items |
|---|---:|---:|
| English | 70% | 7/10 |
| Hindi (Devanagari) | 10% | 1/10 |
| Romanized Hindi | 40% | 4/10 |
| Hinglish | 20% | 2/10 |

Manual semantic accuracy by category was 12.5% for arithmetic/time, 37.5% for
family relationships, 12.5% for spatial reasoning, 87.5% for logical
constraints, and 25% for multi-turn correction.

The item-level decisions and error labels are recorded in
`qwen3-1.7b-v1-adjudication.csv` so the manual metric can be audited or revised.

## What the inspection revealed

1. **The language gap is visible even in this tiny pilot.** The model solved
   seven English forms semantically but only one Devanagari Hindi form.
2. **Romanized prompts sometimes caused script drift.** One Romanized Hindi
   response switched into Devanagari while expressing the correct relationship.
3. **Arithmetic and direction reasoning were unexpectedly weak.** The model
   returned `12:30 PM` for `9:35 + 2:25` in English and answered `south` after
   two right turns from east.
4. **Logical assignment was the strongest category.** Seven of eight outputs
   were semantically correct across the two logical-constraint items.
5. **Multi-turn correction did not transfer evenly.** Both English correction
   items were correct; all six Hindi, Romanized Hindi, and Hinglish outputs were
   semantically wrong or did not provide an answer.
6. **Answer-mention rate is not trustworthy as an accuracy metric.** A model can
   echo a candidate name from the question while giving a wrong conclusion.
   Strict exact match should remain the reproducible primary metric, paired with
   blinded human adjudication for analysis.

## Diagnostic run retained

An earlier run used a weaker user-only instruction and a 32-token cap. It scored
12.5% strict exact accuracy and showed several truncations. It is retained as
`qwen3-1.7b.jsonl` for auditability but superseded by the `answer-only-v1` run.

## Next experiment

Run a stronger 4B autoregressive model with the identical prompt version and
settings. If local memory pressure is acceptable, use a quantized local model;
otherwise run it on Colab. Only after that comparison should the diffusion
baseline be introduced.
