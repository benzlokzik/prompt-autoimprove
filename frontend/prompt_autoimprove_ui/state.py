import contextlib
from typing import TypedDict

import reflex as rx

from prompt_autoimprove_ui.api_client import BackendClient
from prompt_autoimprove_ui.i18n import EXAMPLE_PROMPTS_EN, EXAMPLE_PROMPTS_RU


class ProfileItem(TypedDict):
    name: str
    family: str
    format: str
    context_window: int
    supports_vision: bool
    family_default: bool


class StageItem(TypedDict):
    stage: str
    payload: str


class MetricItem(TypedDict):
    name: str
    value: float
    weight: float


class RevisionItem(TypedDict):
    revision_id: str
    text: str
    strategy: str
    rationale: str
    created_at: str


class HistoryItem(TypedDict):
    prompt_id: str
    text: str
    modality: str
    created_at: str
    revisions: list[RevisionItem]


class PipelineState(rx.State):
    prompt: str = ""
    profile: str = "qwen"
    session_ref: str = ""
    language: str = "en"
    profiles: list[ProfileItem] = []
    history_items: list[HistoryItem] = []
    stages: list[StageItem] = []
    metrics: list[MetricItem] = []
    candidate_text: str = ""
    candidate_strategy: str = ""
    candidate_rationale: str = ""
    integrated_score: float = 0.0
    explanation: str = ""
    probation_text: str = ""
    complexity_label: str = ""
    complexity_score: float = 0.0
    llm_rewrite_text: str = ""
    is_running: bool = False
    error: str = ""

    @rx.var
    def example_prompts(self) -> list[str]:
        prompts = EXAMPLE_PROMPTS_RU if self.language == "ru" else EXAMPLE_PROMPTS_EN
        return list(prompts)

    @rx.var
    def unique_families(self) -> list[str]:
        seen: list[str] = []
        for p in self.profiles:
            if p["family"] not in seen:
                seen.append(p["family"])
        return seen

    @rx.event
    def toggle_language(self) -> None:
        self.language = "ru" if self.language == "en" else "en"

    @rx.event
    async def load_profiles(self) -> None:
        try:
            data = await BackendClient.from_env().list_profiles()
            self.profiles = [
                ProfileItem(
                    name=p["name"],
                    family=p["family"],
                    format=p["format"],
                    context_window=int(p["context_window"]),
                    supports_vision=bool(p["supports_vision"]),
                    family_default=bool(p.get("family_default", False)),
                )
                for p in data
            ]
        except Exception as exc:
            self.error = f"Failed to load profiles: {exc}"

    @rx.event
    async def load_history(self) -> None:
        if not self.session_ref:
            self.history_items = []
            return
        try:
            data = await BackendClient.from_env().history(self.session_ref)
            self.history_items = [
                HistoryItem(
                    prompt_id=item["prompt_id"],
                    text=item["text"],
                    modality=item["modality"],
                    created_at=item["created_at"],
                    revisions=[
                        RevisionItem(
                            revision_id=r["revision_id"],
                            text=r["text"],
                            strategy=r["strategy"],
                            rationale=r["rationale"],
                            created_at=r["created_at"],
                        )
                        for r in item.get("revisions", [])
                    ],
                )
                for item in data
            ]
        except Exception as exc:
            self.error = f"Failed to load history: {exc}"

    @rx.event
    def set_prompt(self, value: str) -> None:
        self.prompt = value

    @rx.event
    def set_profile(self, value: str) -> None:
        self.profile = value

    @rx.event
    def set_session_ref(self, value: str) -> None:
        self.session_ref = value

    @rx.event
    def use_example(self, idx: int) -> None:
        examples = EXAMPLE_PROMPTS_RU if self.language == "ru" else EXAMPLE_PROMPTS_EN
        if 0 <= idx < len(examples):
            self.prompt = examples[idx]

    @rx.event
    def reset_run(self) -> None:
        self.stages = []
        self.metrics = []
        self.candidate_text = ""
        self.candidate_strategy = ""
        self.candidate_rationale = ""
        self.integrated_score = 0.0
        self.explanation = ""
        self.probation_text = ""
        self.complexity_label = ""
        self.complexity_score = 0.0
        self.llm_rewrite_text = ""
        self.error = ""

    def _apply_stage(self, stage: str, payload: dict) -> None:
        import json as _json

        self.stages = [*self.stages, StageItem(stage=stage, payload=_json.dumps(payload))]
        if stage == "candidate":
            self.candidate_text = payload.get("text", "")
            self.candidate_rationale = payload.get("rationale", "")
        elif stage == "strategy_selected":
            self.candidate_strategy = payload.get("strategy", "")
        elif stage == "evaluated":
            self.integrated_score = float(payload.get("score", 0.0))
        elif stage == "probation":
            self.probation_text = payload.get("output", "")
        elif stage == "final_decision":
            self.explanation = payload.get("explanation", "")
        elif stage == "complexity_checked":
            self.complexity_label = payload.get("label", "")
            self.complexity_score = round(float(payload.get("score", 0.0)), 3)
        elif stage == "llm_rewrite_candidate":
            self.llm_rewrite_text = payload.get("text", "")

    @rx.event(background=True)
    async def submit(self) -> None:
        async with self:
            self.reset_run()
            if not self.prompt.strip():
                self.error = "Prompt is empty" if self.language == "en" else "Промпт пустой"
                return
            self.is_running = True

        try:
            client = BackendClient.from_env()
            async for stage, payload in client.stream_improve(
                prompt=self.prompt, profile=self.profile
            ):
                async with self:
                    self._apply_stage(stage, payload)
            full = await client.improve(
                prompt=self.prompt,
                profile=self.profile,
                session_ref=self.session_ref or None,
            )
            async with self:
                self.metrics = [
                    MetricItem(
                        name=m["name"],
                        value=float(m["value"]),
                        weight=float(m["weight"]),
                    )
                    for m in full.get("metrics", [])
                ]
                if not self.session_ref:
                    self.session_ref = full.get("session_id", "")
        except Exception as exc:
            async with self:
                self.error = str(exc)
        finally:
            async with self:
                self.is_running = False
                if self.session_ref:
                    with contextlib.suppress(Exception):
                        await self.load_history()
