# Запуск сервиса

Эта страница описывает запуск `prompt-autoimprove` целиком — через Docker
Compose для полного стека или локально для разработки.

## Через Docker Compose

```bash
docker compose up -d --build app
```

Compose запускает зависимости по порядку и ждёт готовности каждой:

1. **postgres** — база данных приложения.
2. **redpanda** — Kafka-совместимый брокер событий.
3. **migrate** — одноразовая задача, выполняющая `alembic upgrade head` и
   завершающаяся. Приложение **не** стартует, пока миграции не выполнятся.
4. **app** — HTTP API FastAPI на `:8000` и gRPC `AutoImproveService` на `:50051`
   в одном процессе.

Веб-клиент (собран через `reflex --env prod`) поднимается отдельно:

```bash
docker compose up -d --build frontend   # http://localhost:3000
```

`minio` включён для хранения артефактов, но от него ничего не зависит. Проверка
готовности:

```bash
curl http://localhost:8000/healthz
# {"status":"ok","orchestrator":true,"persistence":true}
```

| Сервис | Порт(ы) | Примечания |
| --- | --- | --- |
| app (HTTP) | 8000 | `/docs`, `/healthz`, `/v1/*` |
| app (gRPC) | 50051 | `AutoImproveService`; отключить `PAI_API__GRPC_ENABLED=false` |
| frontend | 3000 | UI на Reflex (single-port) |
| postgres | 5432 | |
| redpanda | 19092 | внешний Kafka-листенер |
| minio | 9000 / 9001 | API / консоль |

Остановка (со сбросом тома, чтобы очистить БД):

```bash
docker compose down -v
```

## Опубликованные образы

Публикация GitHub-релиза собирает и пушит оба образа в GitHub Container
Registry (через workflow `Publish images`) с тегами версии релиза
(`X.Y.Z`, `X.Y`) и `latest`:

```bash
docker pull ghcr.io/benzlokzik-university/prompt-autoimprove:latest
docker pull ghcr.io/benzlokzik-university/prompt-autoimprove-frontend:latest
```

Чтобы использовать опубликованный образ вместо локальной сборки, переопределите
`image:` (убрав `build:`) в compose или запустите `docker run` напрямую с теми
же переменными `PAI_*`, что и у сервиса `app`.

## Локально (без Docker)

```bash
uv sync
uv run alembic upgrade head            # или PAI_DB__AUTO_CREATE=1 для временной БД
uv run uvicorn prompt_autoimprove.api.http.app:app --reload --port 8000
```

Другие точки входа используют тот же рантайм пайплайна:

```bash
uv run pai improve --prompt "Summarize this PR" --profile qwen3-7b   # CLI
uv run pai serve-grpc                                                # только gRPC
uv run pai profiles                                                  # список профилей
```

База данных необязательна для HTTP/CLI: без неё сервис работает в режиме
улучшения без сохранения истории (`/healthz` показывает `persistence: false`).

## Конфигурация

Все настройки сервиса используют префикс `PAI_*` и `__` как разделитель
вложенности.

| Переменная | По умолчанию | Назначение |
| --- | --- | --- |
| `PAI_API__API_KEY` | `dev-key` в dev | Обязательна вне dev, если не задан `PAI_API__ALLOW_DEV_KEY=1`. |
| `PAI_API__GRPC_ENABLED` | `true` | Запуск встроенного gRPC-сервера. |
| `PAI_API__CORS_ORIGINS` | localhost:3000 | Разрешённые origin через запятую. |
| `PAI_DB__DSN` | локальный Postgres | Async DSN для SQLAlchemy. |
| `PAI_DB__AUTO_CREATE` | `false` | Создавать таблицы при старте вместо миграций (только dev). |
| `PAI_KAFKA__ENABLED` | `false` | Публиковать события пайплайна в Kafka/Redpanda. |
| `PAI_CLASSIFIER__BACKEND` | `heuristic` | `heuristic`, `embeddings`, `judge` или `composite`. |
| `PAI_SCORER__SEMANTIC` | `false` | Смешивать эмбеддинг-близость намерения в скоринг (нужна группа `ml`). |

## Дополнительные группы зависимостей

```bash
uv sync --group ml             # токенизатор tiktoken, эмбеддинги, semantic scorer
uv sync --group local-models   # llama.cpp / GGUF локальный инференс
uv sync --group frontend       # веб-клиент Reflex
```

Образ Docker принимает `--build-arg INCLUDE_ML=1` и
`--build-arg INCLUDE_LOCAL_MODELS=1`, чтобы вшить их.
