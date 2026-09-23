# Odo S3M smoke test

**Date:** 2026-09-22  
**Project:** ACE IRI concept  
**Status:** completed successfully

## Purpose

This test checked that the S3M token used for Defiant can also submit and
monitor a minimal Slurm job on Odo. Odo is an OLCF open-enclave training system
with Frontier-like hardware.

## Verified access and scheduler settings

- The Defiant-token header returned `HTTP 200` from Odo's S3M ping endpoint.
- The S3M partition endpoint reported that `batch` was up.
- Odo's documented project-shared compute filesystem is
  `/gpfs/wolf2/olcf/stf053/proj-shared`.
- The S3M endpoint used Slurm OpenAPI `v0.0.44`.

## Submitted smoke job

| Field | Value |
| --- | --- |
| Job ID | `44416` |
| Account | `stf053` |
| Partition | `batch` |
| Resources | 1 node, 1 task, 5 minutes |
| Working directory | `/gpfs/wolf2/olcf/stf053/proj-shared` |
| Result | `COMPLETED`, exit status `SUCCESS`, return code `0` |

The source script is [`hpc/odo-smoke.sbatch`](../hpc/odo-smoke.sbatch). During
`prepare`, the client reads this file and places its contents in the JSON
`script` field required by S3M. The batch script printed the current date and
hostname, then launched `srun --ntasks=1 /bin/hostname`. It did not request a GPU explicitly. Odo's
compute nodes include GPUs, so this small job remains a real one-node batch
allocation even though the command is CPU-only.

## Repeat safely

First run local checks, then create a **new** run ID and inspect the request:

```bash
cd /Users/vga/projects/lcf-workflows/ace-iri-concept
make test
python3 s3m_defiant.py prepare --config odo-s3m.json \
  --header-file /Users/vga/.config/olcf/stf053-s3m.header--open \
  --run-id odo-smoke-002
cat runs/s3m-odo-smoke-002/request.json
```

After reviewing the request and obtaining authorization for a live job:

```bash
python3 s3m_defiant.py submit --config odo-s3m.json \
  --header-file /Users/vga/.config/olcf/stf053-s3m.header--open \
  --run-id odo-smoke-002 --execute
python3 s3m_defiant.py status --config odo-s3m.json \
  --header-file /Users/vga/.config/olcf/stf053-s3m.header--open \
  --job-id JOB_ID --execute
```

The token remains outside the repository. S3M status confirms scheduler state,
but this workflow still does not retrieve files from Odo through a filesystem
API.

## Sources

- [Odo user guide](https://docs.olcf.ornl.gov/systems/odo_user_guide.html)
- [OLCF S3M compute API](https://docs.olcf.ornl.gov/services_and_applications/s3m/api/compute.html)
