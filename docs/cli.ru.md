# Использование CLI

Команда `pai` — самый быстрый способ запустить improvement pipeline из
терминала.

## Список профилей

```bash
uv run pai profiles
```

Команда печатает профили, загруженные из
`src/prompt_autoimprove/registry/profiles/`.

## Улучшить промпт

```bash
uv run pai improve --prompt "Extract emails from this text" --profile claude-sonnet-4-6
```

Команда выводит выбранную стратегию, candidate prompt, integrated score и
explanation.

CLI `pai` — поддерживаемый терминальный интерфейс; он использует тот же пайплайн,
что и HTTP- и gRPC-серверы.

## Запуск gRPC

```bash
uv run pai serve-grpc
```

Запускает gRPC-сервер `AutoImproveService` (порт 50051) с тем же рантаймом, что и
HTTP-приложение. HTTP-приложение по умолчанию уже поднимает gRPC внутри процесса,
поэтому это нужно для gRPC-only или многопроцессных развертываний. Отключить
встроенный сервер можно через `PAI_API__GRPC_ENABLED=false`.

## Частые флаги

| Флаг | По умолчанию | Примечания |
| --- | --- | --- |
| `--profile` | `qwen3-7b` | Любой профиль из `registry/profiles/*.yaml`. |
| `--locale` | unset | Принудительное определение языка, например `en` или `ru`. |
| `--sensitive` | `false` | Ограничивает маршрутизацию только локальными профилями. |

## Выполнение моделью

CLI работает в режиме improvement-only, пока adapter не подключен в
`AutoImproveOrchestrator.adapters`. Настройте Anthropic, OpenAI-compatible,
GGUF или HF adapters, если нужно выполнить выбранного кандидата реальной
моделью во время probation probe.
