import reflex as rx

from prompt_autoimprove_ui.state import PipelineState


def _stage_dot(stage) -> rx.Component:
    return rx.vstack(
        rx.box(
            rx.icon("check", size=12, color="white"),
            background=rx.color("iris", 9),
            border_radius="999px",
            padding="2",
            width="28px",
            height="28px",
            display="flex",
            align_items="center",
            justify_content="center",
            box_shadow=f"0 0 0 4px {rx.color('iris', 3)}",
        ),
        rx.text(
            stage["stage"],
            size="1",
            color=rx.color("gray", 11),
            weight="medium",
        ),
        spacing="1",
        align="center",
        flex_shrink="0",
    )


def _empty_state() -> rx.Component:
    return rx.hstack(
        rx.icon("activity", size=14, color=rx.color("gray", 9)),
        rx.text(
            "Submit a prompt to watch the pipeline run live",
            size="2",
            color=rx.color("gray", 11),
        ),
        spacing="2",
        align="center",
        padding_y="3",
    )


def pipeline_timeline() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("activity", size=16, color=rx.color("iris", 10)),
                rx.heading("Pipeline", size="3"),
                rx.spacer(),
                rx.cond(
                    PipelineState.is_running,
                    rx.hstack(
                        rx.spinner(size="1"),
                        rx.text(
                            "running",
                            size="1",
                            color=rx.color("iris", 11),
                            weight="medium",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    rx.cond(
                        PipelineState.stages.length() > 0,
                        rx.badge(
                            "done",
                            color_scheme="green",
                            variant="soft",
                            size="1",
                        ),
                        rx.fragment(),
                    ),
                ),
                align="center",
                width="100%",
            ),
            rx.cond(
                PipelineState.stages.length() > 0,
                rx.scroll_area(
                    rx.hstack(
                        rx.foreach(PipelineState.stages, _stage_dot),
                        spacing="6",
                        align="center",
                        padding_y="2",
                        padding_x="2",
                    ),
                    scrollbars="horizontal",
                    type="hover",
                    width="100%",
                ),
                _empty_state(),
            ),
            spacing="3",
            align="stretch",
        ),
        size="2",
        width="100%",
    )
