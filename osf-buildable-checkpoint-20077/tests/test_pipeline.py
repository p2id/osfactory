import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from osf_factory.core import ExactDeduplicator, ProjectValidator
from osf_factory.pipeline import FixtureProvider, ProductionController
from osf_factory.buildable_provider import BuildableCatalogProvider
from osf_factory.pipeline import UniquenessGate

ROOT = Path(__file__).resolve().parents[1]


class PipelineTests(unittest.TestCase):
    def test_schema_fixture_validates(self):
        project = json.loads((ROOT / "representative_project.json").read_text())
        self.assertEqual(ProjectValidator(ROOT / "project.schema.json").validate(project), [])

    def test_duplicate_detection(self):
        project = json.loads((ROOT / "representative_project.json").read_text())
        dedupe = ExactDeduplicator()
        accepted, _ = dedupe.check(project)
        duplicate, reason = dedupe.check(project)
        self.assertTrue(accepted)
        self.assertFalse(duplicate)
        self.assertEqual(reason, "duplicate_id")

    def test_pilot_exact_target_and_resume(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "pilot"
            controller = ProductionController(BuildableCatalogProvider(ROOT / "representative_project.json"), output, ROOT / "project.schema.json")
            report = controller.run(5)
            self.assertEqual(report.accepted, 5)
            self.assertEqual(len((output / "projects.jsonl").read_text().splitlines()), 5)
            resumed = ProductionController(BuildableCatalogProvider(ROOT / "representative_project.json"), output, ROOT / "project.schema.json")
            report2 = resumed.run(7)
            self.assertEqual(report2.accepted, 7)
            self.assertEqual(len((output / "projects.jsonl").read_text().splitlines()), 7)
            self.assertTrue((output / "manifest.json").exists())

    def test_index_is_queryable(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "pilot"
            controller = ProductionController(BuildableCatalogProvider(ROOT / "representative_project.json"), output, ROOT / "project.schema.json")
            controller.run(3)
            index_path = Path(temporary) / "pilot.sqlite"
            from osf_factory.core import build_index
            build_index(output / "projects.jsonl", index_path)
            connection = sqlite3.connect(index_path)
            count = connection.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
            connection.close()
            self.assertEqual(count, 3)

    def test_uniqueness_gate_rejects_near_duplicate(self):
        project = json.loads((ROOT / "representative_project.json").read_text())
        gate = UniquenessGate()
        accepted, reason, _ = gate.check(project)
        self.assertTrue(accepted)
        duplicate = json.loads((ROOT / "representative_project.json").read_text())
        duplicate["id"] = "OSF-00000002"
        accepted2, reason2, similarity = gate.check(duplicate)
        self.assertFalse(accepted2)
        self.assertIn(reason2, {"DUPLICATE", "NEAR_DUPLICATE"})
        self.assertGreaterEqual(similarity, 0.82)

    def test_buildable_catalog_pilot(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "buildable"
            provider = BuildableCatalogProvider(ROOT / "representative_project.json")
            report = ProductionController(provider, output, ROOT / "project.schema.json").run(5, max_attempts=20)
            self.assertEqual(report.accepted, 5)
            records = [json.loads(line) for line in (output / "projects.jsonl").read_text().splitlines()]
            self.assertEqual({record["maturity"]["status"] for record in records}, {"mvp_ready"})
            self.assertEqual({record["validation"]["demand"] for record in records}, {"not_started"})


if __name__ == "__main__":
    unittest.main()
