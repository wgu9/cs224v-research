/**
 * Query-Answer Pair Metadata
 *
 * 单个query-answer对的元数据
 * 每个pair代表一个user query及其对应的assistant response(s)
 */

/**
 * Defines the data structure for a single query-answer pair within a session,
 * representing a sub-task.
 *
 * Task Type枚举（LLM生成时使用）：
 * - code: 新功能实现 / 代码编写
 * - doc: 文档更新 / 翻译 / README修改
 * - test: 测试编写 / 测试运行
 * - debug: Bug修复 / 调试
 * - refactor: 代码重构 / 优化
 * - config: 配置文件修改 / 环境设置
 * - qa: 问答 / 代码解释 / 咨询
 * - other: 其他类型
 */
export type TaskType = 'code' | 'doc' | 'test' | 'debug' | 'refactor' | 'config' | 'qa' | 'other';


/**
 * Query-Answer Pair的完整元数据
 */
export interface QueryAnswerPair {
  // 标识信息
  pair_id: string;                 // 唯一标识，格式：<session_id>_q<index>
                                   // 示例："s_20251026_cursor_001_q05"
  session_id: string;              // 所属session的ID
  query_index: number;             // 在session中的序号（1-based）
                                   // 示例：5 表示第5个query

  // 时间信息
  timestamp?: string;              // 该query的时间戳（如果可从对话提取）

  // 内容引用
  markdown_path: string;           // 该pair的markdown文件路径
                                   // 示例："pairs/q05_fix_authentication_bug.md"

  // 上下文信息
  prev_pair_id?: string;               // 前一个pair的ID（如果存在）
                                       // 示例："s_20251026_cursor_001_q04"

  // 任务信息（LLM提取）
  objective_llm: string;               // 该query的具体目标（LLM生成）
                                       // 示例："Fix authentication bug in login.py"
  task_type_llm: TaskType;             // 任务类型（LLM生成）
  related_files_llm: string[];         // 提到或修改的文件列表（LLM生成）
                                       // 示例：["src/auth/login.py", "tests/test_auth.py"]
  is_followup_llm: boolean;            // 是否是前一个query的后续问题（LLM生成）
                                       // true表示与前一个query紧密相关
  has_context_dependency_llm: boolean; // 是否依赖前面的上下文（LLM生成）
                                       // true表示理解本query需要前面的信息

  // Goal.json引用
  goal_json_path?: string;         // 该pair生成的goal.json文件路径
                                   // 示例："goals/q05_goal.json"

  // 扩展字段
  meta?: Record<string, any>;      // 任意扩展字段
}


/**
 * Query-Answer Pair的简化视图
 * 用于列表展示和快速查询
 */
export interface QueryAnswerPairSummary {
  pair_id: string;
  query_index: number;
  objective_llm: string;           // LLM生成的objective
  task_type_llm: TaskType;         // LLM生成的task_type
  is_followup_llm: boolean;        // LLM生成的is_followup
  has_drift?: boolean;             // 该query是否触发drift警告（需要从guards读取）
}


/**
 * Pair处理结果
 * 包含pair元数据及其关联的goal和分析结果
 */
export interface QueryAnswerPairResult {
  pair: QueryAnswerPair;           // pair元数据
  goal: any;                       // goal.json内容（GoalConfig类型）
  events?: any[];                  // events.jsonl内容（如果已运行Q1）
  guards?: any[];                  // guards.jsonl内容（如果已运行Q1）
  has_drift: boolean;              // 是否有drift
  drift_score?: number;            // 最高的drift score（如果存在）
}
