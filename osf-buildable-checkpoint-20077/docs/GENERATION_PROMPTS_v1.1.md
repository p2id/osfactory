# OSF Generation Prompt Contract v1.1

## System objective

Produce one distinct, technically coherent software project specification. Treat the project as a theoretical hypothesis. Do not claim demand, profitability, adoption, or market validation unless a later feedback event supplies evidence.

## Required reasoning order

```text
Problem
→ User
→ Context
→ Constraint
→ Opportunity
→ Solution
→ MVP
→ Requirements
→ Architecture
→ Technology
→ Data
→ Interfaces
→ Security
→ Testing
→ Deployment
→ Tasks
→ Risks and unknowns
```

## Required output behavior

The output must identify a concrete problem and affected users. It must define the MVP and explicit exclusions. It must specify applicable use cases, functional and non-functional requirements, constraints, architecture and rationale, technology choices and rationale, data, interfaces, security, testing, deployment, roadmap, tasks, dependencies, risks, assumptions, hypotheses, and unknowns.

Select the lifecycle status honestly:

- `theoretical` when the concept is coherent but implementation detail is incomplete.
- `buildable` when technical feasibility and implementation boundaries are sufficiently specified.
- `mvp_ready` when a team can begin implementing the MVP.
- Later statuses require implementation or deployment evidence.

Set `validation.demand` to `not_started` or `unknown` when no post-build market feedback exists. This is acceptable and must not cause rejection. Do not fabricate market evidence.

## Distinctness instruction

Do not create a variant by changing only the title, color, framework, database, or wording. Keep a candidate only when it materially differs in problem, users, context, workflow, constraints, outputs, interaction model, deployment, architecture, or technical requirements.

## Negative instructions

Reject or repair vague concepts, cosmetic variants, contradictory requirements, impossible architectures, unsupported technology assumptions, untestable behavior, undeployable designs, missing users, missing problems, missing scope boundaries, and duplicated workflows. Do not reject a project merely because market demand is unknown.

## Provenance instruction

Record references when external factual claims, standards, protocols, technical constraints, or domain requirements are used. If a fact is not verified, label it as an assumption or unknown. Never invent references or URLs. Provenance records the actual production method accurately; it must not be removed to disguise how a record was produced.
