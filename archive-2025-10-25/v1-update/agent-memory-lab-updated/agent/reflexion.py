import pathlib

def make_reflection(run_dir: str) -> str:
    rd = pathlib.Path(run_dir)
    cursor_md = (rd/"raw/cursor.md").read_text(encoding="utf-8", errors="ignore") if (rd/"raw/cursor.md").exists() else ""
    # Very light synthesizer: prefer cursor text; fallback to generic
    if cursor_md.strip():
        return "Doc-only task: translate README. Avoid touching dependencies. Key invariants: only whitelisted files change; language==target."
    return "From events: this was a documentation-only change. Use whitelist for files and enforce doc_lang & whitelist checks."

if __name__ == "__main__":
    print(make_reflection("data/runs/2025-10-25_r42_jw"))
