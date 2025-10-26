#!/usr/bin/env python3
import sys, pathlib, subprocess, json, csv

def run(cmd):
    print("$", cmd); subprocess.check_call(cmd, shell=True)

def main(run_id: str):
    rd = pathlib.Path(f"data/runs/{run_id}")
    assert rd.exists(), f"run {run_id} not found"
    run(f"python tools/patch2events.py {rd}")
    term = rd/'raw'/'term.log'
    if term.exists():
        run(f"python tools/term2events.py {rd}")
    run(f"python tools/events2guards.py {rd}")
    guards = [json.loads(l) for l in open(rd/'guards.jsonl','r',encoding='utf-8')]
    print("\n== Drift Summary ==")
    for g in guards:
        if g['action'] != 'ok':
            print(f"[{run_id}] step={g['step']} file={g.get('file')} drift={g['drift_score']:.2f} action={g['action']} auto_fix={g['auto_fixable']}")
    print("Done. Guards written to", rd/'guards.jsonl')

if __name__ == "__main__":
    rid = sys.argv[1] if len(sys.argv)>1 else "r42"
    main(rid)
