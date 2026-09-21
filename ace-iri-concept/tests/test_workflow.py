import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('workflow', BASE / 'workflow.py')
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for name in w.PAYLOAD:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(BASE / name, target)
        self.rootpatch = patch.object(w, 'ROOT', self.root)
        self.rootpatch.start()
        with patch.object(w, 'run', return_value='abc123\n'):
            w.prepare('test')
        self.dest = self.root / 'runs/test'
        self.calls = []

    def tearDown(self):
        self.rootpatch.stop()
        self.tmp.cleanup()

    def invoke(self, *args):
        with patch.object(sys, 'argv', ['workflow.py', *args]), contextlib.redirect_stdout(io.StringIO()):
            w.main()

    def fake(self, cmd):
        self.calls.append(cmd)
        if cmd[0] == 'ssh' and 'sbatch' in cmd[-1]:
            return '12345;riker\n'
        if cmd[0] == 'rsync' and 'retrieved' in cmd[-1]:
            target = Path(cmd[-1]) / 'results'
            target.mkdir(parents=True)
            shutil.copy2(self.dest / 'results/result.json', target / 'result.json')
        return ''

    def test_simulated_lifecycle(self):
        with patch.object(w, 'run', side_effect=self.fake):
            self.invoke('stage', 'test', '--execute')
            self.invoke('submit', 'test', '--execute')
            self.invoke('status', 'test', '--execute')
            # Execute the real workload locally; simulate only transport/scheduler.
            subprocess.run(['bash', 'src/smoke.sh'], cwd=self.dest, check=True)
            self.invoke('fetch', 'test', '--execute')
            self.invoke('check', 'test')
        self.assertEqual((self.dest / 'job-id.txt').read_text(), '12345\n')
        self.assertEqual(len(self.calls), 6)
        self.assertIn('--account=stf053', self.calls[2][-1])
        with patch.object(w, 'run') as remote:
            with self.assertRaises(FileExistsError):
                self.invoke('submit', 'test', '--execute')
            remote.assert_not_called()

    def test_prepare_in_empty_git_repo(self):
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        dest = w.prepare('empty-repo')
        manifest = json.loads((dest / 'manifest.json').read_text())
        self.assertIsNone(manifest['git_commit'])
        w.verify(dest)

    def test_preview_never_connects(self):
        (self.dest / 'job-id.txt').write_text('12345\n')
        with patch.object(w, 'run') as remote:
            for action in ('stage', 'submit', 'status', 'fetch'):
                self.invoke(action, 'test')
            remote.assert_not_called()
        self.assertFalse((self.dest / 'submission-attempted').exists())

    def test_changed_payload_rejected(self):
        (self.dest / 'src/smoke.sh').write_text('changed')
        with self.assertRaises(ValueError):
            w.verify(self.dest)

    def test_ambiguous_submission_cannot_retry(self):
        with patch.object(w, 'run', side_effect=subprocess.CalledProcessError(255, 'ssh')):
            with self.assertRaises(subprocess.CalledProcessError):
                self.invoke('submit', 'test', '--execute')
        with patch.object(w, 'run') as remote:
            with self.assertRaises(FileExistsError):
                self.invoke('submit', 'test', '--execute')
            remote.assert_not_called()

    def test_bad_result_rejected(self):
        path = self.dest / 'retrieved/results'
        path.mkdir(parents=True)
        (path / 'result.json').write_text('{}')
        with self.assertRaises(ValueError):
            self.invoke('check', 'test')

if __name__ == '__main__':
    unittest.main()
