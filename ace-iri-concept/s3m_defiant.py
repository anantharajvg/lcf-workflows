#!/usr/bin/env python3
"""Token-file-based, explicit S3M operations for the Defiant testbed."""
import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def load_config(config_name="defiant-s3m.json"):
    if config_name not in ("defiant-s3m.json", "odo-s3m.json"):
        raise ValueError("Unexpected S3M configuration")
    cfg = json.loads((ROOT / "configs" / config_name).read_text())
    if cfg["base_url"] not in (
        "https://s3m.olcf.ornl.gov/slurm/open/v0.0.43/defiant",
        "https://s3m.olcf.ornl.gov/slurm/open/v0.0.44/odo",
    ):
        raise ValueError("Unexpected S3M base URL")
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", cfg["account"]):
        raise ValueError("Invalid account")
    if cfg["base_url"].endswith("/defiant"):
        if cfg["partition"] != "batch-cpu" or not cfg["working_directory"].startswith("/lustre/polis/"):
            raise ValueError("Defiant requires batch-cpu and a Polis working directory")
    else:
        if cfg["partition"] != "batch" or not cfg["working_directory"].startswith("/gpfs/wolf2/olcf/"):
            raise ValueError("Odo requires batch and a wolf2 working directory")
    return cfg

def header_file(path):
    p = Path(path).expanduser().resolve()
    line = p.read_text().strip()
    if not p.is_file() or not line.startswith("Authorization:") or len(line.partition(":")[2].strip()) < 20:
        raise ValueError("Header file must contain one Authorization: token line")
    if p.stat().st_mode & 0o077:
        raise ValueError("Header file must not be group- or world-readable")
    return p

def curl(cfg, header, path, method="GET", body=None):
    cmd = ["curl", "--fail-with-body", "--silent", "--show-error", "--max-time", "30",
           "-H", f"@{header}", "-H", "Accept: application/json", "-X", method]
    if body:
        cmd += ["-H", "Content-Type: application/json", "--data-binary", f"@{body}"]
    cmd.append(cfg["base_url"] + path)
    return cmd

def request(cfg, run_id):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,40}", run_id):
        raise ValueError("Invalid run ID")
    resource = cfg["base_url"].rsplit("/", 1)[-1]
    script = "\n".join((
        "#!/bin/bash", "set -euo pipefail", f"echo 'S3M {resource} smoke test'",
        "date -u +%FT%TZ", "hostname", "srun --ntasks=1 /bin/hostname",
    )) + "\n"
    return {"job": {
        "name": f"ace-iri-{resource}-{run_id}"[:128], "account": cfg["account"],
        "partition": cfg["partition"], "nodes": "1", "tasks": 1,
        "time_limit": {"set": True, "number": 5},
        "current_working_directory": cfg["working_directory"],
        "environment": ["PATH=/usr/bin:/bin"], "script": script,
    }}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("probe", "jobs", "prepare", "submit", "status"))
    parser.add_argument("--header-file", required=True)
    parser.add_argument("--config", default="defiant-s3m.json",
                        choices=("defiant-s3m.json", "odo-s3m.json"))
    parser.add_argument("--run-id")
    parser.add_argument("--job-id")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    cfg = load_config(args.config)
    header = header_file(args.header_file)
    if args.action == "prepare":
        if not args.run_id:
            parser.error("prepare requires --run-id")
        path = ROOT / "runs" / f"s3m-{args.run_id}" / "request.json"
        if path.exists():
            raise FileExistsError("Request already exists; choose a new run ID")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(request(cfg, args.run_id), indent=2) + "\n")
        print(path)
        return
    if args.action == "probe":
        cmd = curl(cfg, header, "/ping")
    elif args.action == "jobs":
        cmd = curl(cfg, header, "/jobs")
    elif args.action == "status":
        if not args.job_id or not re.fullmatch(r"[0-9]+", args.job_id):
            parser.error("status requires a numeric --job-id")
        cmd = curl(cfg, header, f"/job/{args.job_id}")
    else:
        if not args.run_id:
            parser.error("submit requires --run-id")
        body = ROOT / "runs" / f"s3m-{args.run_id}" / "request.json"
        if not body.is_file():
            raise FileNotFoundError("Run prepare first")
        cmd = curl(cfg, header, "/job/submit", method="POST", body=body)
    if not args.execute:
        print("Preview only. Add --execute to run the command.")
        return
    marker = None
    if args.action == "submit":
        marker = body.parent / "submission-attempted"
        if marker.exists():
            raise FileExistsError("Submission was already attempted; inspect Defiant before retrying")
        marker.write_text("Check Defiant before any retry.\n")
    completed = subprocess.run(cmd, check=False, text=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    if args.action == "submit":
        (body.parent / "submission-response.json").write_text(completed.stdout)
    if completed.returncode:
        detail = completed.stdout.strip() or completed.stderr.strip() or "no response body"
        raise RuntimeError(f"S3M request failed: {detail}")
    result = completed.stdout
    if args.action == "jobs":
        print(json.dumps({"job_count": len(json.loads(result).get("jobs", []))}, indent=2))
    elif args.action == "status":
        data = json.loads(result)
        job = data.get("job") or (data.get("jobs") or [{}])[0]
        print(json.dumps({key: job.get(key) for key in ("job_id", "name", "state", "exit_code")}, indent=2))
    else:
        print(result)

if __name__ == "__main__":
    main()
