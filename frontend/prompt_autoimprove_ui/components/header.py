import reflex as rx

from prompt_autoimprove_ui.i18n import t
from prompt_autoimprove_ui.state import PipelineState


def header() -> rx.Component:
    return rx.hstack(
        rx.hstack(
            rx.image(
                src="/logo.svg",
                width="40px",
                height="40px",
                border_radius="11px",
                box_shadow="0 6px 20px -8px var(--iris-9)",
            ),
            rx.vstack(
                rx.heading("prompt-autoimprove", size="4", weight="bold"),
                rx.text(
                    t("tagline", PipelineState.language),
                    size="1",
                    color=rx.color("gray", 11),
                ),
                spacing="0",
                align="start",
            ),
            spacing="3",
            align="center",
        ),
        rx.spacer(),
        rx.hstack(
            rx.button(
                rx.icon("languages", size=14),
                t("language", PipelineState.language),
                on_click=PipelineState.toggle_language,
                variant="soft",
                color_scheme="iris",
                size="2",
            ),
            rx.link(
                rx.button(
                    rx.icon("book-open", size=14),
                    rx.text(t("docs", PipelineState.language)),
                    variant="ghost",
                    color_scheme="gray",
                    size="2",
                ),
                href="https://github.com/benzlokzik-university/prompt-autoimprove",
                is_external=True,
            ),
            rx.link(
                rx.button(
                    rx.icon("github", size=14),
                    rx.text(t("github", PipelineState.language)),
                    variant="ghost",
                    color_scheme="gray",
                    size="2",
                ),
                href="https://github.com/benzlokzik-university/prompt-autoimprove",
                is_external=True,
            ),
            rx.color_mode.button(),
            spacing="2",
            align="center",
        ),
        width="100%",
        padding_y="5",
        padding_x="6",
        align="center",
        border_bottom=f"1px solid {rx.color('gray', 4)}",
        background=rx.color("gray", 1),
        position="sticky",
        top="0",
        z_index="50",
        backdrop_filter="blur(12px)",
    )
