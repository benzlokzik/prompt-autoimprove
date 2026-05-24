import reflex as rx

from prompt_autoimprove_ui.i18n import t
from prompt_autoimprove_ui.state import PipelineState


def _example_chip(idx: int) -> rx.Component:
    text_var = PipelineState.example_prompts[idx]
    short = rx.cond(
        text_var.length() > 70,
        text_var[:67] + "…",
        text_var,
    )
    return rx.button(
        short,
        size="1",
        variant="surface",
        color_scheme="gray",
        on_click=PipelineState.use_example(idx),
        cursor="pointer",
    )


def _attachment_thumb(item, idx) -> rx.Component:
    return rx.box(
        rx.image(
            src=item["uri"],
            width="52px",
            height="52px",
            object_fit="cover",
            border_radius="8px",
            border=f"1px solid {rx.color('gray', 5)}",
        ),
        rx.icon_button(
            rx.icon("x", size=12),
            on_click=PipelineState.remove_attachment(idx),
            size="1",
            color_scheme="red",
            variant="solid",
            radius="full",
            position="absolute",
            top="-6px",
            right="-6px",
            cursor="pointer",
        ),
        position="relative",
    )


def _image_section() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.icon("image", size=14, color=rx.color("gray", 10)),
            rx.text(
                t("add_image", PipelineState.language),
                size="1",
                color=rx.color("gray", 11),
                weight="medium",
            ),
            rx.badge(
                t("image_experimental", PipelineState.language),
                color_scheme="amber",
                variant="soft",
                size="1",
            ),
            rx.tooltip(
                rx.icon("info", size=12, color=rx.color("gray", 9)),
                content=t("image_note", PipelineState.language),
            ),
            spacing="2",
            align="center",
        ),
        rx.upload(
            rx.text(
                t("add_image", PipelineState.language),
                size="1",
                color=rx.color("gray", 10),
            ),
            id="pai_image_upload",
            accept={
                "image/png": [".png"],
                "image/jpeg": [".jpg", ".jpeg"],
                "image/webp": [".webp"],
                "image/gif": [".gif"],
            },
            multiple=True,
            max_files=4,
            on_drop=PipelineState.handle_image_upload(
                rx.upload_files(upload_id="pai_image_upload")
            ),
            border=f"1px dashed {rx.color('gray', 6)}",
            border_radius="8px",
            padding="3",
            width="100%",
            cursor="pointer",
        ),
        rx.cond(
            PipelineState.attachments.length() > 0,
            rx.flex(
                rx.foreach(PipelineState.attachments, _attachment_thumb),
                wrap="wrap",
                gap="2",
                width="100%",
            ),
            rx.fragment(),
        ),
        spacing="2",
        align="stretch",
        width="100%",
    )


def prompt_card() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.icon("message-square", size=16, color=rx.color("iris", 10)),
                    rx.heading(t("your_prompt", PipelineState.language), size="3"),
                    spacing="2",
                    align="center",
                ),
                rx.spacer(),
                rx.cond(
                    PipelineState.session_ref != "",
                    rx.badge(
                        t("session", PipelineState.language) + PipelineState.session_ref[:8],
                        variant="soft",
                        color_scheme="iris",
                    ),
                    rx.fragment(),
                ),
                width="100%",
                align="center",
            ),
            rx.text_area(
                placeholder=t("placeholder", PipelineState.language),
                value=PipelineState.prompt,
                on_change=PipelineState.set_prompt,
                rows="9",
                width="100%",
                resize="vertical",
                style={
                    "font_family": (
                        "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"
                    ),
                    "font_size": "13px",
                    "line_height": "1.6",
                },
            ),
            rx.flex(
                rx.text(
                    t("try_one", PipelineState.language),
                    size="1",
                    color=rx.color("gray", 11),
                    weight="medium",
                ),
                _example_chip(0),
                _example_chip(1),
                _example_chip(2),
                wrap="wrap",
                gap="2",
                align="center",
                width="100%",
            ),
            _image_section(),
            rx.hstack(
                rx.hstack(
                    rx.icon("cpu", size=14, color=rx.color("gray", 10)),
                    rx.text(
                        t("routing_to", PipelineState.language),
                        rx.text.strong(PipelineState.profile, color=rx.color("iris", 11)),
                        size="2",
                        color=rx.color("gray", 11),
                    ),
                    spacing="1",
                    align="center",
                ),
                rx.spacer(),
                rx.tooltip(
                    rx.hstack(
                        rx.switch(
                            checked=PipelineState.sensitive,
                            on_change=PipelineState.set_sensitive,
                            color_scheme="iris",
                            size="1",
                        ),
                        rx.text(
                            t("sensitive", PipelineState.language),
                            size="2",
                            color=rx.color("gray", 11),
                        ),
                        spacing="2",
                        align="center",
                    ),
                    content=t("sensitive_note", PipelineState.language),
                ),
                rx.button(
                    rx.cond(
                        PipelineState.is_running,
                        rx.hstack(
                            rx.spinner(size="1"),
                            rx.text(t("improving", PipelineState.language)),
                            spacing="2",
                            align="center",
                        ),
                        rx.hstack(
                            rx.icon("zap", size=15),
                            rx.text(t("improve_btn", PipelineState.language)),
                            spacing="2",
                            align="center",
                        ),
                    ),
                    on_click=PipelineState.submit,
                    disabled=PipelineState.is_running,
                    color_scheme="iris",
                    size="3",
                    style={"box_shadow": "0 6px 24px -10px var(--iris-9)"},
                ),
                width="100%",
                align="center",
            ),
            spacing="4",
            align="stretch",
        ),
        size="3",
        width="100%",
    )
