/**
 * Defines the core data structures for the Q1 drift detection pipeline,
 * including GoalConfig, Event, and GuardScores.
 */
export type Phase = 'reproduce' | 'modify' | 'test' | 'regress';
export type Tool = 'edit' | 'shell' | 'browse' | 'plan';
export type GuardAction = 'ok' | 'warn' | 'rollback';
export type UserLevel = 'novice' | 'intermediate' | 'expert';
export type TaskDifficulty = 'low' | 'medium' | 'high';

export interface GoalConfig {
  run_id: string;
  objective: string;
  allowed_paths: string[];
  forbidden_paths?: string[];
  checkpoints: Phase[];
  required_tests?: string[];
  allowed_tools_by_phase?: Partial<Record<Phase, Tool[]>>;
  thresholds?: { warn: number; rollback: number };
  weights?: { scope: number; plan: number; test: number; evidence: number };
  meta?: Record<string, any>;
}

export interface BaseEvent {
  id: string;
  run_id: string;
  step: number;
  ts?: string;
  phase: Phase;
  tool: Tool;
  why?: string;
  evidence?: { tests?: string[]; logs?: string[]; links?: string[] };
  confidence?: 'low'|'medium'|'high';
}

export interface EditEvent extends BaseEvent {
  tool: 'edit'|'plan';
  where: { path: string; start?: number; end?: number };
  what: { diff?: string; ast_hint?: string };
  override?: { acknowledged: boolean; reason: string; approved_by?: string };
}

export interface ShellEvent extends BaseEvent {
  tool: 'shell';
  cmd: string;
  exit_code?: number;
  stdout_digest?: string;
}

export type Event = EditEvent | ShellEvent;

export interface GuardScores {
  id: string;
  run_id: string;
  step: number;
  scope_guard: number;
  plan_guard: number;
  test_guard: number;
  evidence_guard: number;
  drift_score: number;
  action: GuardAction;
  auto_fixable: boolean;
  fix_cmd?: string;
  file?: string;
  notes?: string;
}
