# Plan: reusable Frontier and Odo agent skills

## Purpose

Create two repository-owned, reviewable skill packages that guide an agent
through the validated workflow paths without embedding credentials, changing
remote state by default, or treating an infrastructure test as scientific
validation.

## Deliverables

- `skills/olcf-frontier-workflow/SKILL.md` for Frontier submissions through
  the OLCF Moderate AmSC client.
- `skills/olcf-odo-workflow/SKILL.md` for Odo Open-enclave S3M smoke tests and
  the optional local-to-Globus-to-Odo-to-Globus fixture workflow.

The skill packages remain in this repository for review. They are not copied
to the user's Codex skill directory and are not activated by this change.

## Shared operating rules

1. Read `AGENTS.md`, the reviewed configuration, and the relevant workflow
   document before recommending a command or changing a remote system.
2. Never read, print, copy, commit, or transmit an S3M token. Accept only a
   user-managed header-file path as a command argument.
3. Treat probes and rendered requests as read-only or local preview steps.
   Require the user's immediate, explicit approval before a job submission,
   cancellation, retry, or Globus transfer.
4. Require a new run ID and preserve run records, scheduler identifiers, and
   Globus task identifiers after ambiguity or failure.
5. Keep the Frontier Moderate-enclave path separate from the Odo
   Open-enclave path. Do not move data between enclaves without confirming its
   classification and approved transfer route.
6. State that a completed scheduler job confirms the workflow path only.
   Scientific claims require documented inputs, acceptance criteria,
   provenance, result checks, and an independent rerun.

## Testing and validation

### Static checks for both packages

- Run the bundled skill validator against each skill directory.
- Confirm frontmatter names match their directory names and descriptions are
  specific enough to avoid routing unrelated OLCF work.
- Review the text for credentials, fixed tokens, and unapproved destructive
  actions. The result must contain none.
- Verify every repository-relative document and script reference exists.

### Local workflow checks

- Run `make test` from `ace-iri-concept/`. It performs shell syntax checks and
  the Python unit test suite; it does not access an OLCF system.
- For Frontier, use `amsc_frontier.py submit` without `--execute` to render a
  reviewed request. Do not submit as part of skill validation.
- For Odo, use `odo_globus_e2e.py prepare`, then `run` without `--execute` to
  inspect the generated record and preview. Use a temporary fresh run ID and
  remove only that local preview record after review if the user requests it.

### Live validation boundary

No live validation is part of drafting these skills. A future live test needs
the user's explicit approval for the named operation, a fresh run ID, and the
documented system-specific verification steps. For Odo's Globus route, it also
requires a running, authenticated local Globus collection and verified
collection permissions.

## Review and release path

After review, update the drafts as needed, run the checks again, commit on a
feature branch, push it, and open a pull request. Install or activate a skill
only in a later, separately authorized step.
