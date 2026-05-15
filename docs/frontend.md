# Frontend

The web client lives in `frontend/` and is built with
[Reflex](https://reflex.dev). Reflex compiles the Python UI definition into a
Next.js, React, Tailwind, and Radix Themes app. Browser/server state sync uses
WebSocket, while pipeline events stream from the FastAPI backend through
Server-Sent Events at `/v1/improve/stream`.

## Layout

```text
frontend/
├── rxconfig.py                        # api_url + port config
├── Dockerfile                         # multi-stage build with uv
└── prompt_autoimprove_ui/
    ├── prompt_autoimprove_ui.py       # rx.App + theme
    ├── state.py                       # PipelineState stages, metrics, history
    ├── api_client.py                  # httpx wrapper for SSE events
    ├── pages/home.py                  # main workspace layout
    └── components/
        ├── header.py
        ├── profile_picker.py
        ├── prompt_card.py
        ├── pipeline_timeline.py
        ├── candidate_view.py
        ├── metric_breakdown.py
        ├── explanation_card.py
        └── history_panel.py
```

## Run locally

```bash
# 1. start the FastAPI backend on port 8000
uv run uvicorn prompt_autoimprove.api.http.app:app --port 8000

# 2. in another shell, start the Reflex dev server
cd frontend
PAI_API_KEY=dev-key PAI_BACKEND_URL=http://127.0.0.1:8000 \
  uv run --group frontend reflex run --frontend-port 3000 --backend-port 8001
```

Open <http://localhost:3000>. The left rail lists model profiles fetched from
`/v1/profiles`. Pick a profile, paste a prompt, and select **Improve**. The
pipeline timeline fills in stage by stage; the metric breakdown and explanation
card update when scoring completes. If the backend has `ANTHROPIC_API_KEY` or
the `OPENAI_*` variables configured, the selected candidate can also run through
a real-model probation probe and show the result in the improved prompt panel.

## Environment

| Variable | Default | Purpose |
| --- | --- | --- |
| `PAI_BACKEND_URL` | `http://localhost:8000` | Backend base URL called by the SPA. |
| `PAI_API_KEY` | `dev-key` | Sent as `x-api-key` on every request. |
| `PAI_FRONTEND_PORT` | `3000` | Reflex dev server port. |
| `PAI_FRONTEND_BACKEND_PORT` | `8001` | Reflex internal WebSocket port. |

## Docker

`docker compose --profile app up --build` starts `postgres`, `redpanda`,
`minio`, the FastAPI `app` on ports `8000` and `50051`, and the Reflex
`frontend` on ports `3000` and `8001`. The frontend image is built from
`frontend/Dockerfile` with the `frontend` dependency group from the same
`uv.lock`.
