<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/wordmark-dark.svg">
    <img alt="prompt-autoimprove" src="docs/assets/wordmark.svg" height="72">
  </picture>
</p>

[![DOI](https://zenodo.org/badge/1240262549.svg)](https://zenodo.org/badge/latestdoi/1240262549)
[![CI](https://github.com/benzlokzik-university/prompt-autoimprove/actions/workflows/ci.yml/badge.svg)](https://github.com/benzlokzik-university/prompt-autoimprove/actions/workflows/ci.yml)
[![Docs](https://github.com/benzlokzik-university/prompt-autoimprove/actions/workflows/docs-pages.yml/badge.svg)](https://benzlokzik-university.github.io/prompt-autoimprove/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)

`prompt-autoimprove` — Python-сервис для улучшения промптов до отправки в
большие языковые или мультимодальные модели. Он нормализует исходный запрос,
классифицирует задачу, генерирует кандидаты по стратегиям, оценивает их,
маршрутизирует лучшую редакцию в целевой профиль, при необходимости запускает
model probation probe и сохраняет объяснение решения.

## Возможности

- Пайплайн нормализации: определение языка, классификация задачи, поиск
  недостающих параметров, редактирование PII и флаги безопасности.
- Шесть стратегий улучшения промптов: role-based, structured-output,
  chain-decomposition, few-shot, self-verification и multimodal adaptation.
- Подключаемые модельные адаптеры за единым протоколом `ModelAdapter`.
- Реестр профилей для Qwen, Llama, Gemma, мультимодального `gemma-4-e2b` и
  профилей Anthropic Claude.
- Интегральная оценка качества:
  `S = 0.30·q_c + 0.25·q_p + 0.20·q_s + 0.15·q_t + 0.10·q_l`.
- FastAPI HTTP API, SSE-поток `/v1/improve/stream` и gRPC
  server-streaming `AutoImproveService`.
- Хранение через SQLAlchemy 2 и Alembic; события пайплайна через Kafka,
  совместимую с Redpanda в разработке.
- Веб-фронтенд на Reflex с Radix Themes; см. [docs/frontend.ru.md](docs/frontend.ru.md).
- CLI-команда: `pai improve --prompt ... --profile qwen3-7b`.

## Быстрый старт

```bash
uv sync --all-groups
uv run prek install --hook-type pre-commit --hook-type commit-msg
uv run pai improve --prompt "Summarize this PR" --profile qwen3-7b
```

## Частые команды

```bash
uv run ruff check .                                                      # lint
uv run ruff format .                                                     # format
uv run ty check src                                                      # typecheck
uv run pytest -q                                                         # tests
uv run uvicorn prompt_autoimprove.api.http.app:app --reload --port 8000  # HTTP API + встроенный gRPC
uv run pai serve-grpc                                                    # только gRPC-сервер
./scripts/gen_proto.sh                                                   # regenerate gRPC stubs
uv run alembic upgrade head                                              # применить миграции (локально)
docker compose up -d                                                     # postgres + redpanda + minio
docker compose --profile app up --build                                  # app + frontend stack
```

HTTP-приложение по умолчанию запускает gRPC-сервис `AutoImproveService`
(порт 50051) в том же процессе; чтобы отключить, задайте
`PAI_API__GRPC_ENABLED=false`, либо запустите отдельный процесс через
`uv run pai serve-grpc`. В docker compose сервис `migrate` выполняет
`alembic upgrade head` до старта приложения, а фронтенд ждёт здоровый бэкенд —
поэтому запуск веб-клиента поднимает вместе с ним HTTP- и gRPC-интерфейсы.

## Веб-клиент

```bash
uv sync --group frontend
cd frontend
PAI_API_KEY=dev-key PAI_BACKEND_URL=http://127.0.0.1:8000 \
  uv run --group frontend reflex run --frontend-port 3000 --backend-port 8001
```

Откройте <http://localhost:3000>. Описание интерфейса находится в
[docs/frontend.ru.md](docs/frontend.ru.md), а запуск с Ollama, LM Studio, GGUF
или Hugging Face моделями описан в [docs/local-models.ru.md](docs/local-models.ru.md).

## Документация

```bash
uv run mkdocs serve
uv run mkdocs build --strict
```

MkDocs собирает английскую версию в `/`, а русскую — в `/ru/`.

## Конфигурация

Переменные окружения сервиса используют префикс `PAI_*`. Переменные адаптеров,
например `OPENAI_BASE_URL` и `ANTHROPIC_API_KEY`, описаны в руководствах по
моделям. Alembic читает настройки из `[tool.alembic]` в [pyproject.toml](pyproject.toml).

Схемой владеют миграции: задавайте `PAI_DB__AUTO_CREATE=1`, только чтобы
приложение само создавало таблицы для быстрого локального запуска без Alembic.
`GET /healthz` сообщает готовность оркестратора и хранилища для проверок
контейнера.

## Лицензия

GNU AGPL-3.0-only; см. [LICENSE](LICENSE). AGPL-3.0 — строгая copyleft-лицензия
с условием о сетевом использовании: если вы запускаете изменённую версию этого
сервиса и даёте пользователям работать с ним по сети, вы обязаны предоставить им
соответствующий исходный код.
