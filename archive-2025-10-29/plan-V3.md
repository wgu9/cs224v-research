# 💭 问题分析与执行策略

> **核心思考**：我觉得这个框架已经搭好了，但是我认为这三个问题和它们的解决我们还没有完全地做好。就是说我想先解决最简单的这个问题，就是最后这个偏移的问题，就是这个drift的问题。然后再解决第二个和第三个问题，你觉得这个方法是不是好？因为我最后是想从简单到难开始，从一个实践的顺序来说，我是想先解决一个简单的问题，然后再解决其他的复杂的问题。
>
> 我感觉第一个问题就是有一个数据之后，我们判断这个AI它是不是偏移了。这个数据是其他两个问题的先驱，因为如果没有这个数据的话，我们也没法match这个匹配度，对吧？我们也没有办法做这个复用的情况，learning from experience的情况。Q2和Q3其实取决于Q1，这是我的理解。所以我想先做Q1，再做Q2，再做Q3，不知道你同意这个方案吗？我觉得大体框架是有的，我们现在就要走一遍细节。
>
> **技术细节需要细化**：举个例子比如Q1的四个守卫+计算score的方式+数据input/output都可以继续细化（是否要定一个ts or数据库结构，枚举结构），Q2的pattern的定义（这些如何定义：经验无法沉淀与迁移，造成重复劳动，是否要定一个ts or数据库结构，枚举结构），Q3的"用户水平 × 任务难度" 这两个也可以定义，是否要定一个ts or数据库结构，枚举结构）
>
> 这是我的想法

## ✅ 执行策略确认

我完全同意你的执行顺序：先打穿 Q1（偏航检测）→ 再做 Q2（模式复用）→ 最后 Q3（动态抽象）。

理由很简单也很工程化：Q1 产出的"规范化事件 + 守卫分数"就是 Q2 抽卡与 Q3 路由的训练/检索数据。没有 Q1，就没有可复用的"事实语料库"。

下面我把三块一次性讲清楚：先给你实现顺序与验收标准，然后给精确的数据结构（TypeScript + 可选 SQLite DDL）与算法细节，最后给端到端示例（和你当前"翻译 README 却误改 requirements.txt"的例子完全对齐）。

---

## 📋 一、实施顺序（从简单到难）

### Phase 1（Q1：偏航检测，P0）

**目标**：对任意一次会话/提交，输出事件流与 drift 评分，并能告警/回滚。

**交付物**：
1. `events.jsonl`（来自 patch.diff/term.log 的规范化事件）
2. `guards.jsonl`（四守卫 + drift_score + action）
3. "最小 UI/CLI"：列出高分事件、显示原因、提供回滚命令

**验收**：
- ≥95% 的越界改动（不在 allowed_paths）被检出
- 假阳性 ≤10%（可通过例外机制逐步下降）

### Phase 2（Q2：模式复用，P1）

**目标**：把"做成的经历"沉淀成模式卡，能在新任务自动检索触发。

**交付物**：
1. `patterns/pc_*.json`（从多个 runs 抽取）
2. 检索与注入：给定 objective/issue_text → 返回命中的模式卡（含两档视图的文案骨架）

**验收**：
- 模式复用率↑、首试成功率↑、平均回合数↓（以小 A/B 验证）

### Phase 3（Q3：动态抽象，P1）

**目标**：同一卡两档视图，按"用户水平 × 任务难度"自动路由。

**交付物**：
1. `profiles/<user>.json`（画像）
2. 路由器：根据画像与任务难度，输出 terse | guided

**验收**：
- 新手在 guided 下成功率/稳定性更高；专家在 terse 下不中断

---

## 🔧 二、数据与接口规范（TS + JSONL + 可选 SQLite）

### 0) 共同枚举

```typescript
// phases/checkpoints
export type Phase = 'reproduce' | 'modify' | 'test' | 'regress';

// tools（新增 plan 类型）
export type Tool = 'edit' | 'shell' | 'browse' | 'plan';

// guard action
export type GuardAction = 'ok' | 'warn' | 'rollback';

// user level & task difficulty
export type UserLevel = 'novice' | 'intermediate' | 'expert';
export type TaskDifficulty = 'low' | 'medium' | 'high';

// confidence levels（Chat-only 用）
export type Confidence = 'low' | 'medium' | 'high';
```

---

### 1) Q1：输入/输出与算法

#### 1.1 目标定义（goal.json）

```typescript
export interface GoalConfig {
  run_id: string;
  objective: string;                         // e.g., "Translate README.md to Chinese"
  allowed_paths: string[];                   // allow-list (prefix match)
  forbidden_paths?: string[];                // optional block-list
  checkpoints: Phase[];                      // ["reproduce","modify","test","regress"]
  required_tests?: string[];                 // names/regex you expect to run/ pass
  allowed_tools_by_phase?: Partial<Record<Phase, Tool[]>>; // default 见下
  thresholds?: { warn: number; rollback: number };         // default 0.5/0.8
  meta?: Record<string, any>;                // 任意扩展
}
```

**默认策略**（若 allowed_tools_by_phase 未给出）：
- reproduce: ['shell','browse']
- modify:    ['edit','shell']
- test:      ['shell']
- regress:   ['shell']

**默认阈值**：warn=0.5，rollback=0.8

#### 1.2 事件（events.jsonl）

```typescript
export interface BaseEvent {
  id: string;                 // uuid
  run_id: string;
  step: number;               // 1,2,3...
  ts?: string;                // ISO time
  phase: Phase;
  tool: Tool;
  why?: string;               // rationale in short
  evidence?: {
    tests?: string[];         // tests names/assertions referenced
    logs?: string[];          // log lines digests or links
    links?: string[];         // issue/PR/docs links
  };
}

export interface EditEvent extends BaseEvent {
  tool: 'edit';
  where: { path: string; start?: number; end?: number };
  what: { diff?: string; ast_hint?: string };
}

export interface PlanEvent extends BaseEvent {
  tool: 'plan';
  where: { path: string; start?: number; end?: number };
  confidence?: Confidence;  // Chat-only 提取的置信度
}

export interface ShellEvent extends BaseEvent {
  tool: 'shell';
  cmd: string;
  exit_code?: number;
  stdout_digest?: string;     // hash/first-N lines
}

export type Event = EditEvent | PlanEvent | ShellEvent;
```

**JSONL 示例**（Diff 路线）：

```json
{"id":"e1","run_id":"r42","step":1,"phase":"modify","tool":"edit","where":{"path":"README.md"},"what":{"diff":"(hunk)"},"why":"from patch.diff"}
{"id":"e2","run_id":"r42","step":2,"phase":"modify","tool":"edit","where":{"path":"requirements.txt"},"what":{"diff":"(hunk)"}}
{"id":"e3","run_id":"r42","step":3,"phase":"test","tool":"shell","cmd":"pytest -k doc_lang_check"}
{"id":"e4","run_id":"r42","step":4,"phase":"test","tool":"shell","cmd":"pytest -k whitelist_diff_check"}
```

**Chat-only 示例**：

```json
{"id":"p1","run_id":"r60","step":1,"phase":"modify","tool":"plan","where":{"path":"README.md"},"why":"计划翻译 README.md","confidence":"medium"}
{"id":"e2","run_id":"r60","step":2,"phase":"modify","tool":"edit","where":{"path":"README.md"},"why":"已将英文内容改为中文","confidence":"high"}
{"id":"t1001","run_id":"r60","step":1001,"phase":"test","tool":"shell","cmd":"pytest -k doc_lang_check"}
```

#### 1.3 守卫输出（guards.jsonl）

```typescript
export interface GuardScores {
  id: string;                 // match event id
  run_id: string;
  step: number;
  scope_guard: number;        // 0~1
  plan_guard: number;         // 0~1
  test_guard: number;         // 0~1
  evidence_guard: number;     // 0~1
  drift_score: number;        // weighted sum
  action: GuardAction;        // ok | warn | rollback
  file?: string;              // for edit events
  notes?: string;             // reason for flag
}
```

**打分算法**（可直接落地）：

```typescript
// 权重（可配置）
const W = { scope: 0.4, plan: 0.3, test: 0.2, evidence: 0.1 };

// 重要：仅对 tool=edit 计分，tool=plan 恒 action=ok
if (event.tool === 'plan') {
  return { scope_guard: 0, plan_guard: 0, test_guard: 0, evidence_guard: 0, 
           drift_score: 0, action: 'ok' };
}

// ScopeGuard：编辑是否越界（prefix allow-list）
scope_guard = (event.tool==='edit')
  ? (inAllowed(event.where.path, goal.allowed_paths) ? 0 : 1)
  : 0;

// PlanGuard：此 phase 是否允许此 tool/此路径类别
plan_guard = (() => {
  const allowTools = goal.allowed_tools_by_phase?.[event.phase] || defaultTools[event.phase];
  if (!allowTools.includes(event.tool)) return 1;
  if (event.tool==='edit' && !inAllowed(event.where.path, goal.allowed_paths)) return 1;
  return 0;
})();

// TestGuard：若 phase 是 test/regress，是否跑了/通过了 required_tests
// MVP：看到相应 pytest 命令则 0，否则 1（或结合 term.log 解析通过率）
test_guard = ((event.phase==='test' || event.phase==='regress') && event.tool==='shell')
  ? (coversRequired(event.cmd, goal.required_tests) ? 0 : 1)
  : 0;

// EvidenceGuard：modify 阶段的 edit 事件，是否带有 tests/logs/links 作为证据
evidence_guard = (event.phase==='modify' && event.tool==='edit')
  ? (event.evidence && (event.evidence.tests?.length || event.evidence.logs?.length || event.evidence.links?.length) ? 0 : 0.5)
  : 0;

// 综合：
drift_score = W.scope*scope_guard + W.plan*plan_guard + W.test*test_guard + W.evidence*evidence_guard;

// 动作：
action = (drift_score >= (goal.thresholds?.rollback ?? 0.8)) ? 'rollback'
       : (drift_score >= (goal.thresholds?.warn ?? 0.5))     ? 'warn'
       : 'ok';
```

**JSONL 示例**：

```json
{"id":"e1","run_id":"r42","step":1,"scope_guard":0,"plan_guard":0,"test_guard":0,"evidence_guard":0,"drift_score":0,"action":"ok","file":"README.md"}
{"id":"e2","run_id":"r42","step":2,"scope_guard":1,"plan_guard":1,"test_guard":0,"evidence_guard":0.5,"drift_score":0.85,"action":"warn","file":"requirements.txt","notes":"not in allowed_paths"}
{"id":"p1","run_id":"r60","step":1,"scope_guard":0,"plan_guard":0,"test_guard":0,"evidence_guard":0,"drift_score":0,"action":"ok","file":"README.md","notes":"plan event, not scored"}
```

**Q1 的评测**：
- 检出率（真正例 / 全部偏航）
- 误报率（假正例 / 全部告警）
- 偏航恢复时间（首次 warn → 回到正确 checkpoint 的步数/秒）
- 覆盖面（被守卫覆盖的偏航类型占比：路径越界/错误 phase/未跑测试/无证据）

---

### 2) Q2：模式卡定义与检索（在 Q1 打好后做）

#### 2.1 模式卡（patterns/pc_*.json）

```typescript
export interface PatternCard {
  version: string;                     // e.g., "1.0"
  pattern_id: string;                  // "pc_doc_only_change"
  title: string;                       // 人类可读标题
  triggers: string[];                  // 检索关键词/正则
  steps: string[];                     // 关键步骤（可用于计划/提示）
  invariants: string[];                // 不变量（必须成立的约束）
  anti_patterns?: string[];            // 禁止或常见误用
  eval_examples?: string[];            // 相关测试/验证名
  risks?: string[];                    // 风险提示（何时需要升级审核/例外）
  views: {                             // Q3 用
    terse: string;                     // 专家版
    guided: string;                    // 新手版
  };
  provenance: {                        // 溯源
    source_runs: string[];             // ["r42","r51"...]
    created_by: string;                // user id
    created_at: string;
  };
  metrics?: {                          // 可选：这张卡带来的 uplift 记录
    reuse_count: number;
    first_try_uplift?: number;
  };
}
```

**最小检索打分**（先规则 + 关键词覆盖；后续可接向量）：

```typescript
score = hits(triggers, goal.objective + issue_text) / triggers.length
// 冲突降权：若卡的 invariants 与 goal.allowed_paths/forbidden_paths 冲突，score -= 0.3
// 阶段性加权：若 Q1 的守卫告警类型与卡的 anti_patterns 相符，优先级↑
```

**沉淀策略**：
- 触发条件：本次 run 通过验证（或人工确认"做对了"）
- 合并：多 run 同类卡可合并（并保留 source_runs 列表）
- 进入库标准：能带来明显 uplift（首试成功率/回合数/时间）才纳入团队库

---

### 3) Q3：画像与路由

#### 3.1 用户画像（profiles/*.json）

```typescript
export interface UserProfile {
  user_id: string;
  self_report: UserLevel;                // 自报水平
  hist_first_try_success: number;        // 0~1
  pref?: 'guided' | 'terse';             // 明示偏好（可覆盖自动路由）
  notes?: string;
}
```

#### 3.2 任务难度估计（无需完美，先启发式）

```typescript
export interface TaskDescriptor {
  files_touched_est?: number;    // 预估修改文件数
  loc_delta_est?: number;        // 预估变更行数
  repo_familiarity?: number;     // 0~1（按贡献/最近互动/文件相似度）
  risk_flags?: string[];         // e.g., ["dependency","security","db-migration"]
}

function estimateDifficulty(d: TaskDescriptor): TaskDifficulty {
  const score = (d.files_touched_est||0)/5 + (d.loc_delta_est||0)/200 + (1-(d.repo_familiarity||0));
  if (score < 0.8) return 'low';
  if (score < 1.6) return 'medium';
  return 'high';
}
```

#### 3.3 视图路由（MVP）

```typescript
function chooseView(profile: UserProfile, task: TaskDescriptor): 'guided'|'terse' {
  const diff = estimateDifficulty(task);
  if (profile.pref) return profile.pref;
  if (profile.self_report === 'novice') return 'guided';
  if (diff === 'high') return 'guided';
  if (profile.hist_first_try_success < 0.5) return 'guided';
  return 'terse';
}
```


---

### 4) 可选数据库（SQLite DDL，占位可后置）

JSONL 先跑通，SQLite 便于做统计/报表/多用户协作。

```sql
-- runs
CREATE TABLE runs (
  run_id TEXT PRIMARY KEY,
  created_at TEXT,
  objective TEXT
);

-- goals
CREATE TABLE goals (
  run_id TEXT,
  content JSON,
  PRIMARY KEY(run_id)
);

-- events
CREATE TABLE events (
  id TEXT PRIMARY KEY,
  run_id TEXT,
  step INTEGER,
  ts TEXT,
  phase TEXT,
  tool TEXT,
  path TEXT,
  cmd TEXT,
  payload JSON
);

-- guards
CREATE TABLE guard_scores (
  id TEXT PRIMARY KEY,
  run_id TEXT,
  step INTEGER,
  scope REAL, plan REAL, test REAL, evidence REAL,
  drift REAL, action TEXT, file TEXT, notes TEXT
);

-- patterns
CREATE TABLE patterns (
  pattern_id TEXT PRIMARY KEY,
  version TEXT,
  title TEXT,
  content JSON,
  reuse_count INTEGER DEFAULT 0
);

-- profiles
CREATE TABLE profiles (
  user_id TEXT PRIMARY KEY,
  content JSON
);
```

---

## 🚀 三、端到端（以你的"文档任务跑题"为例）

**输入**：
- `goal.json`：只允许 README.md / docs/**
- `patch.diff`：改了 README.md 并误改 requirements.txt
- （可选）`term.log`：包含 pytest -k doc_lang_check 与 pytest -k whitelist_diff_check

**步骤**：
1. `patch2events` → 生成两条 edit 事件（README.md / requirements.txt）
2. `term2events` → 生成两条 shell 事件（测试）
3. `events2guards` → 对 requirements.txt 给出 Scope=1.0，Plan=1.0，Evidence=0.5 → drift=0.85 → action=warn
4. （通过/确认后）抽卡 → `pc_doc_only_change` 入库
5. 新任务"翻译文档"启动时，检索命中该卡：
   - terse 给专家：白名单 + 禁改依赖 + 两个检查
   - guided 给新手：逐步配置白名单/语言检测/例外流程/坑点
6. 度量：相似任务在有卡 vs 无卡下，比较首试成功率/回合数/用时，出 ablation 图。

---

## 🛠️ 四、你今天就能推进的细节（Q1 打穿）

1. **把四个守卫写成纯函数**（方便单元测试）
   - `scopeGuard(e, goal) -> 0|1`
   - `planGuard(e, goal) -> 0|1`
   - `testGuard(e, goal, termLog?) -> 0|1`
   - `evidenceGuard(e) -> 0|0.5`
   - `driftScore(scores, weights, thresholds) -> {score, action}`

2. **建立 8 个最小单测**
   - 允许路径编辑 / 非允许路径编辑
   - modify 阶段使用非法 tool
   - 测试应跑未跑 / 已跑
   - 有/无 evidence
   - **plan 事件恒 action=ok（不计分）**
   - **Chat-only vs Diff 路线等价性**
   - 综合 case 触发 warn 与 rollback

3. **做一个"例外机制"**（把假阳性降下来）
   - UI/CLI：`ack --reason="需要临时改依赖以修 build"`
   - 例外写入 `events.jsonl` 的 `evidence.links/notes`，下一次守卫见到 有效例外 可降权

4. **工具链验证**
   - `tools/chat2events.py`：Chat-only 提取器（planned vs applied）
   - `tools/events2guards.py`：四守卫 + plan 忽略策略
   - `scripts/e2e_chat_only.py`：一键 Chat-only 流程

---

## 🔗 五、为何 Q1→Q2→Q3 是正确的依赖关系

- **Q1 输出 = Q2/Q3 的训练与检索数据**：没有 `events.jsonl` 的"事实"，模式卡只能凭空想象。
- **Q1 还能给 Q2 提供"anti_patterns/risks"**：哪些越界最常见？直接写进卡，下次先天规避。
- **Q3 的"难度估计/视图路由"需要 Q1 的统计**：历史首试成功率、偏航率、偏航恢复时间 → 画像与路由的依据。

---

## ✅ 下一步行动

如果你认可上面的规范，我可以把这些 TS 接口 + 守卫函数样例直接合入你仓库的 `types/` 与 `src/guards/`，并加上8 条单测；你就能马上跑 Phase 1 的端到端（不依赖外部模型）。

接着，我们用 3–5 次真实 run 抽出 第一批模式卡（Q2），最后再接上 视图路由（Q3）。