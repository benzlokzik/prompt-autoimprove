import reflex as rx

from prompt_autoimprove_ui.state import EXAMPLE_PROMPTS, PipelineState


def _example_chip(idx: int, text: str) -> rx.Component:
    short = text if len(text) <= 70 else text[:67] + "…"
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
                    rx.heading("Your prompt", size="3"),
                    spacing="2",
                    align="center",
                ),
                rx.spacer(),
                rx.cond(
                    PipelineState.session_ref != "",
                    rx.badge(
                        "session " + PipelineState.session_ref[:8],
                        variant="soft",
                        color_scheme="iris",
                    ),
                    rx.fragment(),
                ),
                width="100%",
                align="center",
            ),
            rx.text_area(
                placeholder="Paste a prompt and we'll route it through normalization, "
                "six improvement strategies, scoring, routing, and a probation run.",
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
                    "Try one:",
                    size="1",
                    color=rx.color("gray", 11),
                    weight="medium",
                ),
                *[_example_chip(i, p) for i, p in enumerate(EXAMPLE_PROMPTS)],
                wrap="wrap",
                gap="2",
                align="center",
                width="100%",
            ),
            rx.hstack(
                rx.hstack(
                    rx.icon("cpu", size=14, color=rx.color("gray", 10)),
                    rx.text(
                        "Routing to ",
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
                            rx.text("Improving…"),
                            spacing="2",
                            align="center",
                        ),
                        rx.hstack(
                            rx.icon("zap", size=15),
                            rx.text("Improve prompt"),
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
