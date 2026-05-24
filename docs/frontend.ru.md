# Фронтенд

Веб-клиент находится в `frontend/` и построен на [Reflex](https://reflex.dev).
Reflex компилирует Python-описание UI в Next.js, React, Tailwind и Radix Themes
приложение. Синхронизация состояния браузера и сервера идет через WebSocket, а
события пайплайна поступают из FastAPI backend через Server-Sent Events на
`/v1/improve/stream`.

## Структура

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

## Локальный запуск

```bash
# 1. start the FastAPI backend on port 8000
uv run uvicorn prompt_autoimprove.api.http.app:app --port 8000

# 2. in another shell, start the Reflex dev server
cd frontend
PAI_API_KEY=dev-key PAI_BACKEND_URL=http://127.0.0.1:8000 \
  uv run --group frontend reflex run --frontend-port 3000 --backend-port 8001
```

Откройте <http://localhost:3000>. Левая панель показывает модельные профили из
`/v1/profiles`. Выберите профиль, вставьте промпт и нажмите **Improve**.
Pipeline timeline заполняется по стадиям; metric breakdown и explanation card
обновляются после scoring. Если backend настроен через `ANTHROPIC_API_KEY` или
`OPENAI_*`, выбранный кандидат может пройти real-model probation probe, а ответ
появится в панели improved prompt.

## Возможности рабочей области

- **Переключатель «чувствительный»** на карточке промпта задаёт `sensitive`:
  маршрутизация остаётся на локальных моделях, LLM-переписывание пропускается;
  активный язык интерфейса отправляется как `locale_hint`.
- **Ввод изображений (экспериментально).** Перетащите или выберите изображения
  на карточке промпта. Они кодируются в base64 data URI и отправляются как
  `attachments` в `POST /v1/improve` для профилей с поддержкой vision.
  Поддержка нестабильна и зависит от модели и формата; максимум 4 изображения по
  8 МБ.
- **«Использовать этот промпт»** копирует улучшенный кандидат обратно в редактор.
- **Раскрытие истории.** Строки истории раскрываются в список прошлых редакций;
  каждую можно загрузить обратно в редактор.
- **Различение ошибок.** Сеть, валидация (422), лимит (429), not-found (404) и
  серверные ошибки (5xx) показывают разные сообщения.
- Сетка метрик берёт число колонок из полученных метрик и адаптируется на узких
  экранах.

## Переменные окружения

| Переменная | По умолчанию | Назначение |
| --- | --- | --- |
| `PAI_BACKEND_URL` | `http://localhost:8000` | Backend base URL для SPA. |
| `PAI_API_KEY` | `dev-key` | Отправляется как `x-api-key` в каждом запросе. |
| `PAI_FRONTEND_PORT` | `3000` | Порт Reflex dev server. |
| `PAI_FRONTEND_BACKEND_PORT` | `8001` | Внутренний WebSocket-порт Reflex. |

## Docker

`docker compose --profile app up --build` запускает `postgres`, `redpanda`,
`minio`, FastAPI `app` на портах `8000` и `50051`, а также Reflex `frontend` на
портах `3000` и `8001`. Образ frontend собирается из `frontend/Dockerfile` с
dependency group `frontend` из того же `uv.lock`.
