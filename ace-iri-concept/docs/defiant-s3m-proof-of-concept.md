# Defiant S3M proof of concept

**Date:** 2026-09-21  
**Status:** completed successfully  
**Project:** ACE IRI concept
**Purpose:** prove that a local Python program can submit and monitor a small
Slurm job on the Defiant testbed through OLCF's S3M service.

## What was built

The repository contains `s3m_defiant.py`. It uses `curl` to call the Slurm REST
API exposed by S3M. It does not need an SSH session on Defiant.

The program reads its non-secret settings from
`configs/defiant-s3m.json`:

| Setting | Value used in this test |
| --- | --- |
| S3M target | Defiant |
| Allocation | `stf053` |
| Slurm partition | `batch-cpu` |
| Working directory | `/lustre/polis/stf053/proj-shared/olcf-s3m-test` |
| Resources | 1 node, 1 task, 5 minutes |

The generated batch script prints the date and hostname, then runs
`srun --ntasks=1 /bin/hostname`. It is intentionally small: its job is to test
authentication, job submission, scheduling, and Slurm completion before adding
a scientific application.

## Credential handling

S3M authenticates requests with an OLCF project token. The token is stored in a
header file outside this repository:

```text
/Users/vga/.config/olcf/stf053-s3m.header
```

The file contains one `Authorization:` header and is readable only by its owner.
The script gives its path to curl as a header file. The token is not copied into
the repository, generated request JSON, command arguments, or documentation.

## What was tested

1. The S3M Defiant ping endpoint accepted the current project token.
2. The script created a versioned JSON job request in `runs/s3m-<run-id>/`.
3. A request was validated against S3M's Slurm API. That validation established
   that `nodes` must be a string and that the batch `script` belongs inside the
   JSON `job` object.
4. A live smoke job, ID `14070`, was accepted and reported `COMPLETED` with exit
   code `0`.
5. A manual repeat of the same procedure, job ID `14071`, also completed.

These two successful jobs show that the local request format, token header,
Defiant allocation, partition, working directory, and minimal Slurm launch all
work together.

## Manual procedure

Start in the ACE IRI concept project directory and run the local checks:

```bash
cd /Users/vga/projects/lcf-workflows/ace-iri-concept
make test
```

Confirm that S3M can authenticate to Defiant:

```bash
python3 s3m_defiant.py probe \
  --header-file /Users/vga/.config/olcf/stf053-s3m.header \
  --execute
```

Prepare a new request. Choose a run ID that has not been used before:

```bash
python3 s3m_defiant.py prepare \
  --header-file /Users/vga/.config/olcf/stf053-s3m.header \
  --run-id manual-002
cat runs/s3m-manual-002/request.json
```

Inspect the JSON before submission. In particular, confirm the allocation,
partition, working directory, resource request, and script. Submit only after
that review:

```bash
python3 s3m_defiant.py submit \
  --header-file /Users/vga/.config/olcf/stf053-s3m.header \
  --run-id manual-002 \
  --execute
```

The response contains a numeric `job_id`. Check it until it is complete:

```bash
python3 s3m_defiant.py status \
  --header-file /Users/vga/.config/olcf/stf053-s3m.header \
  --job-id JOB_ID \
  --execute
```

Success means `state` is `COMPLETED` and the exit code is `0`. A pending or
running job should be checked again later. Do not submit the same run ID twice:
the script writes `submission-attempted` before the network call and blocks a
second attempt. If the response is lost, inspect the scheduler before starting
another submission.

## Limits of this proof of concept

The S3M interface used here reports scheduler state but does not currently give
this workflow a way to retrieve files from Defiant. It therefore cannot collect
stdout, scientific outputs, or logs through the API alone. The test proves job
submission and completion; it does not prove a particular science package,
input-data transfer method, output-retention policy, or performance level.

Generated run records are intentionally ignored by Git because they can contain
site-specific job responses. Keep only small, reviewed examples in source
control and do not commit tokens, raw data, or large results.

## Related resources

- [OLCF S3M overview](https://docs.olcf.ornl.gov/services_and_applications/s3m/overview.html)
- [Defiant quick-start guide](https://docs.olcf.ornl.gov/ace_testbed/defiant_quick_start_guide.html)
- [Data-analysis extension plan](data-analysis-extension-plan.md)
