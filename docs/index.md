# prompt-autoimprove

<section class="pai-hero" markdown>
<p class="pai-kicker">Prompt optimization pipeline</p>
<p class="pai-pron"><strong>prompt-autoimprove</strong> → <em>pai</em>, <code>/paɪ/</code> (like &ldquo;pie&rdquo;)</p>

`prompt-autoimprove` improves raw prompts before they reach a target model. It
normalizes input, selects candidate strategies, scores the results, routes the
winner, optionally runs a model probation probe, and explains the decision.

<p class="pai-lede">
The project is designed for local experiments, API-backed services, and
repeatable evaluation workflows where every prompt revision should be traceable.
</p>
</section>

## Pipeline

<div class="pai-pipeline" markdown>
<div class="pai-step" markdown>Normalize text, locale, task type, missing parameters, PII, and safety flags.</div>
<div class="pai-step" markdown>Generate candidates with task-aware strategies.</div>
<div class="pai-step" markdown>Validate structure, length, contradictions, and safety constraints.</div>
<div class="pai-step" markdown>Score candidates with the integrated quality formula.</div>
<div class="pai-step" markdown>Route the winner to a local or API-backed profile.</div>
<div class="pai-step" markdown>Explain the winning revision and persist the run.</div>
</div>

## Start here

<div class="pai-links" markdown>

[Architecture](architecture.md){ .md-button }
[CLI](cli.md){ .md-button }
[Scoring](scoring.md){ .md-button }
[Local models](local-models.md){ .md-button }

</div>

## Capabilities

<div class="pai-grid" markdown>
<div class="pai-card" markdown>

### CLI

Run `pai improve` for local prompt improvement and inspect the selected
strategy, score, and explanation.

</div>

<div class="pai-card" markdown>

### API

Use the FastAPI HTTP backend, SSE pipeline stream at `/v1/improve/stream`, or gRPC `AutoImproveService`.

</div>

<div class="pai-card" markdown>

### Frontend

Operate the pipeline from a Reflex web client with profile selection, live stage updates, scoring details, and history.

</div>

<div class="pai-card" markdown>

### Scoring

Compare revisions with the weighted sum $S = \sum_i w_i\,q_i$. See
[Scoring](scoring.md) for the full formula and weights.

</div>

<div class="pai-card" markdown>

### Local models

Route to Ollama, LM Studio, local GGUF, Hugging Face safetensors, or OpenAI-compatible endpoints.

</div>
</div>

## Quickstart

```bash
uv sync --all-groups
uv run pai improve --prompt "Summarize this PR" --profile qwen3-7b
```

## Develop the docs

```bash
uv run mkdocs serve   # live preview at http://127.0.0.1:8000
uv run mkdocs build   # static site in ./site
```
