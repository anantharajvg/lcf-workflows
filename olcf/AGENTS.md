# OLCF / Riker workflow

- Target Riker, user vga, allocation stf053. Do not use Frontier templates.
- Keep authentication interactive and human-controlled. Never collect or store RSA credentials.
- Current milestone is local-only. Do not connect, transfer or submit remotely without an explicit user request.
- Validate with `make test`. Shell syntax and simulated remote operations do not establish cluster compatibility.
- Keep design and operating instructions in README.md; cluster settings in configs/riker.json.
- Do not log the full process environment. Record only selected provenance.
- Never commit runs, results, credentials or large datasets.
