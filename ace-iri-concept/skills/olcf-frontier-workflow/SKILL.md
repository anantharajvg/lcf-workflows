---
name: olcf-frontier-workflow
description: Prepare, validate, and explicitly submit Frontier jobs through the OLCF Moderate AmSC client. Use for the reviewed ACE IRI Frontier workflow, not direct SSH or Open-enclave S3M jobs.
---

# Frontier workflow through AmSC

Use this skill for the ACE IRI concept's Frontier path. It uses the OLCF
Moderate AmSC client and the reviewed configuration in
`configs/frontier-amsc.json`. It does not apply to Odo, Defiant, Riker, or a
direct SSH workflow.

## Start with the reviewed materials

Read `AGENTS.md`, `docs/frontier-amsc-client.md`, `amsc_frontier.py`, and
`configs/frontier-amsc.json`. Treat them as the project source of truth for
the endpoint, allocation, queue, and approved staging path. Check the current
working tree before changing a tracked file.

Use a user-managed Moderate-enclave authorization header file passed through
`--header-file`. Never open it, print it, copy it into a request, or record its
contents. Do not use an Open-enclave token for Frontier.

## Safe workflow

1. Run `make test` before changing the workflow. These are local checks only.
2. With explicit authorization for a read-only probe, run:

   ```bash
   .venv/bin/python amsc_frontier.py probe --header-file <moderate-header-file>
   ```

   A successful probe verifies resource discovery, not that the credential can
   submit a job.
3. Choose a fresh human-readable run ID and render the request without
   `--execute`:

   ```bash
   .venv/bin/python amsc_frontier.py submit --run-id <run-id> \
     --header-file <moderate-header-file>
   ```

   Review the resource, allocation, queue, staging directory, resource size,
   command, and expected output path.
4. Request explicit approval immediately before submitting the specific job.
   Only then use `--execute`.
5. Record the returned job ID, generated job name, UTC time, Git revision, and
   final scheduler state. Use `sacct` and inspect the job-name-prefixed stdout
   file in the configured staging directory. A `COMPLETED` result with `0:0`
   confirms the smoke path; it does not validate a scientific payload.

## Failure handling

If AmSC reports unauthorized access, report that the Moderate credential is
not accepted and stop. Do not retry automatically. If status lookup fails
after submission, preserve the returned job ID and use the documented Slurm
accounting check before deciding whether any further action is needed.

For scientific payloads, define acceptance criteria and data provenance before
submission, keep data in the approved Moderate path, and follow
`docs/research-integrity.md`.

## Validation when editing this skill or workflow

- Run the skill validator on this directory.
- Run `make test` from the project root.
- Render, but do not execute, a Frontier submission and verify that it uses the
  Moderate endpoint and reviewed configuration.
- Confirm the skill contains no credential value, live job ID, or unapproved
  remote operation.
