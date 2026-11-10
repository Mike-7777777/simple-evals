# HealthBench Professional parity with Harbor

This branch adds what the original-benchmark side of the Harbor adapter's parity
runs needs (harbor-framework/adapters, `src/healthbench-professional`):

- `sampler/claude_code_sampler.py`: Claude Code in a container, run the way
  Harbor's `claude-code` agent runs it, with the adapter's instruction and
  `/workspace/conversation.md`. Registered as `claude-code-sonnet-5-5`.
- `healthbench_professional_input.py`: converts the pinned, sha256-checked
  dataset file to the HealthBench input format, restricted to a list of ids.
- `healthbench_professional_parity_ids.txt`: the 150-task parity subset, a copy
  of the adapter's `parity_task_ids.txt`.
- `run_hbp_parity.sh`: one run with the HealthBench Professional settings
  (`gpt-5.4-2026-03-05` judge at low reasoning, length adjustment centre 2000,
  0.0147 per 500 characters).

## Run

Needs Docker and Python 3.12. Clone this branch as `simple_evals_hbp/`, then:

```bash
python -m venv .venv && . .venv/bin/activate
pip install openai pandas blobfile jinja2 tqdm numpy requests anthropic scipy tabulate "setuptools<81"
pip install --no-build-isolation "human-eval @ git+https://github.com/openai/human-eval"
export ANTHROPIC_API_KEY=... OPENAI_API_KEY=... CLAUDE_CODE_VERSION=2.1.322
simple_evals_hbp/run_hbp_parity.sh simple_evals_hbp/healthbench_professional_parity_ids.txt
```

Each run writes `hbp_runs/<timestamp>/`: the converted input, the simple-evals
report and results, and per-task agent logs (`agent_logs/*/`). The parity score
is `overall_score_length_adjusted` in the results JSON: the mean task score,
clipped to [0, 1] after averaging.
