# LLM Prompts

这个目录包含所有用于 `process_long_conversation.py` 的LLM prompts。

## Prompt 文件

| 文件名 | 用途 | 调用位置 |
|--------|------|----------|
| `extract_session_metadata.txt` | 从对话中提取session级别的元数据 | `extract_session_metadata()` |
| `extract_pair_metadata.txt` | 从单个query-answer pair提取元数据 | `extract_pair_metadata()` |
| `generate_goal_from_pair.txt` | 为单个pair生成goal.json | `generate_goal_for_pair()` |

## 如何修改

1. 直接编辑 `.txt` 文件
2. 保存后，下次运行 `process_long_conversation.py` 时自动生效
3. 无需重启或重新加载

## Prompt 格式

所有prompts都应该：
- 使用纯文本（UTF-8编码）
- 包含清晰的 **Output Schema** (JSON格式)
- 包含详细的 **Instructions**
- 以 "Output ONLY the JSON, nothing else." 结尾

## 加载机制

Prompts通过 `load_prompt()` 函数从此目录加载：

```python
def load_prompt(filename: str) -> str:
    prompt_dir = pathlib.Path(__file__).parent / 'prompts'
    prompt_path = prompt_dir / filename
    return prompt_path.read_text(encoding='utf-8')
```

## 版本控制

- ✅ Prompts现在独立于代码
- ✅ 易于追踪prompt变更历史
- ✅ 可以A/B测试不同的prompts



