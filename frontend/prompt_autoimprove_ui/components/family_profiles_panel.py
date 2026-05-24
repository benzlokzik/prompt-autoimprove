import reflex as rx

from prompt_autoimprove_ui.state import PipelineState, ProfileItem


def _meta_badge(label) -> rx.Component:
    return rx.badge(label, variant="soft", color_scheme="gray", size="1")


def _profile_card(profile: ProfileItem) -> rx.Component:
    context_window = (profile["context_window"] // 1000).to_string() + "k ctx"
    max_output_tokens = (profile["max_output_tokens"] // 1000).to_string() + "k out"
    return rx.card(
        rx.vstack(
            rx.code(
                profile["name"],
                size="1",
                color=rx.color("gray", 11),
                white_space="nowrap",
            ),
            rx.flex(
                rx.cond(
                    profile["family_default"],
                    rx.badge("default", color_scheme="iris", size="1"),
                    rx.fragment(),
                ),
                rx.cond(
                    profile["supports_vision"],
                    rx.badge("vision", color_scheme="purple", size="1"),
                    rx.fragment(),
                ),
                rx.cond(
                    profile["supports_tools"],
                    rx.badge("tools", color_scheme="green", size="1"),
                    rx.fragment(),
                ),
                rx.cond(
                    profile["reasoning_mode"] != "none",
                    rx.badge(profile["reasoning_mode"], color_scheme="amber", size="1"),
                    rx.fragment(),
                ),
                wrap="wrap",
                gap="2",
                width="100%",
            ),
            rx.flex(
                _meta_badge(context_window),
                rx.cond(
                    profile["max_output_tokens"] > 0,
                    _meta_badge(max_output_tokens),
                    rx.fragment(),
                ),
                rx.cond(
                    profile["cost_per_1k_input"] > 0,
                    _meta_badge("$" + profile["cost_per_1k_input"].to_string() + "/1k"),
                    rx.fragment(),
                ),
                rx.cond(
                    profile["p50_latency_ms"] > 0,
                    _meta_badge(profile["p50_latency_ms"].to_string() + "ms"),
                    rx.fragment(),
                ),
                wrap="wrap",
                gap="2",
                width="100%",
            ),
            spacing="3",
            align="start",
            min_width="190px",
        ),
        size="2",
        width="240px",
        flex_shrink="0",
        background=rx.color("gray", 1),
        border=f"1px solid {rx.color('gray', 4)}",
    )


def family_profiles_panel() -> rx.Component:
    return rx.cond(
        PipelineState.selected_family_profiles.length() > 0,
        rx.scroll_area(
            rx.hstack(
                rx.foreach(PipelineState.selected_family_profiles, _profile_card),
                spacing="4",
                padding_y="3",
                padding_right="3",
                width="max-content",
            ),
            scrollbars="horizontal",
            type="hover",
            width="100%",
        ),
        rx.fragment(),
    )
