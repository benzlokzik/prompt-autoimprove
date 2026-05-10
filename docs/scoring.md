# Integrated quality score

Each candidate prompt is evaluated against five metrics, each in $[0, 1]$, and
combined with the weighted formula

$$
S = 0.30\,q_c + 0.25\,q_p + 0.20\,q_s + 0.15\,q_t + 0.10\,q_l
$$

with weights $\mathbf{w} = (0.30, 0.25, 0.20, 0.15, 0.10)$ satisfying
$\sum w_i = 1$.

| Symbol | Metric             | What it captures                                                  |
| ------ | ------------------ | ----------------------------------------------------------------- |
| $q_c$  | Clarity            | Structure, unambiguous wording, explicit role and output format.  |
| $q_p$  | Prompt compliance  | Coverage of the user's intent and constraints.                    |
| $q_s$  | Safety             | Absence of forbidden content; presence of safety guards.          |
| $q_t$  | Token cost         | Inverse of token consumption against the model's budget.          |
| $q_l$  | Latency            | Inverse of estimated latency against the configured SLO.          |

The token-cost component is normalized against the active profile's context
window $C$:

$$
q_t = 1 - \min\!\left(\frac{n_{\text{tokens}}}{C},\; 1\right)
$$

The latency component is normalized against a target SLO $T$:

$$
q_l = \mathrm{clip}_{[0,1]}\!\left(\frac{T}{p_{50}}\right)
$$

where $p_{50}$ is the profile's measured median latency.

## Custom weights

Weights are configurable per deployment mode (`production`, `research`,
`eval`). The `core.evaluator.IntegratedScorer` re-normalizes any custom weight
vector $\mathbf{w}'$ so that $\sum w'_i = 1$ before applying the formula. Any
out-of-range raw component is clipped to $[0, 1]$ first.

## Reproducibility

Every evaluation persists:

- the candidate prompt id,
- the resolved `ModelProfile`,
- per-metric raw values $q_i^{\text{raw}}$ and normalized values $q_i$,
- the integrated $S$ score,
- the human-readable explanation.

This guarantees that diploma reviewers can reconstruct any decision via
`GET /v1/history/{session_ref}`.
