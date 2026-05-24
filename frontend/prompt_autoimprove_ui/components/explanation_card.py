import reflex as rx

from prompt_autoimprove_ui.components.code_view import code_view
from prompt_autoimprove_ui.i18n import t
from prompt_autoimprove_ui.state import PipelineState


def explanation_card() -> rx.Component:
    return rx.cond(
        PipelineState.explanation != "",
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.icon("lightbulb", size=16, color=rx.color("amber", 10)),
                    rx.heading(t("why_candidate", PipelineState.language), size="3"),
                    spacing="2",
                    align="center",
                ),
                code_view(PipelineState.explanation, "log", can_copy=False),
                spacing="4",
                align="stretch",
                width="100%",
            ),
            size="3",
            width="100%",
        ),
        rx.fragment(),
    )
