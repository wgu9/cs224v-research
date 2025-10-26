import fnmatch, os, re, hashlib
from typing import List

IGNORE_PREFIXES = ('.git/', 'venv/', 'node_modules/')

def norm(path: str) -> str:
    path = path.replace('\\', '/')
    while '//' in path:
        path = path.replace('//','/')
    if path.startswith('./'):
        path = path[2:]
    return path

def in_allowed(path: str, allowed_patterns: List[str]) -> bool:
    p = norm(path)
    if any(p.startswith(x) for x in IGNORE_PREFIXES):
        return False
    if not allowed_patterns:
        return False
    for pat in allowed_patterns:
        pat = norm(pat)
        if fnmatch.fnmatch(p, pat):
            return True
    return False

def is_forbidden(path: str, forbidden_patterns: List[str]) -> bool:
    p = norm(path)
    for pat in forbidden_patterns or []:
        pat = norm(pat)
        if fnmatch.fnmatch(p, pat):
            return True
    return False

# Pytest parsing (kept for term.log and summary parsing, if needed elsewhere)
PYTEST_PASS_RE = re.compile(r"=+\s*(\d+) passed.*=+")
PYTEST_FAIL_RE = re.compile(r"=+\s*(\d+) failed.*=+")
PYTEST_COLLECT_RE = re.compile(r"collected\s+(\d+)\s+items")

def parse_pytest_summary(text: str):
    passed = 0; failed = 0; collected = None
    m = PYTEST_PASS_RE.search(text)
    if m: passed = int(m.group(1))
    m = PYTEST_FAIL_RE.search(text)
    if m: failed = int(m.group(1))
    m = PYTEST_COLLECT_RE.search(text)
    if m: collected = int(m.group(1))
    return {'passed': passed, 'failed': failed, 'collected': collected}

def sha1_short(s: str) -> str:
    return hashlib.sha1(s.encode('utf-8', 'ignore')).hexdigest()[:10]
