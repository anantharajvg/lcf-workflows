# ACE IRI concept: OLCF workflows

- Target Riker, user vga, allocation stf053. Do not use Frontier templates.
- Keep authentication interactive and human-controlled. Never collect or store RSA credentials.
- The SSH/Riker workflow remains local-only until explicitly authorized. The Defiant
  S3M workflow may make read-only API requests when explicitly requested. Never
  submit or cancel a job without explicit user authorization for that action.
- Validate with `make test`. Shell syntax and simulated remote operations do not establish cluster compatibility.
- Keep design and operating instructions in README.md; cluster settings in configs/riker.json.
- Do not log the full process environment. Record only selected provenance.
- Never commit runs, results, credentials or large datasets.
