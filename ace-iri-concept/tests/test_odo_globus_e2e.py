import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("odo_globus_e2e", BASE / "odo_globus_e2e.py")
o = importlib.util.module_from_spec(spec)
spec.loader.exec_module(o)


class OdoGlobusE2ETests(unittest.TestCase):
    def test_prepare_creates_unique_record(self):
        config = o.load_config(BASE / "configs/odo-globus-e2e.json")
        with tempfile.TemporaryDirectory() as tmp, patch.object(o, "ROOT", Path(tmp)):
            path = o.prepare(config, "e2e-001")
            record = o.read_record(path)
            self.assertEqual(record["remote_output"], "/gpfs/wolf2/olcf/stf053/proj-shared/e2e-001")
            self.assertTrue(record["local_output"].endswith("fixtures/globus-dataset-001/retrieved/e2e-001"))
            with self.assertRaises(FileExistsError):
                o.prepare(config, "e2e-001")

    def test_validate_checks_manifest_against_local_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_dir = root / "input"
            output_dir = root / "output"
            input_dir.mkdir()
            output_dir.mkdir()
            (input_dir / "observations.tsv").write_text("value\n1.250\n2.750\n")
            (output_dir / "result.txt").write_text("4.000\n")
            (output_dir / "result.json").write_text('{"analysis":"fixture-sum","result":4.0}\n')
            lines = []
            for path in (input_dir / "observations.tsv", output_dir / "result.txt", output_dir / "result.json"):
                lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  /remote/{path.name}")
            (output_dir / "SHA256SUMS").write_text("\n".join(lines) + "\n")
            o.validate({"local_input": str(input_dir), "local_output": str(output_dir)})
