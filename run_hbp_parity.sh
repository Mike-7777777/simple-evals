#!/bin/bash
# One original-side HealthBench Professional parity run with Claude Code.
# Usage (from the directory that contains this checkout as simple_evals_hbp/):
#   simple_evals_hbp/run_hbp_parity.sh IDS_FILE [N_THREADS]
# IDS_FILE: simple_evals_hbp/healthbench_professional_parity_ids.txt for a full
# run, or a shorter list (e.g. the 10-task sanity check).
# Env: ANTHROPIC_API_KEY (and ANTHROPIC_BASE_URL), OPENAI_API_KEY (and
# OPENAI_BASE_URL) for the gpt-5.4-2026-03-05 judge, CLAUDE_CODE_VERSION.
set -euo pipefail
ids=$1
threads=${2:-4}
stamp=$(date -u +%Y%m%dT%H%M%SZ)
out=hbp_runs/$stamp
mkdir -p "$out"
export HBP_AGENT_LOG_DIR=$out/agent_logs
python -m simple_evals_hbp.healthbench_professional_input --ids "$ids" --out "$out/input.jsonl"
python -m simple_evals_hbp.simple_evals \
  --eval healthbench --model claude-code-haiku-5-5 \
  --healthbench-input-path "$out/input.jsonl" \
  --healthbench-professional-mode --healthbench-use-gpt-5-4-low-grader \
  --healthbench-length-adjustment-center 2000 \
  --healthbench-length-adjustment-penalty-per-500-chars 0.0147 \
  --n-repeats 1 --n-threads "$threads" 2>&1 | tee "$out/run.log"
# simple_evals.py writes its report and results under /tmp; keep them with the run.
grep -oE '/tmp/[^ ]+\.(json|html)' "$out/run.log" | sort -u | xargs -r -I{} cp {} "$out/"
echo "run directory: $out"
