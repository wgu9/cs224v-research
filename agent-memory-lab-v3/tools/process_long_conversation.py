#!/usr/bin/env python3
"""
Process Long Conversation - 处理长cursor对话

This script takes a long chat log file (e.g., from Cursor), splits it into
logical query-answer pairs, and uses an LLM to generate metadata and a
`goal.json` for each pair. The output is a structured session directory
in `data/1_sessions/` that is ready for Q1 analysis.

**LLM Usage**: ✅ YES - MULTIPLE LLM CALLS
  Step 1a: ❌ NO LLM - Regex-based cursor header extraction
  Step 1b: ✅ LLM CALL - Extract session metadata (1 call per session)
  Step 2:  ❌ NO LLM - Regex-based conversation splitting
  Step 3:  ✅ LLM CALLS - For each query-answer pair (N queries × 2 calls):
           - Extract pair metadata (objective, task_type, etc.)
           - Generate goal.json (allowed_paths, required_tests, etc.)

**Total LLM Calls**: 1 + (N_queries × 2)
  Example: 10 queries = 1 + 20 = 21 LLM calls

**Usage**: Run with runner.sh to ensure correct PYTHONPATH
  ./runner.sh python tools/process_long_conversation.py cursor.md
"""

import sys
import json
import pathlib
import re
import time
from typing import List, Tuple, Optional, Dict, Any, Literal

# 导入LLM客户端
from tools.llm_client import get_llm_client


# ============================================
# Type Definitions (matching TypeScript)
# ============================================

# TaskType枚举（与types/cursor-chat/pair.ts保持一致）
TaskType = Literal['code', 'doc', 'test', 'debug', 'refactor', 'config', 'qa', 'other']

VALID_TASK_TYPES = ['code', 'doc', 'test', 'debug', 'refactor', 'config', 'qa', 'other']


def validate_task_type(task_type: str) -> str:
    """
    验证并修正task_type

    Args:
        task_type: LLM返回的task_type

    Returns:
        有效的task_type（如果无效则返回'other'）
    """
    if task_type in VALID_TASK_TYPES:
        return task_type
    else:
        print(f"   ⚠️  Invalid task_type '{task_type}', defaulting to 'other'")
        return 'other'


# ============================================
# LLM Prompts - Loaded from files
# ============================================

def load_prompt(filename: str) -> str:
    """
    从tools/prompts/目录加载prompt文件

    Args:
        filename: prompt文件名（如 'extract_session_metadata.txt'）

    Returns:
        prompt文本内容
    """
    prompt_dir = pathlib.Path(__file__).parent / 'prompts'
    prompt_path = prompt_dir / filename

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    return prompt_path.read_text(encoding='utf-8')


# 加载prompts
EXTRACT_SESSION_METADATA_PROMPT = load_prompt('extract_session_metadata.txt')
EXTRACT_PAIR_METADATA_PROMPT = load_prompt('extract_pair_metadata.txt')
GENERATE_GOAL_FROM_PAIR_PROMPT = load_prompt('generate_goal_from_pair.txt')


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
            "model": "auto",
            "max_mode": "No",
            "project_context_llm": "Unknown",
            "overall_objective_llm": "Unknown",
            "tags_llm": []
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

        # 验证task_type_llm
        if 'task_type_llm' in meta:
            meta['task_type_llm'] = validate_task_type(meta['task_type_llm'])

        return meta

    except Exception as e:
        print(f"   ⚠️  LLM extraction failed, using defaults: {e}")
        # 返回默认值
        return {
            "pair_id": f"{session_id}_q{query_index:02d}",
            "session_id": session_id,
            "query_index": query_index,
            "objective_llm": f"Query {query_index}",
            "task_type_llm": "code",
            "related_files_llm": [],
            "is_followup_llm": False,
            "has_context_dependency_llm": False
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

    # 合并header信息到session metadata（header优先，因为是确定性提取）
    # header字段：conversation_title, exported_datetime, cursor_version
    # 这些字段不会与LLM生成的字段冲突（LLM字段都有_llm后缀）
    for key, value in header_info.items():
        if key in session_meta:
            print(f"   ⚠️  Warning: Header field '{key}' overwrites LLM field")
        session_meta[key] = value

    session_id = session_meta['session_id']

    print(f"✅ Session ID: {session_id}")
    print(f"   Model: {session_meta.get('model', 'auto')}")
    print(f"   Max Mode: {session_meta.get('max_mode', 'No')}")
    print(f"   Project: {session_meta.get('project_context_llm', 'N/A')}")
    print(f"   Objective: {session_meta.get('overall_objective_llm', 'N/A')}")

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

        print(f"   Objective: {pair_meta['objective_llm']}")
        print(f"   Task Type: {pair_meta['task_type_llm']}")
        print(f"   Is Followup: {pair_meta.get('is_followup_llm', False)}")
        print(f"   Has Context Dependency: {pair_meta.get('has_context_dependency_llm', False)}")

        # 创建query目录（聚合结构：pairs/q01/）
        query_dir = session_dir / 'pairs' / f"q{idx+1:02d}"
        query_dir.mkdir(parents=True, exist_ok=True)

        # 保存chat.md（固定名称）
        chat_path = query_dir / 'chat.md'

        # 根据是否有上下文依赖，决定保存的内容
        if pair_meta.get('has_context_dependency_llm') and prev_pair_content:
            final_content = f"""# Query {idx+1}: {pair_meta['objective_llm']}

## Context from Previous Query

{prev_pair_content[:500]}...

---

## Current Query-Answer

{pair_content}
"""
        else:
            final_content = f"""# Query {idx+1}: {pair_meta['objective_llm']}

{pair_content}
"""

        chat_path.write_text(final_content, encoding='utf-8')
        pair_meta['markdown_path'] = str(chat_path.relative_to(session_dir))

        # 生成goal.json（保存在同一目录）
        # 根据has_context_dependency_llm决定输入
        goal_input = pair_content_with_context if pair_meta.get('has_context_dependency_llm') else pair_content
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
    print(f"   - Followup Queries: {sum(1 for p in pair_metas if p.get('is_followup_llm'))}")
    print(f"   - Context Dependent: {sum(1 for p in pair_metas if p.get('has_context_dependency_llm'))}")
    print(f"\n📝 Task Types:")
    task_types = {}
    for p in pair_metas:
        t = p.get('task_type_llm', 'unknown')
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
