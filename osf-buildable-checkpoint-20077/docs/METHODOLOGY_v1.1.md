# Open Software Factory Methodology v1.1

## Decision

OSF produces software project hypotheses that are sufficiently specified to begin implementation. **Market research, demand proof, market testing, and commercial validation are not prerequisites for accepting a project into the theoretical/buildable dataset.** Every project is a hypothesis until community implementation and later feedback establish otherwise.

The Factory’s pre-build responsibility is technical and product definition. Market learning is a post-build feedback loop.

## Lifecycle

Projects use the following ordered lifecycle:

```text
THEORETICAL
  ↓
BUILDABLE
  ↓
MVP_READY
  ↓
BUILT
  ↓
DEPLOYED
  ↓
MARKET_TESTED
  ↓
MARKET_VALIDATED
  ↓
GROWING
```

The Factory normally produces records through `MVP_READY`. Later statuses are reported only when an implementation or deployment provides evidence. A project may remain `THEORETICAL` when its concept is coherent but its implementation details are incomplete. It may become `BUILDABLE` when technical feasibility and boundaries are sufficiently understood. It becomes `MVP_READY` when a community team can begin the MVP from the specification.

## Acceptance gates before production

A project is accepted into the OSF dataset when it has a clear problem, user, context, solution, MVP scope, out-of-scope boundary, use cases, functional requirements, non-functional requirements, constraints, coherent architecture, justified technology choices, applicable interfaces, data model, security considerations, testing strategy, deployment approach, tasks, dependencies, risks, and explicit unknowns.

The project must be internally consistent and technically plausible. It must not be impossible to test, deploy, or implement under its stated constraints. It must pass exact and semantic distinctness checks. The project must distinguish facts, assumptions, hypotheses, and unknowns.

Evidence is welcome when available, but evidence about demand is informational metadata rather than an acceptance gate. A project with `demand: not_started` or `demand: unknown` may still be `MVP_READY`.

## Post-build feedback loop

After a community implementation exists, the project can record feedback events for `BUILT`, `DEPLOYED`, `MARKET_TESTED`, `MARKET_VALIDATED`, and `GROWING`. These events must be sourced from observed implementation or deployment activity. They do not rewrite the original theoretical specification; they create versioned feedback and amendment records.

## Consequences for generation

Generation prompts must begin with problem, users, context, constraints, and opportunity. They must not ask the generator to prove demand or claim market success. A generator may identify an existing alternative or a possible user signal, but it must label the information accurately. The quality system optimizes for distinctness, usefulness, coherence, and buildability rather than demand certainty.

## Consequences for quality metrics

The primary pre-build metrics are schema validity, completeness, technical consistency, architecture fit, interface applicability, testability, deployability, task readiness, uncertainty clarity, and semantic uniqueness. Market metrics are tracked separately as post-build feedback coverage and are not used to reject theoretical projects merely because they are unknown.
