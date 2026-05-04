import reflex as rx

from prompt_autoimprove_ui.state import PipelineState

_METRIC_LABEL: dict[str, str] = {
    "q_c": "Clarity",
    "q_p": "Compliance",
    "q_s": "Safety",
    "q_t": "Token cost",
    "q_l": "Latency",
}


def _metric_row(metric) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.text(metric["name"], size="2"),
            rx.spacer(),
            rx.text(
                "weight ",
                metric["weight"],
                size="1",
                color=rx.color("gray", 11),
            ),
            rx.text(
                metric["value"],
                size="2",
                weight="bold",
                color=rx.color("indigo", 11),
            ),
            width="100%",
            align="center",
        ),
        rx.progress(
            value=(metric["value"] * 100).to(int),
            color_scheme="indigo",
            size="2",
        ),
        spacing="1",
        align="stretch",
        width="100%",
    )


def metric_breakdown() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("gauge", size=18, color=rx.color("indigo", 10)),
                rx.heading("Score", size="3"),
                rx.spacer(),
                rx.heading(
                    PipelineState.integrated_score,
                    size="6",
                    color=rx.color("indigo", 11),
                ),
                width="100%",
                align="center",
            ),
            rx.cond(
                PipelineState.metrics.length() > 0,
                rx.vstack(
                    rx.foreach(PipelineState.metrics, _metric_row),
                    spacing="3",
                    align="stretch",
                    width="100%",
                ),
                rx.text(
                    "Metric breakdown will appear after the run completes.",
                    size="2",
                    color=rx.color("gray", 11),
                ),
            ),
            spacing="3",
            align="stretch",
            width="100%",
        ),
        size="2",
        width="100%",
    )
