#!/usr/bin/env python3
"""
Converts a chat log into a structured sequence of events (`events.jsonl`).

This script reads a `cursor.md` file from a run directory and uses heuristics
(or a `RUNLOG` YAML block) to identify actions like editing files, planning
steps, and running tests. It is a key part of the Q1 analysis pipeline.

**LLM Usage**: ❌ NO LLM CALLS
  - Uses regex patterns and heuristics only
  - Extracts file paths, actions, and test commands from text
  - Optionally uses git diff if CHAT2EVENTS_GIT_ROOT is set (still no LLM)

**New Fields Added** (code-inferred, not LLM):
  - operation: 'read' | 'write' | 'run' | 'plan'
  - artifact_type: 'code' | 'test' | 'doc' | 'config'
  - scope: 'file' | 'multi_file'

**Usage**: Run with runner.sh
  ./runner.sh python tools/chat2events.py data/2_runs/<run_id>
"""
import sys, json, pathlib, uuid, datetime, os, re
from typing import List, Dict, Any, Optional
import yaml

APPLIED_HINTS = re.compile(r"""\b(
    i\s*(have|'ve)?\s*(applied|updated|modified|changed|fixed|edited|refactored|committed|added|removed|created|deleted)
   |已(修改|更新|修复|添加|删除|应用)
   |done\s*
)\b""", re.IGNORECASE | re.X)

PLANNED_HINTS = re.compile(r"""\b(
    will|would|plan|should|could|propose|suggest|let\'s|let us|可以|将要|计划|建议|打算
)\b""", re.IGNORECASE | re.X)

TEST_CMD_RE = re.compile(r"""\b(
    pytest\s+[^\n]*|npm\s+test[^\n]*|yarn\s+test[^\n]*|go\s+test[^\n]*|mvn\s+test[^\n]*|tox[^\n]*
)""", re.IGNORECASE | re.X)

PASSED_HINT = re.compile(r"\b(pass|passed|ok|成功)\b", re.IGNORECASE)
FAILED_HINT = re.compile(r"\b(fail|failed|错误|失败)\b", re.IGNORECASE)

# crude path pattern with common extensions
FILE_PATH_RE = re.compile(r"([A-Za-z0-9_./-]+\.(py|md|rst|txt|json|yaml|yml|ini|cfg|toml|lock|ts|js|tsx|jsx|css|html))\b" )

def infer_artifact_type(path: str) -> str:
    """Infer artifact type from file extension."""
    path_lower = path.lower()

    # Test files (check first, before general code)
    if any(pattern in path_lower for pattern in ['test_', '_test.', '.test.', '.spec.', 'test/', '/tests/']):
        return 'test'

    # Documentation
    if path_lower.endswith(('.md', '.rst', '.txt', '.adoc')):
        return 'doc'

    # Configuration
    if path_lower.endswith(('.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.env', '.lock', '.config')):
        return 'config'

    # Code (default for common extensions)
    if path_lower.endswith(('.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.java', '.cpp', '.c', '.rs', '.rb', '.php', '.swift', '.kt', '.cs', '.html', '.css')):
        return 'code'

    return 'code'  # default

def infer_operation(tool: str) -> str:
    """Infer operation from tool type."""
    if tool == 'edit':
        return 'write'
    elif tool == 'plan':
        return 'plan'
    elif tool == 'shell':
        return 'run'
    elif tool == 'browse':
        return 'read'
    else:
        return 'write'  # default

def find_runlog_block(text: str) -> Optional[str]:
    # detect fenced YAML runlog starting with 'RUNLOG:'
    m = re.search(r"RUNLOG:\s*(\n|\r|\r\n)([\s\S]+)", text, re.IGNORECASE)
    if not m:
        return None
    block = m.group(2)
    # cut at next triple backticks if present
    fence = re.search(r"```", block)
    if fence:
        block = block[:fence.start()]
    return "RUNLOG:\n" + block.strip()

def parse_runlog_yaml(runlog_text: str) -> Optional[Dict[str, Any]]:
    try:
        data = yaml.safe_load(runlog_text)
        if isinstance(data, dict) and 'RUNLOG' in data:
            return data['RUNLOG']
    except Exception:
        pass
    return None

def window(lines: List[str], idx: int, span: int = 2) -> str:
    lo = max(0, idx - span); hi = min(len(lines), idx + span + 1)
    return "\n".join(lines[lo:hi])

def extract_from_chat(chat_md: str) -> Dict[str, Any]:
    # 1) Try RUNLOG YAML
    rl = find_runlog_block(chat_md)
    if rl:
        data = parse_runlog_yaml(rl)
        if data and isinstance(data, dict):
            changes = []
            for ch in data.get('changes') or []:
                if not isinstance(ch, dict): 
                    continue
                p = ch.get('path') or ''
                if not p: 
                    continue
                action = (ch.get('action') or 'edit').lower()
                changes.append({
                    'action': action,
                    'path': p,
                    'rationale': ch.get('rationale',''),
                    'status': 'applied',             # RUNLOG 默认视为已实施
                    'confidence': 'high'
                })
            tests = data.get('tests') or {}
            return {
                'objective': data.get('objective',''),
                'changes': changes,
                'tests': {
                    'ran': tests.get('ran') or [],
                    'passed': tests.get('passed', None)
                },
                'confidence': 'high',
                'source': 'runlog'
            }

    # 2) Heuristic extraction from natural chat
    lines = chat_md.splitlines()
    files = []
    for i, ln in enumerate(lines):
        for m in FILE_PATH_RE.finditer(ln):
            files.append((i, m.group(1)))
    # unique preserve order
    seen = set(); files_unique = []
    for i, p in files:
        if p not in seen:
            seen.add(p); files_unique.append((i, p))

    # Determine applied/planned per file by local context window
    changes = []
    for i, p in files_unique:
        ctx = window(lines, i, 2)
        # default
        status = 'planned'; confidence = 'medium'
        action = 'edit'
        rationale = ''

        if APPLIED_HINTS.search(ctx):
            status = 'applied'; confidence = 'high'
        elif PLANNED_HINTS.search(ctx):
            status = 'planned'; confidence = 'medium'
        else:
            status = 'planned'; confidence = 'low'

        if re.search(r"\b(create|新增|新建|add\s+new)\b", ctx, re.IGNORECASE):
            action = 'create'
        if re.search(r"\b(delete|remove|删|移除)\b", ctx, re.IGNORECASE):
            action = 'delete'
        if re.search(r"\brefactor|重构\b", ctx, re.IGNORECASE):
            action = 'edit'

        # rationale: simple grab sentence after filename
        rationale = ctx.strip().split('\n')[-1][:200]

        changes.append({'action': action, 'path': p, 'rationale': rationale, 'status': status, 'confidence': confidence})

    # Tests
    tests_cmds = TEST_CMD_RE.findall(chat_md)
    passed = None
    if tests_cmds:
        # Look around the last occurrence for pass/fail hints
        last_idx = chat_md.lower().rfind(tests_cmds[-1].lower())
        around = chat_md[max(0,last_idx-200): last_idx+200]
        if FAILED_HINT.search(around): passed = False
        elif PASSED_HINT.search(around): passed = True

    return {
        'objective': '',  # could be inferred but optional
        'changes': changes,
        'tests': {'ran': tests_cmds, 'passed': passed},
        'confidence': 'medium' if changes else 'low',
        'source': 'chat-heuristic'
    }

def maybe_git_verify(extracted: Dict[str, Any], git_root: Optional[str]) -> Dict[str, Any]:
    need = (extracted.get('confidence') == 'low' or len(extracted.get('changes',[])) == 0)
    if not need or not git_root:
        return extracted
    try:
        out = subprocess.check_output(['git','-C', git_root, 'diff','--name-only'], stderr=subprocess.STDOUT)
        files = [ln.strip() for ln in out.decode('utf-8','ignore').splitlines() if ln.strip()]
        existing = {c['path'] for c in extracted.get('changes',[])}
        for f in files:
            if f not in existing:
                extracted.setdefault('changes',[]).append({'action':'edit','path':f,'rationale':'git-verify','status':'applied','confidence':'low'})
        extracted['confidence'] = 'low'
    except Exception:
        pass
    return extracted

def changes_to_events(run_id: str, changes: List[Dict[str,Any]]) -> List[Dict[str,Any]]:
    evs = []; step = 0
    total_files = len(changes)
    scope = 'file' if total_files == 1 else 'multi_file'

    for ch in changes:
        status = ch.get('status','planned')
        tool = 'edit' if status=='applied' else 'plan'
        path = ch.get('path', '')

        step += 1
        evs.append({
            "id": str(uuid.uuid4()),
            "run_id": run_id,
            "step": step,
            "ts": datetime.datetime.utcnow().isoformat() + "Z",
            "phase": "modify",
            "tool": tool,
            "where": {"path": path},
            "what": {"diff": "(from chat)"},
            "why": ch.get('rationale',''),
            "confidence": ch.get('confidence','low'),

            # New fields (code-inferred)
            "operation": infer_operation(tool),
            "artifact_type": infer_artifact_type(path),
            "scope": scope
        })
    return evs

def tests_to_events(run_id: str, tests: Dict[str,Any]) -> List[Dict[str,Any]]:
    evs = []; step = 1000
    for i, cmd in enumerate(tests.get('ran') or []):
        evs.append({
            "id": str(uuid.uuid4()),
            "run_id": run_id,
            "step": step+i,
            "ts": datetime.datetime.utcnow().isoformat() + "Z",
            "phase": "test",
            "tool": "shell",
            "cmd": cmd,

            # New fields (code-inferred)
            "operation": "run",
            "artifact_type": "test",
            "scope": "file"
        })
    return evs

def main(run_dir: str):
    rd = pathlib.Path(run_dir)
    chat_path = rd/'raw'/'cursor.md'
    if not chat_path.exists():
        raise SystemExit(f"missing {chat_path}")
    goal = json.loads((rd/'goal.json').read_text(encoding='utf-8')) if (rd/'goal.json').exists() else {"run_id": rd.name}

    chat_md = chat_path.read_text(encoding='utf-8', errors='ignore')
    extracted = extract_from_chat(chat_md)

    # Optional git verification (set env CHAT2EVENTS_GIT_ROOT=/path/to/repo)
    git_root = os.environ.get('CHAT2EVENTS_GIT_ROOT')
    extracted = maybe_git_verify(extracted, git_root)

    # Build events
    events = changes_to_events(goal.get('run_id', rd.name), extracted.get('changes',[]))
    events += tests_to_events(goal.get('run_id', rd.name), extracted.get('tests',{}))

    # Write events.jsonl
    ev_path = rd/'events.jsonl'
    ev_path.write_text("", encoding="utf-8")
    with ev_path.open("a", encoding="utf-8") as fh:
        for ev in events:
            fh.write(json.dumps(ev, ensure_ascii=False)+"\n")
    # Also write a light reflection stub
    (rd/'artifacts').mkdir(parents=True, exist_ok=True)
    reflect = {
        "source": extracted.get('source'),
        "objective_guess": extracted.get('objective',''),
        "changed_files": [c.get('path') for c in extracted.get('changes',[])],
        "tests": extracted.get('tests',{}),
        "note": "stub reflection; replace with LLM-generated summary if needed"
    }
    (rd/'artifacts'/'reflection.txt').write_text(json.dumps(reflect, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Wrote {ev_path} and artifacts/reflection.txt")

def cli():
    if len(sys.argv) < 2:
        print("Usage: python -m tools.chat2events <run_directory>")
        sys.exit(1)
    main(sys.argv[1])

if __name__ == "__main__":
    cli()
