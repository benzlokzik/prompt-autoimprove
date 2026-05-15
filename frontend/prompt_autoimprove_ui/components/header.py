import reflex as rx


def header() -> rx.Component:
    return rx.hstack(
        rx.hstack(
            rx.box(
                rx.icon("sparkles", color="white", size=18),
                background=(
                    "linear-gradient(135deg, "
                    "var(--iris-9) 0%, var(--violet-9) 50%, var(--purple-9) 100%)"
                ),
                padding="2",
                border_radius="10px",
                box_shadow="0 6px 20px -8px var(--iris-9)",
            ),
            rx.vstack(
                rx.heading("prompt-autoimprove", size="4", weight="bold"),
                rx.text(
                    "Improve any prompt for any LLM",
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
            rx.link(
                rx.button(
                    rx.icon("book-open", size=14),
                    rx.text("Docs"),
                    variant="ghost",
                    color_scheme="gray",
                    size="2",
                ),
                href="https://github.com/benzlokzik/prompt-autoimprove",
                is_external=True,
            ),
            rx.link(
                rx.button(
                    rx.icon("github", size=14),
                    rx.text("GitHub"),
                    variant="ghost",
                    color_scheme="gray",
                    size="2",
                ),
                href="https://github.com/benzlokzik/prompt-autoimprove",
                is_external=True,
            ),
            rx.color_mode.button(),
            spacing="2",
            align="center",
        ),
        width="100%",
        padding_y="3",
        padding_x="6",
        align="center",
        border_bottom=f"1px solid {rx.color('gray', 4)}",
        background=rx.color("gray", 1),
        position="sticky",
        top="0",
        z_index="50",
        backdrop_filter="blur(12px)",
    )
