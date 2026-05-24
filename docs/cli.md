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

The `pai` CLI is the supported terminal interface and shares the pipeline with
the HTTP and gRPC servers.

## Serve gRPC

```bash
uv run pai serve-grpc
```

Runs the `AutoImproveService` gRPC server (port 50051) using the same runtime as
the HTTP app. The HTTP app already starts gRPC in-process by default, so this is
for gRPC-only or multi-worker deployments. Disable the embedded server with
`PAI_API__GRPC_ENABLED=false`.

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
