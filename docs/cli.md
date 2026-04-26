# CLI usage

```bash
uv run pai profiles
```
Lists available model profiles in a table.

```bash
uv run pai improve --prompt "Extract emails from this text" --profile claude-sonnet-4-6
```
Runs the full pipeline and prints the chosen strategy, candidate prompt,
integrated score, and the explanation.

Common flags:

| Flag         | Default     | Notes                                            |
| ------------ | ----------- | ------------------------------------------------ |
| `--profile`  | `qwen3-7b`  | Any profile from `registry/profiles/*.yaml`.     |
| `--locale`   | unset       | Force language detection (`en`, `ru`, …).        |
| `--sensitive`| `false`     | Restrict routing to local profiles only.         |

The CLI runs in improvement-only mode by default — no real model is called.
Wire an adapter (Anthropic, OpenAI-compatible, GGUF, HF) into
`AutoImproveOrchestrator.adapters` to actually execute the candidate.
