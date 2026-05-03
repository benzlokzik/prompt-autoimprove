import reflex as rx

from prompt_autoimprove_ui.state import PipelineState


def candidate_view() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("file-text", size=18, color=rx.color("indigo", 10)),
                rx.heading("Improved prompt", size="3"),
                rx.spacer(),
                rx.cond(
                    PipelineState.candidate_strategy != "",
                    rx.badge(
                        PipelineState.candidate_strategy,
                        color_scheme="indigo",
                        variant="solid",
                    ),
                    rx.fragment(),
                ),
                width="100%",
                align="center",
            ),
            rx.cond(
                PipelineState.candidate_text != "",
                rx.code_block(
                    PipelineState.candidate_text,
                    can_copy=True,
                    wrap_long_lines=True,
                    width="100%",
                ),
                rx.text(
                    "The chosen candidate prompt will appear here.",
                    size="2",
                    color=rx.color("gray", 11),
                ),
            ),
            rx.cond(
                PipelineState.probation_text != "",
                rx.vstack(
                    rx.text("Probation output", size="2", weight="bold"),
                    rx.code_block(
                        PipelineState.probation_text,
                        can_copy=True,
                        wrap_long_lines=True,
                        width="100%",
                    ),
                    spacing="2",
                    align="stretch",
                    width="100%",
                ),
                rx.fragment(),
            ),
            spacing="3",
            align="stretch",
            width="100%",
        ),
        size="2",
        width="100%",
    )
