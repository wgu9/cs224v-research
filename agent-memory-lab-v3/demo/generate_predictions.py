"""
生成 SWE-bench Evaluator 所需的 predictions.jsonl（含自动基线对齐与校验）

用途
- 读取 data/swebench/verified.jsonl 中的任务，调用 Agent 生成补丁，
  并在“基线代码”（repo@base_commit）上自动对齐后再写出 predictions.jsonl。
- 目标是最大限度避免在 evaluator 阶段出现 “Hunk FAILED”。

快速开始
- 基本用法（自动浅拉取 + 对齐 + 重导出，默认开启）
  python generate_predictions.py

- 指定任务索引与更大上下文
  python generate_predictions.py --task_index 0 --unified 10

- 使用数据集 gold 补丁（环境/流程自检）
  python generate_predictions.py --use_gold true

输出
- logs/predictions.jsonl 生成的预测文件（每行包含 instance_id / model_patch / model_name_or_path）。
- 失败时会写 logs/bad_patch.diff，便于排查补丁上下文不匹配。

主要参数（可组合）
- --task_index int      选择 verified.jsonl 中的第几个任务（0-based，默认 0）。
- --use_gold bool       使用数据集提供的金标准补丁，跳过模型生成与自动对齐（默认 false）。
- --auto_clone bool     自动浅拉取 repo@base_commit 并在基线工作树内应用 & 重导出补丁（默认 true）。
- --cache_dir path      镜像缓存目录（默认 ~/.cache/swebench_repos）。
- --work_dir path       临时工作树目录（默认 /tmp/swebench_work）。
- --unified int         git diff 的上下文行数（默认 3，可调大如 8~10 提升容器端匹配稳定性）。

兼容参数（可选预检）
- --enforce_precheck bool  若提供 --local_repo，则在本地仓库上执行 git apply --check 作为额外预检（默认 false）。
- --local_repo path        本地 git 仓库路径（仅当你已有仓库镜像时使用；常规无需提供）。

注意
- 需要本机安装 git；当 --auto_clone 为 true 时需要网络以浅拉取指定 commit。
- 若你仅想验证 evaluator 环境，建议使用 --use_gold true；若要评测 Agent 真正能力，建议保留自动对齐（默认）。
"""

from pathlib import Path
import os
import re
import subprocess
import tempfile
import argparse
import shutil
import re
from steps import load_task
from utils import SimpleBedrockAgent, prepare_predictions

# Auto clone + worktree cache defaults
DEFAULT_CACHE_DIR = Path(os.getenv("Q1_REPO_CACHE", str(Path.home() / ".cache/swebench_repos")))
DEFAULT_WORK_DIR = Path(os.getenv("Q1_WORK_DIR", "/tmp/swebench_work"))


def _check_unified_diff_format(patch: str) -> None:
    """严格校验统一 diff 基本格式；不修改补丁，失败即抛错。

    - 必须包含 diff --git / --- a/ / +++ b/ / 至少一个 @@ hunk
    - @@ 之后的行，只能以 ' ', '+', '-' 开头；允许特殊行 "\\ No newline at end of file"
    - 补丁末尾必须有换行
    """
    if not patch:
        raise ValueError("Empty patch")

    if not patch.endswith("\n"):
        raise ValueError("Patch must end with a newline")

    lines = patch.splitlines()

    if not any(l.startswith("diff --git ") for l in lines):
        raise ValueError("Missing 'diff --git' header")
    if not any(l.startswith("--- a/") for l in lines):
        raise ValueError("Missing '--- a/...' file header")
    if not any(l.startswith("+++ b/") for l in lines):
        raise ValueError("Missing '+++ b/...' file header")
    if not any(l.startswith("@@ ") for l in lines):
        raise ValueError("Missing '@@' hunk header")

    in_hunk = False
    for idx, l in enumerate(lines, start=1):
        if l.startswith("@@ "):
            in_hunk = True
            continue
        if l.startswith("diff --git ") or l.startswith("--- a/") or l.startswith("+++ b/") or l.startswith("index "):
            # 这些是头部行，重置 hunk 状态
            in_hunk = False
            continue
        if in_hunk:
            if l.startswith(" ") or l.startswith("+") or l.startswith("-"):
                continue
            if l.startswith("\\ No newline at end of file"):
                # 统一 diff 特殊标记
                continue
            raise ValueError(f"Invalid diff content at line {idx}: must start with ' ', '+' or '-' inside hunk")


def _optional_git_apply_check(patch: str, repo_dir: Path, base_commit: str) -> None:
    """可选：在本地 Git 仓库上验证补丁是否可应用（不联网）。

    使用条件：
      - 环境变量 Q1_VALIDATE_PATCH_GIT=1
      - repo_dir 存在且是一个 git 工作区（用户自行准备该仓库的本地镜像）
    """
    if os.getenv("Q1_VALIDATE_PATCH_GIT") != "1":
        return
    if not repo_dir.exists() or not (repo_dir / ".git").exists():
        raise RuntimeError(f"Q1_VALIDATE_PATCH_GIT=1 but repo_dir not found or not a git repo: {repo_dir}")

    # 将补丁写入临时文件，使用 git apply --check 校验
    with tempfile.TemporaryDirectory() as td:
        tmp_patch = Path(td) / "patch.diff"
        tmp_patch.write_text(patch)

        # 保存并切换到 base_commit，校验后尽力切回
        def _run(cmd):
            return subprocess.run(cmd, cwd=str(repo_dir), capture_output=True, text=True)

        head = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip() or _run(["git", "rev-parse", "HEAD"]).stdout.strip()
        try:
            r1 = _run(["git", "checkout", "-f", base_commit])
            if r1.returncode != 0:
                raise RuntimeError(f"git checkout base_commit failed: {r1.stderr}")

            r2 = _run(["git", "apply", "--check", str(tmp_patch)])
            if r2.returncode != 0:
                raise RuntimeError(f"git apply --check failed:\n{r2.stderr}\n{r2.stdout}")
        finally:
            if head:
                _run(["git", "checkout", "-f", head])


def _run(cmd, cwd: Path | None = None):
    """Run a command, raising a helpful error on failure."""
    p = subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(cmd)}\nCWD: {cwd}\nSTDOUT:\n{p.stdout}\nSTDERR:\n{p.stderr}"
        )
    return p.stdout


def _ensure_repo_mirror(repo_slug: str, cache_dir: Path) -> Path:
    """Ensure a bare mirror exists for the given GitHub slug (owner/repo)."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    mirror = cache_dir / (repo_slug.replace("/", "__") + ".git")
    if not mirror.exists():
        url = f"https://github.com/{repo_slug}.git"
        _run(["git", "clone", "--mirror", url, str(mirror)])
    else:
        _run(["git", "remote", "update"], cwd=mirror)
    return mirror


def _ensure_worktree_at_commit(mirror: Path, base_commit: str, work_dir: Path) -> Path:
    """Create a fresh detached worktree at base_commit under work_dir and return its path."""
    work_dir.mkdir(parents=True, exist_ok=True)
    wt = work_dir / f"wt_{base_commit[:12]}_{next(tempfile._get_candidate_names())}"
    if wt.exists():
        shutil.rmtree(wt)
    # make sure commit is present locally
    _run(["git", "fetch", "origin", base_commit], cwd=mirror)
    _run(["git", "worktree", "add", "--detach", str(wt), base_commit], cwd=mirror)
    return wt


def _apply_and_rediff(patch: str, wt: Path, unified: int = 3) -> str:
    """Apply patch to worktree (staged) and return a normalized git diff string."""
    with tempfile.TemporaryDirectory() as td:
        pfile = Path(td) / "patch.diff"
        pfile.write_text(patch)
        _run(["git", "apply", "--index", str(pfile)], cwd=wt)
        diff = _run(["git", "diff", "--staged", f"--unified={unified}"], cwd=wt)
        if not diff:
            raise RuntimeError("Rediff produced empty diff (no changes detected)")
        diff = diff.replace("\r\n", "\n").replace("\r", "\n")
        if not diff.endswith("\n"):
            diff += "\n"
        return diff


# =============== Target file inference helpers ===============
_TEST_RE = re.compile(r"([\w/\.-]+/tests?/test[_-][\w\.-]+\.py)")
_SYM_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]{3,})\b")


def _extract_paths_from_patch(patch_text: str) -> list:
    """Parse unified diff text and collect file paths from '+++ b/...'."""
    files = []
    for line in (patch_text or "").splitlines():
        if line.startswith("+++ b/"):
            files.append(line[len("+++ b/") :].strip())
    # dedupe preserving order
    seen, out = set(), []
    for f in files:
        if f and f not in seen:
            seen.add(f)
            out.append(f)
    return out


def _guess_from_tests(problem_statement: str) -> list:
    """Infer source paths from test file paths by common conventions."""
    cands = []
    for m in _TEST_RE.finditer(problem_statement or ""):
        t = m.group(1)
        # pkg/foo/tests/test_bar.py -> pkg/foo/bar.py
        cand = t.replace("/tests/", "/").replace("/test_", "/").replace("/test-", "/")
        cands.append(cand)
    # dedupe
    seen, out = set(), []
    for f in cands:
        if f and f not in seen:
            seen.add(f)
            out.append(f)
    return out


def _guess_by_symbols(worktree: Path, problem_statement: str, topk: int = 3) -> list:
    """Score .py files by presence of symbols (functions/classes/keywords)."""
    if not problem_statement:
        return []
    symbols = [s for s in _SYM_RE.findall(problem_statement) if not s.isupper()]
    # limit and dedupe
    symbols = list(dict.fromkeys(symbols))[:20]
    scores = {}
    for p in worktree.rglob("*.py"):
        try:
            txt = p.read_text(errors="ignore")
        except Exception:
            continue
        sc = 0
        for s in symbols:
            if f"def {s}(" in txt or f"class {s}(" in txt:
                sc += 5
            if s in txt:
                sc += 1
        if sc:
            rel = str(p.relative_to(worktree))
            scores[rel] = sc
    return [k for k, _ in sorted(scores.items(), key=lambda kv: -kv[1])[:topk]]


def infer_target_files(task, worktree: Path, agent=None, allow_agent_diff: bool = True) -> list:
    """Infer target files with priority: gold > agent diff > tests > symbols."""
    cands = []
    # 1) Gold (Verified) — only extract file list
    gold_patch = getattr(task, "ground_truth_patch", None)
    if gold_patch:
        cands += _extract_paths_from_patch(gold_patch)

    # 2) Agent diff (if allowed)
    if not cands and allow_agent_diff and agent is not None:
        try:
            diff = agent.solve(task)  # only used to extract file names
            cands += _extract_paths_from_patch(diff)
        except Exception:
            pass

    # 3) From tests
    if not cands:
        cands += _guess_from_tests(getattr(task, "problem_statement", "") or "")

    # 4) Symbol search
    if not cands:
        cands += _guess_by_symbols(worktree, getattr(task, "problem_statement", "") or "")

    # Filter to existing files and dedupe
    seen, out = set(), []
    for rel in cands:
        rel = rel.strip().lstrip("./")
        if rel and (worktree / rel).exists() and rel not in seen:
            seen.add(rel)
            out.append(rel)
    return out


def main():
    """生成 1 个任务的 predictions.jsonl（写出前做严格校验）"""
    # CLI 参数：允许指定本地仓库与任务索引，并强制启用 git 预检
    parser = argparse.ArgumentParser(description="Generate predictions.jsonl with strict git precheck")
    parser.add_argument("--task_index", type=int, default=0, help="Task index in verified.jsonl (0-based)")
    parser.add_argument(
        "--full_file_mode",
        type=lambda x: str(x).lower() in {"1", "true", "yes", "y"},
        default=False,
        help="Use full-file rewrite: fetch baseline, get originals, ask Agent to return full new files, then git diff",
    )
    parser.add_argument(
        "--target_files",
        type=str,
        default="",
        help="Comma-separated relative paths to files to rewrite (required for --full_file_mode if agent cannot infer)",
    )
    parser.add_argument(
        "--auto_clone",
        type=lambda x: str(x).lower() in {"1", "true", "yes", "y"},
        default=True,
        help="Automatically fetch repo@base_commit and re-diff patch against baseline",
    )
    parser.add_argument("--cache_dir", type=str, default=str(DEFAULT_CACHE_DIR), help="Repo mirror cache directory")
    parser.add_argument("--work_dir", type=str, default=str(DEFAULT_WORK_DIR), help="Transient worktrees directory")
    parser.add_argument("--unified", type=int, default=3, help="git diff context lines when re-diffing")
    parser.add_argument(
        "--use_gold",
        type=lambda x: str(x).lower() in {"1", "true", "yes", "y"},
        default=False,
        help="If true, emit the dataset gold patch instead of model output (for pipeline sanity checks)",
    )
    parser.add_argument(
        "--local_repo",
        type=str,
        default=os.getenv("Q1_LOCAL_REPO_PATH", ""),
        help="Path to a local git clone of the target repo (checked out to base commit during precheck)",
    )
    parser.add_argument(
        "--enforce_precheck",
        type=lambda x: str(x).lower() in {"1", "true", "yes", "y"},
        default=False,
        help="If true AND --local_repo is provided, run git apply --check before writing predictions",
    )
    args = parser.parse_args()

    print("=" * 80)
    print("Generating predictions.jsonl for SWE-bench Evaluator (with strict patch validation)")
    print("=" * 80)

    # Load task
    data_file = Path(__file__).parent.parent / "data" / "swebench" / "verified.jsonl"
    task = load_task(data_file, task_index=args.task_index)
    print(f"\n✅ Task loaded: {task.instance_id}")
    print(f"   Repo: {task.repo}")
    print(f"   Base commit: {task.base_commit[:12]}...")

    # Generate patch (from real agent or gold)
    if args.use_gold:
        patch = task.ground_truth_patch
        print(f"✅ Using GOLD patch from dataset ({len(patch)} characters)")
    else:
        agent = SimpleBedrockAgent(require_token=False)
        if args.full_file_mode:
            # Full-file rewrite pipeline
            try:
                mirror = _ensure_repo_mirror(task.repo, Path(args.cache_dir))
                wt = _ensure_worktree_at_commit(mirror, task.base_commit, Path(args.work_dir))
                try:
                    # Determine target files: gold -> agent diff -> tests -> symbols
                    targets = [p.strip() for p in args.target_files.split(",") if p.strip()]
                    if not targets:
                        targets = infer_target_files(task, wt, agent=agent, allow_agent_diff=not args.use_gold)
                    if not targets:
                        raise SystemExit("❌ --full_file_mode 需要提供 --target_files，或让模型先吐一个包含目标文件的 diff。")

                    originals = {}
                    for rel in targets:
                        fpath = wt / rel
                        if not fpath.exists():
                            raise SystemExit(f"❌ Target file not found in baseline: {rel}")
                        originals[rel] = fpath.read_text()

                    # Ask agent for full new files (requires real model token)
                    new_files = agent.produce_new_files(task, originals)
                    # Write new files into worktree and create diff
                    for rel, text in new_files.items():
                        abs_f = wt / rel
                        abs_f.parent.mkdir(parents=True, exist_ok=True)
                        if text and not text.endswith("\n"):
                            text += "\n"
                        abs_f.write_text(text or "")
                    # Stage and diff
                    _run(["git", "add", "-A"], cwd=wt)
                    patch = _run(["git", "diff", "--staged", f"--unified={args.unified}"], cwd=wt)
                    if not patch.strip():
                        raise SystemExit("❌ Full-file rewrite produced empty diff (no changes)")
                    if not patch.endswith("\n"):
                        patch += "\n"
                    print(f"✅ Full-file rewrite produced diff ({len(patch)} characters)")
                finally:
                    try:
                        _run(["git", "worktree", "remove", "--force", str(wt)], cwd=mirror)
                    except Exception:
                        shutil.rmtree(wt, ignore_errors=True)
            except Exception as e:
                bad = Path("logs/bad_patch.diff")
                bad.parent.mkdir(parents=True, exist_ok=True)
                bad.write_text(str(e))
                raise SystemExit(f"❌ Full-file rewrite failed: {e}\nSaved error to: {bad}")
        else:
            patch = agent.solve(task)
            print(f"✅ Patch generated ({len(patch)} characters)")

    # Strict validation (format)
    try:
        _check_unified_diff_format(patch)
    except Exception as e:
        bad = Path("logs/bad_patch.diff")
        bad.parent.mkdir(parents=True, exist_ok=True)
        bad.write_text(patch)
        raise SystemExit(f"❌ Patch format invalid: {e}\nSaved to: {bad}\nPlease fix the agent to output strict unified diff.")

    # Auto clone + apply + re-diff against baseline (preferred; skips for gold or full-file mode which already produced baseline diff)
    if (not args.use_gold) and (not args.full_file_mode) and args.auto_clone:
        try:
            mirror = _ensure_repo_mirror(task.repo, Path(args.cache_dir))
            wt = _ensure_worktree_at_commit(mirror, task.base_commit, Path(args.work_dir))
            try:
                patch = _apply_and_rediff(patch, wt, unified=args.unified)
                print("✅ Patch re-diffed against baseline (auto_clone)")
            finally:
                # clean worktree
                try:
                    _run(["git", "worktree", "remove", "--force", str(wt)], cwd=mirror)
                except Exception:
                    shutil.rmtree(wt, ignore_errors=True)
        except Exception as e:
            bad = Path("logs/bad_patch.diff")
            bad.parent.mkdir(parents=True, exist_ok=True)
            bad.write_text(patch)
            raise SystemExit(
                f"❌ Auto clone + re-diff failed: {e}\nSaved patch to: {bad}\n"
                f"Repo: {task.repo} @ {task.base_commit}"
            )

    # Enforced: validate with git apply --check on local repo mirror (early failure if not provided or invalid)
    if args.enforce_precheck:
        if not args.local_repo:
            print(
                "⚠️  Precheck requested but --local_repo not provided. Skipping git precheck.\n"
                "    To enable, pass --local_repo /path/to/clone or set Q1_LOCAL_REPO_PATH."
            )
        else:
            repo_path = Path(args.local_repo)
            if not (repo_path.exists() and (repo_path / ".git").exists()):
                print(f"⚠️  Invalid --local_repo: {repo_path} (not a git repo). Skipping git precheck.")
            else:
                # Force-enable the optional checker by environment to reuse existing function
                os.environ["Q1_VALIDATE_PATCH_GIT"] = "1"
                try:
                    _optional_git_apply_check(patch, repo_path, task.base_commit)
                    print("✅ git apply --check passed on local repo mirror")
                except Exception as e:
                    bad = Path("logs/bad_patch.diff")
                    bad.parent.mkdir(parents=True, exist_ok=True)
                    bad.write_text(patch)
                    raise SystemExit(
                        f"❌ Patch cannot be applied on local repo mirror: {e}\n"
                        f"Repo path: {repo_path}\nSaved patch to: {bad}"
                    )

    # Prepare predictions (write JSONL)
    output_file = Path("logs/predictions.jsonl")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    prepare_predictions(tasks=[task], patches=[patch], output_file=output_file)
    print(f"\n✅ Predictions saved to: {output_file}")

    # Preview first line of JSONL (not json.load)
    import json
    with open(output_file, "r") as f:
        first = f.readline()
        try:
            preview = json.loads(first)
        except Exception:
            raise SystemExit("❌ Written predictions.jsonl is not valid JSONL (first line parse failed)")

    print("\n📝 Predictions preview (first line):")
    print("-" * 80)
    print(f"instance_id: {preview.get('instance_id')}")
    print(f"model_patch: {str(preview.get('model_patch',''))[:200]}...")
    print(f"model_name_or_path: {preview.get('model_name_or_path')}")
    print("-" * 80)

    print("\n💡 Next step: Run official SWE-bench evaluator")
    print("   python -m swebench.harness.run_evaluation -d princeton-nlp/SWE-bench_Verified \\")
    print(f"      -p {output_file} --max_workers 1 -i {task.instance_id} \\")
    print("      --report_dir /path/to/eval_results -id run-001")

    return output_file


if __name__ == "__main__":
    main()
