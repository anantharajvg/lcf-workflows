# ACE IRI concept: OLCF workflows

## Git workflow

- Never make changes, commits, or pushes directly on `main`.
- Start each new unit of work on a descriptive branch created from an updated
  `main` branch, such as `feature/odo-payload` or `docs/reproduction-guide`.
- Commit and push work to that branch. Merge it into `main` only after review
  and explicit user authorization.
- Release tags are created from reviewed snapshots on `main`.

## Systems and approved paths

- User: `vga`; allocation: `stf053`.
- Riker uses the interactive SSH workflow in `interactive-workflows/`. It remains
  local-only until a live Riker operation is explicitly authorized.
- Defiant and Odo use the Open-enclave S3M workflow. Defiant is a scheduler
  smoke test; Odo has both a smoke test and a validated Globus data workflow.
- Frontier uses the Moderate-enclave AmSC Python Client workflow in
  `amsc_frontier.py`. Direct SSH Frontier scripts are experimental only.

## Credentials, enclaves, and data

- Keep authentication interactive and human-controlled. Never collect, store,
  or transmit RSA credentials.
- Use `/Users/vga/.config/olcf/stf053-s3m.header--open` only for Defiant and
  Odo. Use `/Users/vga/.config/olcf/stf053-s3m.header--moderate` only for
  Frontier. Token headers must remain owner-readable only.
- Never print, copy, log, commit, or place tokens in command arguments,
  generated requests, environment dumps, or documentation.
- Do not transfer Moderate-enclave data through Open-enclave systems or
  collections. Confirm the data classification and approved enclave before a
  transfer.

## Live-operation safety

- Read-only API requests require explicit user authorization.
- Never submit, cancel, retry, or modify a Slurm job without explicit user
  authorization for that operation.
- Never create, cancel, retry, mirror, or delete a Globus transfer without
  explicit user authorization for that operation.
- For every live run, use a fresh run ID and run-specific output path. Verify
  transfer and automation-account permissions before submission.
- After an ambiguous or failed transfer or submission, preserve its run record,
  task ID, and job ID. Inspect its state before deciding whether to retry. Never
  delete a record or marker to bypass this protection.

## Validation, documentation, and artifacts

- Validate local changes with `make test`. Shell syntax and simulated remote
  operations do not establish cluster compatibility.
- Before a live scientific run, define its input dataset, scientific question,
  expected outputs, acceptance criteria, and validation method. Scheduler
  success alone does not establish scientific validity.
- Record selected provenance for every live run: UTC start and finish times,
  Git commit and release tag, configuration checksum, input and output
  checksums, exact command, system, job ID, Globus task IDs, and final state.
- Record the application version, relevant modules, container image digest when
  used, and random seed. Do not dump the full process environment.
- Keep raw inputs immutable. Record their source, classification, authorization
  or license, transfer lineage, and durable storage location. Keep large raw
  and derived data outside Git, but commit a reviewed metadata summary and
  checksums.
- Require an independent rerun from a clean checkout or separate environment
  before describing a scientific payload as reproducible.
- Call a workflow validated only when the documented record includes the
  command path, final scheduler and transfer state, identifiers, result check,
  checksum evidence where applicable, and known limitations.
- Keep quick-start reproduction instructions in `README.md`, detailed evidence
  and recovery guidance in `docs/`, and system-specific settings in reviewed
  files under `configs/`.
- Do not log the full process environment. Record only selected provenance.
- Never commit runs, results, credentials, or large datasets.
- Maintain `CITATION.cff`. Before an external release, choose and add a license,
  archive durable scientific artifacts, and update the release documentation.
- Follow the sources in `docs/research-integrity.md` when applying these rules.
