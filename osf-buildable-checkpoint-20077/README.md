# Open Software Factory — Buildable Project Dataset

This release contains a checkpointed set of **20,077 software project hypotheses** generated under OSF Schema v1.1. The records are technical specifications at the `mvp_ready` lifecycle stage. They are not claims of market demand, commercial success, or market validation.

## Contents

- `projects.jsonl`: canonical streaming project records.
- `project.schema.json`: Draft 2020-12 project schema.
- `indexes/projects.sqlite`: rebuildable local search index.
- `docs/`: methodology, prompts, quality gates, and release guidance.
- `reports/public_release_audit.json`: privacy and integrity audit.
- `reports/checkpoint_status.json`: exact stopped-run state.

## Quality and privacy

The release contains 20,077 valid JSONL records and 20,077 unique IDs. The public-release audit found no email addresses, phone numbers, or prohibited AI references. The records contain project-level concepts and technical specifications, not personal profiles or private contact information.

The generation gate rejects exact and high-confidence near-duplicates using normalized problem, solution, feature, architecture, and software-type fields. The dataset is checkpointed and can be extended later to 100,000 and 1,000,000 records using the same controller.

## Lifecycle and feedback

Records are `mvp_ready` theoretical hypotheses. Market feedback is intentionally not required before acceptance. Later implementation, deployment, market testing, validation, and growth observations belong in the feedback loop.

## Reproducibility

Run the schema validator and tests before modifying the dataset. Rebuild the SQLite index from `projects.jsonl`; the index is derived and is not the canonical source.

## License

The dataset and accompanying implementation are released under the MIT License. Third-party references, if added later, remain subject to their own licenses.
