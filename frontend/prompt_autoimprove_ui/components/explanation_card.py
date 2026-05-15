import reflex as rx

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
                rx.code_block(
                    PipelineState.explanation,
                    can_copy=False,
                    wrap_long_lines=True,
                    language="log",
                    theme=rx.code_block.themes.atom_dark,
                    width="100%",
                ),
                spacing="2",
                align="stretch",
                width="100%",
            ),
            size="2",
            width="100%",
        ),
        rx.fragment(),
    )
