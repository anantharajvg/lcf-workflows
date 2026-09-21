# ACE IRI concept: Riker and Defiant workflow prototypes

## Project documents

- [Defiant S3M proof of concept](docs/defiant-s3m-proof-of-concept.md) records
  the completed scheduler test and gives a manual, reproducible procedure.
- [Data-analysis extension plan](docs/data-analysis-extension-plan.md) describes
  the next milestones for turning this smoke test into an analysis workflow.
- [Handoff for the next collaborator or agent](docs/handoff-defiant-s3m.md)
  records verified state, constraints, and the next decision needed.

## Scope and decisions

Develop locally, prepare a versioned payload, stage it to Riker, submit a Slurm
job, inspect status, and retrieve a verifiable numerical result. This milestone
is validated locally only. No live Riker connection or submission has been made.

User: `vga`; allocation: `stf053`; host: `riker.olcf.ornl.gov`.
Proposed working directory: `/lustre/orion/stf053/scratch/vga/ace-iri-concept`.
The path follows OLCF's documented scratch layout; access and allocation validity
must be confirmed on Riker. Runs get separate subdirectories.

The first workload sums squares from 1 to 10,000 with Bash and awk. Expected
result: 333383335000. It needs no Python or MPI installation on Riker. Python 3
is required on the laptop, along with ssh and rsync.

One node, one task, one CPU, 1 GB requested memory, two minutes, partition `batch`.
Riker couples CPU and memory shares, so actual allocated memory can exceed the
request. Slurm launches the workload through srun on a compute node.

## Local validation

```bash
cd /Users/vga/projects/lcf-workflows/ace-iri-concept
make test
python3 workflow.py prepare smoke-001
python3 workflow.py stage smoke-001
python3 workflow.py submit smoke-001
```

Prepare writes only local files. All remote actions **preview by default**.
Payloads include a SHA-256 manifest and Git commit when one exists. File hashes
identify actual payload contents even when the checkout is dirty. Configuration
is snapshotted per run. Prepare a new run after changing source or configuration.

## Later: human-operated remote test

Only after authorizing a real cluster test, execute these in your own terminal:

```bash
python3 workflow.py stage smoke-001 --execute
python3 workflow.py submit smoke-001 --execute
python3 workflow.py status smoke-001 --execute
# After status shows COMPLETED with ExitCode 0:0:
python3 workflow.py fetch smoke-001 --execute
python3 workflow.py check smoke-001
```

SSH/RSA prompts remain in your terminal. SSH multiplexing is disabled. Each SSH
or rsync operation can require authentication. Verify any first-use host key
through OLCF's normal procedure. No credentials belong in this repository.

Staging uses mkdir and rsync without deletion. Fetch copies the remote run into
`runs/<run>/retrieved/`, including results, Slurm logs, job metadata and manifest.
No remote data is removed. The first prototype intentionally has no automatic
polling, cancellation, submission retries, parameter sweeps or GPU support.

## Defiant S3M test workflow

`s3m_defiant.py` is a separate, direct REST workflow for the Defiant ACE testbed.
It uses the S3M OpenAPI gateway with a project token header file outside this
repository. The first request is a one-node, one-task, five-minute CPU smoke test
on `batch-cpu`, running `hostname` through `srun`. Its working directory must
already exist and be writable by the project automation user:
`/lustre/polis/stf053/proj-shared/olcf-s3m-test`. This existing, verified
remote path has not been renamed as part of the local project rename.

```bash
python3 s3m_defiant.py probe --header-file /Users/vga/.config/olcf/stf053-s3m.header --execute
python3 s3m_defiant.py jobs --header-file /Users/vga/.config/olcf/stf053-s3m.header --execute
python3 s3m_defiant.py prepare --header-file /Users/vga/.config/olcf/stf053-s3m.header --run-id first
python3 s3m_defiant.py submit --header-file /Users/vga/.config/olcf/stf053-s3m.header --run-id first
```

The last command remains preview-only until `--execute` is added. Before any live
submission, inspect the generated `runs/s3m-<run>/request.json` and confirm that
the Polis working directory exists with correct project automation-user access.
S3M is an early-release test API; do not use it as a production workflow.
The first live smoke test, job `14070` on 2026-09-21, completed successfully
with exit code 0. S3M does not currently provide OLCF filesystem access, so the
workflow verifies scheduler completion but cannot retrieve the job's stdout.

Submission records an attempt before sending sbatch. A second attempt with the
same run ID is blocked, including after an interrupted connection. If a response
is lost, inspect squeue/sacct manually before retrying anything. If a job exists,
record its numeric ID in `runs/<run>/job-id.txt` to continue monitoring. Do not
remove the attempt marker or create a replacement job until its outcome is known.

Success requires **both** Slurm COMPLETED/0:0 and a passing numerical check.
A missing job in squeue alone does not prove success; consult sacct. Accounting
may lag. Local simulations cannot validate partition access, site policies,
filesystem permissions, authentication, available commands or actual scheduling.

## Sources

- https://docs.olcf.ornl.gov/systems/riker_user_guide.html
  Consulted 2026-09-21: login host, batch partition, node sharing, Orion scratch,
  sbatch and srun. The prototype uses a consistent one-task CPU layout.
- https://docs.olcf.ornl.gov/services_and_applications/s3m/overview.html
  Consulted 2026-09-21: S3M is an early-release, project-token-authenticated API
  that can submit Slurm jobs programmatically. It is not part of this initial
  SSH/RSA workflow. If evaluated later, use a least-privilege, project-scoped
  token stored outside Git and never pass it on a command line.
- https://docs.olcf.ornl.gov/ace_testbed/index.html
  Consulted 2026-09-21: ACE documents the Defiant testbed. Defiant is the first
  S3M target that authenticated successfully; use its quick-start guide for any
  testbed-specific Slurm or environment settings.
- Prior project discussion: interactive RSA authentication; local-only first
  milestone; keep workflow design, scripts and validation together.
