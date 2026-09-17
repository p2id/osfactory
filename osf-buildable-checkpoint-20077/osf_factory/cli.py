from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import ProjectValidator, build_index
from .pipeline import FixtureProvider, ProductionController, UniquenessGate
from .buildable_provider import BuildableCatalogProvider

ROOT = Path(__file__).resolve().parent.parent


def cmd_pilot(args: argparse.Namespace) -> None:
    fixture = Path(args.fixture)
    provider = FixtureProvider(fixture)
    controller = ProductionController(provider, Path(args.output), ROOT / "project.schema.json")
    report = controller.run(args.count, max_attempts=args.max_attempts)
    print(json.dumps(report.to_dict(), indent=2))


def cmd_validate(args: argparse.Namespace) -> None:
    validator = ProjectValidator(ROOT / "project.schema.json")
    total = 0
    failures = 0
    with Path(args.input).open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            total += 1
            errors = validator.validate(json.loads(line))
            if errors:
                failures += 1
                print(f"record {total}: " + "; ".join(errors))
    print(json.dumps({"records": total, "invalid": failures}, indent=2))
    raise SystemExit(1 if failures else 0)


def cmd_index(args: argparse.Namespace) -> None:
    build_index(Path(args.input), Path(args.output))
    print(json.dumps({"input": args.input, "output": args.output, "status": "indexed"}, indent=2))


def cmd_buildable_pilot(args: argparse.Namespace) -> None:
    provider = BuildableCatalogProvider(Path(args.fixture))
    controller = ProductionController(provider, Path(args.output), ROOT / "project.schema.json", uniqueness_gate=UniquenessGate(args.similarity_threshold))
    report = controller.run(args.count, max_attempts=args.max_attempts)
    print(json.dumps(report.to_dict(), indent=2))


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="osf", description="Open Software Factory production utilities")
    sub = root.add_subparsers(dest="command", required=True)

    pilot = sub.add_parser("pilot", help="Generate a deterministic calibration dataset")
    pilot.add_argument("--count", type=int, required=True)
    pilot.add_argument("--output", required=True)
    pilot.add_argument("--fixture", default=str(ROOT / "representative_project.json"))
    pilot.add_argument("--max-attempts", type=int, default=None)
    pilot.set_defaults(func=cmd_pilot)

    validate = sub.add_parser("validate", help="Validate JSONL records against the locked schema")
    validate.add_argument("--input", required=True)
    validate.set_defaults(func=cmd_validate)

    index = sub.add_parser("index", help="Build a local SQLite index from canonical JSONL")
    index.add_argument("--input", required=True)
    index.add_argument("--output", required=True)
    index.set_defaults(func=cmd_index)

    buildable = sub.add_parser("buildable-pilot", help="Generate a distinct technical-buildability pilot")
    buildable.add_argument("--count", type=int, required=True)
    buildable.add_argument("--output", required=True)
    buildable.add_argument("--fixture", default=str(ROOT / "representative_project.json"))
    buildable.add_argument("--max-attempts", type=int, default=None)
    buildable.add_argument("--similarity-threshold", type=float, default=0.95)
    buildable.set_defaults(func=cmd_buildable_pilot)
    return root


def main() -> None:
    args = parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
