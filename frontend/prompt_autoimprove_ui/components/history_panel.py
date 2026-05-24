import reflex as rx

from prompt_autoimprove_ui.i18n import t
from prompt_autoimprove_ui.state import PipelineState


def _revision_row(rev) -> rx.Component:
    return rx.hstack(
        rx.vstack(
            rx.badge(rev["strategy"], variant="soft", color_scheme="iris", size="1"),
            rx.text(
                rev["text"],
                size="1",
                no_of_lines=2,
                color=rx.color("gray", 11),
            ),
            spacing="1",
            align="start",
            width="100%",
        ),
        rx.button(
            rx.icon("pencil", size=12),
            on_click=PipelineState.load_revision(rev["text"]).stop_propagation,
            size="1",
            variant="soft",
            color_scheme="gray",
            cursor="pointer",
            title=t("load_into_editor", PipelineState.language),
        ),
        spacing="2",
        align="center",
        width="100%",
        padding="2",
        border_radius="8px",
        background=rx.color("gray", 3),
    )


def _history_row(item) -> rx.Component:
    expanded = PipelineState.expanded_prompt_id == item["prompt_id"]
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon(
                    rx.cond(expanded, "chevron-down", "chevron-right"),
                    size=14,
                    color=rx.color("gray", 10),
                ),
                rx.text(
                    item["text"],
                    size="2",
                    weight="medium",
                    no_of_lines=2,
                    color=rx.color("gray", 12),
                ),
                spacing="2",
                align="start",
                width="100%",
            ),
            rx.hstack(
                rx.text(
                    item["created_at"],
                    size="1",
                    color=rx.color("gray", 10),
                ),
                rx.spacer(),
                rx.cond(
                    item["revisions"].length() > 0,
                    rx.badge(
                        item["revisions"].length().to_string()
                        + t("revisions", PipelineState.language),
                        variant="soft",
                        color_scheme="iris",
                        size="1",
                    ),
                    rx.fragment(),
                ),
                rx.badge(
                    item["modality"],
                    variant="soft",
                    color_scheme="gray",
                    size="1",
                ),
                width="100%",
                align="center",
                spacing="2",
            ),
            rx.cond(
                expanded,
                rx.vstack(
                    rx.foreach(item["revisions"], _revision_row),
                    spacing="2",
                    align="stretch",
                    width="100%",
                    padding_top="1",
                ),
                rx.fragment(),
            ),
            spacing="2",
            align="start",
            width="100%",
        ),
        on_click=PipelineState.toggle_history_item(item["prompt_id"]),
        padding="3",
        border_radius="10px",
        background=rx.color("gray", 2),
        border=f"1px solid {rx.color('gray', 4)}",
        width="100%",
        cursor="pointer",
        _hover={"border_color": rx.color("iris", 7)},
        transition="border-color 120ms",
    )


def history_panel() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("history", size=16, color=rx.color("iris", 10)),
                rx.heading(t("history", PipelineState.language), size="3"),
                rx.spacer(),
                rx.cond(
                    PipelineState.history_items.length() > 0,
                    rx.badge(
                        PipelineState.history_items.length().to_string()
                        + t("runs", PipelineState.language),
                        variant="soft",
                        color_scheme="iris",
                        size="1",
                    ),
                    rx.fragment(),
                ),
                width="100%",
                align="center",
            ),
            rx.input(
                rx.input.slot(rx.icon("search", size=14)),
                placeholder=t("search_session", PipelineState.language),
                value=PipelineState.session_ref,
                on_change=PipelineState.set_session_ref,
                on_blur=PipelineState.load_history,
                size="2",
                width="100%",
            ),
            rx.cond(
                PipelineState.history_items.length() > 0,
                rx.vstack(
                    rx.foreach(PipelineState.history_items, _history_row),
                    spacing="2",
                    align="stretch",
                    width="100%",
                ),
                rx.text(
                    t("history_empty", PipelineState.language),
                    size="1",
                    color=rx.color("gray", 10),
                ),
            ),
            spacing="3",
            align="stretch",
        ),
        size="2",
        width="100%",
    )
