import reflex as rx

from prompt_autoimprove_ui.state import PipelineState

_STAGE_ICON: dict[str, str] = {
    "received": "inbox",
    "normalized": "broom",
    "strategy_selected": "compass",
    "candidate": "sparkles",
    "partial_eval": "ruler",
    "evaluated": "ruler",
    "probation": "play",
    "probation_failed": "triangle-alert",
    "final_decision": "check-check",
}

_STAGE_LABEL: dict[str, str] = {
    "received": "Received",
    "normalized": "Normalized",
    "strategy_selected": "Strategy chosen",
    "candidate": "Candidate built",
    "partial_eval": "Scoring",
    "evaluated": "Evaluated",
    "probation": "Probation run",
    "probation_failed": "Probation failed",
    "final_decision": "Final decision",
}


def _stage_card(stage) -> rx.Component:
    return rx.hstack(
        rx.box(
            rx.icon(
                "circle-dot",
                size=16,
                color=rx.color("indigo", 10),
            ),
            background=rx.color("indigo", 3),
            padding="2",
            border_radius="full",
        ),
        rx.vstack(
            rx.text(
                stage["stage"],
                size="2",
                weight="bold",
            ),
            rx.code(
                stage["payload"],
                size="1",
                color_scheme="gray",
                variant="ghost",
            ),
            spacing="1",
            align="start",
            width="100%",
        ),
        spacing="3",
        align="start",
        padding="2",
        width="100%",
        border_left=f"2px solid {rx.color('indigo', 6)}",
    )


def pipeline_timeline() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("activity", size=18, color=rx.color("indigo", 10)),
                rx.heading("Pipeline", size="3"),
                rx.spacer(),
                rx.cond(
                    PipelineState.is_running,
                    rx.spinner(size="2"),
                    rx.fragment(),
                ),
                align="center",
                width="100%",
            ),
            rx.cond(
                PipelineState.stages.length() > 0,
                rx.vstack(
                    rx.foreach(PipelineState.stages, _stage_card),
                    spacing="2",
                    align="stretch",
                    width="100%",
                ),
                rx.text(
                    "Submit a prompt to see the pipeline run live.",
                    size="2",
                    color=rx.color("gray", 11),
                ),
            ),
            spacing="3",
            align="stretch",
        ),
        size="2",
        width="100%",
    )
