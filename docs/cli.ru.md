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
