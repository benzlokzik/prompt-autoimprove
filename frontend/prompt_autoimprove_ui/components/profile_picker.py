import reflex as rx

from prompt_autoimprove_ui.i18n import t
from prompt_autoimprove_ui.state import PipelineState


def _family_chip(family: str) -> rx.Component:
    is_active = PipelineState.profile == family
    return rx.box(
        rx.text(
            family,
            size="3",
            weight="medium",
            color=rx.cond(is_active, "white", rx.color("gray", 12)),
            line_height="1",
            white_space="nowrap",
        ),
        padding_x="5",
        padding_y="0",
        height="40px",
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
        on_click=PipelineState.set_profile(family),
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
                t("model_family", PipelineState.language),
                size="1",
                weight="bold",
                color=rx.color("gray", 11),
                letter_spacing="0.05em",
                text_transform="uppercase",
            ),
            rx.spacer(),
            rx.cond(
                PipelineState.profile != "",
                rx.hstack(
                    rx.icon("cpu", size=12, color=rx.color("gray", 10)),
                    rx.text(
                        PipelineState.profile,
                        size="1",
                        color=rx.color("gray", 10),
                        font_family="ui-monospace, monospace",
                    ),
                    spacing="1",
                    align="center",
                ),
                rx.fragment(),
            ),
            spacing="2",
            align="center",
            width="100%",
        ),
        rx.cond(
            PipelineState.unique_families.length() > 0,
            rx.scroll_area(
                rx.hstack(
                    rx.foreach(PipelineState.unique_families, _family_chip),
                    spacing="4",
                    padding_y="3",
                    padding_right="3",
                ),
                scrollbars="horizontal",
                type="hover",
                width="100%",
            ),
            rx.hstack(
                rx.cond(
                    PipelineState.is_loading_profiles,
                    rx.spinner(size="1"),
                    rx.fragment(),
                ),
                rx.text(
                    t("loading", PipelineState.language),
                    size="1",
                    color=rx.color("gray", 10),
                ),
                spacing="2",
                align="center",
            ),
        ),
        spacing="5",
        align="stretch",
        width="100%",
    )
