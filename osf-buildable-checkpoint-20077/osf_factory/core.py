from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Protocol

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "project.schema.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def slugify(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value or "project"


def normalize_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def project_fingerprint(project: dict[str, Any]) -> str:
    identity = project.get("identity", {})
    problem = project.get("problem", {})
    solution = project.get("solution", {})
    fields = [
        normalize_text(identity.get("title", "")),
        normalize_text(problem.get("statement", "")),
        normalize_text(solution.get("summary", "")),
        identity.get("type", ""),
    ]
    return hashlib.sha256("|".join(fields).encode()).hexdigest()


class ProjectProvider(Protocol):
    def generate(self, project_id: str, ordinal: int) -> dict[str, Any]: ...


@dataclass
class RecordResult:
    project_id: str
    status: str
    errors: list[str]
    fingerprint: str | None = None


@dataclass
class BatchReport:
    requested: int
    accepted: int = 0
    rejected: int = 0
    duplicates: int = 0
    errors: int = 0
    started_at: str = ""
    finished_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ProjectValidator:
    def __init__(self, schema_path: Path = SCHEMA_PATH) -> None:
        schema = json.loads(schema_path.read_text())
        Draft202012Validator.check_schema(schema)
        self.validator = Draft202012Validator(schema, format_checker=FormatChecker())

    def validate(self, project: dict[str, Any]) -> list[str]:
        return [
            f"{'.'.join(map(str, error.path)) or '<root>'}: {error.message}"
            for error in sorted(self.validator.iter_errors(project), key=lambda e: list(e.path))
        ]


class ExactDeduplicator:
    def __init__(self) -> None:
        self.seen_ids: set[str] = set()
        self.seen_fingerprints: set[str] = set()

    def check(self, project: dict[str, Any]) -> tuple[bool, str]:
        project_id = project.get("id", "")
        fingerprint = project_fingerprint(project)
        if project_id in self.seen_ids:
            return False, "duplicate_id"
        if fingerprint in self.seen_fingerprints:
            return False, "normalized_duplicate"
        self.seen_ids.add(project_id)
        self.seen_fingerprints.add(fingerprint)
        return True, fingerprint


class JsonlWriter:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = path.open("a", encoding="utf-8")

    def write(self, project: dict[str, Any]) -> None:
        self.handle.write(canonical_json(project) + "\n")
        self.handle.flush()

    def close(self) -> None:
        self.handle.close()


def load_existing_state(path: Path) -> tuple[set[str], set[str]]:
    ids: set[str] = set()
    fingerprints: set[str] = set()
    if not path.exists():
        return ids, fingerprints
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        project = json.loads(line)
        ids.add(project["id"])
        fingerprints.add(project_fingerprint(project))
    return ids, fingerprints


def write_checkpoint(path: Path, *, target: int, accepted: int, next_ordinal: int, report: BatchReport) -> None:
    payload = {"target": target, "accepted": accepted, "next_ordinal": next_ordinal, "updated_at": utc_now(), "report": report.to_dict()}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def build_manifest(directory: Path, files: Iterable[Path], metadata: dict[str, Any]) -> None:
    entries = []
    for path in sorted(files):
        if path.exists():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            entries.append({"path": str(path.relative_to(directory)), "sha256": digest, "bytes": path.stat().st_size})
    manifest = {"created_at": utc_now(), "metadata": metadata, "files": entries}
    (directory / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def build_index(input_path: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(output_path)
    connection.executescript("""
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            slug TEXT NOT NULL,
            type TEXT NOT NULL,
            category TEXT NOT NULL,
            complexity TEXT,
            novelty TEXT,
            status TEXT NOT NULL,
            fingerprint TEXT NOT NULL,
            record_json TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_projects_type ON projects(type);
        CREATE INDEX IF NOT EXISTS idx_projects_category ON projects(category);
        CREATE INDEX IF NOT EXISTS idx_projects_fingerprint ON projects(fingerprint);
    """)
    with input_path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            project = json.loads(line)
            identity = project["identity"]
            connection.execute(
                """INSERT OR REPLACE INTO projects
                (id, title, slug, type, category, complexity, novelty, status, fingerprint, record_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (project["id"], identity["title"], identity["slug"], identity["type"], identity["category"], identity.get("complexity"), identity.get("novelty"), project["maturity"]["status"], project_fingerprint(project), canonical_json(project)),
            )
    connection.commit()
    connection.close()
