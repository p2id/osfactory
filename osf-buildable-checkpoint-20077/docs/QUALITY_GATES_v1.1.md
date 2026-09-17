# OSF Quality Gates v1.1

## Pre-build acceptance

A candidate may enter the accepted theoretical/buildable dataset when all applicable gates pass:

1. **Identity:** stable ID, valid type, taxonomy references, and lifecycle status.
2. **Problem:** specific problem, context, affected users, and current workarounds or explicit absence of known workarounds.
3. **Solution:** coherent solution and core value.
4. **Scope:** concrete MVP and explicit out-of-scope boundaries.
5. **Use cases:** at least one meaningful actor/scenario/result path.
6. **Requirements:** functional and non-functional requirements with acceptance criteria.
7. **Constraints:** technical, operational, legal, and economic constraints are explicit where relevant.
8. **Architecture:** suitable style, components, data flow, scaling assumptions, and rationale.
9. **Technology:** choices support the requirements and deployment model; unsupported assumptions are flagged.
10. **Data and interfaces:** applicable logical data and interfaces are specified. UX is conditional.
11. **Security:** authentication, authorization, threats, mitigations, privacy, and secrets are addressed where relevant.
12. **Testing:** the project has a strategy capable of detecting requirement failures.
13. **Deployment:** development, production, packaging, configuration, migration, monitoring, backup, and recovery are addressed where relevant.
14. **Tasks:** implementation tasks have dependencies and acceptance criteria.
15. **Consistency:** no unresolved contradiction exists across requirements, architecture, technology, data, interfaces, security, and deployment.
16. **Distinctness:** exact, normalized, semantic, and functional-overlap checks pass or the candidate is classified as a meaningful variant.
17. **Uncertainty:** assumptions, hypotheses, unknowns, and experiments are separated from facts.

Market demand is deliberately absent from this list. `demand: not_started` and `demand: unknown` are valid states for a theoretical project.

## Post-build feedback

The following are lifecycle observations, not pre-build rejection gates:

- `built`: an implementation exists and meets the project’s declared build criteria.
- `deployed`: an implementation is available in a real target environment.
- `market_tested`: a defined user or usage test has been run and recorded.
- `market_validated`: evidence supports the project’s demand hypothesis under a declared method.
- `growing`: sustained usage or other declared growth evidence is recorded.

Feedback events must include status, observation date, evidence IDs when available, and notes. They may trigger a versioned project amendment, but they do not retroactively turn a hypothesis into a pre-build fact.

## Release metrics

Pre-build release reports must include schema validity, completeness, technical consistency, architecture and technology validity, testability, deployability, semantic duplicate rate, functional overlap rate, and lifecycle distribution. Post-build feedback metrics are reported separately and may be empty for a newly generated dataset.
