import contextlib
from typing import Any

import reflex as rx

from prompt_autoimprove_ui.api_client import BackendClient

EXAMPLE_PROMPTS = (
    "Summarize the key benefits of microservices in 3 bullet points",
    "Extract all email addresses and phone numbers from this customer note: "
    "alice@example.com called from +1 555 123 4567 about invoice #42.",
    "Explain how the integrated quality score is computed and weight each component.",
)


class PipelineState(rx.State):
    prompt: str = ""
    profile: str = "qwen3-7b"
    session_ref: str = ""
    profiles: list[dict[str, Any]] = []
    history_items: list[dict[str, Any]] = []
    stages: list[dict[str, Any]] = []
    metrics: list[dict[str, Any]] = []
    candidate_text: str = ""
    candidate_strategy: str = ""
    candidate_rationale: str = ""
    integrated_score: float = 0.0
    explanation: str = ""
    probation_text: str = ""
    is_running: bool = False
    error: str = ""

    @rx.event
    async def load_profiles(self) -> None:
        try:
            self.profiles = await BackendClient.from_env().list_profiles()
        except Exception as exc:
            self.error = f"Failed to load profiles: {exc}"

    @rx.event
    async def load_history(self) -> None:
        if not self.session_ref:
            self.history_items = []
            return
        try:
            self.history_items = await BackendClient.from_env().history(self.session_ref)
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
        if 0 <= idx < len(EXAMPLE_PROMPTS):
            self.prompt = EXAMPLE_PROMPTS[idx]

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
        self.error = ""

    @rx.event(background=True)
    async def submit(self) -> None:
        async with self:
            self.reset_run()
            if not self.prompt.strip():
                self.error = "Prompt is empty"
                return
            self.is_running = True

        try:
            client = BackendClient.from_env()
            async for stage, payload in client.stream_improve(
                prompt=self.prompt, profile=self.profile
            ):
                async with self:
                    self.stages = [*self.stages, {"stage": stage, "payload": payload}]
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
            full = await client.improve(
                prompt=self.prompt,
                profile=self.profile,
                session_ref=self.session_ref or None,
            )
            async with self:
                self.metrics = full.get("metrics", [])
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
                        self.history_items = await BackendClient.from_env().history(
                            self.session_ref
                        )
