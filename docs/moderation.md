# Moderation

An optional spam/abuse signal scores incoming prompts and feeds the result into
the safety metric. It is backed by [`benzlokzik/spam-detector`][spam-detector]
(the BERT/`transformers` variant, fine-tuned from `cointegrated/rubert-tiny2`)
and is **off by default**. When disabled — or when the dependency or model is
unavailable — the pipeline produces byte-identical output to a build without it.

## Scope

- **Russian only.** The signal runs solely when the normalized prompt is
  detected as Russian (`detect_language(...) == "ru"`); English and other
  prompts are never scored.
- **Optional dependency.** The model and its `torch`/`transformers` stack live
  in the `moderation` dependency group; a default install does not pull them.
- **Graceful degradation.** Any import, load, or inference failure degrades to
  a neutral result: no flag, no penalty.

## Enabling it

Install the group and turn the signal on:

```bash
uv sync --group moderation
PAI_MODERATION_ENABLED=1 \
  uv run uvicorn prompt_autoimprove.api.http.app:app --port 8000
```

### Configuration

All settings use the `PAI_MODERATION_` prefix.

| Variable | Default | Meaning |
| --- | --- | --- |
| `PAI_MODERATION_ENABLED` | `false` | Build and attach the spam scorer. |
| `PAI_MODERATION_HF_MODEL` | `cointegrated/rubert-tiny2` | Hugging Face repo id (or local path) of the fine-tuned classifier. |
| `PAI_MODERATION_THRESHOLD` | `0.8` | P(spam) at or above which a prompt is rejected, when blocking is on. |
| `PAI_MODERATION_WEIGHT` | `0.5` | Bounded factor by which a spam score lowers the safety metric. |
| `PAI_MODERATION_BLOCK` | `false` | Reject prompts at/above the threshold instead of only penalizing them. |

## How the score is used

When enabled, the normalizer appends a `spam:<score>` entry to the prompt's
safety flags, where `<score>` is `P(spam)` in $[0, 1]$. That flag then:

- **lowers the safety metric** $q_s$ by a bounded factor —
  $q_s \leftarrow q_s \cdot (1 - w_m \cdot p)$, with moderation weight
  $w_m =$ `PAI_MODERATION_WEIGHT` and $p$ the spam score; and
- **optionally rejects the request** before any model call when
  `PAI_MODERATION_BLOCK=1` and $p \ge$ `PAI_MODERATION_THRESHOLD`, surfaced as
  HTTP `422`.

## Where it shows up

- **HTTP:** `POST /v1/improve` returns the prompt's `safety_flags`, including any
  `spam:<score>` entry.
- **gRPC:** `Normalization.safety_flags` already carries the flags in the
  streamed `normalized` message.
- **Frontend:** the candidate view shows a "Possible spam" badge with the
  percentage when the signal fires.

## Building a moderation image

The model weights download from the Hugging Face Hub at build time so the image
ships self-contained:

```bash
docker build \
  --build-arg INCLUDE_MODERATION=1 \
  --build-arg PAI_MODERATION_HF_MODEL=<your-hf-model> \
  -t prompt-autoimprove:moderation .
```

The base image is glibc Debian (`python:3.13-slim`) because `torch` ships no
musllinux wheels; a default build stays slim with no `torch`.

[spam-detector]: https://github.com/benzlokzik/spam-detector
