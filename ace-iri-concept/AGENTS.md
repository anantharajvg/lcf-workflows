# ACE IRI concept: OLCF workflows

## Git workflow

- Never make changes, commits, or pushes directly on `main`.
- Start each new unit of work on a descriptive branch created from an updated
  `main` branch, such as `feature/odo-payload` or `docs/reproduction-guide`.
- Commit and push work to that branch. Merge it into `main` only after review
  and explicit user authorization.
- Release tags are created from reviewed snapshots on `main`.

- Target Riker, user vga, allocation stf053. Do not use Frontier templates.
- Keep authentication interactive and human-controlled. Never collect or store RSA credentials.
- The SSH/Riker workflow remains local-only until explicitly authorized. The Defiant
  S3M workflow may make read-only API requests when explicitly requested. Never
  submit or cancel a job without explicit user authorization for that action.
- Validate with `make test`. Shell syntax and simulated remote operations do not establish cluster compatibility.
- Keep design and operating instructions in README.md; cluster settings in configs/riker.json.
- Do not log the full process environment. Record only selected provenance.
- Never commit runs, results, credentials or large datasets.
