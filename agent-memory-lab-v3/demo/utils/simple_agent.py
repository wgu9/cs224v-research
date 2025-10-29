"""
Simple LLM Agent - 使用Bedrock API
并支持在本地仓库基线上应用补丁并用 git diff 重新导出，确保上下文对齐。
"""

import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from litellm import completion


def _run(cmd, cwd: Optional[Path] = None):
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
    )


def _apply_and_rediff_on_worktree(patch: str, repo_dir: Path, base_commit: str) -> str:
    """在 repo 的临时 worktree 上应用补丁，并用 git diff 导出标准统一 diff。

    - 创建临时 worktree（detached HEAD 到 base_commit）
    - git apply 补丁
    - git diff 导出补丁（确保上下文与基线一致）
    - 清理 worktree
    """
    if not (repo_dir.exists() and (repo_dir / ".git").exists()):
        raise RuntimeError(f"Not a git repo: {repo_dir}")

    with tempfile.TemporaryDirectory() as td:
        worktree = Path(td) / "wt"
        worktree.parent.mkdir(parents=True, exist_ok=True)

        # 添加临时 worktree，detached 到 base_commit
        r = _run(["git", "worktree", "add", "--detach", str(worktree), base_commit], cwd=repo_dir)
        if r.returncode != 0:
            raise RuntimeError(f"git worktree add failed: {r.stderr}\n{r.stdout}")

        try:
            # 将补丁写入临时文件
            tmp_patch = Path(td) / "patch.diff"
            tmp_patch.write_text(patch)

            # 尝试应用补丁
            r2 = _run(["git", "apply", "--index", str(tmp_patch)], cwd=worktree)
            if r2.returncode != 0:
                raise RuntimeError(f"git apply failed on worktree: {r2.stderr}\n{r2.stdout}")

            # 导出统一 diff（相对 HEAD/base_commit）
            r3 = _run(["git", "diff"], cwd=worktree)
            if r3.returncode != 0:
                raise RuntimeError(f"git diff failed: {r3.stderr}\n{r3.stdout}")

            normalized = r3.stdout.replace("\r\n", "\n").replace("\r", "\n")
            if not normalized.endswith("\n"):
                normalized += "\n"
            if not normalized.strip():
                raise RuntimeError("Rediff result is empty (no changes after applying patch)")
            return normalized
        finally:
            # 移除临时 worktree
            _run(["git", "worktree", "remove", "--force", str(worktree)], cwd=repo_dir)


class SimpleBedrockAgent:
    """
    最简化的Agent - 使用AWS Bedrock

    只用1个LLM调用生成patch，不需要工具调用
    """

    def __init__(self, require_token=True, local_repo: Optional[str] = None, use_git_rediff: bool = True):
        """初始化Agent"""
        # 检查环境变量
        self.has_token = bool(os.getenv('AWS_BEARER_TOKEN_BEDROCK'))

        if require_token and not self.has_token:
            raise ValueError(
                "Missing AWS_BEARER_TOKEN_BEDROCK environment variable. "
                "Please set: export AWS_BEARER_TOKEN_BEDROCK=..."
            )

        # Bedrock model; can be overridden via env Q1_BEDROCK_MODEL
        # Example IDs:
        # - Claude 3.5 Sonnet (2024-10, on-demand):
        #   "bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0"
        # - Global Claude Sonnet 4 (system-defined inference profile ARN):
        #   "bedrock/arn:aws:bedrock:us-west-2:339713039693:inference-profile/global.anthropic.claude-sonnet-4-20250514-v1:0"
        # - Claude Sonnet 4.5 (foundation model – requires an application/system inference profile):
        #   "bedrock/anthropic.claude-sonnet-4-5-20250929-v1:0"
        self.model = os.getenv(
            "Q1_BEDROCK_MODEL",
            "bedrock/arn:aws:bedrock:us-west-2:339713039693:inference-profile/global.anthropic.claude-sonnet-4-20250514-v1:0",
        )
        # 本地仓库（用于在基线上应用补丁并重新导出 diff）
        repo_env = os.getenv("Q1_LOCAL_REPO_PATH")
        self.local_repo = Path(local_repo) if local_repo else (Path(repo_env) if repo_env else None)
        if self.local_repo and not (self.local_repo.exists() and (self.local_repo / ".git").exists()):
            print(f"⚠️  Local repo path not valid or not a git repo: {self.local_repo}. Disabling git rediff.")
            self.local_repo = None
        # 允许通过环境变量开关重定diff
        env_use_rediff = os.getenv("Q1_USE_GIT_REDIFF")
        self.use_git_rediff = use_git_rediff if env_use_rediff is None else (env_use_rediff.lower() not in {"0", "false", "no"})

    def solve(self, task):
        """
        生成patch解决任务

        Args:
            task: SWEBenchTask对象

        Returns:
            patch: git diff格式的字符串
        """
        # 构造prompt
        prompt = f"""You are a software engineer fixing a bug.

Problem:
{task.problem_statement}

Repository: {task.repo}

Generate a git diff patch to fix this bug.
STRICT REQUIREMENTS:
- Output MUST be a valid unified git diff exactly as produced by `git diff`.
- Do NOT wrap in code fences. Do NOT include any explanation before or after.
- Each file diff MUST include headers:
  diff --git a/<path> b/<path>
  --- a/<path>
  +++ b/<path>
  @@ -<oldstart>,<oldlen> +<newstart>,<newlen> @@
- Within each hunk:
  - Unchanged context lines MUST start with a single space ' '.
  - Removed lines MUST start with '-'.
  - Added lines MUST start with '+'.
- Ensure the patch ENDS WITH A SINGLE NEWLINE.
- Only output the patch, nothing else.

Example (format only):
diff --git a/path/to/file.py b/path/to/file.py
--- a/path/to/file.py
+++ b/path/to/file.py
@@ -10,7 +10,7 @@ def function():
-    old line
+    new line
"""

        # 如果没有token，返回mock patch用于测试
        if not self.has_token:
            print("⚠️  No AWS token - returning mock patch for testing")
            mock = (
                "diff --git a/example/file.py b/example/file.py\n"
                "--- a/example/file.py\n"
                "+++ b/example/file.py\n"
                "@@ -10,7 +10,7 @@ def function():\n"
                "-    old implementation\n"
                "+    new implementation\n"
            )
            # 尝试在本地仓库上应用并 rediff（如果提供了 local_repo），否则直接返回 mock
            if self.use_git_rediff and self.local_repo:
                try:
                    return _apply_and_rediff_on_worktree(mock, self.local_repo, task.base_commit)
                except Exception as e:
                    print(f"❌ git rediff on mock failed: {e}")
            return mock

        try:
            # 调用Bedrock
            response = completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=int(os.getenv("Q1_PATCH_MAX_TOKENS", "2000")),
                temperature=float(os.getenv("Q1_LLM_TEMPERATURE", "0.1")),
            )

            # 提取并规范化 patch
            raw = response.choices[0].message.content or ""

            # 1) 去除代码围栏与多余说明，只保留从第一个 diff --git 开始
            text = raw.strip()
            if text.startswith("```"):
                # 移除首尾 ```/```diff 围栏
                text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
                text = re.sub(r"\n?```$", "", text)
            idx = text.find("diff --git ")
            if idx != -1:
                text = text[idx:]

            # 2) 标准化换行并强制末尾换行
            text = text.replace("\r\n", "\n").replace("\r", "\n")
            if not text.endswith("\n"):
                text += "\n"

            # 3) 基本头部存在性检查（早失败，便于定位）
            if "diff --git " not in text or "--- a/" not in text or "+++ b/" not in text or "@@ " not in text:
                raise ValueError("LLM output is not a valid unified git diff (missing required headers)")

            # 如果提供 local_repo，则在基线 worktree 上应用并用 git diff 重新导出，确保上下文正确
            if self.use_git_rediff and self.local_repo:
                try:
                    return _apply_and_rediff_on_worktree(text, self.local_repo, task.base_commit)
                except Exception as e:
                    print(f"❌ git rediff failed: {e}\nFalling back to raw LLM diff output.")
            return text
        except Exception as e:
            print(f"❌ Error calling Bedrock: {e}")
            # 返回空patch作为fallback
            return "diff --git a/placeholder.py b/placeholder.py\n"

    def produce_new_files(self, task, originals: dict):
        """
        基于“基线文件原文”产出“完整的新文件文本”（full-file rewrite 模式）。

        Args:
            task: SWEBenchTask
            originals: {relative_path -> original_text}

        Returns:
            dict: {relative_path -> new_full_text}

        说明：
        - 该模式更稳，因为补丁由 git diff 生成，与基线上下文天然对齐。
        - 需要真实 LLM 能力（默认使用 Bedrock）。若没有 token，将抛错以避免写出空变更。
        """
        if not self.has_token:
            raise RuntimeError(
                "Full-file rewrite requires a real model. Set AWS_BEARER_TOKEN_BEDROCK or use --use_gold/patch mode."
            )

        # 目前实现支持单文件重写为主；多文件可扩展为分块提示
        if not originals:
            raise ValueError("originals is empty")
        if len(originals) > 1:
            # 简化处理：将多文件拼接到一个提示中，期望模型一次返回所有文件的新文本
            pass

        # 构造 prompt（单文件主用例）
        rp, rv = next(iter(originals.items()))
        prompt = f"""You are fixing a SWE-bench task by editing the actual baseline file.

Task (id={task.instance_id}):
{task.problem_statement}

Target file relative path:
{rp}

Current baseline content:
<ORIGINAL_FILE>
{rv}
</ORIGINAL_FILE>

Return ONLY the full, updated file content for {rp}.
Requirements:
- Keep a valid, compilable file.
- Preserve unrelated code.
- Do not include any explanation or fencing, just the new file content.
"""

        try:
            response = completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=int(os.getenv("Q1_FULLFILE_MAX_TOKENS", "4000")),
                temperature=float(os.getenv("Q1_LLM_TEMPERATURE", "0.1")),
            )
            new_text = response.choices[0].message.content or ""
            # 规范化换行
            new_text = new_text.replace("\r\n", "\n").replace("\r", "\n")
            return {rp: new_text}
        except Exception as e:
            raise RuntimeError(f"Error calling Bedrock for full-file rewrite: {e}")


def test_agent():
    """测试Agent是否能工作"""
    from pathlib import Path
    import sys

    # 添加路径
    sys.path.insert(0, str(Path(__file__).parent.parent))

    from steps.step1_load_data import load_task

    print("=" * 80)
    print("Testing SimpleBedrockAgent")
    print("=" * 80)

    # 加载1个任务
    data_file = Path(__file__).parent.parent.parent / "data" / "swebench" / "verified.jsonl"
    task = load_task(data_file, task_index=0)

    print(f"\n📋 Task: {task.instance_id}")
    print(f"📦 Repo: {task.repo}")
    print(f"📝 Problem: {task.problem_statement[:100]}...")

    # 创建Agent (allow testing without token)
    agent = SimpleBedrockAgent(require_token=False)

    print(f"\n🔧 Agent Configuration:")
    print(f"   Model: {agent.model}")
    print(f"   Has Token: {agent.has_token}")
    print(f"   Local Repo: {agent.local_repo}")
    print(f"   Use Git Rediff: {agent.use_git_rediff}")
    
    # 显示参数
    temperature = float(os.getenv("Q1_LLM_TEMPERATURE", "0.1"))
    patch_max_tokens = int(os.getenv("Q1_PATCH_MAX_TOKENS", "2000"))
    fullfile_max_tokens = int(os.getenv("Q1_FULLFILE_MAX_TOKENS", "4000"))
    print(f"\n📊 LLM Parameters:")
    print(f"   Temperature: {temperature}")
    print(f"   Patch Max Tokens: {patch_max_tokens}")
    print(f"   Full-file Max Tokens: {fullfile_max_tokens}")

    # 构造完整的 prompt 用于展示（与实际调用时相同）
    full_prompt = f"""You are a software engineer fixing a bug.

Problem:
{task.problem_statement}

Repository: {task.repo}

Generate a git diff patch to fix this bug.
STRICT REQUIREMENTS:
- Output MUST be a valid unified git diff exactly as produced by `git diff`.
- Do NOT wrap in code fences. Do NOT include any explanation before or after.
- Each file diff MUST include headers:
  diff --git a/<path> b/<path>
  --- a/<path>
  +++ b/<path>
  @@ -<oldstart>,<oldlen> +<newstart>,<newlen> @@
- Within each hunk:
  - Unchanged context lines MUST start with a single space ' '.
  - Removed lines MUST start with '-'.
  - Added lines MUST start with '+'.
- Ensure the patch ENDS WITH A SINGLE NEWLINE.
- Only output the patch, nothing else.

Example (format only):
diff --git a/path/to/file.py b/path/to/file.py
--- a/path/to/file.py
+++ b/path/to/file.py
@@ -10,7 +10,7 @@ def function():
-    old line
+    new line
"""
    print(f"\n💬 Full Prompt ({len(full_prompt)} characters):")
    print("=" * 80)
    print(full_prompt)
    print("=" * 80)

    print(f"\n🤖 Calling Bedrock API...")
    patch = agent.solve(task)

    print(f"\n✅ Generated patch ({len(patch)} characters, {patch.count(chr(10))} lines):")
    print("-" * 80)
    print(patch[:500])
    if len(patch) > 500:
        print(f"... (truncated, total {len(patch)} chars)")
    print("-" * 80)

    # 验证patch格式
    if "diff --git" in patch:
        print("\n✅ Patch format looks valid!")
    else:
        print("\n⚠️  Warning: Patch may not be in correct format")

    return patch


if __name__ == "__main__":
    test_agent()
