import reflex as rx

from prompt_autoimprove_ui.components.candidate_view import candidate_view
from prompt_autoimprove_ui.components.explanation_card import explanation_card
from prompt_autoimprove_ui.components.header import header
from prompt_autoimprove_ui.components.history_panel import history_panel
from prompt_autoimprove_ui.components.metric_breakdown import metric_breakdown
from prompt_autoimprove_ui.components.pipeline_timeline import pipeline_timeline
from prompt_autoimprove_ui.components.profile_picker import profile_picker
from prompt_autoimprove_ui.components.prompt_card import prompt_card
from prompt_autoimprove_ui.state import PipelineState


def _error_banner() -> rx.Component:
    return rx.cond(
        PipelineState.error != "",
        rx.callout(
            PipelineState.error,
            icon="triangle-alert",
            color_scheme="red",
            size="1",
            width="100%",
        ),
        rx.fragment(),
    )


def home() -> rx.Component:
    return rx.vstack(
        header(),
        rx.hstack(
            rx.vstack(
                profile_picker(),
                rx.divider(),
                history_panel(),
                spacing="4",
                align="stretch",
                width="260px",
                padding="4",
            ),
            rx.vstack(
                _error_banner(),
                prompt_card(),
                pipeline_timeline(),
                candidate_view(),
                spacing="4",
                align="stretch",
                width="100%",
                padding_y="4",
                padding_x="2",
            ),
            rx.vstack(
                metric_breakdown(),
                explanation_card(),
                spacing="4",
                align="stretch",
                width="340px",
                padding="4",
            ),
            spacing="0",
            align="start",
            width="100%",
            max_width="1400px",
        ),
        on_mount=PipelineState.load_profiles,
        spacing="0",
        align="center",
        width="100%",
        min_height="100vh",
    )
