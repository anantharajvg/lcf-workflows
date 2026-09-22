import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("s3m_defiant", BASE / "s3m_defiant.py")
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)

class S3MDefiantTests(unittest.TestCase):
    def test_request_is_a_small_cpu_job(self):
        body = s.request(s.load_config(), "trial-01")
        self.assertEqual(body["job"]["account"], "stf053")
        self.assertEqual(body["job"]["partition"], "batch-cpu")
        self.assertEqual(body["job"]["nodes"], "1")
        self.assertEqual(body["job"]["tasks"], 1)
        self.assertIn("srun --ntasks=1 /bin/hostname", body["job"]["script"])

    def test_odo_configuration_uses_documented_project_storage(self):
        cfg = s.load_config("odo-s3m.json")
        body = s.request(cfg, "trial-01")
        self.assertEqual(body["job"]["partition"], "batch")
        self.assertEqual(body["job"]["current_working_directory"], "/gpfs/wolf2/olcf/stf053/proj-shared")
        self.assertTrue(body["job"]["name"].startswith("ace-iri-odo-"))

    def test_invalid_run_id_is_rejected(self):
        with self.assertRaises(ValueError):
            s.request(s.load_config(), "bad/path")

    def test_prepare_allows_an_empty_existing_run_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "configs").mkdir()
            shutil.copy2(BASE / "configs/defiant-s3m.json", root / "configs/defiant-s3m.json")
            (root / "runs/s3m-trial").mkdir(parents=True)
            header = root / "header"
            header.write_text("Authorization: enough-token-characters-here\n")
            header.chmod(0o600)
            with patch.object(s, "ROOT", root), patch("sys.argv", [
                "s3m_defiant.py", "prepare", "--header-file", str(header), "--run-id", "trial",
            ]):
                s.main()
            self.assertTrue((root / "runs/s3m-trial/request.json").is_file())

    def test_submit_command_uses_post_and_request_file(self):
        cmd = s.curl(s.load_config(), Path("/tmp/header"), "/job/submit", "POST", Path("/tmp/request.json"))
        self.assertIn("POST", cmd)
        self.assertIn("@/tmp/request.json", cmd)
        self.assertTrue(cmd[-1].endswith("/job/submit"))

    def test_status_url_uses_a_single_numeric_job_id(self):
        cmd = s.curl(s.load_config(), Path("/tmp/header"), "/job/14069")
        self.assertTrue(cmd[-1].endswith("/job/14069"))

    def test_header_permissions_are_checked(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("Authorization: enough-token-characters-here\n")
            p = Path(f.name)
        try:
            p.chmod(0o600)
            self.assertEqual(s.header_file(p), p.resolve())
            p.chmod(0o644)
            with self.assertRaises(ValueError):
                s.header_file(p)
        finally:
            p.unlink(missing_ok=True)

    def test_submit_refuses_a_second_attempt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "configs").mkdir()
            shutil.copy2(BASE / "configs/defiant-s3m.json", root / "configs/defiant-s3m.json")
            run = root / "runs/s3m-trial"
            run.mkdir(parents=True)
            (run / "request.json").write_text("{}")
            header = root / "header"
            header.write_text("Authorization: enough-token-characters-here\n")
            header.chmod(0o600)
            with patch.object(s, "ROOT", root), patch.object(s, "subprocess") as process:
                process.run.return_value.stdout = "{\"job_id\": 123}\n"
                process.run.return_value.stderr = ""
                process.run.return_value.returncode = 0
                with patch("sys.argv", ["s3m_defiant.py", "submit", "--header-file", str(header), "--run-id", "trial", "--execute"]):
                    s.main()
                with patch("sys.argv", ["s3m_defiant.py", "submit", "--header-file", str(header), "--run-id", "trial", "--execute"]):
                    with self.assertRaises(FileExistsError):
                        s.main()
            self.assertTrue((run / "submission-attempted").exists())
