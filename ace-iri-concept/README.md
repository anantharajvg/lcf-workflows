# ACE IRI concept: OLCF workflow prototypes

## Project documents

- [Defiant S3M proof of concept](docs/defiant-s3m-proof-of-concept.md) records
  the completed scheduler test and gives a manual, reproducible procedure.
- [Data-analysis extension plan](docs/data-analysis-extension-plan.md) describes
  the next milestones for turning this smoke test into an analysis workflow.
- [Handoff for the next collaborator or agent](docs/handoff-defiant-s3m.md)
  records verified state, constraints, and the next decision needed.
- [Odo S3M smoke test](docs/odo-s3m-smoke-test.md) records the successful
  Odo submission and reusable procedure.
- [Semi-production scientific workflow plan](docs/semi-production-plan.md)
  defines the next staged work: data transfer, payload execution, validation,
  and recovery.
- [Odo and Globus end-to-end test](docs/odo-globus-end-to-end-test.md) records
  the successful input-transfer, Odo-analysis, output-transfer, and local
  validation loop.
- [Odo–Globus orchestrator](docs/odo-globus-orchestrator.md) documents the
  stateful command that ran the validated fixture workflow end to end on
  2026-09-23.
- [Frontier AmSC client smoke test](docs/frontier-amsc-client.md) records the
  successful Moderate-enclave Frontier submission and manual reproduction.

## Contributors

- **vga** — project owner, OLCF user, workflow validation, and operational
  decisions.
- **Codex (OpenAI)** — coding-agent assistance with workflow implementation,
  testing, and technical documentation.

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
python3 s3m_defiant.py probe --header-file /Users/vga/.config/olcf/stf053-s3m.header--open --execute
python3 s3m_defiant.py jobs --header-file /Users/vga/.config/olcf/stf053-s3m.header--open --execute
python3 s3m_defiant.py prepare --header-file /Users/vga/.config/olcf/stf053-s3m.header--open --run-id first
python3 s3m_defiant.py submit --header-file /Users/vga/.config/olcf/stf053-s3m.header--open --run-id first
```

The last command remains preview-only until `--execute` is added. Before any live
submission, inspect the generated `runs/s3m-<run>/request.json` and confirm that
the Polis working directory exists with correct project automation-user access.
The readable batch-script source is `hpc/defiant-smoke.sbatch`; `prepare` loads
it into the S3M JSON `script` field required by the API.
S3M is an early-release test API; do not use it as a production workflow.
The first live smoke test, job `14070` on 2026-09-21, completed successfully
with exit code 0. S3M does not currently provide OLCF filesystem access, so the
workflow verifies scheduler completion but cannot retrieve the job's stdout.

Submission records an attempt before sending sbatch. A second attempt with the
same run ID is blocked, including after an interrupted connection. If a response
is lost, inspect squeue/sacct manually before retrying anything. If a job exists,
record its numeric ID in `runs/<run>/job-id.txt` to continue monitoring. Do not
remove the attempt marker or create a replacement job until its outcome is known.

## Odo S3M smoke test

The same client supports Odo with `--config odo-s3m.json`. Odo's project-shared
compute filesystem is `/gpfs/wolf2/olcf/stf053/proj-shared` and its active
compute partition is `batch`. Use an Odo-authorized token header, then prepare
and inspect a fresh run before submitting:

```bash
python3 s3m_defiant.py prepare --config odo-s3m.json \
  --header-file /Users/vga/.config/olcf/stf053-s3m.header--open \
  --run-id odo-smoke-001
cat runs/s3m-odo-smoke-001/request.json
python3 s3m_defiant.py submit --config odo-s3m.json \
  --header-file /Users/vga/.config/olcf/stf053-s3m.header--open \
  --run-id odo-smoke-001 --execute
```

Odo is an OLCF training system with Frontier-like GPU nodes. This smoke test
does not request GPUs explicitly; its one-node allocation is still a live Odo
batch allocation. Job `44416` completed successfully on 2026-09-22 with return
code `0`. The readable batch-script source is `hpc/odo-smoke.sbatch`; `prepare`
embeds its contents in the API request. Consult the current Odo guide before
scaling it.

Success requires **both** Slurm COMPLETED/0:0 and a passing numerical check.
A missing job in squeue alone does not prove success; consult sacct. Accounting
may lag. Local simulations cannot validate partition access, site policies,
filesystem permissions, authentication, available commands or actual scheduling.

## Frontier via AmSC

Frontier uses the OLCF **Moderate** AmSC facility endpoint, not the direct S3M
OpenAPI endpoint used by Defiant and Odo. The non-secret configuration is in
`configs/frontier-amsc.json`; the client is `amsc_frontier.py`. The project S3M
token remains outside the repository in an owner-readable Authorization-header
file.

The read-only access check is:

```bash
.venv/bin/python amsc_frontier.py probe \
  --header-file /Users/vga/.config/olcf/stf053-s3m.header--moderate
```

The first live smoke job, `5529532`, was submitted on 2026-09-22 with one node
and a five-minute limit. It completed with Slurm exit code `0:0`. AmSC placed
its stdout at
`/lustre/orion/stf053/proj-shared/amsc-iri/ace-iri-frontier-frontier-smoke-001.stdout`.
The precise manual procedure, including installation and Slurm-accounting
validation, is in [the Frontier AmSC record](docs/frontier-amsc-client.md).

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
- https://docs.olcf.ornl.gov/systems/odo_user_guide.html
  Consulted 2026-09-22: Odo is an open-enclave training system. Project-shared
  GPFS storage is `/gpfs/wolf2/olcf/[projid]/proj-shared`; Odo otherwise shares
  much of Frontier's architecture.
- https://github.com/amsc-interfaces/amsc-client-tutorial/tree/main
  Added 2026-09-21: upstream AmSC Python Client tutorial repository. Its
  facility and filesystem notebooks provide the client pattern used for the
  Frontier Moderate-enclave workflow.
- Prior project discussion: interactive RSA authentication; local-only first
  milestone; keep workflow design, scripts and validation together.
