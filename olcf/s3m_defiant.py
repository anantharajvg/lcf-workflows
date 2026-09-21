#!/usr/bin/env python3
"""Token-file-based, explicit S3M operations for the Defiant testbed."""
import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def load_config():
    cfg = json.loads((ROOT / "configs/defiant-s3m.json").read_text())
    if not re.fullmatch(r"https://s3m\.olcf\.ornl\.gov/slurm/open/v0\.0\.43/defiant", cfg["base_url"]):
        raise ValueError("Unexpected S3M base URL")
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", cfg["account"]):
        raise ValueError("Invalid account")
    if cfg["partition"] != "batch-cpu":
        raise ValueError("This CPU smoke test requires Defiant batch-cpu")
    if not cfg["working_directory"].startswith("/lustre/polis/"):
        raise ValueError("Defiant working directory must be on Polis")
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
    script = "\n".join((
        "#!/bin/bash", "set -euo pipefail", "echo 'S3M Defiant smoke test'",
        "date -u +%FT%TZ", "hostname", "srun --ntasks=1 /bin/hostname",
    )) + "\n"
    return {"script": script, "job": {
        "name": f"s3m-smoke-{run_id}"[:128], "account": cfg["account"],
        "partition": cfg["partition"], "nodes": 1, "tasks": 1,
        "time_limit": {"set": True, "number": 5},
        "current_working_directory": cfg["working_directory"],
        "environment": ["PATH=/usr/bin:/bin"],
    }}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("probe", "jobs", "prepare", "submit"))
    parser.add_argument("--header-file", required=True)
    parser.add_argument("--run-id")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    cfg = load_config()
    header = header_file(args.header_file)
    if args.action == "prepare":
        if not args.run_id:
            parser.error("prepare requires --run-id")
        path = ROOT / "runs" / f"s3m-{args.run_id}" / "request.json"
        if path.exists():
            raise FileExistsError("Request already exists; choose a new run ID")
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(request(cfg, args.run_id), indent=2) + "\n")
        print(path)
        return
    if args.action == "probe":
        cmd = curl(cfg, header, "/ping")
    elif args.action == "jobs":
        cmd = curl(cfg, header, "/jobs")
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
    result = subprocess.run(cmd, check=True, text=True, stdout=subprocess.PIPE).stdout
    if args.action == "submit":
        (body.parent / "submission-response.json").write_text(result)
    if args.action == "jobs":
        print(json.dumps({"job_count": len(json.loads(result).get("jobs", []))}, indent=2))
    else:
        print(result)

if __name__ == "__main__":
    main()
