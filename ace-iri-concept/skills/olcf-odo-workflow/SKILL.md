---
name: olcf-odo-workflow
description: Prepare, validate, and explicitly run the ACE IRI Odo Open-enclave S3M and Globus workflow. Use for the reviewed Odo path, not Frontier Moderate-enclave or direct SSH work.
---

# Odo workflow through Open S3M and Globus

Use this skill for the ACE IRI concept's Odo path. Odo and Defiant use the
Open-enclave S3M workflow. This skill covers Odo's smoke test and the reviewed
fixture workflow that transfers input through Globus, runs Odo, returns output,
and validates checksums.

## Start with the reviewed materials

Read `AGENTS.md`, `docs/odo-s3m-smoke-test.md`,
`docs/odo-globus-orchestrator.md`, `s3m_defiant.py`, `odo_globus_e2e.py`, and
the relevant reviewed configuration in `configs/`. Do not reuse the fixture
configuration for scientific data without a separately reviewed configuration,
payload, and acceptance criteria.

Use only a user-managed Open-enclave authorization header file supplied with
`--header-file`. Never inspect, print, copy, commit, or transmit its contents.
Do not use a Frontier Moderate-enclave token or path for Odo.

## Smoke-test workflow

1. Run `make test` from the project root.
2. With explicit authorization for a read-only request, optionally use the
   S3M probe/status commands documented in `docs/odo-s3m-smoke-test.md`.
3. Choose a fresh run ID and render the Odo request without `--execute`:

   ```bash
   .venv/bin/python s3m_defiant.py submit --config odo-s3m.json \
     --run-id <run-id> --header-file <open-header-file>
   ```

4. Review the request, then obtain explicit approval before adding `--execute`.
5. Preserve the request, response, and job ID. Inspect the documented Odo job
   state and output before deciding whether it succeeded.

## Globus fixture workflow

This path creates two Globus transfers and one Odo job. Confirm that Globus is
authenticated, the local collection is running, and both collection paths are
approved before any remote operation.

1. Choose a fresh run ID and create a local run record:

   ```bash
   .venv/bin/python odo_globus_e2e.py prepare --run-id <run-id>
   ```

2. Render the planned record without remote effects:

   ```bash
   .venv/bin/python odo_globus_e2e.py run --run-id <run-id> \
     --header-file <open-header-file>
   ```

3. Review the local and remote paths, task labels, data classification, and
   run record. Obtain explicit approval immediately before `--execute`.
4. After a live run, preserve `record.json`, both Globus task IDs, the Odo job
   ID, final states, and checksum evidence. Do not retry an ambiguous transfer
   or submission automatically; inspect the record and remote status first.

The fixture's validated output is `4.000` plus the documented JSON and SHA-256
checks. That confirms the fixture workflow, not a scientific analysis.

## Validation when editing this skill or workflow

- Run the skill validator on this directory.
- Run `make test` from the project root.
- Use a fresh temporary run ID to run `prepare` and preview `run` without
  `--execute`; do not create a Globus task or Slurm job during validation.
- Confirm that this skill contains no credential value, collection secret, or
  unapproved remote operation.
