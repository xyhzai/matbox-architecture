# Matbox AI 任务运行时 / Durable AI Task Runtime（F-TASK-001）

正式开发文档 · V1.0-RC · 2026-08-30

## 当前定位

本专项解决"AI员工执行小时级/天级长任务时，怎么等待、怎么在中途暂停、怎么在崩溃后从断点恢复、怎么让人类接管"的问题。是 Platform Core 的共享运行时，被所有需要长时间运行的AI员工业务模块（F-AIEMP-001等）依赖。

**这是核查《Matbox_多端平台_CURRENT_正式开发文档_V3.0》F-TASK-001章节后确认的模块**——原本与 [F-QUEUE-001](Matbox_任务队列_正式开发文档_V1.0-RC.md) 存在引擎选型冲突（本模块选Temporal，F-QUEUE-001原选Hatchet），2026-08-30已解决：**两者共用同一套Temporal实例，但业务逻辑保持分开**（详见架构原则第31条）。本文档补齐F-TASK-001自己一直缺失的独立正式文档。

**2026-08-30核对AI员工底层包后补强**：底层包的Control Plane Runtime Spec给出了比本文档更细的TaskRun状态机、Checkpoint/Resume正式对象、以及架构原则第28条一直挂账等待的Kill Switch具体设计（Pause/Suspend/Kill/Takeover/Revoke/Retire），本文档采纳并入，状态机、数据Contract、P0规则均有相应调整。任务分发不引入NATS等额外消息队列——Temporal原生支持按能力(text/image/video/3d/browser)分Worker Pool+内置PriorityKey优先级，足够覆盖底层包`worker_queue_contract.md`提出的需求，不新增第三个基础设施组件（详见本次决定的技术选型说明）。

**DocID**: MATBOX-TASK-RUNTIME-20260830-V1.0-RC（2026-08-30二次修订）
**状态**: DRAFT_RESEARCH_COMPLETE（内容级核查通过，未进入 Stage 10 真实施工）
**依赖方（已知阻塞）**: 与 F-QUEUE-001 共用同一套Temporal基础设施部署

## 1｜不可变原则

1. 不让HTTP长连接承载业务任务——任务状态必须能在客户端断线重连后从服务端真实状态补齐，不依赖前端内存。
2. 不把Temporal/Redis当业务真相源（Source of Truth）——`ai_task`/`ai_task_step`/`ai_task_event` 才是业务层SoT，Temporal History是执行层记录。
3. Activity不得直接写client response——所有进度必须经Task API+事件序列传递给前端。
4. 任务队列必须按租户/按任务类型隔离，不允许一个租户的异常任务（死循环、批量堆积）通过noisy-neighbor效应拖垮其他任务执行。

## 2｜全球调研结论（2026-08-30）

### 2.1 为什么是Temporal，不是重新选型（复用已确认结论）

本模块与F-QUEUE-001管的是同类问题（长时间运行的任务怎么持久化、怎么恢复），2026-08-30已完成一次跨模块技术选型核实并确认结论：Hatchet官方不支持Java SDK（仅TS/Python/Go/Ruby），与《多端平台V3.0》确定的Java/Spring Boot（RuoYi）技术栈不契合；Temporal有成熟Java SDK，原生契合。真实AI场景证据：OpenAI自己的Codex生产环境跑在Temporal上，处理每分钟数百万级请求；2026年3月OpenAI Agents SDK正式GA集成Temporal。Temporal Cloud托管服务$100/月起，此前"自建运维负担重"的否决理由不再成立（详见[Matbox_任务队列_正式开发文档](Matbox_任务队列_正式开发文档_V1.0-RC.md)2.1节、架构原则第31条）。

### 2.2 与F-QUEUE-001的边界划分

| | F-QUEUE-001（任务队列） | F-TASK-001（本模块） |
|---|---|---|
| 管什么 | WorkPackage（施工任务）的派发、冲突检测、执行追踪 | AI员工的通用业务长任务（goal驱动的多步骤执行） |
| SoT | RC5 WorkPackage业务状态 + QueueRun技术状态 | ai_task/ai_task_step/ai_task_event |
| Temporal用法 | 每个WorkPackage派发映射一个Workflow执行 | 每个ai_task映射一个Workflow，含pause/resume/cancel/takeover信号 |
| 共用什么 | 同一套Temporal集群/Cloud账号，不建第二套持久化工作流系统 | 同上 |

不共用的部分：两者的业务语义、数据表、API契约完全独立，避免"因为共用引擎就混用业务状态字段"（这是[Matbox_任务队列_正式开发文档](Matbox_任务队列_正式开发文档_V1.0-RC.md)已明确记录过的真实风险点：QueueRun.runStatus不能与RC5 WorkPackage状态混用，本模块同理，ai_task状态不能与QueueRun状态混用）。

### 2.3 状态机升级（2026-08-30从AI员工底层包并入，更细）

原状态枚举`RUNNING|PAUSED|WAITING|COMPLETED|CANCELLED|FAILED|NEEDS_TAKEOVER`偏粗，AI员工底层Control Plane Runtime Spec给出的状态机更完整，本模块采纳：

**CREATED → VALIDATED → QUEUED → RUNNING → WAITING_APPROVAL / WAITING_DEPENDENCY → SUCCEEDED / FAILED / CANCELLED**

所有状态变更必须带`version`/`expected_state`防并发覆盖（乐观锁），并生成Audit/Event。PAUSED、NEEDS_TAKEOVER不再是独立顶层状态，改为RUNNING状态下的子标记（`pausedFlag`/`takeoverFlag`），因为"暂停"和"接管"本质是RUNNING状态下的一种控制干预，不是任务本身走到了新阶段——这个区分是核对底层包状态机定义后发现的建模问题，原设计混淆了"任务所处阶段"和"任务是否被人工干预"两个维度。

### 2.4 Kill Switch正式设计（2026-08-30从AI员工底层包并入，解决架构原则第28条挂账项）

架构原则第28条曾把Kill Switch"挂账在Agent Runtime模块上，等AI员工正式文档到手时作为硬性核查项"——现在到手，具体设计如下（源自Control Plane Runtime Spec第8节）：

| 动作 | 语义 |
|---|---|
| Pause Employee | 停止新任务进入，可恢复（作用于F-AIEMP-001的员工实例，不是单个任务） |
| Suspend Employee | 安全/合规停职，拒绝新执行 |
| Kill Task | 终止指定TaskRun并触发补偿（作用于本模块的AiTask） |
| Takeover | 人工获得当前任务控制权 |
| Revoke | 撤回身份/工具授权（对应F-CRED-001的Grant撤销） |
| Retire | 员工实例不再接新任务，保留历史审计 |

其中Kill Task属于本模块（TASK-F005），Pause/Suspend/Revoke/Retire作用于AI员工身份层，属于F-AIEMP-001（见该文档更新）。

### 2.5 任务分发不引入NATS，用Temporal原生能力（2026-08-30技术选型确认）

底层包`worker_queue_contract.md`要求"按text/image/video/3d/browser分优先级队列"，本地示例用NATS JetStream实现，但明确"implementation MAY replace transport behind QueueAdapter"，未强制。查证确认Temporal原生支持：①按能力路由到不同Worker Pool（GPU/普通机器各自的Task Queue）；②内置PriorityKey（1-5级）优先级，同一Task Queue内自动按优先级派发，不需要额外队列系统。跟外部系统的事件分发（webhook等）复用本会话已建立的Transactional Outbox+Dispatcher模式（同F-APPROVAL-001）。**结论：不引入NATS JetStream，Postgres+Temporal两个组件覆盖全部需求**，避免团队多维护第三套基础设施（详见本次决定说明；来源：[Temporal Task Queue Priority and Fairness](https://docs.temporal.io/develop/task-queue-priority-fairness)、[Route Specialized Workloads with Task Queues](https://temporal.io/blog/route-specialized-workloads)）。

### 2.6 长时程任务中途漂移检测（2026-08-30从"AI员工能力缺口调研清单"#4并入）

长时程Agent研究确认真实风险："早期的小错误会在后续阶段累积成严重失败"，Agent会"逐渐漂移进不安全的状态"。TASK-F005的Checkpoint是**崩溃恢复**用的，不解决"任务还在跑、没崩溃，但已经偏离原计划"这个问题。**结论**：长任务（步骤数超过阈值或运行时长超过阈值）必须定期做"计划再验证"——把当前执行结果跟原始goal/plan对比，偏离超过阈值触发人工Takeover或自动终止，不是等到任务彻底失败或用户投诉才发现。

### 2.7 Temporal Event History硬限制与Continue-As-New（2026-08-30从"AI员工能力缺口调研清单"#8并入）

Temporal官方文档确认：单个Workflow Execution的Event History硬限制**51,200个事件或50MB**，超过10,240个事件/10MB即开始警告。本模块管的是小时/天级长任务，步骤多、暂停恢复次数多、信号多时真实会撞到这条线。官方推荐做法是**Continue-As-New**——跑到接近上限时把Workflow重置成一个新实例，历史清零但业务状态（ai_task的业务字段）通过延续参数传递给新实例，不丢失。**这是官方文档直接确认的做法，不是我们自己猜的方案**。

### 2.8 任务内自我纠错——Reflexion式闭环（2026-08-30从"AI员工能力缺口调研清单"#12并入，仅"单次任务内"部分）

查证确认："每个动作视为可证伪、直到被验证为止"是2026年生产级Agent系统的标准控制循环，几乎每个主流框架都把"生成→自我批判→修正"这个闭环直接内建到控制流里，这条研究脉络（Self-Refine→Reflexion→CRITIC→Self-RAG→PRM）从2023年演进到2026年已经是成熟共识，不是实验性想法。真实权衡：反思/校验会带来额外的模型调用次数和Token开销，这正是为什么不能无限重试，必须跟DELEGATION-F005已确认的"硬上限防重试风暴"用同一个原则，不是重新发明。**结论**：本模块只解决"单次任务/单个步骤内的自我纠错"，属于结构现在就能定的部分；"跨任务、靠生产数据驱动的长期自动进化"（如Cursor Composer每5小时用生产数据更新一次）需要真实生产流量才能设计具体机制，本模块不覆盖，留在调研清单🟡分层。

## 3｜Own / Reuse / Must Not Rebuild

| 类型 | 对象 | 说明 |
|---|---|---|
| OWN | ai_task/ai_task_step/ai_task_event schema、Task API、pause/resume/takeover业务语义 | Matbox自己的AI任务生命周期业务规则 |
| REUSE | Temporal Workflow/Activity/Timer/Signal/Versioning（与F-QUEUE-001共用同一套基础设施） | 不重新造持久化工作流引擎，不建第二套Temporal部署 |
| MUST NOT REBUILD | Temporal自身的crash恢复、replay、幂等去重机制 | 直接用Temporal原生能力，不在应用层重新实现 |

## 4｜Feature Register

| FeatureID | 名称 | 说明 |
|---|---|---|
| TASK-F001 | Task状态机 | ai_task/ai_task_step/ai_task_event，WorkflowBridge做Task命令到Temporal Signal的映射 |
| TASK-F002 | 暂停/恢复/人接管 | pause/resume/cancel/edit plan/takeover信号，Activity不得直接写client response |
| TASK-F003 | Workflow版本管理 | version pin，防止运行中任务因代码升级发生不兼容执行（对应Gate G-P0-WFVERSION-001） |
| TASK-F004 | 断线重连状态补齐 | 前端断线重连后从服务端真实状态重新拉取，不信任本地缓存的进度 |
| TASK-F005 | Kill/Checkpoint/Resume | Kill Task+补偿，Checkpoint对象(state_snapshot_uri/resume_token)，Resume对象(expected_state/lease) |
| TASK-F006 | 中途漂移检测 | 长任务定期做计划再验证，偏离原goal超阈值触发Takeover或终止 |
| TASK-F007 | Continue-As-New | Event History接近硬限(51,200事件/50MB)时重置Workflow实例，业务状态延续不丢失 |
| TASK-F008 | 任务内自我纠错（Reflexion式） | 单步骤产出经"生成→自我批判→修正"闭环，达标或触碰硬上限才进入下一步；跨任务长期进化不在本条范围 |

### TASK-F001 · Task状态机（2026-08-30状态枚举升级，见2.3节）
- **目标**：`employee + goal + context snapshot + version pins + budget` 作为上游输入，驱动一个可暂停、可恢复、可追溯的多步骤任务执行。状态机：CREATED→VALIDATED→QUEUED→RUNNING→WAITING_APPROVAL/WAITING_DEPENDENCY→SUCCEEDED/FAILED/CANCELLED。
- **验收标准**：crash后从最后一个已确认的ai_task_step恢复，不重复执行已完成的副作用（幂等）；状态变更必须带version/expected_state防并发覆盖。

### TASK-F002 · 暂停/恢复/人接管
- **目标**：人类可以在任务执行中途暂停、编辑执行计划、接管控制权，不需要等任务自然结束。
- **验收标准**：接管后AI员工的后续执行必须感知到计划已被人类修改，不能忽略人类的编辑继续按旧计划跑。

### TASK-F003 · Workflow版本管理
- **目标**：Task Runtime代码升级时，正在运行的旧版本任务不因新代码部署而执行错误逻辑或直接崩溃。
- **验收标准**：新旧worker混跑期间，老版本任务能被老逻辑正确处理完，不出现新旧版本状态错乱（对应Gate G-P0-WFVERSION-001）。

### TASK-F004 · 断线重连状态补齐
- **目标**：客户端断线重连后，任务列表/详情/时间线显示的是服务端真实状态，不是断线前的过期本地状态。
- **验收标准**：人为模拟断线重连场景，验证前端显示与服务端状态一致（对应Gate G-P1-PROGRESS-001）。

### TASK-F005 · Kill/Checkpoint/Resume（2026-08-30从AI员工底层包并入，解决架构原则第28条挂账项）
- **目标**：Kill Task终止指定任务并触发补偿；Checkpoint保存可恢复的执行快照；Resume从Checkpoint精确恢复，不重复产生副作用。
- **验收标准**：Worker崩溃可从Checkpoint恢复；重复的Resume命令不产生重复副作用；Kill触发的补偿动作必须留痕（对应F-ACTION-001的compensation引用）。

### TASK-F006 · 中途漂移检测（2026-08-30从调研清单#4并入）
- **目标**：步骤数或运行时长超过阈值的长任务，定期把当前执行结果跟原始goal/context snapshot对比，偏离超过阈值触发人工Takeover或自动终止，不等任务彻底失败或用户投诉才发现。
- **2026-09-04场景模拟发现的断点**：推演"偏离阈值触发人工Takeover"这一步——原描述只说"触发人工Takeover"，没写这个"触发"具体怎么让人真的看到。查证发现跟本轮在F-QUEUE-001的QUEUE-F010最初犯的是同一类问题（"转人工"没真调用审批/通知机制）。[Matbox_证据审计与监控_正式开发文档](Matbox_证据审计与监控_正式开发文档_V1.0-RC.md)的OBS-F004（高信号告警规则）原话就写着要重点抓"行为偏离历史基准（drift）"——这跟本条要检测的东西是同一件事，本模块不该另起一套通知逻辑。**修正**：检测到偏离超过阈值时，本模块调用OBS-F004生成一条可行动告警（不是自己发通知/建通知表），告警接收人决定执行Takeover还是终止——这两个动作本身已经是TASK-F005 Kill Switch里定义好的具体操作，不用新造，缺的只是"从检测到发出告警"这一步的连接。
- **验收标准**：人为构造任务执行逐渐偏离原目标的场景，验证在偏离超过阈值时被检测到、且能在OBS-F004的告警记录里查到对应条目，不是只在ai_task表里悄悄改了个字段没人看得到。

### TASK-F007 · Continue-As-New（2026-08-30从调研清单#8并入，Temporal官方推荐做法）
- **目标**：单个Workflow Execution的Event History接近硬限（51,200事件/50MB，10,240/10MB时预警）前，主动Continue-As-New重置为新Workflow实例，ai_task的业务状态通过延续参数传递，不丢失。
- **验收标准**：人为构造超长步骤数的任务，验证在接近History上限前完成Continue-As-New且任务业务状态（AiTask.state等字段）连续不丢失。

### TASK-F008 · 任务内自我纠错（Reflexion式，2026-08-30从调研清单#12并入，仅"单次任务内"部分）
- **目标**：AiTaskStep产出后先经AI员工自我批判（对照该步骤的验收标准/goal），不达标则自动修正重试，达标或触碰硬上限（selfCorrectionMaxAttempts）才进入下一步或转人工审批，不是产出即通过。
- **依赖**：与DELEGATION-F005共用"硬上限防止无限重试/风暴"这一条原则，不新建一套上限逻辑。
- **Out of Scope（明确排除）**：跨任务/跨会话的长期自动进化（靠生产数据反哺持续更新AI员工行为）不属于本条，需要真实生产流量数据才能设计具体机制，留在调研清单🟡分层，不在本次执行范围内。
- **2026-09-04系统性排查发现（同一模式第10处）**：原文"触碰硬上限...转人工审批"没写这个"转人工审批"具体怎么转——跟本文档TASK-F006、[Matbox_任务队列_正式开发文档](Matbox_任务队列_正式开发文档_V1.0-RC.md)QUEUE-F010、[DQ正式文档](Matbox_代码持续质检与安全自检_正式开发文档_V1.1-RC_CURRENT_Stage9内容级重验版_2026-08-19.docx)BLOCKED_MANUAL是同一类断点。**修正**：触碰`selfCorrectionMaxAttempts`时，调用[F-APPROVAL-001](Matbox_AI动作审批_正式开发文档_V1.0-RC.md)创建`AiApproval`记录（`actionSourceType=TASK_SELFCORRECTION`，F-APPROVAL-001已同步新增这个来源类型），不是只把`AiTaskStep.status`标一下就算完。
- **验收标准**：人为构造一个初次产出有明显缺陷的步骤，验证自我批判能捕捉到并在硬上限内修正；超过硬上限的步骤必须转人工审批，且能在F-APPROVAL-001查到对应的AiApproval记录，不允许无限重试（对应P0规则）。

## 5｜核心数据 Contract（逻辑模型，可直接建表/建接口）

**AiTask**（2026-08-30状态枚举升级）
taskId, tenantId, employeeId, goal, contextSnapshotRef, versionPin, budgetRef, temporalWorkflowId, state(CREATED|VALIDATED|QUEUED|RUNNING|WAITING_APPROVAL|WAITING_DEPENDENCY|SUCCEEDED|FAILED|CANCELLED), pausedFlag(bool), takeoverFlag(bool), version(乐观锁), idempotencyKey, createdAt, updatedAt

**ContextSnapshot**（`contextSnapshotRef`指向的内容，2026-09-02首次正式定义内部结构，落实架构原则第41条+专项00f发现的缺口——此前只是个不透明引用，没人定义过里面到底能装什么）
snapshotId, rawInput（原始指令文字）, attachments[]?（参考图片/尺寸文档等StorageRef列表，设计师类任务的核心输入）, structuredParams{}?（预算/尺寸/风格标签等结构化参数，任务类型不同字段不同，不强制统一Schema）, sourceRoutingRequestId（关联F-ORCHESTRATOR-001的RoutingRequest，同一批附件/参数不重复上传）

**AiTaskStep**（2026-08-30新增自我纠错字段，对应TASK-F008；2026-09-04补`subagentId`，见下方说明）
stepId, taskId, stepIndex, description, actionRef(关联F-ACTION-001的actionId，若该步骤涉及外部动作), **subagentId?**（关联F-AIEMP-001 AIEMP-F006的Subagent，标注这一步具体是哪个Subagent做出的判断，不填代表由员工顶层Prompt直接处理未经Subagent分工）, status(PENDING|RUNNING|SUCCEEDED|FAILED|SKIPPED), checkpointId?, selfCorrectionAttempts(int，默认0), selfCorrectionMaxAttempts(int，具体数值Stage 10用真实数据调参), startedAt, finishedAt
**2026-09-04自查发现的真实缺口**：F-AIEMP-001新增AIEMP-F006（Subagent分工层）后，其验收标准要求"给定一个真实任务，可以追溯到具体是哪个Subagent做出的判断"——但本实体此前没有任何字段能承载这个追溯，AIEMP-F006这条验收标准在当时实际是无法满足的。本模块是任务执行记录的真实归属方（F-AIEMP-001明确是配置层、不记执行），`subagentId?`补在step级别而不是AiTask顶层，是因为同一个任务内部不同步骤完全可能由不同Subagent处理（参照Salesforce真实案例：路由→检索→研究，一个任务里换了好几个Subagent），顶层单个字段装不下这个粒度。

**Checkpoint**（2026-08-30从AI员工底层包`checkpoint`表并入）
checkpointId, taskId, stepId?, stateSnapshotUri, checksum, resumeTokenHash, createdAt

**AiTaskEvent**（2026-09-02新增`INSTRUCTION_APPENDED`事件类型）
eventId, taskId, eventType(PAUSED|RESUMED|CANCELLED|PLAN_EDITED|TAKEOVER|TIMER_FIRED|APPROVAL_WAIT|KILLED|INSTRUCTION_APPENDED), actorId(AI或人类), payload, occurredAt

**API 端点（最小集合）**
- `POST /task` — 创建一个新的AI员工长任务，返回taskId+temporalWorkflowId
- `POST /task/{taskId}/pause` — 暂停任务（通过Temporal Signal传递，Activity不直接响应client）
- `POST /task/{taskId}/resume` — 恢复任务
- `POST /task/{taskId}/takeover` — 人类接管，标记后续步骤需要人工确认
- `POST /task/{taskId}/instructions` — 追加一条轻量指令（2026-09-02新增，落实架构原则第41条+专项00f发现的缺口）：任务运行中，人类想补充一句"沙发颜色改成米色"这种小修正，不需要走`takeover`这种重量级"接管控制权"流程；轻量指令进入AI员工当前步骤的输入队列，AI员工按自己的判断决定何时采纳，不强制打断当前执行，产生`INSTRUCTION_APPENDED`事件留痕；如果需要立即停下重新规划，仍然用`takeover`
- `POST /task/{taskId}:cancel` — Kill Task，终止并触发补偿（对应AI员工底层`/v1/tasks/{run_id}:cancel`）
- `GET /task/{taskId}` — 查询任务当前状态+时间线（断线重连后前端调用此接口补齐状态）

## 6｜P0 冻结规则

1. Activity直接写client response：不允许，必须经Task API+事件序列。
2. Redis或Temporal History被当作业务SoT查询：不允许，业务查询必须走ai_task/ai_task_step/ai_task_event。
3. 断线重连后前端信任本地缓存而非服务端真实状态：不允许（对应Gate G-P1-PROGRESS-001）。
4. Workflow版本不兼容导致运行中任务执行错误逻辑：不可降级P0（对应Gate G-P0-WFVERSION-001）。
5. 状态变更不带version/expected_state（并发覆盖风险）：不允许。
6. Resume/重放造成重复发布、重复扣费、重复副作用：不可降级P0。
7. 任务内自我纠错（TASK-F008）无硬上限、无限重试：不允许，必须与DELEGATION-F005同一套"硬上限防重试风暴"原则，超限必须转人工审批。

## 7｜当前唯一继续断点

Stage 10（真实部署Temporal或接入Temporal Cloud，与F-QUEUE-001协调共用同一套实例）尚未开始。下一步：把 TASK-F001~F004 转成 WorkPackage，部署时与F-QUEUE-001的Temporal实例部署计划合并考虑，避免重复建集群。

## 附录｜来源

- 内容来源：《Matbox_多端平台_CURRENT_正式开发文档_V3.0》F-TASK-001 章节（2026-08-30核对确认，详见架构原则第31条）
- 技术选型依据（与F-QUEUE-001共享，2026-08-30核实）：Temporal官方Java SDK commit `af2f8537727ed62e89bebdfb2da206084b270e59`、[Hatchet vs Temporal](https://hatchet.run/versus/hatchet-vs-temporal)、[Temporal Cloud Pricing Update](https://temporal.io/blog/temporal-cloud-pricing-update)、[Of course you can build dynamic AI agents with Temporal](https://temporal.io/blog/of-course-you-can-build-dynamic-ai-agents-with-temporal)
- **状态机/Kill Switch/Checkpoint升级依据（2026-08-30）**：《Matbox_AI_Employee_System_V6.3_Final_Frozen》底层包`05_Control_Plane_Runtime/V6.3_Control_Plane_Runtime_Spec.docx`第3/5/8节、`04_Domain_Schema/migrations/003_runtime.sql`（task_run/task_step/checkpoint表）
- **TASK-F008依据（2026-08-30）**：[Matbox_AI员工能力缺口调研清单_2026-08-30.md](Matbox_AI员工能力缺口调研清单_2026-08-30.md)#12；[Agentic AI self-correction: How to build systems that fix their own mistakes — Weights & Biases](https://wandb.ai/site/articles/agentic-ai-self-correction-how-to-build-systems-that-fix-their-own-mistakes/)；[Reflection Agent: Self-Correcting AI](https://www.emergentmind.com/topics/reflection-agent)
- **ContextSnapshot结构定义+`/task/{taskId}/instructions`轻量指令接口依据（2026-09-02）**：[Matbox_专项00f_AI员工指令交互流程设计_2026-09-02.md](技术选型报告/Matbox_专项00f_AI员工指令交互流程设计_2026-09-02.md)；架构原则第41条
- **不引入NATS的技术选型依据（2026-08-30）**：[Temporal Task Queue Priority and Fairness](https://docs.temporal.io/develop/task-queue-priority-fairness)、[Route Specialized Workloads with Task Queues](https://temporal.io/blog/route-specialized-workloads)
- **TASK-F006/F007依据（2026-08-30）**：[Matbox_AI员工能力缺口调研清单_2026-08-30.md](Matbox_AI员工能力缺口调研清单_2026-08-30.md)#4#8；[Managing very long-running Workflows with Temporal](https://temporal.io/blog/very-long-running-workflows)；[Workflow Execution limits | Temporal Platform Documentation](https://docs.temporal.io/workflow-execution/limits)
- **`AiTaskStep.subagentId`依据（2026-09-04）**：F-AIEMP-001新增AIEMP-F006（Subagent分工层，见架构原则第72条）后自查发现，AIEMP-F006自己的验收标准要求"能追溯到具体是哪个Subagent做出的判断"，但当时本实体没有字段能承载，属真实契约缺口，本次同步补上
