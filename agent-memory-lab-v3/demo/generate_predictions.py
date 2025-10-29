"""
生成 predictions.jsonl（在写出前对补丁做根因级校验）
"""

from pathlib import Path
import os
import re
import subprocess
import tempfile
from steps import load_task
from utils import SimpleBedrockAgent, prepare_predictions


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


def main():
    """生成 1 个任务的 predictions.jsonl（写出前做严格校验）"""
    print("=" * 80)
    print("Generating predictions.jsonl for SWE-bench Evaluator (with strict patch validation)")
    print("=" * 80)

    # Load task
    data_file = Path(__file__).parent.parent / "data" / "swebench" / "verified.jsonl"
    task = load_task(data_file, task_index=0)
    print(f"\n✅ Task loaded: {task.instance_id}")
    print(f"   Repo: {task.repo}")
    print(f"   Base commit: {task.base_commit[:12]}...")

    # Generate patch (from real agent or mock)
    agent = SimpleBedrockAgent(require_token=False)
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

    # Optional: validate with git apply --check on local repo mirror
    local_repo_env = os.getenv("Q1_LOCAL_REPO_PATH")  # e.g., a local clone of astropy checkout
    if local_repo_env:
        try:
            _optional_git_apply_check(patch, Path(local_repo_env), task.base_commit)
            print("✅ git apply --check passed on local repo mirror")
        except Exception as e:
            bad = Path("logs/bad_patch.diff")
            bad.parent.mkdir(parents=True, exist_ok=True)
            bad.write_text(patch)
            raise SystemExit(
                f"❌ Patch cannot be applied on local repo mirror: {e}\n"
                f"Repo path: {local_repo_env}\nSaved patch to: {bad}"
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
