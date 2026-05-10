# Architecture

`prompt-autoimprove` is organized as a set of cooperating modules that may be
deployed in-process or split into independent services. The end-to-end pipeline
is the same in both deployments.

## Pipeline

```mermaid
flowchart LR
    user([Raw prompt]) --> normalizer[Normalizer]
    normalizer --> selector[Strategy selector]
    selector --> generator[Candidate generator]
    generator --> validator[Validator]
    validator --> evaluator[Evaluator]
    evaluator --> router[Router]
    router --> adapter[Model adapter]
    adapter --> probation[Probation run]
    probation --> explainer[Explainer]
    explainer --> result([Final decision])

    classDef io fill:#1e293b,stroke:#6366f1,color:#fff
    classDef core fill:#312e81,stroke:#6366f1,color:#fff
    class user,result io
    class normalizer,selector,generator,validator,evaluator,router,adapter,probation,explainer core
```

## Component graph

```mermaid
flowchart TB
    subgraph clients[Clients]
        cli[pai CLI]
        web[Reflex web UI]
        grpc_cli[gRPC client]
    end

    subgraph api[API layer]
        http[FastAPI<br/>HTTP + SSE]
        grpc[gRPC server-streaming<br/>AutoImproveService]
    end

    subgraph core[Core pipeline]
        orchestrator[AutoImproveOrchestrator]
        strategies[6 strategies]
        evaluator[IntegratedScorer]
        router[Router + circuit breaker]
    end

    subgraph adapters[Model adapters]
        anthropic[Anthropic API]
        openai[OpenAI-compatible<br/>Ollama / LM Studio]
        gguf[Local GGUF<br/>llama-cpp]
        hf[Safetensors<br/>transformers]
    end

    subgraph infra[Infrastructure]
        pg[(Postgres<br/>SQLAlchemy + Alembic)]
        kafka[(Redpanda<br/>pai.events)]
    end

    cli & web & grpc_cli --> api
    http --> orchestrator
    grpc --> orchestrator
    orchestrator --> strategies --> evaluator --> router --> adapters
    orchestrator --> pg
    orchestrator --> kafka

    classDef io fill:#1e293b,stroke:#6366f1,color:#fff
    classDef core fill:#312e81,stroke:#6366f1,color:#fff
    classDef infra fill:#1f2937,stroke:#10b981,color:#fff
    class cli,web,grpc_cli,http,grpc io
    class orchestrator,strategies,evaluator,router,anthropic,openai,gguf,hf core
    class pg,kafka infra
```

## Components

| Module          | Responsibility                                                                |
| --------------- | ----------------------------------------------------------------------------- |
| `core/normalizer`      | Detects language, classifies task type, finds missing parameters, redacts PII. |
| `core/strategies/*`    | Six strategies that produce improved candidates from a normalized prompt. |
| `core/strategy_selector` | Picks a subset of strategies given $(\text{TaskType}, \text{ModelProfile})$. |
| `core/validator`       | Static checks: length, contradictions, format, safety.                 |
| `core/evaluator`       | Integrated score formula; produces `Score` and per-metric breakdown.  |
| `core/explainer`       | Human-readable reasoning for the winning candidate.                    |
| `adapters/*`           | `ModelAdapter` implementations: GGUF (llama-cpp), HF safetensors, OpenAI-compatible HTTP, Anthropic. |
| `adapters/circuit_breaker` | Trips after $k$ consecutive failures, half-opens after a reset window. |
| `registry`             | Loads YAML `ModelProfile`s.                                             |
| `routing`              | Picks a deployment target based on availability, security, cost budget. |
| `services/orchestrator`| Wires the pipeline; emits Kafka events on each stage transition.        |
| `api/http`             | FastAPI public backend with API-key auth, rate limiting, SSE stream. |
| `api/grpc`             | `AutoImproveService` server-streaming gRPC service.                     |
| `persistence`          | SQLAlchemy 2 async ORM + Alembic migrations.                            |

## Data model

```mermaid
erDiagram
    Session ||--o{ Prompt : owns
    Prompt ||--o{ PromptRevision : refines
    PromptRevision ||--o{ EvaluationRun : evaluates
    PromptRevision ||--o{ RoutingDecision : routes
    EvaluationRun ||--o{ EvaluationMetric : breaks_down
    ModelProfile ||--o{ RoutingDecision : targets

    Session {
        uuid id
        string user_ref
        datetime created_at
    }
    Prompt {
        uuid id
        uuid session_id
        text text
        string modality
        string locale_hint
    }
    PromptRevision {
        uuid id
        uuid prompt_id
        text text
        string strategy
        int estimated_tokens
    }
    EvaluationRun {
        uuid id
        uuid revision_id
        float integrated_score
        text explanation
    }
    EvaluationMetric {
        uuid id
        uuid run_id
        string name
        float value
        float weight
    }
    RoutingDecision {
        uuid id
        uuid revision_id
        string profile_name
        string adapter_name
    }
    ModelProfile {
        string name
        string family
        string format
        int context_window
    }
```

## Deployment topologies

1. **All-in-one** — single Python process; great for local experiments and CI.
2. **Split** — public backend, orchestrator, and adapters run as separate
   containers, communicating over gRPC; events on Kafka; state in PostgreSQL.

## Source layout

See the top-level README for the directory tree. Domain types live in
`prompt_autoimprove.domain` and are pure dataclasses with no I/O. All
side-effecting code lives behind the protocols in `adapters/` and `persistence/`.
