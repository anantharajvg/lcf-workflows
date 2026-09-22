#!/bin/bash
set -euo pipefail
input="${ACE_IRI_INPUT_DIR:?}"
output="${ACE_IRI_OUTPUT_DIR:?}"
expected="05a7f070e7c576221b00401597519a21c24d10ad121eff9efdd0fb23eb4350d0"
mkdir -p "$output"
test "$(sha256sum "$input/observations.tsv" | awk '{print $1}')" = "$expected"
awk -F '\t' 'NR > 1 {sum += $2} END {if (NR != 3) exit 1; printf "%.3f\n", sum}' \
  "$input/observations.tsv" > "$output/result.txt"
test "$(cat "$output/result.txt")" = "4.000"
printf '{"analysis":"fixture-sum","result":4.000}\n' > "$output/result.json"
sha256sum "$input/observations.tsv" "$output/result.txt" "$output/result.json" > "$output/SHA256SUMS"
srun --ntasks=1 /bin/hostname >> "$output/hosts.txt"
