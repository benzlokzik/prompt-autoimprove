import reflex as rx


def code_view(content, language: str, *, can_copy: bool = True) -> rx.Component:
    """A code block with a small language label header (rx.code_block shows none)."""
    return rx.box(
        rx.hstack(
            rx.icon("code", size=12, color=rx.color("gray", 9)),
            rx.text(
                language,
                size="1",
                color=rx.color("gray", 10),
                weight="medium",
                style={"font_family": "ui-monospace, monospace", "letter_spacing": "0.04em"},
            ),
            spacing="1",
            align="center",
            width="100%",
            padding_x="3",
            padding_y="1",
            background=rx.color("gray", 3),
            border_radius="8px 8px 0 0",
            border=f"1px solid {rx.color('gray', 4)}",
        ),
        rx.code_block(
            content,
            can_copy=can_copy,
            wrap_long_lines=True,
            language=language,
            theme=rx.code_block.themes.atom_dark,
            width="100%",
            style={"margin": "0", "border_radius": "0 0 8px 8px"},
        ),
        width="100%",
    )
