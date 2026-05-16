import reflex as rx

from prompt_autoimprove_ui.i18n import t
from prompt_autoimprove_ui.state import PipelineState


def _empty() -> rx.Component:
    return rx.vstack(
        rx.icon("file-text", size=28, color=rx.color("gray", 8)),
        rx.text(
            t("improved_empty_title", PipelineState.language),
            size="2",
            color=rx.color("gray", 11),
            weight="medium",
        ),
        rx.text(
            t("improved_empty_sub", PipelineState.language),
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


def _complexity_badge() -> rx.Component:
    return rx.cond(
        PipelineState.complexity_label != "",
        rx.hstack(
            rx.badge(
                PipelineState.complexity_label,
                color_scheme=rx.cond(PipelineState.complexity_label == "hard", "red", "green"),
                variant="soft",
                size="1",
            ),
            rx.text(
                PipelineState.complexity_score,
                size="1",
                color=rx.color("gray", 10),
                font_family="ui-monospace, monospace",
            ),
            spacing="1",
            align="center",
        ),
        rx.fragment(),
    )


def _llm_rewrite_section() -> rx.Component:
    return rx.cond(
        PipelineState.llm_rewrite_text != "",
        rx.vstack(
            rx.hstack(
                rx.icon("bot", size=14, color=rx.color("violet", 10)),
                rx.text(
                    t("llm_rewrite_candidate", PipelineState.language),
                    size="2",
                    weight="bold",
                    color=rx.color("gray", 12),
                ),
                rx.spacer(),
                rx.tooltip(
                    rx.icon("info", size=13, color=rx.color("gray", 9)),
                    content=t("llm_rewrite_note", PipelineState.language),
                ),
                spacing="2",
                align="center",
                width="100%",
            ),
            rx.code_block(
                PipelineState.llm_rewrite_text,
                can_copy=True,
                wrap_long_lines=True,
                language="markdown",
                theme=rx.code_block.themes.atom_dark,
                width="100%",
            ),
            spacing="2",
            align="stretch",
            width="100%",
            padding="3",
            border_radius="8px",
            background=rx.color("violet", 2),
            border=f"1px solid {rx.color('violet', 4)}",
        ),
        rx.fragment(),
    )


def candidate_view() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.icon("sparkles", size=16, color=rx.color("iris", 10)),
                    rx.heading(t("improved_prompt", PipelineState.language), size="3"),
                    spacing="2",
                    align="center",
                ),
                rx.spacer(),
                _complexity_badge(),
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
                gap="2",
                width="100%",
                align="center",
                wrap="wrap",
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
            _llm_rewrite_section(),
            rx.cond(
                PipelineState.probation_text != "",
                rx.vstack(
                    rx.hstack(
                        rx.icon("play", size=14, color=rx.color("green", 10)),
                        rx.text(
                            t("probation", PipelineState.language),
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
