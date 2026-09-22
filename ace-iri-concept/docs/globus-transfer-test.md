# Globus transfer test: dataset 001

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

## Transfer rules

- Use a fresh destination directory; do not mirror or delete destination files.
- Submit a recursive transfer with checksum synchronization and verification.
- Record the Globus task ID in an ignored local run record.
- Do not submit an Odo analysis job until Globus reports success and the
  destination checksum is verified.

## Prerequisites still required

1. A Globus collection that exposes this laptop directory. Globus Connect
   Personal is suitable for this small fixture if no institutional collection is
   already available.
2. One-time Globus browser authentication for the local CLI.
3. The collection UUID for the source and confirmation that the OLCF Open DTN
   collection can write to the planned Wolf2 destination.
