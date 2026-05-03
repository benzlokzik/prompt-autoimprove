import os

import reflex as rx

config = rx.Config(
    app_name="prompt_autoimprove_ui",
    api_url=os.environ.get("PAI_FRONTEND_BACKEND_URL", "http://localhost:8000"),
    frontend_port=int(os.environ.get("PAI_FRONTEND_PORT", "3000")),
    backend_port=int(os.environ.get("PAI_FRONTEND_BACKEND_PORT", "8001")),
    telemetry_enabled=False,
    show_built_with_reflex=False,
)
