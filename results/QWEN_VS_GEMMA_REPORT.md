# Qwen3 1.7B vs Gemma 3 4B Pilot Comparison

## Status

Preliminary pipeline-validation comparison on ten reviewed-but-not-independently-
adjudicated benchmark items. Each model answered 40 prompts under the same
`answer-only-v1` protocol. A difference of one item changes a language score by
10 percentage points, so these results generate hypotheses rather than support
general conclusions.

## Controlled setup

| Field | Qwen3 1.7B | Gemma 3 4B |
|---|---:|---:|
| Ollama model ID | `8f68893c685c` | `a2af6cc3eb7f` |
| Reported parameters | 2.0B | 4.3B |
| Quantization | Q4_K_M | Q4_K_M |
| Local package size | 1.4 GB | 3.3 GB |
| Loaded Metal size | 1.5 GB | 2.8 GB |
| Runtime context | 4096 | 4096 |
| Hardware | Apple M2 Air, 8 GB | Apple M2 Air, 8 GB |
| Prompt version | `answer-only-v1` | `answer-only-v1` |
| Temperature / seed | 0 / 42 | 0 / 42 |
| Maximum generated tokens | 64 | 64 |

Both models ran locally through Ollama 0.32.0 with thinking disabled and 100%
Metal execution.

## Headline results

| Metric | Qwen3 1.7B | Gemma 3 4B | Gemma minus Qwen |
|---|---:|---:|---:|
| Strict exact accuracy | 22.5% | 15.0% | -7.5 pp |
| Manual semantic accuracy | 35.0% | 42.5% | +7.5 pp |
| Answer-mention rate | 40.0% | 42.5% | +2.5 pp |
| Mean latency | 0.535 s | 2.259 s | +1.724 s |
| Total latency | 21.4 s | 90.4 s | +69.0 s |

Gemma was approximately **4.22 times slower** per prompt. It produced three more
semantically correct answers overall, but three fewer strictly compliant exact
answers. Model size improved semantic correctness modestly while worsening
answer-format compliance.

## Manual semantic accuracy by language form

| Variant | Qwen3 1.7B | Gemma 3 4B | Gemma minus Qwen |
|---|---:|---:|---:|
| English | 70% | 50% | -20 pp |
| Hindi (Devanagari) | 10% | 50% | +40 pp |
| Romanized Hindi | 40% | 30% | -10 pp |
| Hinglish | 20% | 40% | +20 pp |

Gemma's result is much more balanced across language forms. Its English-to-
Devanagari semantic gap is zero in this pilot, compared with 60 points for
Qwen. This does **not** mean Gemma has solved Hindi reasoning: it reached only
5/10 in both English and Devanagari, and the sample is extremely small.

## Manual semantic accuracy by category

| Category | Qwen3 1.7B | Gemma 3 4B | Gemma minus Qwen |
|---|---:|---:|---:|
| Arithmetic and time | 12.5% | 12.5% | 0 pp |
| Family relationships | 37.5% | 62.5% | +25 pp |
| Spatial reasoning | 12.5% | 25.0% | +12.5 pp |
| Logical constraints | 87.5% | 87.5% | 0 pp |
| Multi-turn correction | 25.0% | 25.0% | 0 pp |

The larger model did not improve arithmetic, logical constraints, or multi-turn
correction. Its gains came from family and spatial items. Both models answered
the two English correction items correctly but failed all six non-English
correction variants, a particularly useful target for the expanded benchmark.

## Interpretation

1. **More parameters did not yield a universal win.** Gemma's semantic accuracy
   improved by 7.5 points, while strict exact accuracy fell by the same amount.
2. **Language balance changed more than overall accuracy.** Gemma traded weaker
   English and Romanized Hindi results for substantially stronger Devanagari
   Hindi and Hinglish results.
3. **Instruction compliance is a separate capability.** The 27.5-point gap
   between Gemma's strict and semantic scores is larger than Qwen's 12.5-point
   gap. Future reports should keep both metrics rather than silently relaxing
   exact matching.
4. **Multi-turn correction is the clearest shared weakness.** Neither model
   successfully handled a non-English correction item.
5. **Accessible local inference is feasible but has a cost.** A quantized 4B
   model ran on an 8 GB M2 Air, but at roughly four times Qwen's latency and with
   noticeable memory compression during initial loading.

## Decision for the next phase

Expand the correction and spatial subsets before introducing a diffusion model.
The present ten-item pilot is too small to distinguish stable model behavior
from item effects. The next dataset version should reach 50 independently
reviewed items while preserving a hidden test split.

Item-level Gemma decisions are in `gemma3-4b-v1-adjudication.csv`; Qwen decisions
are in `qwen3-1.7b-v1-adjudication.csv`. The strict comparison is generated from
raw outputs in `qwen-vs-gemma-automated.md` and `.json`.
