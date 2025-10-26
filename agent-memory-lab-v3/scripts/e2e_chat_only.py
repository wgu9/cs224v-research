#!/usr/bin/env python3
"""
A simple end-to-end script for running Q1 analysis on a single, manually 
prepared run directory.

This script is a simple wrapper that calls `chat2events` and `events2guards` 
for a given run ID. It is useful for quick, individual tests but has been 
largely superseded by the more powerful `tools/run_q1_batch.py` for the 
standard workflow.
"""
import sys, pathlib, subprocess, json

def run(cmd):
    print("$", cmd); subprocess.check_call(cmd, shell=True)

def main(run_id: str):
    rd = pathlib.Path(f"data/runs/{run_id}")
    assert rd.exists(), f"run {run_id} not found"
    run(f"python -m tools.chat2events {rd}")
    run(f"python -m tools.events2guards {rd}")
    guards = [json.loads(l) for l in open(rd/'guards.jsonl','r',encoding='utf-8')]
    print("\n== Drift Summary ==")
    for g in guards:
        if g['action'] != 'ok':
            print(f"[{run_id}] step={g['step']} file={g.get('file')} drift={g['drift_score']:.2f} action={g['action']} auto_fix={g['auto_fixable']} notes={g.get('notes','')}")
    print("Done. Guards written to", rd/'guards.jsonl')

if __name__ == "__main__":
    rid = sys.argv[1] if len(sys.argv)>1 else "r60"
    main(rid)
