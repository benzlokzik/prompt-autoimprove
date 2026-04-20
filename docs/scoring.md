# Integrated quality score

Each candidate prompt is evaluated against five metrics, each in `[0, 1]`, and
combined with the weighted formula:

```
S = 0.30·q_c + 0.25·q_p + 0.20·q_s + 0.15·q_t + 0.10·q_l
```

| Symbol | Metric             | What it captures                                                  |
| ------ | ------------------ | ----------------------------------------------------------------- |
| `q_c`  | Clarity            | Structure, unambiguous wording, explicit role and output format.  |
| `q_p`  | Prompt compliance  | Coverage of the user's intent and constraints.                    |
| `q_s`  | Safety             | Absence of forbidden content; presence of safety guards.          |
| `q_t`  | Token cost         | Inverse of token consumption against the model's budget.          |
| `q_l`  | Latency            | Inverse of estimated latency against the configured SLO.          |

Weights are configurable per deployment mode (`production`, `research`, `eval`).
The `core.evaluator.IntegratedScorer` normalizes any out-of-range component to
`[0, 1]` before applying weights.

## Reproducibility

Every evaluation persists:

- the candidate prompt id,
- the resolved `ModelProfile`,
- per-metric raw values and normalized values,
- the integrated `S` score,
- the human-readable explanation.

This guarantees that diploma reviewers can reconstruct any decision.
