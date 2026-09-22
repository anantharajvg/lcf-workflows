# Frontier via the AmSC Python Client

Frontier is exposed through the OLCF Moderate AmSC facility API, not the open
S3M Slurm endpoint used for Odo and Defiant. The client uses the S3M token
outside the repository and submits the job through the `Frontier` resource.

## Setup

Install the tutorial-supported client into the local, ignored virtual environment:

```bash
.venv/bin/python -m pip install \
  --extra-index-url https://gitlab.com/api/v4/projects/77567162/packages/pypi/simple \
  --extra-index-url https://gitlab.com/api/v4/projects/76368190/packages/pypi/simple \
  --extra-index-url https://gitlab.com/api/v4/projects/80654726/packages/pypi/simple \
  'amsc-client>=0.4.1,<0.5'
```

The configuration in `configs/frontier-amsc.json` uses allocation `stf053`,
the Moderate facility, and the approved staging directory:

```text
/lustre/orion/stf053/proj-shared/amsc-iri/
```

That directory must remain writable by the OLCF project automation account as
well as by the project users.

## Verify access

The probe is read-only. It reads the header file directly and never prints its
token value.

```bash
.venv/bin/python amsc_frontier.py probe \
  --header-file /Users/vga/.config/olcf/stf053-s3m.header--frontier
```

Expected output identifies resource `Frontier` and reports `"status": "up"`.

## Review a smoke submission

This renders the one-node, five-minute CPU smoke request but makes no remote
change:

```bash
.venv/bin/python amsc_frontier.py submit --run-id frontier-smoke-001 \
  --header-file /Users/vga/.config/olcf/stf053-s3m.header--frontier
```

Submit only after reviewing the preview:

```bash
.venv/bin/python amsc_frontier.py submit --run-id frontier-smoke-001 \
  --header-file /Users/vga/.config/olcf/stf053-s3m.header--frontier --execute
```

The submission prints only the AmSC job identifier and state. Use the AmSC
client's job object or the OLCF service to monitor the resulting job.

## Validated smoke test

On 2026-09-22, the following submission was accepted through the AmSC client:

| Item | Value |
| --- | --- |
| Run ID | `frontier-smoke-001` |
| Slurm job ID | `5529532` |
| Requested resources | One Frontier node, five-minute limit |
| Final Slurm state | `COMPLETED` |
| Exit code | `0:0` |

The AmSC client returned `queued` on submission. Its subsequent status lookup
received a transient S3M upstream `502` connection-reset error, so `sacct -j
5529532` was used to verify the final Slurm result. All three Slurm job records
(`5529532`, batch, and extern) completed with exit code `0:0`.
