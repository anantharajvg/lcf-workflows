#!/bin/bash

cd /Users/vga/projects/lcf-workflows/ace-iri-concept

RUN_ID="globus-e2e-$(date -u +%Y%m%dT%H%M%SZ)"

python3 odo_globus_e2e.py prepare --run-id "$RUN_ID"

# Review only; no remote operations.
python3 odo_globus_e2e.py run --run-id "$RUN_ID" \
  --header-file /Users/vga/.config/olcf/stf053-s3m.header--open

# Executes transfers and submits the Odo job.
python3 odo_globus_e2e.py run --run-id "$RUN_ID" \
  --header-file /Users/vga/.config/olcf/stf053-s3m.header--open \
  --execute
