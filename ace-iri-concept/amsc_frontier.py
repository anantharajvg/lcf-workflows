#!/usr/bin/env python3
"""Discover Frontier or submit an explicit minimal AmSC CPU smoke job.

The S3M token stays in an Authorization-header file outside this repository.
Submitting requires --execute; without it, the command only prints the request.
"""

import argparse
import json
import re
from pathlib import Path

from amsc_client import Client


ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG = ROOT / "configs" / "frontier-amsc.json"
DEFAULT_HEADER = Path("/Users/vga/.config/olcf/stf053-s3m.header--frontier")


def load_config(path: Path) -> dict:
    config = json.loads(path.read_text())
    expected = {
        "base_url",
        "facility_name",
        "resource_name",
        "account",
        "queue",
        "directory",
    }
    if set(config) != expected:
        raise ValueError("Unexpected Frontier AmSC configuration fields")
    if config["base_url"] != "https://amsc-moderate.s3m.olcf.ornl.gov/":
        raise ValueError("Frontier must use the OLCF Moderate AmSC endpoint")
    if config["resource_name"] != "Frontier":
        raise ValueError("Unexpected compute resource")
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", config["account"]):
        raise ValueError("Invalid allocation name")
    if not config["directory"].startswith("/lustre/orion/stf053/proj-shared/"):
        raise ValueError("Use the approved Frontier project-shared staging directory")
    return config


def read_token(header_file: Path) -> str:
    header_file = header_file.expanduser().resolve()
    if not header_file.is_file():
        raise ValueError(f"Token header file does not exist: {header_file}")
    if header_file.stat().st_mode & 0o077:
        raise ValueError("Token header file must not be group- or world-readable")
    name, separator, token = header_file.read_text().strip().partition(":")
    if name.lower() != "authorization" or not separator:
        raise ValueError("Token file must contain one Authorization header")
    token = token.strip()
    if token.lower().startswith("bearer "):
        token = token[7:].strip()
    if len(token) < 20:
        raise ValueError("Token is missing or unexpectedly short")
    return token


def frontier_client(config: dict, token: str):
    client = Client(token="not-needed-for-facilities")
    client.register_facility(
        config["facility_name"],
        base_url=config["base_url"],
        display_name="Oak Ridge Leadership Computing Facility (Moderate)",
        auth_method="token",
        token=token,
    )
    facility = client.facility(config["facility_name"])
    return facility.resource(config["resource_name"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("probe", "submit"))
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--header-file", type=Path, default=DEFAULT_HEADER)
    parser.add_argument("--run-id", help="Required for submit; letters, digits, _ and - only")
    parser.add_argument("--execute", action="store_true", help="Actually submit the job")
    args = parser.parse_args()

    config = load_config(args.config)
    frontier = frontier_client(config, read_token(args.header_file))
    if args.action == "probe":
        print(json.dumps({
            "resource_id": frontier.id,
            "resource_name": frontier.name,
            "status": str(frontier.status),
        }, indent=2))
        return

    if not args.run_id or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,48}", args.run_id):
        parser.error("submit requires a valid --run-id")
    job_name = f"ace-iri-frontier-{args.run_id}"[:128]
    request = {
        "executable": "/bin/bash",
        "arguments": ["-lc", "set -euo pipefail; echo 'AmSC Frontier CPU smoke test'; date -u +%FT%TZ; hostname"],
        "directory": config["directory"],
        "name": job_name,
        "queue": config["queue"],
        "account": config["account"],
        "duration": 300,
        "nodes": 1,
        "environment": {"ACE_IRI_RUN_ID": args.run_id},
    }
    if not args.execute:
        print(json.dumps(request, indent=2))
        print("Preview only. Add --execute only after reviewing this request.")
        return
    job = frontier.submit(**request)
    print(json.dumps({
        "job_id": job.id,
        "state": str(job.state),
        "expected_stdout": f"{config['directory'].rstrip('/')}/{job_name}.stdout",
    }, indent=2))


if __name__ == "__main__":
    main()
