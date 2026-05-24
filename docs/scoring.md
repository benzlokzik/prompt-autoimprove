# Integrated quality score

Each candidate prompt is evaluated against five normalized metrics in $[0, 1]$.
The final score is a weighted sum:

$$
S = 0.30\,q_c + 0.25\,q_p + 0.20\,q_s + 0.15\,q_t + 0.10\,q_l
$$

The default weight vector is
$\mathbf{w} = (0.30, 0.25, 0.20, 0.15, 0.10)$, with $\sum w_i = 1$.

| Symbol | Metric | What it captures |
| --- | --- | --- |
| $q_c$ | Clarity | Structure, unambiguous wording, explicit role, and output format. |
| $q_p$ | Prompt compliance | Coverage of the user's intent and constraints. |
| $q_s$ | Safety | Absence of forbidden content and presence of safety guards. |
| $q_t$ | Token cost | Inverse of token consumption against the model budget. |
| $q_l$ | Latency | Inverse of estimated latency against the configured SLO. |

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

Weights are configurable per deployment mode: `production`, `research`, and
`eval`. `core.evaluator.IntegratedScorer` re-normalizes any custom vector
$\mathbf{w}'$ so that $\sum w'_i = 1$ before applying the formula. Raw metric
components outside $[0, 1]$ are clipped before scoring.

## Profile- and task-aware weights

When `IntegratedScorer.profile_aware` is enabled (the default),
`core.evaluator.resolve_weights` adjusts the base vector for each evaluation
before re-normalizing:

- **Local profiles** (`gguf`/`safetensors`) raise the token-cost and latency
  weights by $1.5\times$, since on-device models are context-bound and slower.
- **Reasoning-heavy tasks** (`reasoning`, `code_generate`, `extract`) raise the
  clarity and prompt-compliance weights by $1.3\times$.

The adjustments compose and the result is re-normalized to $\sum w_i = 1$, so
the score stays in $[0, 1]$. Pass `profile_aware=False` to score with a fixed
vector. `scripts/benchmark.py` prints the per-task score delta between the two
modes.

## Reproducibility

Every evaluation persists:

- the candidate prompt id,
- the resolved `ModelProfile`,
- per-metric raw values $q_i^{\text{raw}}$ and normalized values $q_i$,
- the integrated score $S$,
- the human-readable explanation.

Reviewers can reconstruct a decision through `GET /v1/history/{session_ref}`.
