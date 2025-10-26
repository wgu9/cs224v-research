/**
 * Session Metadata
 *
 * 长对话的会话级元数据
 * 用于管理和追踪一个完整的cursor对话session
 */

/**
 * Defines the data structure for session-level metadata, representing a
 * full conversation processed from a long chat log.
 */
export interface SessionMetadata {
  // 基本标识
  session_id: string;              // 唯一标识，格式：s_<timestamp>_<source>_<seq>
                                   // 示例："s_20251026_cursor_001"

  source: string;                  // 对话来源："cursor" | "claude" | "aider" 默认是cursor 我们目前只负责cursor

  // Cursor导出信息（从文件头部提取）
  conversation_title?: string;     // 对话标题（第1行的# ...）
                                   // 示例："Document updates and alignment suggestions"
  exported_datetime?: string;      // 导出时间，ISO8601格式
                                   // 示例："2025-10-25T20:26:15-07:00" (PDT)
  cursor_version?: string;         // Cursor版本号
                                   // 示例："1.7.53"

  // 时间信息
  start_datetime: string;          // 会话开始时间，ISO8601格式
                                   // 示例："2025-10-26T10:00:00Z"
  end_datetime?: string;           // 会话结束时间（可选）

  // 统计信息
  total_queries: number;           // user query总数，如 50
  total_turns: number;             // 总轮次（user + assistant），如 100

  // LLM配置
  model?: string;                  // LLM模型名称，默认："auto"
  max_mode?: string;               // 最大模式，默认："No"

  // 上下文信息（LLM提取）
  project_context_llm?: string;    // 项目上下文描述（LLM生成）
                                   // 示例："Python web API project with authentication"
  overall_objective_llm?: string;  // 整体目标，跨所有queries的总结（LLM生成）
                                   // 示例："Add authentication and internationalization features"
  tags_llm?: string[];             // 标签，用于分类和检索（LLM生成）
                                   // 示例：["authentication", "i18n", "refactoring"]

  // 扩展字段
  meta?: Record<string, any>;      // 任意扩展字段
}


/**
 * Session统计信息
 * 用于概览和分析
 */
export interface SessionStats {
  session_id: string;
  total_queries: number;
  task_type_distribution: Record<string, number>;  // {"doc": 10, "code": 20, ...}
  followup_count: number;                          // 后续query的数量
  context_dependent_count: number;                 // 有上下文依赖的query数量
  has_drift: boolean;                              // 是否有任何query触发drift警告
  drift_count: number;                             // 触发drift的query数量
}
