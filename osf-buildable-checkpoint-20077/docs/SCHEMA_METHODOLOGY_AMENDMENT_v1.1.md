# Schema Methodology Amendment v1.1

The OSF lifecycle and acceptance semantics are updated without changing the core project identity model.

The former pre-build interpretation of market or demand validation is removed. A project can be accepted as a theoretical, buildable, or MVP-ready specification when its problem, users, solution, scope, requirements, architecture, technology, data, interfaces, security, testing, deployment, tasks, risks, uncertainty, and distinctness are sufficiently defined. Demand may be `not_started` or `unknown`.

The lifecycle enum is now:

```text
THEORETICAL
BUILDABLE
MVP_READY
BUILT
DEPLOYED
MARKET_TESTED
MARKET_VALIDATED
GROWING
```

The `validation.feedback_loop` field stores later observations. Market status is feedback metadata and is not a pre-production acceptance gate.

This amendment is schema version **1.1.0**. Existing 1.0.0 fixture archives remain immutable historical artifacts and are not silently relabeled. New records must use the 1.1.0 contract. A migration may map an old `ready_to_build` label to `mvp_ready` only when the record passes the revised technical and distinctness gates; the migration must not claim market validation.
