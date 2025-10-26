/**
 * Cursor Chat Long Session Types
 *
 * 长对话处理的数据结构定义
 * 支持将长cursor对话拆分为多个独立的query-answer pairs
 */

// Session相关类型
/**
 * Barrel file for exporting all types related to Cursor chat session processing.
 */
export * from './session';

// Query-Answer Pair相关类型
export type {
  TaskType,
  QueryAnswerPair,
  QueryAnswerPairSummary,
  QueryAnswerPairResult
} from './pair';


/**
 * 目录结构说明
 *
 * data/sessions/<session_id>/
 * ├── session.json                      # SessionMetadata
 * ├── pairs.json                        # QueryAnswerPair[]
 * ├── raw/
 * │   └── full_conversation.md          # 原始完整对话
 * ├── pairs/
 * │   ├── q01_<objective>.md           # 每个独立的QA pair
 * │   ├── q02_<objective>.md
 * │   └── ...
 * ├── goals/
 * │   ├── q01_goal.json                # 每个pair的goal（GoalConfig）
 * │   ├── q02_goal.json
 * │   └── ...
 * └── runs/
 *     ├── q01/                          # Q1分析结果
 *     │   ├── events.jsonl
 *     │   └── guards.jsonl
 *     ├── q02/
 *     └── ...
 */
