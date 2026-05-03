import reflex as rx

from prompt_autoimprove_ui.state import PipelineState


def explanation_card() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("lightbulb", size=18, color=rx.color("indigo", 10)),
                rx.heading("Why this candidate", size="3"),
                width="100%",
                align="center",
            ),
            rx.cond(
                PipelineState.explanation != "",
                rx.code_block(
                    PipelineState.explanation,
                    can_copy=False,
                    wrap_long_lines=True,
                    width="100%",
                ),
                rx.text(
                    "An explanation of the chosen strategy will appear here.",
                    size="2",
                    color=rx.color("gray", 11),
                ),
            ),
            spacing="2",
            align="stretch",
            width="100%",
        ),
        size="2",
        width="100%",
    )
