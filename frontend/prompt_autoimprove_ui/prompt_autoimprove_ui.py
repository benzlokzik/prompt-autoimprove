import reflex as rx

from prompt_autoimprove_ui.pages.home import home

app = rx.App(
    theme=rx.theme(
        appearance="dark",
        has_background=True,
        accent_color="iris",
        gray_color="slate",
        radius="large",
        scaling="100%",
    ),
    style={
        "font_family": (
            "InterVariable, Inter, ui-sans-serif, system-ui, "
            "-apple-system, BlinkMacSystemFont, sans-serif"
        ),
        "background": (
            "radial-gradient(1200px 600px at 90% -10%, rgba(99,102,241,0.18), transparent 60%), "
            "radial-gradient(900px 500px at -10% 110%, rgba(168,85,247,0.14), transparent 60%), "
            "var(--color-background)"
        ),
        "min_height": "100vh",
    },
    stylesheets=[
        "https://rsms.me/inter/inter.css",
    ],
)
app.add_page(home, route="/", title="prompt-autoimprove")
