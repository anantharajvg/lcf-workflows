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

## Discover the resource

The probe is read-only. It reads the header file directly and never prints its
token value.

```bash
.venv/bin/python amsc_frontier.py probe \
  --header-file /Users/vga/.config/olcf/stf053-s3m.header--moderate
```

Expected output identifies resource `Frontier` and reports `"status": "up"`.
Resource discovery is public, so this check confirms the client and endpoint
but does **not** prove that a token can submit jobs.

## Review a smoke submission

This renders the one-node, five-minute CPU smoke request but makes no remote
change:

```bash
.venv/bin/python amsc_frontier.py submit --run-id frontier-smoke-001 \
  --header-file /Users/vga/.config/olcf/stf053-s3m.header--moderate
```

Submit only after reviewing the preview:

```bash
.venv/bin/python amsc_frontier.py submit --run-id frontier-smoke-001 \
  --header-file /Users/vga/.config/olcf/stf053-s3m.header--moderate --execute
```

The submission prints the AmSC job identifier, its initial state, job name, and
expected stdout path. It appends a UTC timestamp with microsecond precision to
the human-readable run ID, so a new submission is unique even when the same
run ID is reused. For example, a run ID of `frontier-smoke` produces a name
like `ace-iri-frontier-frontier-smoke-20260922T153045123456Z`.

## Manually verify the result

AmSC job-status requests can occasionally fail upstream even when a job was
accepted. Use Slurm accounting as the authoritative completion check:

```bash
sacct -X -j <job-id> --format=JobID,JobName,Partition,Account,AllocCPUS,State,ExitCode
```

Wait for the parent record to show `COMPLETED` and `0:0`. Then inspect the
files written by AmSC in the configured directory:

```bash
ls -l /lustre/orion/stf053/proj-shared/amsc-iri/ace-iri-frontier-<run-id>-<utc-timestamp>.*
cat /lustre/orion/stf053/proj-shared/amsc-iri/ace-iri-frontier-<run-id>-<utc-timestamp>.stdout
```

The minimal smoke job prints its label, a UTC timestamp, and its execution-host
name. It has no intentional stderr output. If AmSC captures stderr for a future
payload, it will have the same job-name prefix in this directory.

## Authentication failure

If submission reports that AmSC rejected the request as unauthorized, generate
or select a new S3M token authorized for **Frontier** in the **OLCF Moderate**
enclave. Replace the contents of the external header file only; never add the
token to this repository. Then use a new run ID for the next submission.

The resource probe can still report Frontier as `up` with an unauthorized token,
because resource discovery is a public endpoint.

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

AmSC stored the smoke job's standard output using its job name, rather than
Slurm's usual `slurm-<job-id>.out` convention:

```text
/lustre/orion/stf053/proj-shared/amsc-iri/ace-iri-frontier-frontier-smoke-001.stdout
```

For future runs, look in the configured staging directory for files whose
prefix matches the submitted AmSC job name.
