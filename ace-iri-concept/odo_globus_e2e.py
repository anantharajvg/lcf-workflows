#!/usr/bin/env python3
"""Run the validated local-Globus-Odo-Globus fixture workflow.

All remote changes require --execute. A run record prevents duplicate Globus
tasks or Slurm submissions after an interrupted command.
"""

import argparse
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path

import s3m_defiant as s3m


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "configs" / "odo-globus-e2e.json"
DEFAULT_HEADER = Path("/Users/vga/.config/olcf/stf053-s3m.header--open")


def load_config(path: Path) -> dict:
    config = json.loads(path.read_text())
    required = {
        "source_collection", "destination_collection", "local_input",
        "remote_input", "remote_output_root", "local_output_root", "s3m_config",
    }
    if set(config) != required:
        raise ValueError("Unexpected Odo Globus configuration fields")
    if config["s3m_config"] != "odo-e2e-s3m.json":
        raise ValueError("This workflow requires the reviewed Odo E2E configuration")
    for key in ("source_collection", "destination_collection"):
        if not re.fullmatch(r"[0-9a-f-]{36}", config[key]):
            raise ValueError(f"Invalid Globus collection ID: {key}")
    for key in ("remote_input", "remote_output_root"):
        if not config[key].startswith("/gpfs/wolf2/olcf/stf053/proj-shared"):
            raise ValueError(f"Unexpected Odo storage path: {key}")
    return config


def run_dir(run_id: str) -> Path:
    return ROOT / "runs" / f"odo-globus-{run_id}"


def read_record(path: Path) -> dict:
    return json.loads((path / "record.json").read_text())


def write_record(path: Path, record: dict) -> None:
    (path / "record.json").write_text(json.dumps(record, indent=2) + "\n")


def prepare(config: dict, run_id: str) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,40}", run_id):
        raise ValueError("Invalid run ID")
    path = run_dir(run_id)
    if path.exists():
        raise FileExistsError("Run already exists; inspect or use a new run ID")
    path.mkdir(parents=True)
    record = {
        "run_id": run_id,
        "input_task_id": None,
        "job_id": None,
        "output_task_id": None,
        "remote_input": config["remote_input"],
        "remote_output": f"{config['remote_output_root'].rstrip('/')}/{run_id}",
        "local_input": str(ROOT / config["local_input"]),
        "local_output": str(ROOT / config["local_output_root"] / run_id),
    }
    write_record(path, record)
    return path


def command(args: list[str]) -> str:
    completed = subprocess.run(args, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip() or "no response body"
        raise RuntimeError(f"Command failed: {detail}")
    return completed.stdout


def globus_transfer(source_collection: str, destination_collection: str, source: str, destination: str, label: str) -> str:
    output = command([
        str(ROOT / ".venv/bin/globus"), "transfer", "--recursive", "--sync-level", "checksum",
        "--verify-checksum", "--label", label, "--format", "json",
        f"{source_collection}:{source}/", f"{destination_collection}:{destination}/",
    ])
    data = json.loads(output)
    task_id = data.get("task_id")
    if not isinstance(task_id, str) or not re.fullmatch(r"[0-9a-f-]{36}", task_id):
        raise RuntimeError("Globus did not return a task ID")
    return task_id


def wait_for_globus(task_id: str) -> None:
    command([str(ROOT / ".venv/bin/globus"), "task", "wait", task_id, "--timeout", "3600", "--heartbeat"])


def s3m_submit(header: Path, run_id: str) -> int:
    config = s3m.load_config("odo-e2e-s3m.json")
    body = s3m.request(config, run_id)
    request_path = ROOT / "runs" / f"s3m-{run_id}" / "request.json"
    if request_path.exists():
        raise FileExistsError("S3M request already exists; inspect it before any retry")
    request_path.parent.mkdir(parents=True, exist_ok=True)
    request_path.write_text(json.dumps(body, indent=2) + "\n")
    marker = request_path.parent / "submission-attempted"
    marker.write_text("Check Odo before any retry.\n")
    output = command(s3m.curl(config, header, "/job/submit", "POST", request_path))
    (request_path.parent / "submission-response.json").write_text(output)
    job_id = json.loads(output).get("job_id")
    if not isinstance(job_id, int):
        raise RuntimeError("S3M did not return a numeric job ID")
    return job_id


def wait_for_job(header: Path, job_id: int) -> None:
    config = s3m.load_config("odo-e2e-s3m.json")
    deadline = time.monotonic() + 3600
    while time.monotonic() < deadline:
        data = json.loads(command(s3m.curl(config, header, f"/job/{job_id}")))
        job = data.get("job") or (data.get("jobs") or [{}])[0]
        state = job.get("state", {})
        current = state.get("current", []) if isinstance(state, dict) else state
        if "COMPLETED" in current:
            exit_code = job.get("exit_code", {}).get("return_code", {}).get("number")
            if exit_code == 0:
                return
            raise RuntimeError(f"Odo job {job_id} completed with return code {exit_code}")
        if any(value in current for value in ("FAILED", "CANCELLED", "TIMEOUT", "NODE_FAIL")):
            raise RuntimeError(f"Odo job {job_id} ended in state {current}")
        time.sleep(10)
    raise RuntimeError(f"Timed out waiting for Odo job {job_id}")


def validate(record: dict) -> None:
    local_input = Path(record["local_input"])
    local_output = Path(record["local_output"])
    if (local_output / "result.txt").read_text().strip() != "4.000":
        raise ValueError("Unexpected result.txt")
    if json.loads((local_output / "result.json").read_text()) != {"analysis": "fixture-sum", "result": 4.0}:
        raise ValueError("Unexpected result.json")
    manifest = (local_output / "SHA256SUMS").read_text().splitlines()
    expected = {Path(line.split(maxsplit=1)[1]).name: line.split(maxsplit=1)[0] for line in manifest}
    for name, path in {
        "observations.tsv": local_input / "observations.tsv",
        "result.txt": local_output / "result.txt",
        "result.json": local_output / "result.json",
    }.items():
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected.get(name):
            raise ValueError(f"Checksum mismatch for {name}")


def execute(config: dict, header: Path, path: Path) -> None:
    record = read_record(path)
    if not record["input_task_id"]:
        record["input_task_id"] = globus_transfer(
            config["source_collection"], config["destination_collection"],
            record["local_input"], record["remote_input"], f"ACE IRI input {record['run_id']}",
        )
        write_record(path, record)
    wait_for_globus(record["input_task_id"])
    if not record["job_id"]:
        record["job_id"] = s3m_submit(header, record["run_id"])
        write_record(path, record)
    wait_for_job(header, record["job_id"])
    if not record["output_task_id"]:
        Path(record["local_output"]).mkdir(parents=True, exist_ok=True)
        record["output_task_id"] = globus_transfer(
            config["destination_collection"], config["source_collection"],
            record["remote_output"], record["local_output"], f"ACE IRI output {record['run_id']}",
        )
        write_record(path, record)
    wait_for_globus(record["output_task_id"])
    validate(record)
    print(json.dumps({"run_id": record["run_id"], "input_task_id": record["input_task_id"], "job_id": record["job_id"], "output_task_id": record["output_task_id"], "result": "4.000"}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "run", "validate"))
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--header-file", type=Path, default=DEFAULT_HEADER)
    parser.add_argument("--config", type=Path, default=CONFIG_PATH)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    config = load_config(args.config)
    if args.action == "prepare":
        print(prepare(config, args.run_id))
        return
    path = run_dir(args.run_id)
    if not (path / "record.json").is_file():
        parser.error("run prepare first")
    if args.action == "validate":
        validate(read_record(path))
        print("Local result and checksums verified.")
        return
    s3m.header_file(args.header_file)
    if not args.execute:
        print(json.dumps(read_record(path), indent=2))
        print("Preview only. Add --execute to submit transfers and the Odo job.")
        return
    execute(config, args.header_file, path)


if __name__ == "__main__":
    main()
