#!/bin/bash
#SBATCH --job-name=olcf-smoke
#SBATCH --partition=batch
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=00:02:00
#SBATCH --output=slurm-%j.out
#SBATCH --error=slurm-%j.err
set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?}"
export OMP_NUM_THREADS=1
mkdir -p results
printf 'job_id=%s\n' "${SLURM_JOB_ID:?}" > results/job.txt
hostname >> results/job.txt
date -u >> results/job.txt
if type module >/dev/null 2>&1; then module -t list > results/modules.txt 2>&1; fi
srun --ntasks=1 --cpus-per-task=1 bash src/smoke.sh
