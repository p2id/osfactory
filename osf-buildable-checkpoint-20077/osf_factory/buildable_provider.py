from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from .core import utc_now


CATALOG = [
    ("Civic Permit Timeline", "A public-facing timeline that explains the status and required next steps of a permit application.", "municipal applicants", "government", ["permit applicants", "case workers"], "web_application", "Track submitted permits, deadlines, decisions, and missing documents without exposing private case data.", ["application lookup", "deadline timeline", "document checklist"]),
    ("Laboratory Sample Chain", "Small laboratories need a traceable chain of custody for samples moving between collection, processing, and storage.", "laboratory technicians", "science_research", ["technicians", "lab supervisors"], "web_application", "Record sample handoffs, storage locations, processing events, and exceptions with an auditable history.", ["sample registration", "handoff scan", "exception log"]),
    ("Accessible Document Preflight", "Document authors need an offline checker that identifies common accessibility defects before publication.", "document authors", "accessibility", ["authors", "accessibility reviewers"], "desktop_application", "Inspect document structure, flag deterministic defects, and produce a remediation checklist without claiming automatic conformance.", ["document import", "rule checks", "remediation report"]),
    ("Farm Irrigation Notebook", "Small farms need a local record of irrigation events when connectivity is unreliable in the field.", "small-farm operators", "agriculture_environment", ["farm operators", "field workers"], "mobile_application", "Capture plots, irrigation events, water volumes, and offline notes with later export.", ["plot register", "offline event capture", "CSV export"]),
    ("Dependency Change Ledger", "Maintainers need to understand which software components changed between two releases and what review is required.", "software maintainers", "developer_tools", ["maintainers", "security reviewers"], "web_application", "Compare dependency manifests, classify changes, and produce a reviewable release ledger.", ["manifest import", "dependency diff", "review export"]),
    ("Community Archive Map", "Local archives need a searchable map of collections and access restrictions without forcing all metadata into one vendor system.", "community archivists", "media_creator", ["archivists", "research visitors"], "web_application", "Catalog collection locations, descriptive metadata, access rules, and digitization status.", ["collection catalog", "map search", "access policy"]),
    ("Workshop Equipment Scheduler", "Shared workshops need conflict-aware booking for equipment with safety prerequisites.", "shared workshop members", "engineering_industrial", ["members", "workshop managers"], "web_application", "Book equipment, enforce prerequisite training, and expose maintenance blackout periods.", ["equipment register", "training eligibility", "conflict-aware booking"]),
    ("Research Protocol Notebook", "Research teams need versioned experimental protocols linked to observations and deviations.", "research teams", "science_research", ["researchers", "lab coordinators"], "web_application", "Store protocol versions, record deviations, and link observations without replacing a laboratory information system.", ["protocol versioning", "deviation capture", "observation links"]),
    ("Transit Stop Accessibility Log", "Transit advocates need a structured way to record accessibility barriers at stops and track remediation proposals.", "transit accessibility advocates", "accessibility", ["advocates", "transport planners"], "mobile_application", "Capture geotagged observations, evidence notes, and remediation status with offline support.", ["stop register", "offline observation", "remediation status"]),
    ("Small Business Cashflow Scenario Tool", "Small businesses need a local tool to compare cashflow scenarios without sending financial data to a hosted service.", "small business operators", "business_enterprise", ["operators", "bookkeepers"], "desktop_application", "Model income and expense scenarios, compare assumptions, and export a reviewable plan.", ["ledger import", "scenario model", "plan export"]),
    ("Open Hardware Test Log", "Open hardware teams need reproducible records of bench tests across prototype revisions.", "open hardware teams", "robotics_hardware", ["hardware designers", "test engineers"], "web_application", "Record test procedures, instruments, results, and prototype revisions with attached evidence paths.", ["revision register", "test run", "result comparison"]),
    ("Neighborhood Mutual Aid Roster", "Volunteer groups need a privacy-conscious roster of capabilities and availability without exposing sensitive personal details.", "mutual-aid coordinators", "social", ["coordinators", "volunteers"], "web_application", "Manage opt-in capabilities, shifts, and contact permissions with minimal personal data.", ["capability roster", "shift coordination", "privacy controls"]),
]

VARIANT_USERS = [
    "single operator", "small team", "regional coordinator", "public reviewer", "field technician",
    "volunteer network", "regulated administrator", "research supervisor", "maintenance contractor", "community steward",
]
VARIANT_WORKFLOWS = [
    "capture and review", "approve and hand off", "compare and export", "schedule and reconcile", "inspect and annotate",
    "register and trace", "plan and simulate", "collect and report", "triage and resolve", "version and audit",
]
VARIANT_CONSTRAINTS = [
    "intermittent connectivity", "strict data minimization", "shared-device operation", "offline export requirement", "human approval before publishing",
    "low-resource deployment", "audit history retention", "multiple time zones", "limited training time", "interoperable file exchange",
]
VARIANT_DEPLOYMENTS = [
    "browser", "mobile", "desktop", "self-hosted", "on-premise", "offline-first", "edge", "institutional server", "local network", "hybrid",
]
VARIANT_MODES = [
    "single-record review", "queue-based handoff", "scheduled batch", "exception-driven triage", "evidence attachment",
    "approval workflow", "periodic reconciliation", "version comparison", "geographic assignment", "controlled export",
]


class BuildableCatalogProvider:
    def __init__(self, fixture_path: Path) -> None:
        self.fixture = json.loads(fixture_path.read_text(encoding="utf-8"))

    def generate(self, project_id: str, ordinal: int) -> dict[str, Any]:
        index = (ordinal - 1) % len(CATALOG)
        title, problem, actor, domain, users, software_type, solution, features = CATALOG[index]
        combination = ordinal - 1
        user_variant = VARIANT_USERS[(combination // 1) % len(VARIANT_USERS)]
        workflow_variant = VARIANT_WORKFLOWS[(combination // 10) % len(VARIANT_WORKFLOWS)]
        constraint_variant = VARIANT_CONSTRAINTS[(combination // 100) % len(VARIANT_CONSTRAINTS)]
        deployment_variant = VARIANT_DEPLOYMENTS[(combination // 1000) % len(VARIANT_DEPLOYMENTS)]
        mode_variant = VARIANT_MODES[(combination // 10000) % len(VARIANT_MODES)]
        version = (ordinal - 1) // len(CATALOG) + 1
        project = copy.deepcopy(self.fixture)
        project.update({"schema_version": "1.1.0", "id": project_id})
        identity = project["identity"]
        identity.update({"title": title if version == 1 else f"{title} Variant {version}", "slug": f"{title.lower().replace(' ', '-')}-{version}", "category": domain, "domains": [domain], "type": software_type, "tags": [domain, "buildable"], "complexity": "C2", "novelty": "N2"})
        project["problem"].update({"statement": f"{problem} The target variation is {workflow_variant} through {mode_variant} for a {user_variant} under {constraint_variant}.", "context": f"The workflow is operated by {actor}; this variant is deployed as {deployment_variant} software, uses {mode_variant}, and must support {constraint_variant}.", "affected_users": [actor.lower().replace(" ", "_")], "current_workarounds": ["spreadsheets", "paper records", "general-purpose tools"]})
        project["users"] = {"primary": [user_variant], "secondary": users}
        project["solution"].update({"summary": f"{solution} It is optimized for {workflow_variant} through {mode_variant} by a {user_variant} using {deployment_variant} deployment under {constraint_variant}.", "description": solution + f" The MVP is deliberately narrow, supports {deployment_variant} deployment, uses {mode_variant}, and records uncertainty instead of claiming outcomes.", "core_value": f"A focused {workflow_variant} workflow with explicit {constraint_variant} boundaries."})
        project["use_cases"][0].update({"actor": users[0], "scenario": f"Uses {title} to complete the primary workflow.", "expected_result": "The system records a coherent, reviewable result."})
        project["scope"] = {"mvp": features + [workflow_variant, deployment_variant, mode_variant], "out_of_scope": ["billing", "general-purpose social networking", "automated market claims"]}
        project["features"] = {"mvp": [{"id": f"FEAT-{index+1:03d}-{n}", "name": feature.title(), "description": f"{feature} for {user_variant} under {constraint_variant}, using {mode_variant} in a {deployment_variant} deployment."} for n, feature in enumerate(features, 1)], "post_mvp": []}
        for req_index, feature in enumerate(features[:2], 1):
            project["requirements"]["functional"][min(req_index-1, len(project["requirements"]["functional"])-1)].update({"id": f"REQ-{index+1:03d}{req_index}", "statement": f"The system must support {feature}.", "acceptance_criteria": [f"A user can complete {feature} and review the result."]})
        project["architecture"].update({"data_flow": f"A {user_variant} performs {workflow_variant} through {mode_variant}; the {deployment_variant} system stores structured records subject to {constraint_variant}, and authorized users review outputs.", "rationale": f"A modular local-capable application fits the bounded {title} workflow for {user_variant}, its {mode_variant} operating model, its {deployment_variant} deployment, and its {constraint_variant} constraint."})
        project["technology"]["selection_rationale"] = "A typed application, durable structured storage, and exportable records support the MVP while keeping deployment replaceable."
        project["data"]["entities"] = [{"id": f"ENT-{index+1:03d}", "name": title.replace(" ", ""), "purpose": "Primary workflow record.", "attributes": ["id", "status", "created_at", "updated_at"], "sensitivity": "internal"}]
        project["interfaces"]["kinds"] = ["ui", "file"]
        project["interfaces"]["endpoints"] = []
        project["ux"]["screens"] = [{"id": f"SCREEN-{index+1:03d}", "name": "Primary workflow", "description": f"Complete the {features[0]} workflow."}]
        project["security"]["privacy"] = ["Collect only fields needed for the workflow.", "Provide export and deletion controls where personal data is stored."]
        project["testing"]["e2e"] = [f"Complete the {features[0]} workflow from start to review."]
        project["deployment"]["production"] = "Deploy as a small application appropriate to the selected software type; support export and recovery."
        project["tasks"][0].update({"id": f"TASK-{index+1:03d}", "title": f"Implement {features[0]}", "description": f"Implement the minimum workflow for {features[0]}.", "acceptance_criteria": [f"The primary user can complete {features[0]} with persisted state."]})
        project["risks"][0].update({"description": "The workflow may require domain-specific review before implementation is expanded.", "mitigation": "Keep the MVP narrow and test the stated acceptance criteria."})
        project["validation"].update({"problem": "unknown", "technical": "supported", "demand": "not_started", "assumptions": ["The stated user group experiences the described workflow."], "hypotheses": ["A focused workflow is more reliable than the current general-purpose workaround."], "unknowns": ["Which optional fields are essential in real use?"], "feedback_loop": []})
        project["maturity"] = {"status": "mvp_ready", "readiness_basis": "Theoretical MVP with explicit scope, coherent technical design, and no market-validation prerequisite."}
        project["quality"]["build_readiness"] = "pass"
        project["quality"]["metrics"] = {"provider": "buildable-catalog-v1", "market_gate": False}
        project["provenance"].update({"generator": "buildable-catalog-v1", "updated_at": utc_now(), "references": []})
        project["relationships"]["belongs_to_family"] = [f"family.{domain}"]
        return project
