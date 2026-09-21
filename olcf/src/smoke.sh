#!/bin/bash
set -euo pipefail
mkdir -p results
awk 'BEGIN { s=0; for(i=1;i<=10000;i++) s+=i*i; printf "{\"sum_of_squares\":%.0f,\"terms\":10000}\n",s }' > results/result.json
