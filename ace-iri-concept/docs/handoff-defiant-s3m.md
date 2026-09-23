# Handoff: ACE IRI concept OLCF workflows

**Last updated:** 2026-09-22
**Repository:** `/Users/vga/projects/lcf-workflows`  
**Working directory:** `/Users/vga/projects/lcf-workflows/ace-iri-concept`
**Git state:** see `git log --oneline` for the current commit

## Purpose and current status

This project is building reproducible workflows for OLCF systems. There are two
separate prototypes in this directory:

1. a local-first SSH/Slurm workflow intended for Riker;
2. a tested S3M REST workflow for the Defiant ACE testbed;
3. a tested S3M REST workflow for Odo, including a Globus data-transfer loop;
   and
4. a tested AmSC Python Client workflow for Frontier in the Moderate enclave.

The Defiant S3M proof of concept is complete. It submits a small CPU Slurm job
from a laptop through S3M and reads back its final scheduler state. Two jobs
completed successfully: `14070` and `14071`.

The project owner repeated the full Defiant manual procedure successfully on
2026-09-23 with the Open-enclave token header. The final job ID was not
recorded; see [the Defiant proof-of-concept record](defiant-s3m-proof-of-concept.md)
for the reproducible procedure and earlier recorded job IDs.

Odo S3M access is also verified using the Defiant-token header. Odo job `44416`
completed on 2026-09-22 with return code `0`. Its configuration is
`configs/odo-s3m.json`; see [the Odo smoke-test record](odo-s3m-smoke-test.md).

The first automated Globus fixture transfer to Odo Wolf2 also completed on
2026-09-22. The task used the restricted local collection and the NCCS Open DTN
collection; see [the transfer-test record](globus-transfer-test.md).

The full Globus-to-Odo-to-Globus fixture analysis completed on 2026-09-22 using
Odo job `44418`; see [the end-to-end test record](odo-globus-end-to-end-test.md).
The test found that Globus-created directories need explicit provisioning for
S3M project-automation write access.

The Frontier AmSC smoke test completed on 2026-09-22. AmSC client version
`0.4.3` registered the OLCF Moderate facility, discovered resource `Frontier`,
and submitted job `5529532` using allocation `stf053`, queue `batch`, and
`/lustre/orion/stf053/proj-shared/amsc-iri/`. Slurm accounting recorded
`COMPLETED` with `0:0`. The job's captured stdout was
`ace-iri-frontier-frontier-smoke-001.stdout` in that staging directory.
The AmSC job-status query subsequently returned a transient upstream S3M 502;
use `sacct` to verify future jobs until that service behavior is resolved.
On a later submission attempt, the configured Frontier header returned HTTP 401
with `{"code":16,"message":"unauthorized"}`. Public resource discovery can
still succeed in that condition. Renew or select a Frontier/OLCF Moderate S3M
token before the next submission; use a new run ID after any failed attempt.

The next planned effort is to turn this scheduler smoke test into a small,
reproducible scientific data-analysis workflow. No scientific application,
input data, transfer method, or output-validation rule has been chosen yet.
The approved direction is recorded in the
[semi-production plan](semi-production-plan.md); its first implementation
decision is the scientific payload and its small input dataset.

## Important constraints

- User: `vga`; allocation: `stf053`.
- Use Defiant for the S3M prototype, with partition `batch-cpu`.
- The tested shared working directory is
  `/lustre/polis/stf053/proj-shared/olcf-s3m-test`.
- The S3M Open-enclave token header file is outside Git at
  `/Users/vga/.config/olcf/stf053-s3m.header--open`. Use it for Defiant and
  Odo. Do not display, copy, log, or commit its contents. It must remain
  readable only by its owner.
- `runs/` is ignored by Git. It contains generated job requests and responses.
- Do not submit, cancel, or retry a live job without the user's explicit
  authorization for that operation.
- The user explicitly corrected the earlier target: direct Slurm experiments
  should use Riker, not Frontier. The S3M work is a separate Defiant testbed
  proof of concept.
- Frontier is now validated only through the AmSC client and the OLCF Moderate
  endpoint.
- The Frontier Moderate-enclave S3M header file is outside Git at
  `/Users/vga/.config/olcf/stf053-s3m.header--moderate`. Treat it as secret and
  do not display, copy, log, or commit it.

## What was implemented

| File | Role |
| --- | --- |
| `s3m_defiant.py` | Direct S3M client for Defiant: probe, prepare, submit, and status. |
| `hpc/defiant-smoke.sbatch`, `hpc/odo-smoke.sbatch` | Readable batch-script sources loaded into the S3M JSON request during preparation. |
| `configs/defiant-s3m.json` | Reviewed non-secret Defiant endpoint, allocation, partition, and working directory. |
| `configs/odo-s3m.json` | Reviewed non-secret Odo endpoint, allocation, `batch` partition, and GPFS project directory. |
| `tests/test_s3m_defiant.py` | Local validation of job shape, header permissions, and no-repeat submission protection. |
| `workflow.py` and `hpc/job.sbatch` | Separate local-first Riker SSH/Slurm prototype; no live Riker submission has occurred. |
| `docs/defiant-s3m-proof-of-concept.md` | Technical record and manual test procedure. |
| `docs/data-analysis-extension-plan.md` | Recommended next milestones. |
| `amsc_frontier.py` | Frontier AmSC client: read-only probe and explicitly gated CPU smoke submission. |
| `configs/frontier-amsc.json` | Non-secret OLCF Moderate endpoint, allocation, queue, and approved staging directory. |
| `docs/frontier-amsc-client.md` | Setup, manual reproduction, validated job record, and output retrieval. |
| `odo_globus_e2e.py` | Stateful local-to-Globus-to-Odo-to-Globus fixture orchestrator. |
| `configs/odo-globus-e2e.json` | Non-secret collection IDs and fixture input/output paths for the orchestrator. |
| `docs/odo-globus-orchestrator.md` | Manual preparation, execution, validation, and recovery guidance. |

`s3m_defiant.py` creates a JSON request for one node, one task, and five
minutes. Its script prints basic host information and runs
`srun --ntasks=1 /bin/hostname`. The API requires `nodes` as a string and
requires the script inside the `job` JSON object; both details were validated
against the live S3M API.

## Reproduce the safe local portion

```bash
cd /Users/vga/projects/lcf-workflows/ace-iri-concept
make test
```

Expected result: 15 passing tests. This command performs no S3M network call
and does not submit a job.

To check authentication only, after obtaining user authorization for a live API
request:

```bash
python3 s3m_defiant.py probe \
  --header-file /Users/vga/.config/olcf/stf053-s3m.header--open \
  --execute
```

For the full manual procedure, see
[`defiant-s3m-proof-of-concept.md`](defiant-s3m-proof-of-concept.md). Review the
generated request before a real submission. The script writes a
`submission-attempted` marker before sending a job, and intentionally refuses
to submit that run ID again.

## Reproduce the validated Frontier AmSC workflow

The project virtual environment needs `amsc-client` version 0.4.x from the
tutorial's GitLab package index. The complete install and run instructions are
in [the Frontier AmSC record](frontier-amsc-client.md). The short procedure is:

```bash
cd /Users/vga/projects/lcf-workflows/ace-iri-concept
.venv/bin/python amsc_frontier.py probe \
  --header-file /Users/vga/.config/olcf/stf053-s3m.header--moderate
.venv/bin/python amsc_frontier.py submit --run-id frontier-smoke-002 \
  --header-file /Users/vga/.config/olcf/stf053-s3m.header--moderate
# Review the JSON preview, then only with the user's explicit approval:
.venv/bin/python amsc_frontier.py submit --run-id frontier-smoke-002 \
  --header-file /Users/vga/.config/olcf/stf053-s3m.header--moderate --execute
```

Use the returned job ID to check final state, then retrieve stdout by its AmSC
job-name prefix:

```bash
sacct -X -j <job-id> --format=JobID,JobName,Partition,Account,AllocCPUS,State,ExitCode
cat /lustre/orion/stf053/proj-shared/amsc-iri/ace-iri-frontier-frontier-smoke-002.stdout
```

Do not assume a `slurm-<job-id>.out` filename. AmSC stores stdout as
`<job-name>.stdout`; new job names append a microsecond-precision UTC timestamp
to the supplied run ID. No intentional stderr is produced by this smoke payload.

## Known limitation and next decision

The S3M endpoint used here can submit and monitor Slurm jobs but does not give
this workflow filesystem retrieval. It cannot currently pull stdout or analysis
results from Defiant.

Before extending the code, ask the user to select the first small scientific
analysis and provide or decide:

1. input data and its Defiant location;
2. the command or application environment to run;
3. expected outputs and a correctness check; and
4. an OLCF-approved method to retrieve outputs from Defiant.

Then implement a self-describing per-run directory, record input checksums and
application version, write a compact result summary, and add local tests for
the result checker. Start with synthetic or public small data and one CPU.

## References

- [Defiant S3M proof of concept](defiant-s3m-proof-of-concept.md)
- [Data-analysis extension plan](data-analysis-extension-plan.md)
- [OLCF S3M overview](https://docs.olcf.ornl.gov/services_and_applications/s3m/overview.html)
- [Defiant quick-start guide](https://docs.olcf.ornl.gov/ace_testbed/defiant_quick_start_guide.html)
- [Riker user guide](https://docs.olcf.ornl.gov/systems/riker_user_guide.html)
- [AmSC client tutorial repository](https://github.com/amsc-interfaces/amsc-client-tutorial/tree/main)
  — upstream reference for later Python-client and filesystem workflow work.
- [Frontier AmSC client smoke test](frontier-amsc-client.md)
