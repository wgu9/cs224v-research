#!/usr/bin/env python3
import pathlib, subprocess, json, csv

RUNS = ["r42","r50","r51","r52","r53"]

def run(cmd):
    print("$", cmd); subprocess.check_call(cmd, shell=True)

def main():
    rows = []
    for rid in RUNS:
        rd = pathlib.Path(f"data/runs/{rid}")
        if not rd.exists(): 
            print("Skip", rid); 
            continue
        run(f"python tools/patch2events.py {rd}")
        if (rd/'raw'/'term.log').exists():
            run(f"python tools/term2events.py {rd}")
        run(f"python tools/events2guards.py {rd}")
        guards = [json.loads(l) for l in open(rd/'guards.jsonl','r',encoding='utf-8')]
        for g in guards:
            rows.append([rid, g['step'], g.get('file',''), g['drift_score'], g['action'], g.get('auto_fixable',False), g.get('fix_cmd','')])
    out = pathlib.Path("data/eval/guards_summary.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["run_id","step","file","drift_score","action","auto_fixable","fix_cmd"])
        w.writerows(rows)
    print("Wrote", out)

if __name__ == "__main__":
    main()
