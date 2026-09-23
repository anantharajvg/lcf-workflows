# Interactive SSH/Slurm workflows

These scripts are human-operated alternatives to the API-based S3M and AmSC
workflows elsewhere in this repository. They prepare a reproducible run,
display every remote command first, and perform remote work only when the user
adds `--execute`.

They use SSH and `rsync` with `keyboard-interactive,password` authentication.
An executed command therefore prompts in the local terminal for the site's
interactive login or MFA flow. The scripts do not read, store, or transmit SSH
keys or credentials.

## Files

| File | Intended target | Status |
| --- | --- | --- |
| `workflow.py` | Riker | Local simulation tested; no live Riker submission recorded. |
| `workflow-frontier.py` | Frontier via direct SSH and `sbatch` | Experimental direct-SSH variant; the supported Frontier workflow is the AmSC client at `../amsc_frontier.py`. |

Both scripts use the common payload at `../src/smoke.sh` and
`../hpc/job.sbatch`. A prepared run is created under `../runs/<run-id>/`; it
contains copies of the payload and configuration plus a SHA-256 manifest.

## Riker procedure

Run these commands from the project root:

```bash
cd /Users/vga/projects/lcf-workflows/ace-iri-concept

# Local-only: prepare immutable input for this run.
python3 interactive-workflows/workflow.py prepare riker-smoke-001

# Preview the exact SSH and rsync commands; no network operation occurs.
python3 interactive-workflows/workflow.py stage riker-smoke-001
python3 interactive-workflows/workflow.py submit riker-smoke-001
```

After reviewing the generated request and obtaining authorization for the live
job, run the interactive lifecycle:

```bash
python3 interactive-workflows/workflow.py stage riker-smoke-001 --execute
python3 interactive-workflows/workflow.py submit riker-smoke-001 --execute
python3 interactive-workflows/workflow.py status riker-smoke-001 --execute
# After COMPLETED with ExitCode 0:0:
python3 interactive-workflows/workflow.py fetch riker-smoke-001 --execute
python3 interactive-workflows/workflow.py check riker-smoke-001
```

`submit` creates `runs/<run-id>/submission-attempted` before invoking `sbatch`.
Do not remove that marker or retry the same run ID after a lost connection;
check `squeue` and `sacct` first.

## Frontier direct-SSH variant

`workflow-frontier.py` follows the same lifecycle but reads
`../configs/frontier.json` and stages under that configuration's `remote_root`.
It is not the validated Frontier route. For the supported Moderate-enclave
workflow, use [the Frontier AmSC procedure](../docs/frontier-amsc-client.md).

The direct-SSH variant is useful only when direct Frontier SSH access, the
target filesystem permissions, and the requested Slurm partition have been
independently verified.

## Validation

Run the local test suite from the project root:

```bash
make test
```

These tests validate command construction, manifests, no-retry protection, and
the numerical smoke result. They do not validate Riker or Frontier access.
