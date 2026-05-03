import reflex as rx


def header() -> rx.Component:
    return rx.hstack(
        rx.hstack(
            rx.icon("sparkles", color=rx.color("indigo", 9), size=22),
            rx.heading("prompt-autoimprove", size="5", weight="bold"),
            rx.badge("v0.1", color_scheme="indigo", variant="soft"),
            spacing="3",
            align="center",
        ),
        rx.spacer(),
        rx.hstack(
            rx.link(
                rx.icon("github", size=18),
                href="https://github.com/benzlokzik/prompt-autoimprove",
                is_external=True,
            ),
            rx.color_mode.button(),
            spacing="3",
            align="center",
        ),
        width="100%",
        padding_y="3",
        padding_x="6",
        border_bottom=f"1px solid {rx.color('gray', 5)}",
    )
