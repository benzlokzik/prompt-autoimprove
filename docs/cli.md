# CLI usage

The `pai` command is the fastest way to exercise the improvement pipeline from
a terminal.

## List profiles

```bash
uv run pai profiles
```

This prints the profiles loaded from `src/prompt_autoimprove/registry/profiles/`.

## Improve a prompt

```bash
uv run pai improve --prompt "Extract emails from this text" --profile claude-sonnet-4-6
```

The command prints the selected strategy, candidate prompt, integrated score,
and explanation.

## Common flags

| Flag | Default | Notes |
| --- | --- | --- |
| `--profile` | `qwen3-7b` | Any profile from `registry/profiles/*.yaml`. |
| `--locale` | unset | Forces language detection, for example `en` or `ru`. |
| `--sensitive` | `false` | Restricts routing to local profiles only. |

## Model execution

The CLI runs in improvement-only mode unless an adapter is wired into
`AutoImproveOrchestrator.adapters`. Configure Anthropic, OpenAI-compatible,
GGUF, or HF adapters when you want the selected candidate to be executed by a
real model during the probation probe.
