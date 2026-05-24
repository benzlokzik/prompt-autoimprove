# prompt-autoimprove

<section class="pai-hero" markdown>
<p class="pai-kicker">Пайплайн оптимизации промптов</p>

`prompt-autoimprove` улучшает исходные промпты до отправки в целевую модель.
Он нормализует ввод, выбирает стратегии-кандидаты, оценивает результат,
маршрутизирует победителя, при необходимости запускает model probation probe и
объясняет принятое решение.

<p class="pai-lede">
Проект подходит для локальных экспериментов, API-сервисов и воспроизводимых
оценочных сценариев, где каждая редакция промпта должна быть прослеживаемой.
</p>
</section>

## Пайплайн

<div class="pai-pipeline" markdown>
<div class="pai-step" markdown>Нормализует текст, язык, тип задачи, недостающие параметры, PII и флаги безопасности.</div>
<div class="pai-step" markdown>Генерирует кандидаты с учетом задачи и профиля модели.</div>
<div class="pai-step" markdown>Проверяет структуру, длину, противоречия и ограничения безопасности.</div>
<div class="pai-step" markdown>Оценивает кандидаты интегральной формулой качества.</div>
<div class="pai-step" markdown>Маршрутизирует победителя в локальный или API-backed профиль.</div>
<div class="pai-step" markdown>Объясняет выигравшую редакцию и сохраняет запуск.</div>
</div>

## С чего начать

<div class="pai-links" markdown>

[Архитектура](architecture.md){ .md-button }
[CLI](cli.md){ .md-button }
[Оценка](scoring.md){ .md-button }
[Локальные модели](local-models.md){ .md-button }

</div>

## Возможности

<div class="pai-grid" markdown>
<div class="pai-card" markdown>

### CLI

Запускайте `pai improve` локально и смотрите выбранную стратегию, оценку и
объяснение.

</div>

<div class="pai-card" markdown>

### API

Используйте FastAPI HTTP backend, SSE-поток `/v1/improve/stream` или gRPC
`AutoImproveService`.

</div>

<div class="pai-card" markdown>

### Фронтенд

Управляйте пайплайном из Reflex web client: выбор профиля, live-стадии,
метрики и история.

</div>

<div class="pai-card" markdown>

### Оценка

Сравнивайте редакции через взвешенную сумму $S = \sum_i w_i\,q_i$. Полная
формула и веса — в разделе [Оценка](scoring.md).

</div>

<div class="pai-card" markdown>

### Локальные модели

Маршрутизируйте запросы в Ollama, LM Studio, local GGUF, Hugging Face
safetensors или OpenAI-compatible endpoints.

</div>
</div>

## Быстрый старт

```bash
uv sync --all-groups
uv run pai improve --prompt "Summarize this PR" --profile qwen3-7b
```

## Разработка документации

```bash
uv run mkdocs serve   # live preview at http://127.0.0.1:8000
uv run mkdocs build   # static site in ./site
```
