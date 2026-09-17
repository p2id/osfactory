from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any

from .core import BatchReport, JsonlWriter, ProjectValidator, build_manifest, load_existing_state, project_fingerprint, utc_now, write_checkpoint


class UniquenessGate:
    """Scalable pre-acceptance gate: exact IDs, normalized signatures, and token blocking."""

    def __init__(self, jaccard_threshold: float = 0.82) -> None:
        self.jaccard_threshold = jaccard_threshold
        self.ids: set[str] = set()
        self.signatures: set[str] = set()
        self.blocks: dict[str, list[set[str]]] = {}

    @staticmethod
    def _normalize(value: str) -> str:
        value = re.sub(r"\b\d+\b", "#", value.lower())
        return re.sub(r"[^a-z0-9#]+", " ", value).strip()

    def _fields(self, project: dict[str, Any]) -> tuple[str, str, str, str, str]:
        identity = project.get("identity", {})
        problem = project.get("problem", {})
        solution = project.get("solution", {})
        features = project.get("features", {}).get("mvp", [])
        feature_text = " ".join(sorted(self._normalize(x.get("description", "")) for x in features))
        return (
            self._normalize(problem.get("statement", "")),
            self._normalize(solution.get("summary", "")),
            feature_text,
            self._normalize(project.get("architecture", {}).get("data_flow", "")),
            identity.get("type", ""),
        )

    def _signature(self, fields: tuple[str, ...]) -> str:
        return "|".join(fields)

    def _tokens(self, fields: tuple[str, ...]) -> set[str]:
        return set(" ".join(fields).split())

    def check(self, project: dict[str, Any]) -> tuple[bool, str, float]:
        project_id = project.get("id", "")
        if project_id in self.ids:
            return False, "DUPLICATE", 1.0
        fields = self._fields(project)
        signature = self._signature(fields)
        if signature in self.signatures:
            return False, "DUPLICATE", 1.0
        tokens = self._tokens(fields)
        block_keys = set(list(tokens)[:8]) or {"<empty>"}
        candidates: list[set[str]] = []
        for key in block_keys:
            candidates.extend(self.blocks.get(key, []))
        best = 0.0
        for candidate in candidates:
            union = tokens | candidate
            similarity = len(tokens & candidate) / len(union) if union else 1.0
            best = max(best, similarity)
        if best >= self.jaccard_threshold and len(tokens) > 0:
            return False, "NEAR_DUPLICATE", best
        self.ids.add(project_id)
        self.signatures.add(signature)
        for key in block_keys:
            self.blocks.setdefault(key, []).append(tokens)
        return True, "UNIQUE", best

    def load_existing(self, project: dict[str, Any]) -> None:
        """Load an already accepted record directly; do not compare it to prior records."""
        fields = self._fields(project)
        self.ids.add(project.get("id", ""))
        self.signatures.add(self._signature(fields))
        tokens = self._tokens(fields)
        for key in (set(list(tokens)[:8]) or {"<empty>"}):
            self.blocks.setdefault(key, []).append(tokens)


class FixtureProvider:
    """Deterministic provider retained only for calibration and pipeline tests."""

    def __init__(self, fixture_path: Path) -> None:
        self.fixture = json.loads(fixture_path.read_text(encoding="utf-8"))

    def generate(self, project_id: str, ordinal: int) -> dict[str, Any]:
        project = copy.deepcopy(self.fixture)
        suffix = f" {ordinal:06d}"
        project["id"] = project_id
        project["schema_version"] = "1.1.0"
        project["identity"]["title"] = "Offline Field Notes" + suffix
        project["identity"]["slug"] = f"offline-field-notes-{ordinal:06d}"
        project["problem"]["statement"] += suffix + "."
        project["problem"]["context"] += suffix + "."
        project["solution"]["summary"] += suffix + "."
        project["solution"]["description"] += suffix + "."
        project["provenance"]["generator"] = "fixture-provider"
        project["provenance"]["updated_at"] = utc_now()
        project["maturity"]["status"] = "mvp_ready"
        project["maturity"]["readiness_basis"] = "Structural calibration fixture; market feedback is not a pre-build gate."
        project["validation"]["problem"] = "unknown"
        project["validation"]["technical"] = "supported"
        project["validation"]["demand"] = "not_started"
        project["validation"]["feedback_loop"] = []
        project["quality"]["build_readiness"] = "pass"
        return project


class ProjectProvider:
    def generate(self, project_id: str, ordinal: int) -> dict[str, Any]:
        raise NotImplementedError


class ProductionController:
    def __init__(self, provider: Any, output_dir: Path, schema_path: Path, uniqueness_gate: UniquenessGate | None = None) -> None:
        self.provider = provider
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.projects_path = output_dir / "projects.jsonl"
        self.checkpoint_path = output_dir / "checkpoint.json"
        self.report_path = output_dir / "batch_report.json"
        self.validator = ProjectValidator(schema_path)
        self.uniqueness = uniqueness_gate or UniquenessGate()
        existing_ids, _ = load_existing_state(self.projects_path)
        if self.projects_path.exists():
            for line in self.projects_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    self.uniqueness.load_existing(json.loads(line))
        else:
            self.uniqueness.ids.update(existing_ids)

    def run(self, target: int, max_attempts: int | None = None) -> BatchReport:
        accepted = len(self.uniqueness.ids)
        attempts = 0
        next_ordinal = 1
        if self.checkpoint_path.exists():
            checkpoint = json.loads(self.checkpoint_path.read_text(encoding="utf-8"))
            next_ordinal = int(checkpoint.get("next_ordinal", 1))
            accepted = max(accepted, int(checkpoint.get("accepted", accepted)))
        report = BatchReport(requested=target, accepted=accepted, started_at=utc_now())
        writer = JsonlWriter(self.projects_path)
        try:
            while accepted < target:
                attempts += 1
                if max_attempts is not None and attempts > max_attempts:
                    raise RuntimeError(f"attempt limit reached before target: accepted={accepted}, target={target}")
                project_id = f"OSF-{next_ordinal:08d}"
                project = self.provider.generate(project_id, next_ordinal)
                errors = self.validator.validate(project)
                if errors:
                    report.rejected += 1
                    report.errors += len(errors)
                    next_ordinal += 1
                    continue
                unique, reason, similarity = self.uniqueness.check(project)
                if not unique:
                    report.rejected += 1
                    report.duplicates += 1
                    next_ordinal += 1
                    continue
                project.setdefault("quality", {}).setdefault("metrics", {})["uniqueness_similarity_max"] = similarity
                project["quality"]["metrics"]["uniqueness_class"] = reason
                writer.write(project)
                accepted += 1
                report.accepted = accepted
                next_ordinal += 1
                write_checkpoint(self.checkpoint_path, target=target, accepted=accepted, next_ordinal=next_ordinal, report=report)
                if accepted % 1000 == 0:
                    print(f"progress accepted={accepted} rejected={report.rejected} next_ordinal={next_ordinal}", flush=True)
        finally:
            writer.close()
        report.finished_at = utc_now()
        self.report_path.write_text(json.dumps(report.to_dict(), indent=2) + "\n", encoding="utf-8")
        build_manifest(self.output_dir, [self.projects_path, self.checkpoint_path, self.report_path], {"target": target, "accepted": accepted, "provider": type(self.provider).__name__, "uniqueness_gate": "multi_field_blocked_jaccard"})
        if accepted != target:
            raise RuntimeError(f"accepted count invariant failed: {accepted} != {target}")
        return report
