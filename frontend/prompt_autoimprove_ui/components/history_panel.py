import reflex as rx

from prompt_autoimprove_ui.state import PipelineState


def _history_row(item: dict) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text(
                item["text"],
                size="2",
                weight="medium",
                no_of_lines=2,
            ),
            rx.hstack(
                rx.text(
                    item["created_at"][:19].replace("T", " "),
                    size="1",
                    color=rx.color("gray", 11),
                ),
                rx.spacer(),
                rx.badge(
                    item["modality"],
                    variant="soft",
                    color_scheme="gray",
                    size="1",
                ),
                width="100%",
            ),
            spacing="1",
            align="start",
            width="100%",
        ),
        padding="2",
        border_radius="medium",
        background=rx.color("gray", 2),
        width="100%",
    )


def history_panel() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.icon("history", size=16, color=rx.color("gray", 11)),
            rx.text("History", size="2", weight="bold", color=rx.color("gray", 11)),
            width="100%",
            align="center",
        ),
        rx.input(
            placeholder="Session id or user ref",
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
                "No prior runs for this session yet.",
                size="1",
                color=rx.color("gray", 11),
            ),
        ),
        spacing="3",
        align="stretch",
        width="100%",
    )
