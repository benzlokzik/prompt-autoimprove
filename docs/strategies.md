# Strategies

Each strategy implements `Strategy` from `core.strategies.base`. They produce a
`CandidatePrompt` from a `NormalizedPrompt` and a target `ModelProfile`.

## Role-based

Prepends an explicit expert role tailored to the detected task. Always
applicable. Cheap and surprisingly effective on small models.

## Structured output

Appends an output contract: JSON for extraction/classification, fenced code
blocks for code generation, bullet lists for summaries, plain text for
translation. Reduces post-processing.

## Chain decomposition

Forces a "restate / plan / execute" pass for reasoning-heavy tasks
(`reasoning`, `code_generate`, `extract`). Skipped for models with native
thinking mode (`reasoning_mode = thinking`) since they decompose internally.

## Few-shot

Adds 1-2 task-specific examples when the remaining context budget allows.
Examples are small and chosen by task category.

## Self-verification

Appends a self-check loop: re-read the request, list missed constraints,
revise. Useful when `max_output_tokens >= 256`.

## Multimodal

Activates only when the profile has `supports_vision: true` and the prompt
carries attachments. Lists each attachment and asks the model to describe
observations before answering.

## Selection

`core.strategy_selector.select` filters strategies by `applies()` and orders
them by static priority. The orchestrator runs all selected strategies in
parallel (logically), validates each candidate, scores them, and picks the
highest integrated `S`.
