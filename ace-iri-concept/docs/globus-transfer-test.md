# Globus transfer test: dataset 001

**Status:** completed successfully on 2026-09-22

## Source fixture

The transfer source is the versioned, non-sensitive fixture at:

```text
fixtures/globus-dataset-001/
```

It contains `observations.tsv`, a short README, and `SHA256SUMS`. The expected
SHA-256 value for `observations.tsv` is:

```text
05a7f070e7c576221b00401597519a21c24d10ad121eff9efdd0fb23eb4350d0
```

## Planned destination

```text
/gpfs/wolf2/olcf/stf053/proj-shared/ace-iri-concept/inputs/globus-dataset-001/
```

## Completed pilot

The fixture was transferred from the restricted local Globus Connect Personal
collection `vga-globus-local` to the OLCF **NCCS Open DTN (Globus 5)**
collection. Globus task ID:

```text
cbaa2870-b677-11f1-9c61-0effcb3df825
```

The task succeeded with all 3 files transferred, 600 bytes transferred, no task
errors, checksum synchronization, and post-transfer checksum verification.
The destination directory was created under the Odo Wolf2 project-shared area
without modifying any pre-existing project files.

## Transfer rules

- Use a fresh destination directory; do not mirror or delete destination files.
- Submit a recursive transfer with checksum synchronization and verification.
- Record the Globus task ID in an ignored local run record.
- Do not submit an Odo analysis job until Globus reports success and the
  destination checksum is verified.

## Prerequisites still required

1. A Globus collection that exposes this laptop directory. This pilot used a
   restricted Globus Connect Personal collection.
2. One-time Globus browser authentication for the local CLI.
3. Confirmation that the OLCF Open DTN collection can write to the planned
   Wolf2 destination.
