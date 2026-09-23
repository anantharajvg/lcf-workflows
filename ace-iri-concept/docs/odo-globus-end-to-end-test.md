# Odo and Globus end-to-end test

**Date:** 2026-09-22  
**Status:** completed successfully

## Purpose

This test validates the complete research-workflow loop with a small,
non-sensitive fixture:

1. transfer input from a restricted local Globus collection to Odo Wolf2;
2. submit an S3M Slurm job on Odo;
3. validate the transferred input and run a small analysis;
4. transfer outputs back to the restricted local collection; and
5. validate the returned result locally.

## Inputs and transfer

The source fixture is `fixtures/globus-dataset-001/`. It contains two numeric
measurements, `1.250` and `2.750`, with a known sum of `4.000`.

The input transfer completed through Globus task:

```text
cbaa2870-b677-11f1-9c61-0effcb3df825
```

The destination was:

```text
/gpfs/wolf2/olcf/stf053/proj-shared/ace-iri-concept/inputs/globus-dataset-001/
```

Globus reported 3 files, 600 bytes, checksum synchronization, and checksum
verification with no task errors.

## Odo analysis

The batch source is [`hpc/odo-globus-e2e.sbatch`](../hpc/odo-globus-e2e.sbatch).
It checks the known input SHA-256 checksum, calculates the sum, writes
`result.txt`, `result.json`, and `SHA256SUMS`, then records the allocated host.

The first attempt, Odo job `44417`, failed before input processing because the
S3M project automation account could not create a directory inside a
Globus-created directory. Its retrieved Slurm log recorded `Permission denied`.

The corrected attempt, Odo job `44418`, used the existing project-shared root
as its output parent and completed with return code `0`. Its output directory
was:

```text
/gpfs/wolf2/olcf/stf053/proj-shared/globus-e2e-002/
```

## Output transfer and local validation

The output transfer completed through Globus task:

```text
41f74114-b679-11f1-985b-0affd5e180af
```

It transferred 4 files with checksum verification and no task errors into the
restricted local result directory. Local validation confirmed:

| Check | Result |
| --- | --- |
| Slurm state | `COMPLETED` |
| Slurm return code | `0` |
| Analysis result | `4.000` |
| `result.json` | `{"analysis":"fixture-sum","result":4.000}` |
| Input, result, and JSON checksums | Match the Odo-generated manifest |

## Outcome and next requirement

The complete transfer-and-analysis path works. Before treating it as a
semi-production run layout, provision a run-output directory that is writable
by both the Globus transfer identity and the S3M project automation account.
The successful test used the project-shared root as a temporary output parent;
future scientific runs should use a dedicated, permission-checked run tree.

## Orchestrated repeat validation

On 2026-09-23, the new `odo_globus_e2e.py` orchestrator repeated the complete
fixture workflow successfully with run ID `globus-e2e-20260923T174943Z`:

| Stage | Identifier | Final result |
| --- | --- | --- |
| Input Globus task | `28f5b1ec-b777-11f1-8240-02ffe792127d` | `SUCCEEDED`, 8 files considered, 0 bytes copied because checksum synchronization found matching input. |
| Odo S3M job | `44434` | `COMPLETED`, return code `0`. |
| Output Globus task | `3f529ff6-b777-11f1-815f-0affd5e180af` | `SUCCEEDED`, 4 files, 498 bytes, no faults. |
| Local validation | — | Result `4.000`, expected JSON, and all recorded SHA-256 hashes verified. |

The orchestrator waited for Odo completion before creating the output transfer,
which prevents the earlier `FILE_NOT_FOUND` failure caused by requesting an
output directory before the job created it.
