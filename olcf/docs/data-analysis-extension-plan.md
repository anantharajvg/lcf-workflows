# Plan for a Defiant S3M data-analysis workflow

The S3M smoke test has established a useful base: a local program can submit a
small CPU job to Defiant and observe its final Slurm state. The next goal is a
reproducible analysis run with declared inputs, an application command, and
results that can be checked after the job finishes.

## Milestone 1: define one small analysis

Choose one scientific calculation that can run in a few minutes on one CPU.
Record the following before writing code:

- the input files and where they are stored;
- the expected output files;
- the application, version, and environment modules or container required;
- the command to run;
- a simple correctness check, such as a known scalar value, file count, or
  small reference result.

Use synthetic or public non-sensitive input at first. Keep the example small
enough to rerun while the workflow is being developed.

## Milestone 2: make the job self-describing

Extend the generated S3M request so that each run has a unique working
directory under the project-shared area. The batch script should:

1. create a run directory;
2. write basic provenance: submission time, job ID when available, application
   version, input checksums, and the exact command;
3. run the analysis;
4. write outputs and a short `result.json` or `summary.txt`;
5. exit nonzero when the analysis or validation fails.

Avoid putting secrets in the job environment or in provenance files.

## Milestone 3: decide how outputs return to the laptop

The current S3M path can submit and monitor jobs but cannot retrieve filesystem
contents. Before relying on it for data analysis, choose and document one
approved transfer path for Defiant outputs. Possible choices must be verified
against current OLCF guidance and project policy. Once selected, automate only
the minimum safe transfer: result summaries and small validated outputs first.

The workflow should retain on-system output locations and checksums even after
files are copied elsewhere.

## Milestone 4: add a local result check

Add a command that validates downloaded results without contacting Defiant. It
should check expected files, parse the result summary, and compare a small
reference value or checksum. Add a test using fixture data so changes to the
workflow do not silently change the scientific result.

## Milestone 5: scale deliberately

After one CPU analysis is reproducible, expand one dimension at a time:

1. more input data;
2. more tasks or nodes;
3. parameter sweeps;
4. accelerators or a different OLCF system, if the application needs them.

For every scale change, record resources requested, elapsed time, application
version, input version, and validation result. This produces a simple
experiment record that can later support performance studies and agent-driven
automation.

## Suggested repository layout

When the first analysis is chosen, keep its durable pieces together:

```text
olcf/
  configs/             # reviewed cluster and workflow settings
  docs/                # design decisions and operating guides
  src/                 # analysis code and batch-script templates
  tests/               # local tests and small fixtures
  runs/                # generated requests and results; ignored by Git
```

The immediate decision needed for the next implementation step is the first
scientific analysis: its input, command, expected result, and the approved way
to retrieve its outputs from Defiant.
