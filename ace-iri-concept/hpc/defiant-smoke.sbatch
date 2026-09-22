#!/bin/bash
set -euo pipefail
echo 'S3M Defiant smoke test'
date -u +%FT%TZ
hostname
srun --ntasks=1 /bin/hostname
