from dataclasses import dataclass
from uuid import UUID

from prompt_autoimprove.adapters.base import ModelAdapter
from prompt_autoimprove.domain.model_profile import ModelFormat, ModelProfile
from prompt_autoimprove.domain.routing import RoutingDecision


class NoRouteError(RuntimeError):
    pass


@dataclass(slots=True, frozen=True)
class RoutingPolicy:
    allow_external: bool = True
    require_local_for_pii: bool = True
    max_cost_per_1k_output: float | None = None
    max_p50_latency_ms: int | None = None


@dataclass(slots=True)
class Router:
    policy: RoutingPolicy
    adapters: dict[str, ModelAdapter]

    def pick(
        self,
        candidates: list[ModelProfile],
        revision_id: UUID,
        *,
        sensitive: bool = False,
    ) -> RoutingDecision:
        for profile in candidates:
            if not self._allowed(profile, sensitive=sensitive):
                continue
            if profile.name not in self.adapters:
                continue
            return RoutingDecision(
                profile=profile,
                adapter_name=self.adapters[profile.name].name,
                reason=self._reason(profile, sensitive=sensitive),
                revision_id=revision_id,
            )
        raise NoRouteError("no profile satisfies routing policy")

    def _allowed(self, profile: ModelProfile, *, sensitive: bool) -> bool:
        if sensitive and self.policy.require_local_for_pii and not profile.is_local:
            return False
        if not self.policy.allow_external and profile.format is ModelFormat.API:
            return False
        if (
            self.policy.max_cost_per_1k_output is not None
            and profile.cost_per_1k_output > self.policy.max_cost_per_1k_output
        ):
            return False
        if (
            self.policy.max_p50_latency_ms is not None
            and profile.p50_latency_ms > self.policy.max_p50_latency_ms
        ):
            return False
        return True

    @staticmethod
    def _reason(profile: ModelProfile, *, sensitive: bool) -> str:
        bits = [f"profile={profile.name}", f"format={profile.format.value}"]
        if sensitive:
            bits.append("sensitive=true")
        return ", ".join(bits)
