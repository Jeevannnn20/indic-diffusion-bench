# Automated Model Comparison

| Model | Exact accuracy | Mean latency (s) |
|---|---:|---:|
| ollama:qwen3:1.7b | 22.5% | 0.535 |
| ollama:gemma3:4b | 15.0% | 2.259 |

## Strict accuracy by language form

| Group | ollama:qwen3:1.7b | ollama:gemma3:4b |
|---|---:|---:|
| english | 60.0% | 30.0% |
| hindi_devanagari | 0.0% | 10.0% |
| hinglish | 20.0% | 10.0% |
| roman_hindi | 10.0% | 10.0% |

## Strict accuracy by category

| Group | ollama:qwen3:1.7b | ollama:gemma3:4b |
|---|---:|---:|
| arithmetic_time | 0.0% | 0.0% |
| family_relationship | 12.5% | 37.5% |
| logical_constraints | 62.5% | 37.5% |
| multi_turn_correction | 25.0% | 0.0% |
| spatial_reasoning | 12.5% | 0.0% |

> Generated from raw run files. Pilot results are not research findings.
