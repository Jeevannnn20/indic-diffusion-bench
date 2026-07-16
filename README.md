# IndicDiffusionBench

IndicDiffusionBench is an early-stage benchmark for measuring whether language
models solve the same reasoning problem consistently across Devanagari Hindi,
Romanized Hindi, natural Hinglish, and English.

The longer-term research question is whether diffusion language models repair
reasoning mistakes differently from autoregressive models, particularly under
script changes, code-switching, and multi-turn corrections.

## Status

This repository currently contains a **10-item pipeline-validation pilot**. The
questions received a primary review from a Hindi speaker who studied the
language through Grade 10. They have not yet been independently checked by a
second Hindi speaker, so the results must not be presented as a research
finding. The pilot exists to validate the data format, model adapters, scoring,
and result export before the dataset is expanded.

## Hypothesis

Small multilingual models will perform worse on native Hindi and Hinglish
reasoning problems than on semantically equivalent English versions. Diffusion
models may repair some intermediate mistakes, but that repair rate may vary by
script and language form.

## MVP research questions

1. What is the accuracy gap between English and the three Indic variants?
2. Which reasoning categories are most sensitive to script or code-switching?
3. In multi-turn tasks, does the model incorporate corrections correctly?
4. For diffusion models, how often does an initially wrong answer become right,
   and how often does a right answer become wrong during denoising?

The current evaluator addresses questions 1-3. Diffusion-trace capture will be
added once a concrete diffusion model is selected.

## Pilot composition

The dataset contains two items from each category:

- arithmetic and time
- family relationships
- spatial reasoning
- logical constraints
- multi-turn correction

Every item has four semantically parallel variants:

- `hindi_devanagari`
- `roman_hindi`
- `hinglish`
- `english`

## Quick start

Python 3.10 or newer is recommended. The core evaluator uses only the Python
standard library.

Validate the dataset:

```bash
python -m src.validate_data --dataset data/pilot.jsonl
```

Run a smoke test using the deliberately non-intelligent mock model:

```bash
python -m src.evaluate \
  --dataset data/pilot.jsonl \
  --provider mock \
  --output results/smoke.jsonl
```

The mock run tests plumbing only. Its accuracy is not a baseline.

Run a locally installed Ollama model:

```bash
python -m src.evaluate \
  --dataset data/pilot.jsonl \
  --provider ollama \
  --model YOUR_MODEL_NAME \
  --output results/ollama.jsonl
```

Ollama is expected at `http://localhost:11434` by default. Override it with
`--base-url`.

Score externally generated answers with the replay adapter:

```bash
python -m src.evaluate \
  --dataset data/pilot.jsonl \
  --provider replay \
  --replay-file path/to/responses.jsonl \
  --output results/replayed.jsonl
```

Each replay row must contain `id`, `variant`, and `response`.

Compare two completed runs and generate reusable JSON and Markdown summaries:

```bash
python -m src.compare_runs \
  results/qwen3-1.7b-v1.jsonl \
  results/another-model.jsonl \
  --json-output results/comparison.json \
  --markdown-output results/comparison.md
```

## Metrics

- **Exact accuracy:** normalized response exactly equals an accepted answer.
- **Answer-mention rate:** an accepted answer appears in a longer response. This
  is diagnostic only, because models are instructed to return only the answer.
- **Language gap:** English exact accuracy minus another variant's accuracy.
- **Category accuracy:** exact accuracy grouped by reasoning category.
- **Correction accuracy:** exact accuracy on the multi-turn subset.

With only ten questions, these metrics are useful for debugging but do not have
enough statistical power for substantive claims.

## Research safeguards

- Keep benchmark items separate from future fine-tuning data.
- Obtain independent bilingual review before publishing benchmark results.
- Record model revision, quantization, prompts, decoding parameters, hardware,
  and random seeds.
- Report uncertainty and individual failure cases, not only aggregate accuracy.
- Do not use an LLM judge where a deterministic answer is available.
- Document ambiguous or excluded items rather than silently editing results.

## Planned milestones

1. Independently review and revise the 10-item pilot.
2. Run one autoregressive and one diffusion baseline.
3. Expand to 50 items only after resolving pipeline and annotation issues.
4. Add diffusion-step trace capture and self-correction metrics.
5. Expand to 200-400 human-reviewed items and introduce a hidden test split.
6. Try one targeted, compute-efficient intervention such as LoRA.

## First local baseline

The first Qwen3 1.7B pilot run is complete. It achieved 22.5% strict exact
accuracy and 35% manually adjudicated semantic accuracy across 40 prompts, with
a mean local latency of 0.535 seconds on an M2 MacBook Air. These are pipeline
validation figures, not research claims. See
[`results/BASELINE_REPORT.md`](results/BASELINE_REPORT.md) for the configuration,
language breakdown, failure analysis, and limitations.

## Second local baseline

Gemma 3 4B has now been evaluated under the identical protocol. It achieved
15.0% strict exact accuracy and 42.5% manually adjudicated semantic accuracy,
at a mean local latency of 2.259 seconds. Compared with Qwen3 1.7B, Gemma was
more semantically accurate and much stronger on Devanagari Hindi, but less
instruction-compliant and about 4.22 times slower. See
[`results/QWEN_VS_GEMMA_REPORT.md`](results/QWEN_VS_GEMMA_REPORT.md).

See [PROTOCOL.md](PROTOCOL.md) for the experiment design and
[data/DATASET_CARD.md](data/DATASET_CARD.md) for dataset limitations.
