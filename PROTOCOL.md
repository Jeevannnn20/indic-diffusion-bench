# Pilot Evaluation Protocol

## Purpose

The pilot determines whether the proposed benchmark can be executed and scored
reliably. It does not estimate general Indic reasoning performance.

## Fixed variables

- Four language forms per logical problem
- Identical underlying facts and expected answer across variants
- Answer-only instruction appended by the evaluator
- Deterministic decoding where supported
- Exact-match scoring as the primary metric

The finalized first Ollama baseline uses prompt version `answer-only-v1`,
`temperature=0`, `seed=42`, `num_predict=64`, and thinking mode disabled. A
localized system instruction and repeated user-level instruction require an
answer of at most five words. Per-prompt wall-clock latency includes local HTTP
and inference time but excludes the one-time model download.

## Independent variables

- Model family: autoregressive or diffusion
- Language form: Devanagari Hindi, Romanized Hindi, Hinglish, or English
- Reasoning category
- In a future diffusion run: number of denoising steps

## Required model metadata

Every publishable run must record:

- full model identifier and revision
- model family
- numerical precision or quantization
- prompt/chat template
- decoding parameters and seed
- inference library and version
- hardware and peak memory
- run date and code commit

## Primary analysis

Compute exact accuracy per language form and the language gap:

```text
language_gap(variant) = accuracy(english) - accuracy(variant)
```

A positive value means the model performed better in English. Because the pilot
is tiny, publish item-level outputs and confidence intervals when the benchmark
is expanded rather than interpreting small differences.

## Diffusion trace analysis (next milestone)

For each item, store the decoded answer at selected denoising steps. Classify
the trajectory as:

- wrong to correct
- correct to wrong
- wrong to different wrong
- stable correct
- stable wrong

The self-correction rate is:

```text
wrong initial trajectories ending correct / all wrong initial trajectories
```

The regression rate is:

```text
correct initial trajectories ending wrong / all correct initial trajectories
```

## Data-quality gate before expansion

Each item must be reviewed by a second bilingual speaker for:

1. Naturalness of the Hindi and Hinglish wording
2. Semantic equivalence of all four variants
3. Uniqueness of the expected answer
4. Absence of unintended cultural or dialect assumptions
5. Correct category and difficulty label

Review decisions should be committed as data changes with a changelog.
