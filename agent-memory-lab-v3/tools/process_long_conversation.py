#!/usr/bin/env python3
"""
Main entry point for processing long conversations.

This script takes a long chat log file (e.g., from Cursor), splits it into
logical query-answer pairs, and uses an LLM to generate metadata and a 
`goal.json` for each pair. The output is a structured session directory
in `data/1_sessions/` that is ready for Q1 analysis.
"""
"""
Process Long Conversation - 处理长cursor对话

将长对话拆分为多个独立的query-answer pairs
为每个pair生成metadata和goal.json
"""

import sys
import json
import pathlib
import re
import time
from typing import List, Tuple, Optional, Dict, Any

# 导入LLM客户端
from tools.llm_client import get_llm_client


# ============================================
# LLM Prompts
# ============================================

EXTRACT_SESSION_METADATA_PROMPT = """You are a conversation analyzer that extracts session-level metadata from long cursor conversations.

**Task**: Analyze the conversation sample (first + last parts) and generate session metadata.

**Output Schema** (Pure JSON, no markdown fences):
{
  "session_id": "s_2025-10-26-10-00-00_cursor",
  "source": "cursor",
  "start_datetime": "2025-10-26T10:00:00Z",
  "total_queries": <count of **User** messages>,
  "total_turns": <count of all messages>,
  "project_context": "brief description of the project",
  "overall_objective": "overall goal across all queries",
  "tags": ["tag1", "tag2", "tag3"]
}

**Instructions**:
1. Infer project_context from the first few user queries
2. Summarize overall_objective across all queries (what is the user trying to achieve overall?)
3. Count total_queries by counting "**User**" occurrences
4. Count total_turns by counting all "**User**" and "**Assistant**/**Cursor**/**Claude**" occurrences
5. Extract tags based on task types mentioned (e.g., "documentation", "authentication", "refactoring")
6. Use ISO8601 format for start_datetime

Output ONLY the JSON, nothing else."""


EXTRACT_PAIR_METADATA_PROMPT = """You are a query-answer pair analyzer.

**Task**: Extract metadata from this query-answer pair.

**Output Schema** (Pure JSON, no markdown fences):
{
  "pair_id": "s_2025-10-26-10-00-00_cursor_q01",
  "query_index": 1,
  "objective": "concise description of what user wants (1 sentence)",
  "task_type": "doc" | "code" | "debug" | "test" | "refactor" | "config",
  "related_files": ["file1.py", "file2.md"],
  "is_followup": true | false,
  "has_context_dependency": true | false
}

**Task Types**:
- "doc": Documentation/translation/README updates
- "code": New feature/implementation
- "debug": Bug fix
- "test": Testing/test creation
- "refactor": Code refactoring
- "config": Configuration changes

**is_followup**: true if this query builds on or continues the previous query's work
**has_context_dependency**: true if understanding this query requires knowing the previous context

**Instructions**:
1. Extract objective from the user's message (what they want to achieve)
2. Identify task type based on the user's request and assistant's actions
3. Extract all file paths mentioned in user or assistant messages
4. Determine if this is a followup (e.g., "also", "then", "next", references to previous work)
5. Determine if context is needed (if query references "it", "that", "above", or incomplete without context)

Output ONLY the JSON, nothing else."""


GENERATE_GOAL_FROM_PAIR_PROMPT = """You are a goal.json generator for code agent monitoring.

**Task**: Analyze this query-answer pair and generate a goal.json file.

**Output Schema** (Pure JSON, no markdown fences):
{
  "run_id": "s_2025-10-26-10-00-00_cursor_q01",
  "objective": "string",
  "allowed_paths": ["string"],
  "forbidden_paths": ["string"],
  "checkpoints": ["reproduce", "modify", "test", "regress"],
  "required_tests": ["string"]
}

**Inference Rules**:

1. **objective**: Extract the main task from user's message (1 sentence)

2. **allowed_paths**: Infer which files the agent is allowed to modify
   - Doc-only task (translate/docs) → ["README.md", "docs/**"]
   - Code task → mentioned source files
   - If unclear → ["**"]

3. **forbidden_paths**: Include ONLY if:
   - User explicitly says "don't change X"
   - Doc-only task → forbid code/dependencies: ["requirements.txt", "setup.py", "src/**", "*.lock"]

4. **required_tests**: Extract test command names
   - "pytest -k X" → ["X"]
   - "npm test" → ["test"]

5. **checkpoints**: Always ["reproduce", "modify", "test", "regress"]

**Task Type Detection**:
- Doc-only: keywords "translate", "docs", "README", "documentation" → strict allowed_paths
- Code: everything else → more permissive

Output ONLY the JSON, nothing else."""


# ============================================
# Cursor Export Header Extraction
# ============================================

def extract_cursor_export_header(full_md: str) -> Dict[str, Any]:
    """
    提取Cursor导出文件的头部信息

    Cursor导出的markdown格式：
    第1行：# <标题>
    第2行：_Exported on <date> at <time> <timezone> from Cursor (<version>)_

    Args:
        full_md: 完整对话内容

    Returns:
        包含conversation_title, exported_datetime, cursor_version的字典
    """
    lines = full_md.split('\n')
    header_info = {}

    # 提取标题（第1行）
    if len(lines) > 0:
        first_line = lines[0].strip()
        if first_line.startswith('# '):
            header_info['conversation_title'] = first_line[2:].strip()

    # 提取导出信息（第2行）
    if len(lines) > 1:
        second_line = lines[1].strip()
        # 格式：_Exported on 10/25/2025 at 20:26:15 PDT from Cursor (1.7.53)_
        export_pattern = r'_Exported on (.+?) at (.+?) (.+?) from Cursor \((.+?)\)_'
        match = re.match(export_pattern, second_line)

        if match:
            date_str = match.group(1)      # "10/25/2025"
            time_str = match.group(2)      # "20:26:15"
            timezone = match.group(3)      # "PDT"
            version = match.group(4)       # "1.7.53"

            # 解析为ISO8601格式
            try:
                from datetime import datetime

                # 解析日期和时间
                dt_str = f"{date_str} {time_str}"
                dt = datetime.strptime(dt_str, "%m/%d/%Y %H:%M:%S")

                # 处理时区（简化：PDT=-07:00, PST=-08:00, 其他默认UTC）
                tz_offsets = {
                    'PDT': '-07:00',  # Pacific Daylight Time
                    'PST': '-08:00',  # Pacific Standard Time
                    'EDT': '-04:00',  # Eastern Daylight Time
                    'EST': '-05:00',  # Eastern Standard Time
                    'CDT': '-05:00',  # Central Daylight Time
                    'CST': '-06:00',  # Central Standard Time
                    'MDT': '-06:00',  # Mountain Daylight Time
                    'MST': '-07:00',  # Mountain Standard Time
                    'UTC': '+00:00',
                }
                tz_offset = tz_offsets.get(timezone, '+00:00')

                # 格式化为ISO8601
                exported_datetime = dt.strftime("%Y-%m-%dT%H:%M:%S") + tz_offset
                header_info['exported_datetime'] = exported_datetime

            except Exception as e:
                # 解析失败，保存原始字符串
                header_info['exported_datetime'] = f"{date_str} {time_str} {timezone}"

            header_info['cursor_version'] = version

    return header_info


# ============================================
# Conversation Splitting
# ============================================

def split_conversation(full_md: str) -> List[Tuple[int, str, str]]:
    """
    拆分长对话为多个query-answer pairs

    Args:
        full_md: 完整对话的markdown内容

    Returns:
        List of (query_index, user_message, assistant_messages)
        query_index从0开始
    """
    pairs = []
    lines = full_md.split('\n')

    current_user = None
    current_assistant = []
    query_idx = 0

    i = 0
    while i < len(lines):
        line = lines[i]

        # 检测到新的User消息
        if re.match(r'\*\*User\*\*', line, re.IGNORECASE):
            # 保存前一个pair
            if current_user is not None:
                pairs.append((
                    query_idx,
                    current_user.strip(),
                    '\n\n'.join(current_assistant)
                ))
                query_idx += 1

            # 开始新的pair
            current_user = ''
            current_assistant = []
            i += 1

            # 收集user消息直到遇到assistant
            while i < len(lines) and not re.match(
                r'\*\*(?:Cursor|Claude|Assistant)\*\*',
                lines[i],
                re.IGNORECASE
            ):
                current_user += lines[i] + '\n'
                i += 1
            continue

        # 检测到Assistant消息
        if re.match(r'\*\*(?:Cursor|Claude|Assistant)\*\*', lines[i], re.IGNORECASE):
            i += 1
            assistant_msg = ''
            # 收集assistant消息直到遇到下一个User
            while i < len(lines) and not re.match(r'\*\*User\*\*', lines[i], re.IGNORECASE):
                assistant_msg += lines[i] + '\n'
                i += 1
            current_assistant.append(assistant_msg.strip())
            continue

        i += 1

    # 保存最后一个pair
    if current_user is not None:
        pairs.append((query_idx, current_user.strip(), '\n\n'.join(current_assistant)))

    return pairs


# ============================================
# LLM Extraction Functions
# ============================================

def extract_session_metadata(full_md: str, llm_client) -> Dict[str, Any]:
    """
    从完整对话提取session metadata

    Args:
        full_md: 完整对话内容
        llm_client: LLM客户端实例

    Returns:
        Session metadata字典
    """
    # 取前2000行 + 后500行作为样本
    lines = full_md.split('\n')
    sample = '\n'.join(lines[:2000] + ['\n...(omitted middle)...\n'] + lines[-500:])

    print("   🤖 Calling LLM to extract session metadata...")

    try:
        meta = llm_client.generate_json(
            system_prompt=EXTRACT_SESSION_METADATA_PROMPT,
            user_prompt=f"Analyze this conversation:\n\n{sample}",
            max_tokens=1000,
            temperature=0.1
        )

        # 生成session_id如果不存在或格式不对
        if not meta.get('session_id') or not meta['session_id'].startswith('s_'):
            # 使用友好的时间戳格式: YYYY-MM-DD-HH-MM-SS
            timestamp = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
            meta['session_id'] = f"s_{timestamp}_cursor"

        return meta

    except Exception as e:
        print(f"   ⚠️  LLM extraction failed, using defaults: {e}")
        # 返回默认值，使用友好的时间戳格式
        timestamp = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        return {
            "session_id": f"s_{timestamp}_cursor",
            "source": "cursor",
            "start_datetime": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_queries": len(re.findall(r'\*\*User\*\*', full_md, re.IGNORECASE)),
            "total_turns": len(re.findall(r'\*\*(?:User|Cursor|Assistant|Claude)\*\*', full_md, re.IGNORECASE)),
            "project_context": "Unknown",
            "overall_objective": "Unknown",
            "tags": []
        }


def extract_pair_metadata(
    pair_content: str,
    query_index: int,
    session_id: str,
    llm_client
) -> Dict[str, Any]:
    """
    从单个QA pair提取metadata

    Args:
        pair_content: pair的完整内容（可能包含前一个pair的上下文）
        query_index: query序号（1-based）
        session_id: session ID
        llm_client: LLM客户端实例

    Returns:
        Pair metadata字典
    """
    print(f"   🤖 Calling LLM to extract pair metadata for Q{query_index}...")

    try:
        # 限制长度，避免超过token限制
        content_sample = pair_content[:4000]

        meta = llm_client.generate_json(
            system_prompt=EXTRACT_PAIR_METADATA_PROMPT,
            user_prompt=f"Analyze this query-answer pair:\n\n{content_sample}",
            max_tokens=1000,
            temperature=0.1
        )

        # 补充字段
        meta['query_index'] = query_index
        meta['session_id'] = session_id
        meta['pair_id'] = f"{session_id}_q{query_index:02d}"

        return meta

    except Exception as e:
        print(f"   ⚠️  LLM extraction failed, using defaults: {e}")
        # 返回默认值
        return {
            "pair_id": f"{session_id}_q{query_index:02d}",
            "session_id": session_id,
            "query_index": query_index,
            "objective": f"Query {query_index}",
            "task_type": "code",
            "related_files": [],
            "is_followup": False,
            "has_context_dependency": False
        }


def generate_goal_for_pair(
    pair_content: str,
    session_id: str,
    query_index: int,
    llm_client
) -> Dict[str, Any]:
    """
    为单个pair生成goal.json

    Args:
        pair_content: pair的内容（可能包含上下文）
        session_id: session ID
        query_index: query序号
        llm_client: LLM客户端实例

    Returns:
        goal.json字典
    """
    print(f"   🎯 Calling LLM to generate goal.json for Q{query_index}...")

    try:
        # 限制长度
        content_sample = pair_content[:6000]

        goal = llm_client.generate_json(
            system_prompt=GENERATE_GOAL_FROM_PAIR_PROMPT,
            user_prompt=f"Generate goal.json for this query-answer pair:\n\n{content_sample}",
            max_tokens=1500,
            temperature=0.1
        )

        # 设置run_id
        goal['run_id'] = f"{session_id}_q{query_index:02d}"

        # 确保必需字段存在
        if 'checkpoints' not in goal:
            goal['checkpoints'] = ["reproduce", "modify", "test", "regress"]

        return goal

    except Exception as e:
        print(f"   ⚠️  Goal generation failed, using defaults: {e}")
        # 返回默认goal
        return {
            "run_id": f"{session_id}_q{query_index:02d}",
            "objective": f"Query {query_index}",
            "allowed_paths": ["**"],
            "checkpoints": ["reproduce", "modify", "test", "regress"]
        }


# ============================================
# Utility Functions
# ============================================

def sanitize_filename(s: str) -> str:
    """清理文件名，移除非法字符"""
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[-\s]+', '_', s)
    return s[:50].lower()


# ============================================
# Main Processing Function
# ============================================

def process_long_conversation(
    full_md_path: str,
    output_dir: str = "data/1_sessions"
) -> str:
    """
    处理长对话的完整流程

    Args:
        full_md_path: 完整对话markdown文件路径
        output_dir: 输出目录 (默认: data/1_sessions)

    Returns:
        session_id
    """
    print(f"🚀 Processing long conversation: {full_md_path}")
    print("="*80)

    # 读取完整对话
    full_md = pathlib.Path(full_md_path).read_text(encoding='utf-8')
    print(f"📄 Loaded conversation: {len(full_md)} characters, {len(full_md.splitlines())} lines")

    # 初始化LLM客户端
    print("\n🔧 Initializing LLM client...")
    try:
        llm_client = get_llm_client()
        print(f"✅ LLM client initialized: {llm_client.base_url}")
    except Exception as e:
        print(f"❌ Failed to initialize LLM client: {e}")
        print("💡 Make sure you have .env file with LLM_API_KEY and LLM_API_ENDPOINT")
        sys.exit(1)

    # Step 1a: 提取Cursor导出header信息
    print("\n📄 Step 1a: Extracting Cursor export header...")
    header_info = extract_cursor_export_header(full_md)
    if header_info.get('conversation_title'):
        print(f"✅ Conversation Title: {header_info['conversation_title']}")
    if header_info.get('exported_datetime'):
        print(f"   Exported: {header_info['exported_datetime']}")
    if header_info.get('cursor_version'):
        print(f"   Cursor Version: {header_info['cursor_version']}")

    # Step 1b: 提取session metadata（通过LLM）
    print("\n📊 Step 1b: Extracting session metadata (via LLM)...")
    session_meta = extract_session_metadata(full_md, llm_client)

    # 合并header信息到session metadata
    session_meta.update(header_info)
    session_id = session_meta['session_id']

    print(f"✅ Session ID: {session_id}")
    print(f"   Project: {session_meta.get('project_context', 'N/A')}")
    print(f"   Objective: {session_meta.get('overall_objective', 'N/A')}")

    # 创建目录结构
    session_dir = pathlib.Path(output_dir) / session_id
    (session_dir / 'raw').mkdir(parents=True, exist_ok=True)
    (session_dir / 'pairs').mkdir(parents=True, exist_ok=True)

    # 保存原始对话
    (session_dir / 'raw' / 'full_conversation.md').write_text(full_md, encoding='utf-8')

    # Step 2: 拆分对话
    print("\n🔪 Step 2: Splitting conversation into query-answer pairs...")
    pairs = split_conversation(full_md)
    print(f"✅ Found {len(pairs)} query-answer pairs")

    # Step 3: 处理每个pair
    print(f"\n📝 Step 3: Processing {len(pairs)} query-answer pairs...")
    pair_metas = []
    prev_pair_content = None

    for idx, (q_idx, user_msg, assistant_msg) in enumerate(pairs):
        print(f"\n{'='*60}")
        print(f"Processing Q{idx+1}/{len(pairs)} (index={q_idx})")
        print(f"{'='*60}")

        # 构建pair内容
        pair_content = f"**User**\n{user_msg}\n\n**Assistant**\n{assistant_msg}"

        # 如果不是第一个pair，附加前一个pair作为上下文
        if idx > 0 and prev_pair_content:
            pair_content_with_context = f"""## Previous Query-Answer:
{prev_pair_content[:500]}...

---

## Current Query-Answer:
{pair_content}
"""
        else:
            pair_content_with_context = pair_content

        # 提取pair metadata
        pair_meta = extract_pair_metadata(
            pair_content_with_context,
            idx + 1,  # 1-based index
            session_id,
            llm_client
        )

        print(f"   Objective: {pair_meta['objective']}")
        print(f"   Task Type: {pair_meta['task_type']}")
        print(f"   Is Followup: {pair_meta.get('is_followup', False)}")
        print(f"   Has Context Dependency: {pair_meta.get('has_context_dependency', False)}")

        # 创建query目录（聚合结构：pairs/q01/）
        query_dir = session_dir / 'pairs' / f"q{idx+1:02d}"
        query_dir.mkdir(parents=True, exist_ok=True)

        # 保存chat.md（固定名称）
        chat_path = query_dir / 'chat.md'

        # 根据是否有上下文依赖，决定保存的内容
        if pair_meta.get('has_context_dependency') and prev_pair_content:
            final_content = f"""# Query {idx+1}: {pair_meta['objective']}

## Context from Previous Query

{prev_pair_content[:500]}...

---

## Current Query-Answer

{pair_content}
"""
        else:
            final_content = f"""# Query {idx+1}: {pair_meta['objective']}

{pair_content}
"""

        chat_path.write_text(final_content, encoding='utf-8')
        pair_meta['markdown_path'] = str(chat_path.relative_to(session_dir))

        # 生成goal.json（保存在同一目录）
        # 根据has_context_dependency决定输入
        goal_input = pair_content_with_context if pair_meta.get('has_context_dependency') else pair_content
        goal = generate_goal_for_pair(goal_input, session_id, idx + 1, llm_client)

        goal_path = query_dir / 'goal.json'
        goal_path.write_text(json.dumps(goal, indent=2, ensure_ascii=False), encoding='utf-8')
        pair_meta['goal_json_path'] = str(goal_path.relative_to(session_dir))

        pair_metas.append(pair_meta)
        prev_pair_content = pair_content

        print(f"   ✅ Saved query dir: pairs/q{idx+1:02d}/")
        print(f"      - chat.md")
        print(f"      - goal.json")

    # Step 4: 保存session metadata和pairs列表
    print(f"\n💾 Step 4: Saving session metadata...")
    session_meta['total_queries'] = len(pairs)
    session_meta['total_turns'] = sum(1 for _ in re.finditer(r'\*\*(?:User|Cursor|Assistant|Claude)\*\*', full_md, re.IGNORECASE))

    (session_dir / 'session.json').write_text(
        json.dumps(session_meta, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )
    print(f"   ✅ Saved session.json")

    (session_dir / 'pairs.json').write_text(
        json.dumps(pair_metas, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )
    print(f"   ✅ Saved pairs.json")

    # Summary
    print(f"\n{'='*80}")
    print(f"✅ SESSION PROCESSED SUCCESSFULLY")
    print(f"{'='*80}")
    print(f"📁 Output Directory: {session_dir}")
    print(f"🆔 Session ID: {session_id}")
    print(f"📊 Statistics:")
    print(f"   - Total Queries: {len(pairs)}")
    print(f"   - Total Turns: {session_meta['total_turns']}")
    print(f"   - Followup Queries: {sum(1 for p in pair_metas if p.get('is_followup'))}")
    print(f"   - Context Dependent: {sum(1 for p in pair_metas if p.get('has_context_dependency'))}")
    print(f"\n📝 Task Types:")
    task_types = {}
    for p in pair_metas:
        t = p.get('task_type', 'unknown')
        task_types[t] = task_types.get(t, 0) + 1
    for task_type, count in sorted(task_types.items()):
        print(f"   - {task_type}: {count}")

    print(f"\n🚀 Next Steps:")
    print(f"   1. Review session.json and pairs.json")
    print(f"   2. Run Q1 batch analysis:")
    print(f"      python tools/run_q1_batch.py {session_dir}")
    print(f"   ")
    print(f"   Or manually analyze each query:")
    print(f"      cd {session_dir}")
    print(f"      for query_dir in pairs/q*/; do")
    print(f'        query_id=$(basename "$query_dir")')
    print(f'        echo "Analyzing $query_id..."')
    print(f"        # Use goal.json and chat.md from $query_dir")
    print(f"      done")

    return session_id


# ============================================
# Command Line Interface
# ============================================

def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("Usage: python process_long_conversation.py <full_conversation.md> [output_dir]")
        print("\nExample:")
        print("  python process_long_conversation.py spot-test/cursor_chat.md")
        print("  python process_long_conversation.py spot-test/cursor_chat.md data/my_sessions")
        print("\nRequires: .env file with LLM_API_KEY and LLM_API_ENDPOINT")
        sys.exit(1)

    full_md_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "data/1_sessions"

    if not pathlib.Path(full_md_path).exists():
        print(f"❌ Error: File not found: {full_md_path}")
        sys.exit(1)

    try:
        session_id = process_long_conversation(full_md_path, output_dir)
        print(f"\n🎉 Done! Session ID: {session_id}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
