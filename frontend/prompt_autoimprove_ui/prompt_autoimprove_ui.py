import reflex as rx

from prompt_autoimprove_ui.pages.home import home

app = rx.App(
    theme=rx.theme(
        appearance="dark",
        accent_color="indigo",
        gray_color="slate",
        radius="large",
        scaling="100%",
    ),
    style={
        "font_family": "Inter, ui-sans-serif, system-ui, sans-serif",
    },
)
app.add_page(home, route="/", title="prompt-autoimprove")
