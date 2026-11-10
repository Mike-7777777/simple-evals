"""
Write HealthBench Professional in the HealthBench input format, for
--healthbench-input-path.

Reads the pinned, sha256-checked file the Harbor adapter uses
(openai/healthbench-professional@349962f) and keeps only the record ids listed
in --ids (one per line), e.g. the adapter's parity_task_ids.txt.

Usage: python -m simple-evals.healthbench_professional_input --ids IDS --out OUT.jsonl
"""

import argparse
import hashlib
import json
import urllib.request
from pathlib import Path

URL = (
    "https://huggingface.co/datasets/openai/healthbench-professional/resolve/"
    "349962fd46dd02343a0d8a606491baf59154ea1a/healthbench_professional_eval.jsonl"
)
SHA256 = "d44b08e6e952e04c945e2c406f02533d9e7a989a84e35820ee7efdff20c9e4e2"


def to_healthbench(row: dict) -> dict:
    return {
        "prompt_id": row["id"],
        "prompt": row["conversation"]["messages"],
        "rubrics": [
            {"criterion": it["criterion_text"], "points": it["points"], "tags": []}
            for it in row["rubric_items"]
        ],
        "example_tags": [f"use_case:{row['use_case']}", f"type:{row['type']}"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ids", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--source", type=Path, help="local copy of the pinned file")
    args = parser.parse_args()
    data = args.source.read_bytes() if args.source else urllib.request.urlopen(URL).read()
    digest = hashlib.sha256(data).hexdigest()
    if digest != SHA256:
        raise SystemExit(f"sha256 mismatch: got {digest}, expected {SHA256}")
    ids = args.ids.read_text().split()
    # Split on "\n" only: records contain U+2028, which splitlines() also breaks on.
    lines = [line for line in data.decode().split("\n") if line.strip()]
    rows = {r["id"]: r for r in map(json.loads, lines)}
    missing = [i for i in ids if i not in rows]
    if missing:
        raise SystemExit(f"{len(missing)} ids not in the dataset, e.g. {missing[0]}")
    with args.out.open("w") as f:
        for i in ids:
            f.write(json.dumps(to_healthbench(rows[i])) + "\n")
    print(f"wrote {len(ids)} examples to {args.out}")


if __name__ == "__main__":
    main()
