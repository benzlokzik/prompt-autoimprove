# Strategies

Each strategy implements `Strategy` from `core.strategies.base`. A strategy
receives a `NormalizedPrompt` and target `ModelProfile`, then returns a
`CandidatePrompt` that the validator and scorer can compare with other
candidates.

## Role-based

Prepends an explicit expert role tailored to the detected task. This strategy
is always applicable and is cheap enough for small local models.

## Structured output

Adds an output contract: JSON for extraction or classification, fenced code
blocks for code generation, bullet lists for summaries, and plain text for
translation. This reduces downstream parsing ambiguity.

## Chain decomposition

Uses a restate, plan, execute structure for reasoning-heavy tasks such as
`reasoning`, `code_generate`, and `extract`. It is skipped for profiles with
`reasoning_mode = thinking`, because those models already perform internal
decomposition.

## Few-shot

Adds one or two compact task-specific examples when the remaining context
budget allows it. Examples are selected by task category and kept small to
avoid crowding out the user's request.

## Self-verification

Appends a self-check loop: re-read the request, list missed constraints, and
revise the answer. It is useful when `max_output_tokens >= 256`.

## Multimodal

Runs only when the selected profile has `supports_vision: true` and the prompt
includes attachments. The candidate names each attachment and asks the model to
describe observations before answering.

## Selection

`core.strategy_selector.select` filters strategies through `applies()` and
orders them by static priority. The orchestrator validates each selected
candidate, computes the integrated `S` score, and returns the highest-scoring
revision.
