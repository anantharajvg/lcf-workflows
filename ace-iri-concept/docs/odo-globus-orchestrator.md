# Odo–Globus end-to-end orchestrator

`odo_globus_e2e.py` combines the validated fixture workflow into one
stateful command sequence:

1. checksum-synchronized input transfer from the restricted local Globus
   collection to Odo Wolf2;
2. wait for the input Globus task;
3. submit the reviewed Odo S3M analysis request;
4. wait for Odo to finish successfully;
5. checksum-synchronized output transfer back to the local collection; and
6. validate the returned result and all three recorded SHA-256 hashes.

The non-secret collection IDs and paths are in
`configs/odo-globus-e2e.json`. The S3M token remains outside Git at
`/Users/vga/.config/olcf/stf053-s3m.header--open`.

## Before running

Authenticate the Globus CLI once and confirm the local Globus Connect Personal
collection is running:

```bash
cd /Users/vga/projects/lcf-workflows/ace-iri-concept
.venv/bin/globus whoami
```

If needed, run `.venv/bin/globus login` and complete browser authentication.
Run `make test` before a live run.

## Prepare and review

Choose a fresh ID. It is used for the Odo output directory, both Globus task
labels, and the ignored local run record.

```bash
RUN_ID="globus-e2e-$(date -u +%Y%m%dT%H%M%SZ)"

python3 odo_globus_e2e.py prepare --run-id "$RUN_ID"
python3 odo_globus_e2e.py run --run-id "$RUN_ID" \
  --header-file /Users/vga/.config/olcf/stf053-s3m.header--open
```

The second command is a preview. It prints the run record and makes no network
request, transfer, or job submission.

## Execute one run

After reviewing the preview and authorizing all remote operations, run:

```bash
python3 odo_globus_e2e.py run --run-id "$RUN_ID" \
  --header-file /Users/vga/.config/olcf/stf053-s3m.header--open \
  --execute
```

The command waits up to one hour for each Globus transfer and for the Odo job.
On success it prints the input Globus task ID, Odo job ID, output Globus task
ID, and result `4.000`.

Run state is saved in `runs/odo-globus-<run-id>/record.json`; S3M's generated
request and submission response remain in `runs/s3m-<run-id>/`. Both locations
are ignored by Git. Do not delete or alter either record during an active run.

## Recovery rules

The script does not retry a failed or ambiguous Globus transfer or job
submission. Inspect the saved record and the relevant Globus task or Odo job
before deciding how to proceed. In particular, it starts the output transfer
only after Odo reports `COMPLETED` with return code `0`, avoiding the earlier
`FILE_NOT_FOUND` condition caused by requesting output before it existed.

The fixture input path is intentionally fixed and checksum-validated. A new
scientific dataset needs a new configuration and a payload checksum update; do
not overwrite the fixture path to reuse this script for scientific data.

## Validated run

The full orchestration completed successfully on 2026-09-23 with run ID
`globus-e2e-20260923T174943Z`. It recorded input task
`28f5b1ec-b777-11f1-8240-02ffe792127d`, Odo job `44434`, and output task
`3f529ff6-b777-11f1-815f-0affd5e180af`. Odo completed with return code `0`;
the output task returned four files with no faults, and local checksum
validation passed. The input task copied zero bytes because its checksum-sync
mode found the fixture already matched the remote destination.
