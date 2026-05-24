import base64
import contextlib
import logging
import mimetypes
from typing import TypedDict

import httpx
import reflex as rx

from prompt_autoimprove_ui.api_client import BackendClient
from prompt_autoimprove_ui.i18n import EXAMPLE_PROMPTS_EN, EXAMPLE_PROMPTS_RU, STRINGS

logger = logging.getLogger("prompt_autoimprove_ui")


class ProfileItem(TypedDict):
    name: str
    family: str
    format: str
    context_window: int
    max_output_tokens: int
    supports_vision: bool
    reasoning_mode: str
    cost_per_1k_input: float
    cost_per_1k_output: float
    p50_latency_ms: int
    supports_tools: bool
    family_default: bool


class StageItem(TypedDict):
    stage: str
    payload: str


class MetricItem(TypedDict):
    name: str
    label: str
    value: float
    value_str: str
    weight_str: str


# Friendly labels for the q_* metric names (the frontend does not render LaTeX).
METRIC_LABELS: dict[str, dict[str, str]] = {
    "en": {
        "q_c": "Clarity",
        "q_p": "Compliance",
        "q_s": "Safety",
        "q_t": "Token cost",
        "q_l": "Latency",
    },
    "ru": {
        "q_c": "Ясность",
        "q_p": "Соответствие",
        "q_s": "Безопасность",
        "q_t": "Стоимость токенов",
        "q_l": "Задержка",
    },
}


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


class AttachmentItem(TypedDict):
    name: str
    uri: str
    mime_type: str
    bytes_size: int


_MAX_ATTACHMENTS = 4
_MAX_ATTACHMENT_BYTES = 8 * 1024 * 1024


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
    score_display: str = ""
    explanation: str = ""
    probation_text: str = ""
    complexity_label: str = ""
    complexity_score: float = 0.0
    llm_rewrite_text: str = ""
    is_running: bool = False
    is_loading_profiles: bool = False
    sensitive: bool = False
    expanded_prompt_id: str = ""
    attachments: list[AttachmentItem] = []
    error: str = ""

    @staticmethod
    def _response_detail(exc: httpx.HTTPStatusError) -> str:
        """Extract the human-readable reason the backend returned, if any."""
        try:
            detail = exc.response.json().get("detail")
        except Exception:
            return ""
        if isinstance(detail, str):
            text = detail
        elif isinstance(detail, list):
            parts = []
            for item in detail:
                loc = ".".join(str(x) for x in item.get("loc", []) if x != "body")
                msg = item.get("msg", "")
                parts.append(f"{loc}: {msg}" if loc else msg)
            text = "; ".join(p for p in parts if p)
        else:
            return ""
        text = text.strip()
        return text if len(text) <= 200 else text[:197] + "…"

    def _humanize_error(self, exc: Exception) -> str:
        logger.error("frontend request failed: %r", exc, exc_info=exc)
        lang = "ru" if self.language == "ru" else "en"
        if isinstance(exc, httpx.HTTPStatusError):
            code = exc.response.status_code
            key = {
                404: "err_unknown_profile",
                422: "err_validation",
                429: "err_rate_limit",
            }.get(code, "err_server" if code >= 500 else "err_generic")
            base = STRINGS[key][lang]
            # Surface the backend's specific reason for actionable client errors.
            detail = self._response_detail(exc) if 400 <= code < 500 and code != 429 else ""
            return f"{base} — {detail}" if detail else base
        if isinstance(exc, httpx.RequestError):
            key = "err_network"
        elif isinstance(exc, (KeyError, ValueError)):
            key = "err_bad_response"
        else:
            key = "err_generic"
        return STRINGS[key][lang]

    @rx.var
    def metric_columns(self) -> str:
        n = len(self.metrics)
        return str(n) if n > 0 else "1"

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

    @rx.var
    def selected_family_profiles(self) -> list[ProfileItem]:
        return [p for p in self.profiles if p["family"] == self.profile]

    @rx.event
    def toggle_language(self) -> None:
        self.language = "ru" if self.language == "en" else "en"

    def _ensure_valid_profile(self) -> None:
        families: list[str] = []
        for p in self.profiles:
            if p["family"] not in families:
                families.append(p["family"])
        if families and self.profile not in families:
            self.profile = families[0]

    @rx.event
    async def load_profiles(self) -> None:
        self.is_loading_profiles = True
        try:
            data = await BackendClient.from_env().list_profiles()
            self.profiles = [
                ProfileItem(
                    name=p["name"],
                    family=p["family"],
                    format=p["format"],
                    context_window=int(p["context_window"]),
                    max_output_tokens=int(p.get("max_output_tokens", 0)),
                    supports_vision=bool(p["supports_vision"]),
                    reasoning_mode=str(p.get("reasoning_mode", "none")),
                    cost_per_1k_input=float(p.get("cost_per_1k_input", 0.0)),
                    cost_per_1k_output=float(p.get("cost_per_1k_output", 0.0)),
                    p50_latency_ms=int(p.get("p50_latency_ms", 0)),
                    supports_tools=bool(p.get("supports_tools", False)),
                    family_default=bool(p.get("family_default", False)),
                )
                for p in data
            ]
            self._ensure_valid_profile()
        except Exception as exc:
            self.error = self._humanize_error(exc)
        finally:
            self.is_loading_profiles = False

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
            self.error = self._humanize_error(exc)

    @rx.event
    def set_prompt(self, value: str) -> None:
        self.prompt = value

    @rx.event
    def set_sensitive(self, value: bool) -> None:
        self.sensitive = value

    @rx.event
    def use_candidate(self) -> None:
        if self.candidate_text:
            self.prompt = self.candidate_text

    @rx.event
    def load_revision(self, text: str) -> None:
        self.prompt = text

    @rx.event
    def toggle_history_item(self, prompt_id: str) -> None:
        self.expanded_prompt_id = "" if self.expanded_prompt_id == prompt_id else prompt_id

    @rx.event
    async def handle_image_upload(self, files: list[rx.UploadFile]) -> None:
        for file in files:
            if len(self.attachments) >= _MAX_ATTACHMENTS:
                break
            data = await file.read()
            if len(data) > _MAX_ATTACHMENT_BYTES:
                self.error = STRINGS["image_too_large"]["ru" if self.language == "ru" else "en"]
                continue
            name = file.name or "image"
            mime = (
                getattr(file, "content_type", None) or mimetypes.guess_type(name)[0] or "image/png"
            )
            encoded = base64.b64encode(data).decode("ascii")
            self.attachments.append(
                AttachmentItem(
                    name=name,
                    uri=f"data:{mime};base64,{encoded}",
                    mime_type=mime,
                    bytes_size=len(data),
                )
            )

    @rx.event
    def remove_attachment(self, idx: int) -> None:
        if 0 <= idx < len(self.attachments):
            self.attachments.pop(idx)

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
        self.score_display = ""
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
            score = float(payload.get("score", 0.0))
            self.integrated_score = score
            self.score_display = f"{score:.8f}"
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
                lang = "ru" if self.language == "ru" else "en"
                self.error = STRINGS["prompt_empty_error"][lang]
                return
            self.is_running = True

        attachments = [
            {
                "modality": "image",
                "uri": a["uri"],
                "mime_type": a["mime_type"],
                "bytes_size": a["bytes_size"],
            }
            for a in self.attachments
        ]
        try:
            client = BackendClient.from_env()
            async for stage, payload in client.stream_improve(
                prompt=self.prompt,
                profile=self.profile,
                locale_hint=self.language,
                sensitive=self.sensitive,
                attachments=attachments,
            ):
                async with self:
                    self._apply_stage(stage, payload)
            full = await client.improve(
                prompt=self.prompt,
                profile=self.profile,
                session_ref=self.session_ref or None,
                sensitive=self.sensitive,
                locale_hint=self.language,
                attachments=attachments,
            )
            labels = METRIC_LABELS["ru" if self.language == "ru" else "en"]
            async with self:
                self.metrics = [
                    MetricItem(
                        name=m["name"],
                        label=f"{labels.get(m['name'], m['name'])} ({m['name']})",
                        value=float(m["value"]),
                        value_str=f"{float(m['value']):.8f}",
                        weight_str=f"{float(m['weight']):.8f}",
                    )
                    for m in full.get("metrics", [])
                ]
                if not self.session_ref:
                    self.session_ref = full.get("session_id", "")
        except Exception as exc:
            async with self:
                self.error = self._humanize_error(exc)
        finally:
            async with self:
                self.is_running = False
                if self.session_ref:
                    with contextlib.suppress(Exception):
                        await self.load_history()
