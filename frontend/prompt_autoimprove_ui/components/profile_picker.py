import reflex as rx

from prompt_autoimprove_ui.state import PipelineState


def _chip(profile) -> rx.Component:
    is_active = PipelineState.profile == profile["name"]
    return rx.box(
        rx.hstack(
            rx.icon(
                "box",
                size=14,
                color=rx.cond(is_active, "white", rx.color("gray", 11)),
                flex_shrink="0",
            ),
            rx.text(
                profile["name"],
                size="2",
                weight="medium",
                color=rx.cond(is_active, "white", rx.color("gray", 12)),
                line_height="1",
                white_space="nowrap",
            ),
            rx.cond(
                profile["supports_vision"],
                rx.badge(
                    "vision",
                    color_scheme="purple",
                    variant=rx.cond(is_active, "solid", "soft"),
                    size="1",
                ),
                rx.fragment(),
            ),
            spacing="3",
            align="center",
        ),
        padding_x="4",
        padding_y="0",
        height="36px",
        display="flex",
        align_items="center",
        border_radius="999px",
        border=rx.cond(
            is_active,
            f"1px solid {rx.color('iris', 9)}",
            f"1px solid {rx.color('gray', 5)}",
        ),
        background=rx.cond(is_active, rx.color("iris", 9), rx.color("gray", 2)),
        cursor="pointer",
        on_click=PipelineState.set_profile(profile["name"]),
        _hover={
            "background": rx.cond(is_active, rx.color("iris", 10), rx.color("gray", 3)),
            "border_color": rx.cond(is_active, rx.color("iris", 10), rx.color("gray", 7)),
        },
        transition="all 120ms ease",
        flex_shrink="0",
    )


def profile_picker() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.icon("layers", size=14, color=rx.color("gray", 11)),
            rx.text(
                "Model profile",
                size="1",
                weight="bold",
                color=rx.color("gray", 11),
                letter_spacing="0.05em",
                text_transform="uppercase",
            ),
            spacing="2",
            align="center",
        ),
        rx.scroll_area(
            rx.hstack(
                rx.foreach(PipelineState.profiles, _chip),
                spacing="3",
                padding_y="2",
                padding_right="2",
            ),
            scrollbars="horizontal",
            type="hover",
            width="100%",
        ),
        spacing="3",
        align="stretch",
        width="100%",
    )
