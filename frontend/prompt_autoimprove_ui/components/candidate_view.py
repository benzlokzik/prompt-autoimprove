import reflex as rx

from prompt_autoimprove_ui.state import PipelineState


def _empty() -> rx.Component:
    return rx.vstack(
        rx.icon("file-text", size=28, color=rx.color("gray", 8)),
        rx.text(
            "The improved prompt appears here",
            size="2",
            color=rx.color("gray", 11),
            weight="medium",
        ),
        rx.text(
            "We'll show the candidate text, the picked strategy, and the model response.",
            size="1",
            color=rx.color("gray", 10),
            text_align="center",
        ),
        spacing="2",
        align="center",
        justify="center",
        padding_y="6",
        width="100%",
    )


def candidate_view() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.icon("sparkles", size=16, color=rx.color("iris", 10)),
                    rx.heading("Improved prompt", size="3"),
                    spacing="2",
                    align="center",
                ),
                rx.spacer(),
                rx.cond(
                    PipelineState.candidate_strategy != "",
                    rx.badge(
                        PipelineState.candidate_strategy,
                        color_scheme="iris",
                        variant="solid",
                        size="2",
                    ),
                    rx.fragment(),
                ),
                width="100%",
                align="center",
            ),
            rx.cond(
                PipelineState.candidate_text != "",
                rx.box(
                    rx.code_block(
                        PipelineState.candidate_text,
                        can_copy=True,
                        wrap_long_lines=True,
                        language="markdown",
                        theme=rx.code_block.themes.atom_dark,
                        width="100%",
                    ),
                    width="100%",
                ),
                _empty(),
            ),
            rx.cond(
                PipelineState.probation_text != "",
                rx.vstack(
                    rx.hstack(
                        rx.icon("play", size=14, color=rx.color("green", 10)),
                        rx.text(
                            "Probation output",
                            size="2",
                            weight="bold",
                            color=rx.color("gray", 12),
                        ),
                        spacing="2",
                        align="center",
                    ),
                    rx.code_block(
                        PipelineState.probation_text,
                        can_copy=True,
                        wrap_long_lines=True,
                        language="log",
                        theme=rx.code_block.themes.atom_dark,
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
        size="3",
        width="100%",
        height="100%",
    )
