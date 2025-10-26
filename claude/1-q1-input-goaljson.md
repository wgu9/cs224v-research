# Q1 输入：用LLM自动生成 goal.json

## 🎯 核心思路

**问题**：用户只有cursor.md对话记录，但系统需要goal.json来定义任务目标和约束。

**方案**：用LLM从cursor.md自动推断并生成goal.json，确保：
1. 严格遵守GoalConfig数据结构
2. 使用预定义的枚举类型（Phase, Tool）
3. 处理多种对话模式（单轮/多轮、明确/隐含）
4. 为Q1偏航检测提供足够的约束

---

## 📐 GoalConfig 数据结构定义

### TypeScript定义（来自 types/index.ts）

```typescript
export type Phase = 'reproduce' | 'modify' | 'test' | 'regress';
export type Tool = 'edit' | 'shell' | 'browse' | 'plan';

export interface GoalConfig {
  run_id: string;                    // 运行ID，格式：r<timestamp>
  objective: string;                 // 任务目标，一句话描述
  allowed_paths: string[];           // 白名单路径（支持glob）
  forbidden_paths?: string[];        // 黑名单路径（可选）
  checkpoints: Phase[];              // 检查点，通常全4个
  required_tests?: string[];         // 必需的测试（从对话提取）
  allowed_tools_by_phase?: Partial<Record<Phase, Tool[]>>;  // 可选，有默认值
  thresholds?: {                     // 可选，默认 warn=0.5, rollback=0.8
    warn: number;
    rollback: number;
  };
  weights?: {                        // 可选，默认 0.4/0.3/0.2/0.1
    scope: number;
    plan: number;
    test: number;
    evidence: number;
  };
  meta?: Record<string, any>;        // 任意扩展字段
}
```

### 字段详解与LLM推断规则

| 字段 | 必需 | 推断规则 | 示例 |
|------|------|----------|------|
| `run_id` | ✅ | 自动生成：`r` + timestamp | `"r1730000000"` |
| `objective` | ✅ | 提取用户第一轮或最主要的请求 | `"Translate README.md to Chinese"` |
| `allowed_paths` | ✅ | 从对话推断要修改的文件；doc-only任务限制为*.md | `["README.md", "docs/**"]` |
| `forbidden_paths` | ❌ | 若明确说"不要改X"，则添加；doc-only任务默认禁止代码/依赖 | `["requirements.txt", "src/**"]` |
| `checkpoints` | ✅ | 默认全4个：`["reproduce","modify","test","regress"]` | `["reproduce","modify","test","regress"]` |
| `required_tests` | ❌ | 从对话提取pytest/npm test等命令 | `["doc_lang_check", "whitelist_diff_check"]` |
| `allowed_tools_by_phase` | ❌ | 通常省略，使用默认值 | 省略 |
| `thresholds` | ❌ | 通常省略，使用默认值 | 省略 |
| `weights` | ❌ | 通常省略，使用默认值 | 省略 |
| `meta` | ❌ | 可选扩展字段 | `{"source": "cursor"}` |

---

## 🤖 LLM Prompt 模板

### System Prompt

```markdown
You are a goal.json generator for a code agent monitoring system.

Your task: Analyze a cursor.md chat conversation and generate a valid goal.json file that defines:
- The task objective
- Which files the agent is allowed to modify (allowed_paths)
- Which files are forbidden to modify (forbidden_paths)
- Required tests to run

**IMPORTANT CONSTRAINTS:**

1. **Data Structure**: Output MUST be valid JSON matching GoalConfig schema
2. **Enums**: Use ONLY these exact values:
   - Phase: "reproduce" | "modify" | "test" | "regress"
   - Tool: "edit" | "shell" | "browse" | "plan"
3. **Glob Patterns**: allowed_paths and forbidden_paths support:
   - `*` (any filename): "*.md"
   - `**` (any subdirectory): "docs/**", "src/**/*.py"
   - Exact paths: "README.md", "requirements.txt"

**Schema:**
```json
{
  "run_id": "r<timestamp>",           // Auto-generate
  "objective": "string",              // Extract from first user message
  "allowed_paths": ["string"],        // Infer from conversation
  "forbidden_paths": ["string"],      // Optional, only if explicitly mentioned
  "checkpoints": ["reproduce","modify","test","regress"],  // Always these 4
  "required_tests": ["string"]        // Optional, extract test commands
}
```

**Inference Rules:**

1. **objective**: Extract the main user request (usually first message)
   - Keep it concise (1 sentence)
   - Example: "Translate README.md to Chinese"

2. **allowed_paths**: Infer from mentioned files + task type
   - If doc-only task (translate/update docs) → ["README.md", "docs/**"]
   - If code task → include mentioned source files
   - If unclear → ["**"] (allow all)

3. **forbidden_paths**: Include ONLY if:
   - User explicitly says "don't change X"
   - Doc-only task → forbid ["requirements.txt", "setup.py", "src/**", "*.lock"]

4. **required_tests**: Extract from conversation
   - Look for: pytest, npm test, go test, mvn test commands
   - Extract test names/patterns: "pytest -k doc_lang_check" → ["doc_lang_check"]

5. **Task Type Detection**:
   - **Doc-only**: keywords like "translate", "update docs", "README", "documentation"
     → Strict allowed_paths (only .md files), forbid code/dependencies
   - **Code change**: default, more permissive

**Edge Cases:**

- Multiple user messages → Use the FIRST clear request as objective
- No explicit file mentions → allowed_paths: ["**"]
- Agent mentions files but user didn't → Still include in allowed_paths
- Tests mentioned but no explicit command → Omit required_tests
- User says "only change X" → allowed_paths: ["X"], forbidden_paths: everything else common

**Output Format:**
- Pure JSON, no markdown fences
- All required fields present
- Optional fields omitted if not applicable (not null/empty array)
```

### User Prompt Template

```python
# Python template
USER_PROMPT = """
Analyze this cursor.md conversation and generate goal.json:

```markdown
{cursor_md_content}
```

Generate goal.json following the schema and rules.
"""
```

---

## 📝 示例：输入输出

### 示例1：文档翻译任务（严格限制）

**Input cursor.md:**
```markdown
**User**
把 README.md 翻译成中文，不要改动任何依赖。

**Cursor**
我会修改 README.md，将英文翻译为中文。

**Cursor**
我已修改 README.md。运行测试：
pytest -k doc_lang_check  # passed
pytest -k whitelist_diff_check  # passed
```

**Output goal.json:**
```json
{
  "run_id": "r1730000001",
  "objective": "Translate README.md to Chinese",
  "allowed_paths": ["README.md"],
  "forbidden_paths": ["requirements.txt", "setup.py", "src/**", "*.lock"],
  "checkpoints": ["reproduce", "modify", "test", "regress"],
  "required_tests": ["doc_lang_check", "whitelist_diff_check"]
}
```

**推断逻辑：**
- ✅ objective: 从用户第一句提取
- ✅ allowed_paths: 只提到README.md
- ✅ forbidden_paths: 用户明确说"不要改动任何依赖"，且是doc-only任务
- ✅ required_tests: 从Cursor输出提取pytest命令

---

### 示例2：代码修复任务（宽松限制）

**Input cursor.md:**
```markdown
**User**
Fix the authentication bug in src/auth/login.py

**Cursor**
I'll review the code and fix the issue.

**Cursor**
Fixed the token validation logic in src/auth/login.py.
Also updated tests in tests/test_auth.py.

Running tests:
pytest tests/test_auth.py  # all passed
```

**Output goal.json:**
```json
{
  "run_id": "r1730000002",
  "objective": "Fix authentication bug in src/auth/login.py",
  "allowed_paths": ["src/auth/login.py", "tests/test_auth.py"],
  "checkpoints": ["reproduce", "modify", "test", "regress"],
  "required_tests": ["test_auth"]
}
```

**推断逻辑：**
- ✅ objective: 从用户请求提取
- ✅ allowed_paths: 用户提到的文件 + agent实际修改的文件
- ⚠️ forbidden_paths: 省略（代码任务不严格限制）
- ✅ required_tests: 从pytest命令提取测试文件名

---

### 示例3：多轮对话（提取主要目标）

**Input cursor.md:**
```markdown
**User**
我想给项目添加国际化支持。

**Cursor**
好的，需要修改哪些语言？

**User**
先支持中文和英文。只修改 i18n/ 目录下的文件，不要动其他代码。

**Cursor**
明白了，我会只修改 i18n/ 下的翻译文件。

**Cursor**
已创建 i18n/zh-CN.json 和 i18n/en-US.json。
```

**Output goal.json:**
```json
{
  "run_id": "r1730000003",
  "objective": "Add internationalization support for Chinese and English",
  "allowed_paths": ["i18n/**"],
  "forbidden_paths": ["src/**", "*.py", "*.ts"],
  "checkpoints": ["reproduce", "modify", "test", "regress"]
}
```

**推断逻辑：**
- ✅ objective: 综合前两轮对话，提取完整目标
- ✅ allowed_paths: 用户明确说"只修改 i18n/ 目录"
- ✅ forbidden_paths: 用户明确说"不要动其他代码"
- ⚠️ required_tests: 未提到测试，省略

---

### 示例4：无明确限制（宽松默认）

**Input cursor.md:**
```markdown
**User**
优化代码性能。

**Cursor**
我会分析代码并进行优化。
```

**Output goal.json:**
```json
{
  "run_id": "r1730000004",
  "objective": "Optimize code performance",
  "allowed_paths": ["**"],
  "checkpoints": ["reproduce", "modify", "test", "regress"]
}
```

**推断逻辑：**
- ✅ objective: 从用户请求提取
- ⚠️ allowed_paths: 未明确提到文件，默认允许所有
- ⚠️ forbidden_paths: 省略（无明确限制）
- ⚠️ required_tests: 省略（未提到）

---

## 🛠️ Python 实现代码

### 完整实现（调用LLM生成goal.json）

```python
#!/usr/bin/env python3
"""
自动从cursor.md生成goal.json
使用LLM推断任务目标、约束和测试要求
"""

import json
import pathlib
import time
from typing import Dict, Any, Optional
import anthropic  # 或者 openai


# ============================================
# 1. System Prompt（严格约束LLM输出）
# ============================================

SYSTEM_PROMPT = """You are a goal.json generator for a code agent monitoring system.

Your task: Analyze a cursor.md chat conversation and generate a valid goal.json file.

**STRICT CONSTRAINTS:**

1. **Output Format**: Pure JSON, no markdown fences, no explanations
2. **Required Fields**: run_id, objective, allowed_paths, checkpoints
3. **Enums**:
   - Phase: "reproduce" | "modify" | "test" | "regress"
   - Tool: "edit" | "shell" | "browse" | "plan"

**Schema:**
```json
{
  "run_id": "r<timestamp>",
  "objective": "string",
  "allowed_paths": ["string"],
  "forbidden_paths": ["string"],
  "checkpoints": ["reproduce","modify","test","regress"],
  "required_tests": ["string"]
}
```

**Inference Rules:**

1. **objective**: Extract main user request (1 sentence)
2. **allowed_paths**:
   - Doc-only task (translate/docs) → ["README.md", "docs/**"]
   - Code task → mentioned files
   - Unclear → ["**"]
3. **forbidden_paths**: Only if user says "don't change X" OR doc-only task
   - Doc-only → ["requirements.txt", "setup.py", "src/**", "*.lock"]
4. **required_tests**: Extract test command patterns
   - "pytest -k X" → ["X"]
   - "npm test" → ["test"]
5. **checkpoints**: Always ["reproduce","modify","test","regress"]

**Task Type Detection:**
- Doc-only: keywords "translate", "docs", "README", "documentation"
- Code: everything else

**Output**: Pure JSON matching schema exactly."""


# ============================================
# 2. 调用LLM生成goal.json
# ============================================

def generate_goal_from_cursor(
    cursor_md: str,
    llm_api_key: str,
    model: str = "claude-3-5-sonnet-20241022"
) -> Dict[str, Any]:
    """
    从cursor.md生成goal.json

    Args:
        cursor_md: cursor对话内容
        llm_api_key: LLM API密钥
        model: 使用的模型

    Returns:
        goal.json字典
    """
    client = anthropic.Anthropic(api_key=llm_api_key)

    user_prompt = f"""Analyze this cursor.md conversation and generate goal.json:

```markdown
{cursor_md[:8000]}
```

Generate goal.json following the schema and rules."""

    response = client.messages.create(
        model=model,
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_prompt}
        ]
    )

    # 提取JSON
    content = response.content[0].text.strip()

    # 移除可能的markdown fence
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(lines[1:-1]) if len(lines) > 2 else content

    goal = json.loads(content)

    # 自动补充run_id（如果LLM未生成或格式不对）
    if not goal.get("run_id") or not goal["run_id"].startswith("r"):
        goal["run_id"] = f"r{int(time.time())}"

    # 验证必需字段
    validate_goal(goal)

    return goal


# ============================================
# 3. 验证goal.json有效性
# ============================================

def validate_goal(goal: Dict[str, Any]) -> None:
    """验证goal.json符合schema"""
    required = ["run_id", "objective", "allowed_paths", "checkpoints"]
    for field in required:
        if field not in goal:
            raise ValueError(f"Missing required field: {field}")

    # 验证checkpoints
    valid_phases = {"reproduce", "modify", "test", "regress"}
    for phase in goal["checkpoints"]:
        if phase not in valid_phases:
            raise ValueError(f"Invalid checkpoint: {phase}. Must be one of {valid_phases}")

    # 验证allowed_paths非空
    if not goal["allowed_paths"]:
        raise ValueError("allowed_paths cannot be empty")


# ============================================
# 4. 主函数：端到端生成
# ============================================

def main(cursor_md_path: str, llm_api_key: str, output_path: Optional[str] = None):
    """
    从cursor.md生成goal.json并保存

    Args:
        cursor_md_path: cursor.md文件路径
        llm_api_key: LLM API密钥
        output_path: 输出路径（可选，默认同目录下的goal.json）
    """
    # 读取cursor.md
    cursor_md = pathlib.Path(cursor_md_path).read_text(encoding="utf-8")

    # 生成goal.json
    print("🤖 Generating goal.json from cursor.md...")
    goal = generate_goal_from_cursor(cursor_md, llm_api_key)

    # 保存
    if output_path is None:
        output_path = pathlib.Path(cursor_md_path).parent / "goal.json"

    pathlib.Path(output_path).write_text(
        json.dumps(goal, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"✅ Generated goal.json:")
    print(json.dumps(goal, indent=2, ensure_ascii=False))
    print(f"\n📁 Saved to: {output_path}")


# ============================================
# 5. 使用示例
# ============================================

if __name__ == "__main__":
    import sys
    import os

    if len(sys.argv) < 2:
        print("Usage: python generate_goal.py <cursor.md> [output.json]")
        print("\nRequires: ANTHROPIC_API_KEY environment variable")
        sys.exit(1)

    cursor_md_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    main(cursor_md_path, api_key, output_path)
```

---

## 🧪 测试计划

### 测试用例

| 用例 | 输入特征 | 预期输出关键点 |
|------|----------|----------------|
| doc-only-single | 单轮，明确doc翻译 | allowed_paths只含.md，forbidden_paths包含代码/依赖 |
| doc-only-multi | 多轮，逐步明确doc | 综合所有轮次，提取完整objective |
| code-fix | 代码修复，提到文件 | allowed_paths包含提到的源文件和测试 |
| no-constraint | 模糊请求，无文件 | allowed_paths: ["**"] |
| explicit-forbid | 明确说"不要改X" | forbidden_paths包含X |
| with-tests | 包含pytest命令 | required_tests提取测试名 |

### 测试脚本

```python
def test_generate_goal():
    """测试goal.json生成"""
    test_cases = [
        {
            "name": "doc-only-single",
            "cursor_md": "**User**\n把 README.md 翻译成中文，不要改依赖。\n\n**Cursor**\n我已修改 README.md。",
            "expected": {
                "objective": "Translate README.md to Chinese",
                "allowed_paths": ["README.md"],
                "forbidden_paths": ["requirements.txt", "setup.py"]
            }
        },
        # ... 更多测试用例
    ]

    for tc in test_cases:
        goal = generate_goal_from_cursor(tc["cursor_md"], api_key)
        assert goal["objective"] == tc["expected"]["objective"]
        assert set(goal["allowed_paths"]) == set(tc["expected"]["allowed_paths"])
```

---

## 🎯 集成到现有工具链

### 修改 chat2events.py（添加 --auto-goal）

```python
# tools/chat2events.py 末尾添加

def auto_generate_goal(cursor_md: str, run_id: str) -> Dict[str, Any]:
    """调用LLM生成goal.json"""
    import os
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set, cannot auto-generate goal")

    from tools.generate_goal import generate_goal_from_cursor
    goal = generate_goal_from_cursor(cursor_md, api_key)
    goal["run_id"] = run_id  # 覆盖为当前run_id
    return goal

def main(run_dir: str, auto_goal: bool = False):
    rd = pathlib.Path(run_dir)
    chat_path = rd/'raw'/'cursor.md'

    # 读取cursor.md
    chat_md = chat_path.read_text(encoding='utf-8')

    # 如果启用auto-goal，生成goal.json
    if auto_goal:
        print("🤖 Auto-generating goal.json from cursor.md...")
        goal = auto_generate_goal(chat_md, rd.name)
        (rd / "goal.json").write_text(json.dumps(goal, indent=2, ensure_ascii=False))
        print(f"✅ Generated goal.json")
    else:
        # 读取现有goal.json
        goal = json.loads((rd/'goal.json').read_text())

    # ... 原有逻辑继续
```

### 新的使用方式

```bash
# 方式1：只有cursor.md，自动生成goal.json
ANTHROPIC_API_KEY=xxx python tools/chat2events.py \
  data/runs/my_run \
  --auto-goal

# 方式2：手动提供goal.json（原有方式）
python tools/chat2events.py data/runs/my_run
```

---

## ✅ 总结

### 你的想法完全正确！

1. ✅ **用LLM生成goal.json** - 最实用的方案
2. ✅ **先定义数据结构** - types/index.ts已定义，足够约束LLM
3. ✅ **提供严格的prompt** - 包含schema、枚举、推断规则
4. ✅ **处理多种对话情况** - 单轮/多轮、明确/模糊、doc/code

### 核心优势

- **用户体验**：只需要cursor.md一个文件
- **准确性**：LLM理解自然语言意图，推断更准确
- **可验证**：生成后自动验证schema
- **可调整**：用户可手动编辑LLM生成的goal.json

### 下一步

1. 把上面的`generate_goal.py`代码独立成工具
2. 测试几个真实cursor.md，调优prompt
3. 集成到chat2events.py，添加`--auto-goal`选项

你需要我立即实现这个工具吗？还是先测试一下prompt效果？
