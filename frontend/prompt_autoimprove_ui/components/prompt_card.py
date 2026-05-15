import reflex as rx

from prompt_autoimprove_ui.i18n import t
from prompt_autoimprove_ui.state import PipelineState


def _example_chip(idx: int) -> rx.Component:
    text_var = PipelineState.example_prompts[idx]
    short = rx.cond(
        text_var.length() > 70,
        text_var[:67] + "…",
        text_var,
    )
    return rx.button(
        short,
        size="1",
        variant="surface",
        color_scheme="gray",
        on_click=PipelineState.use_example(idx),
        cursor="pointer",
    )


def prompt_card() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.icon("message-square", size=16, color=rx.color("iris", 10)),
                    rx.heading(t("your_prompt", PipelineState.language), size="3"),
                    spacing="2",
                    align="center",
                ),
                rx.spacer(),
                rx.cond(
                    PipelineState.session_ref != "",
                    rx.badge(
                        t("session", PipelineState.language) + PipelineState.session_ref[:8],
                        variant="soft",
                        color_scheme="iris",
                    ),
                    rx.fragment(),
                ),
                width="100%",
                align="center",
            ),
            rx.text_area(
                placeholder=t("placeholder", PipelineState.language),
                value=PipelineState.prompt,
                on_change=PipelineState.set_prompt,
                rows="9",
                width="100%",
                resize="vertical",
                style={
                    "font_family": (
                        "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"
                    ),
                    "font_size": "13px",
                    "line_height": "1.6",
                },
            ),
            rx.flex(
                rx.text(
                    t("try_one", PipelineState.language),
                    size="1",
                    color=rx.color("gray", 11),
                    weight="medium",
                ),
                _example_chip(0),
                _example_chip(1),
                _example_chip(2),
                wrap="wrap",
                gap="2",
                align="center",
                width="100%",
            ),
            rx.hstack(
                rx.hstack(
                    rx.icon("cpu", size=14, color=rx.color("gray", 10)),
                    rx.text(
                        t("routing_to", PipelineState.language),
                        rx.text.strong(PipelineState.profile, color=rx.color("iris", 11)),
                        size="2",
                        color=rx.color("gray", 11),
                    ),
                    spacing="1",
                    align="center",
                ),
                rx.spacer(),
                rx.button(
                    rx.cond(
                        PipelineState.is_running,
                        rx.hstack(
                            rx.spinner(size="1"),
                            rx.text(t("improving", PipelineState.language)),
                            spacing="2",
                            align="center",
                        ),
                        rx.hstack(
                            rx.icon("zap", size=15),
                            rx.text(t("improve_btn", PipelineState.language)),
                            spacing="2",
                            align="center",
                        ),
                    ),
                    on_click=PipelineState.submit,
                    disabled=PipelineState.is_running,
                    color_scheme="iris",
                    size="3",
                    style={"box_shadow": "0 6px 24px -10px var(--iris-9)"},
                ),
                width="100%",
                align="center",
            ),
            spacing="4",
            align="stretch",
        ),
        size="3",
        width="100%",
    )
