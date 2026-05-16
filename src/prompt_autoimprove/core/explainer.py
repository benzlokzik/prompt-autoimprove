from prompt_autoimprove.core.strategies.base import CandidatePrompt
from prompt_autoimprove.domain.evaluation import Score


def explain(candidate: CandidatePrompt, score: Score, runner_ups: list[Score]) -> str:
    lines = [
        f"Selected strategy: {candidate.strategy.value}",
        f"Reason: {candidate.rationale}",
        f"Integrated score: {score.integrated:.3f}",
    ]
    lines.append("Component breakdown:")
    for metric in score.metrics:
        lines.append(
            f"  - {metric.name.value}: value={metric.value:.2f} weight={metric.weight:.2f}"
        )
    if runner_ups:
        gap = score.integrated - max(s.integrated for s in runner_ups)
        lines.append(f"Margin over next-best candidate: {gap:+.3f}")
    return "\n".join(lines)
