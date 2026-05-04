# Frontend

The web client lives in `frontend/` and is built with [Reflex](https://reflex.dev),
which compiles a pure-Python definition to a Next.js + React + Tailwind +
Radix Themes app. State sync between browser and server is over WebSocket;
streaming pipeline events arrive through Server-Sent Events from the FastAPI
backend at `/v1/improve/stream`.

## Layout

```
frontend/
├── rxconfig.py                        # api_url + port config
├── Dockerfile                         # multi-stage build with uv
└── prompt_autoimprove_ui/
    ├── prompt_autoimprove_ui.py       # rx.App + dark indigo theme
    ├── state.py                       # PipelineState (typed stages/metrics/history)
    ├── api_client.py                  # httpx wrapper that consumes SSE events
    ├── pages/home.py                  # three-column layout
    └── components/                    # 8 focused UI cards
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
# 1. start the FastAPI backend (port 8000)
uv run uvicorn prompt_autoimprove.api.http.app:app --port 8000

# 2. in another shell, start the Reflex dev server
cd frontend
PAI_API_KEY=dev-key PAI_BACKEND_URL=http://127.0.0.1:8000 \
  uv run --group frontend reflex run --frontend-port 3000 --backend-port 8001
```

Open <http://localhost:3000>. The left rail lists model profiles fetched from
`/v1/profiles`. Pick one, paste a prompt, hit **Improve**. The pipeline timeline
fills in stage by stage; the metric breakdown and explanation card light up at
the end. If you set `ANTHROPIC_API_KEY` or the `OPENAI_*` envs on the backend,
the candidate is also probated against the real model and the result shows in
the Improved prompt card.

## Environment

| Variable | Default | Purpose |
| --- | --- | --- |
| `PAI_BACKEND_URL` | `http://localhost:8000` | Backend base URL the SPA calls. |
| `PAI_API_KEY` | `dev-key` | Sent as `x-api-key` on every call. |
| `PAI_FRONTEND_PORT` | `3000` | Reflex dev server port. |
| `PAI_FRONTEND_BACKEND_PORT` | `8001` | Reflex's internal WebSocket port. |

## Docker

`docker compose --profile app up --build` brings up `postgres`, `redpanda`,
`minio`, the FastAPI `app` (8000 / 50051), and the Reflex `frontend` (3000 /
8001) together. The frontend image is built from `frontend/Dockerfile` against
the same uv lockfile, only pulling the `frontend` dependency group.
