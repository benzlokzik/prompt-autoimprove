import reflex as rx

from prompt_autoimprove_ui.i18n import t
from prompt_autoimprove_ui.state import PipelineState


def _metric_card(metric) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text(
                    metric["label"],
                    size="1",
                    color=rx.color("gray", 11),
                    weight="bold",
                ),
                rx.spacer(),
                rx.text(
                    "w ",
                    metric["weight_str"],
                    size="1",
                    color=rx.color("gray", 10),
                    style={"font_variant_numeric": "tabular-nums"},
                ),
                width="100%",
                align="center",
            ),
            rx.heading(
                metric["value_str"],
                size="5",
                color=rx.color("iris", 11),
                style={"font_variant_numeric": "tabular-nums"},
            ),
            rx.progress(
                value=(metric["value"] * 100).to(int),
                color_scheme="iris",
                size="2",
            ),
            spacing="2",
            align="stretch",
            width="100%",
        ),
        size="1",
        width="100%",
    )


def metric_breakdown() -> rx.Component:
    return rx.cond(
        PipelineState.metrics.length() > 0,
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.icon("gauge", size=16, color=rx.color("iris", 10)),
                    rx.heading(t("score", PipelineState.language), size="3"),
                    spacing="2",
                    align="center",
                ),
                rx.spacer(),
                rx.box(
                    rx.text(
                        PipelineState.score_display,
                        size="6",
                        weight="bold",
                        color=rx.color("iris", 11),
                        style={"font_variant_numeric": "tabular-nums"},
                    ),
                    padding_x="4",
                    padding_y="2",
                    border_radius="12px",
                    background=rx.color("iris", 3),
                    border=f"1px solid {rx.color('iris', 6)}",
                ),
                align="center",
                width="100%",
            ),
            rx.grid(
                rx.foreach(PipelineState.metrics, _metric_card),
                columns=rx.breakpoints(
                    initial="2",
                    sm="3",
                    md=PipelineState.metric_columns,
                ),
                spacing="3",
                width="100%",
            ),
            spacing="4",
            align="stretch",
            width="100%",
        ),
        rx.fragment(),
    )
