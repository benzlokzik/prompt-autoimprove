SIMPLE_EXEMPLARS: tuple[str, ...] = (
    "Translate this release note into Spanish: 'Login now supports passkeys.'",
    (
        "Summarize this incident update in one sentence: API latency spiked for 8 "
        "minutes after deploy and recovered after rollback."
    ),
    "Format 2026-05-16T14:35:00Z as a human-readable date for a status page.",
    "What does HTTP 429 mean in one sentence?",
    "Rename variable `tmp` to something clearer in this Python line: tmp = user_ids[:10]",
    "Write a one-line regex that matches a US ZIP code.",
    "Convert 250 MiB to bytes.",
    "List five KPI names for a B2B SaaS dashboard.",
    "Write a SQL snippet under 5 lines to count orders per day.",
    (
        "Rewrite this Slack message to be more concise: 'Can everyone please remember "
        "to update Jira before standup tomorrow?'"
    ),
)

HARD_EXEMPLARS: tuple[str, ...] = (
    (
        "Refactor this Python service to separate validation, persistence, and retry "
        "logic; preserve behavior, identify risks, and outline the tests you would add."
    ),
    (
        "Design a multi-tenant feature flag system for 5M users across regions, "
        "including data model, rollout strategy, failure modes, and observability."
    ),
    (
        "Debug an intermittent 502 error that appears only during peak traffic; propose "
        "a step-by-step investigation plan, likely root causes, and safe mitigations."
    ),
    (
        "Produce a structured postmortem with timeline, impact, contributing factors, "
        "corrective actions, owners, and follow-up metrics for a failed deploy."
    ),
    (
        "Answer these three questions about the funnel drop: what changed, how large is "
        "the effect by segment, and what experiment should we run next?"
    ),
    (
        "Prove whether this cache invalidation strategy is correct, then justify the "
        "tradeoffs, then propose a safer alternative for partial failures."
    ),
    (
        "Given this long architecture context, identify the hidden constraints, extract "
        "assumptions, and recommend a migration path that minimizes downtime."
    ),
    (
        "Perform a security review of this OAuth callback flow, list concrete "
        "vulnerabilities, rank severity, and suggest code-level remediations."
    ),
    (
        "Create a database migration plan from Postgres 13 to 16 with prechecks, "
        "rollout stages, rollback criteria, and monitoring during cutover."
    ),
    (
        "Review this Kubernetes incident dump, correlate events across pods and nodes, "
        "and explain the most likely chain of failure with evidence gaps."
    ),
)
