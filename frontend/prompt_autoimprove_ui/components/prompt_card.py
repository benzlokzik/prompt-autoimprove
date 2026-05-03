import reflex as rx

from prompt_autoimprove_ui.state import EXAMPLE_PROMPTS, PipelineState


def _example_chip(idx: int, text: str) -> rx.Component:
    short = text if len(text) <= 60 else text[:57] + "…"
    return rx.button(
        short,
        size="1",
        variant="soft",
        color_scheme="gray",
        on_click=PipelineState.use_example(idx),
        cursor="pointer",
    )


def prompt_card() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("message-square", size=18, color=rx.color("indigo", 10)),
                rx.heading("Your prompt", size="3"),
                rx.spacer(),
                rx.cond(
                    PipelineState.session_ref != "",
                    rx.badge(
                        "session " + PipelineState.session_ref[:8],
                        variant="soft",
                        color_scheme="indigo",
                    ),
                    rx.fragment(),
                ),
                width="100%",
                align="center",
            ),
            rx.text_area(
                placeholder="Type or paste a prompt for the LLM…",
                value=PipelineState.prompt,
                on_change=PipelineState.set_prompt,
                rows="6",
                width="100%",
                resize="vertical",
            ),
            rx.hstack(
                rx.text("Examples:", size="1", color=rx.color("gray", 11)),
                *[_example_chip(i, p) for i, p in enumerate(EXAMPLE_PROMPTS)],
                wrap="wrap",
                spacing="2",
                width="100%",
            ),
            rx.hstack(
                rx.text(
                    "Profile: " + PipelineState.profile,
                    size="2",
                    color=rx.color("gray", 11),
                ),
                rx.spacer(),
                rx.button(
                    rx.cond(
                        PipelineState.is_running,
                        rx.hstack(rx.spinner(size="1"), rx.text("Improving…")),
                        rx.hstack(rx.icon("zap", size=16), rx.text("Improve")),
                    ),
                    on_click=PipelineState.submit,
                    disabled=PipelineState.is_running,
                    color_scheme="indigo",
                    size="3",
                ),
                width="100%",
                align="center",
            ),
            spacing="3",
            align="stretch",
        ),
        size="2",
        width="100%",
    )
