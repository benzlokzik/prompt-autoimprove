import reflex as rx

from prompt_autoimprove_ui.state import PipelineState

_FAMILY_ICON: dict[str, str] = {
    "qwen": "circle-dot",
    "llama": "flame",
    "gemma": "gem",
    "mistral": "wind",
    "other": "box",
}


def _profile_card(profile: dict) -> rx.Component:
    name = profile["name"]
    family = profile.get("family", "other")
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon(_FAMILY_ICON.get(family, "box"), size=16),
                rx.text(name, weight="bold", size="2"),
                rx.spacer(),
                rx.cond(
                    profile["supports_vision"],
                    rx.badge("vision", color_scheme="purple", variant="soft", size="1"),
                    rx.fragment(),
                ),
                width="100%",
                align="center",
            ),
            rx.text(
                f"{profile['format']} · ctx {profile['context_window']}",
                size="1",
                color=rx.color("gray", 11),
            ),
            spacing="1",
            align="start",
        ),
        as_child=False,
        size="1",
        variant=rx.cond(PipelineState.profile == name, "surface", "ghost"),
        on_click=PipelineState.set_profile(name),
        cursor="pointer",
        width="100%",
    )


def profile_picker() -> rx.Component:
    return rx.vstack(
        rx.text("Profiles", size="2", weight="bold", color=rx.color("gray", 11)),
        rx.foreach(PipelineState.profiles, _profile_card),
        spacing="2",
        align="stretch",
        width="100%",
    )
