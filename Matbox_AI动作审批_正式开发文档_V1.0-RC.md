# Matbox AI 动作审批 / AI Action Approval + Transactional Outbox Bridge（F-APPROVAL-001）

正式开发文档 · V1.0-RC · 2026-08-30

## 当前定位

本专项解决"高风险AI Action怎么可靠地跟企业审批流程（Flowable BPM）桥接，事务提交后才恢复durable workflow"的问题——防止DB事务还没提交就先发出外部信号或消息，导致状态不一致。是 [F-ACTION-001](Matbox_Action网关_正式开发文档_V1.0-RC.md) 高风险动作的审批环节，被F-TASK-001（AI员工长任务中途需要人类批准时）依赖。**2026-09-04新增：也被[F-QUEUE-001](Matbox_任务队列_正式开发文档_V1.0-RC.md)的QUEUE-F010（Implementer AI施工期间实时拦截，命中Tier3/4动作时）依赖**——场景模拟发现QUEUE-F010此前"转人工"只是改了个状态字段，没有真正创建审批请求，本模块是唯一的审批-通知-决策桥接入口，两类高风险动作（AI员工业务动作 / Implementer AI施工动作）共用同一套审批流程，不新建第二套。**同一轮系统性排查又发现F-TASK-001的TASK-F008（任务内自我纠错触碰硬上限）也有同样断点，已接上（`actionSourceType=TASK_SELFCORRECTION`）**——三类高风险/需人工场景全部共用本模块一套流程，不是各自为政。

**这是核查《Matbox_多端平台_CURRENT_正式开发文档_V3.0》F-APPROVAL-001章节后确认的模块**。技术选型直接复用已建成的RuoYi Flowable BPM引擎和已确认的Temporal决定，Transactional Outbox是成熟工业模式，不构成新的厂商选型判断。

**2026-08-30核对AI员工底层包**：底层包的Approval Service（`approval`表）**没有指定具体用什么BPM引擎**，只定义了抽象的审批状态机（PENDING/APPROVED/REJECTED/超时/撤回）和字段要求——本文档选RuoYi Flowable落地这个抽象契约，属于"补齐底层包没规定的实现细节"，不是冲突。已核对字段并补充：`requested_payload_hash`（审批的是哪个具体payload的哈希，防止审批通过后payload被偷换）、`decision_reason`（审批/拒绝理由）、`expires_at`（审批本身也有超时时间，不只是Action有超时）。

**DocID**: MATBOX-APPROVAL-OUTBOX-20260830-V1.0-RC
**状态**: DRAFT_RESEARCH_COMPLETE（内容级核查通过，未进入 Stage 10 真实施工）
**依赖方（已知阻塞）**：[F-ACTION-001](Matbox_Action网关_正式开发文档_V1.0-RC.md)（本轮同步建成）、F-QUEUE-001/F-TASK-001的Temporal基础设施（已建成）

## 1｜不可变原则

1. 不建第二套BPM引擎——审批流程复用RuoYi已有的Flowable，不重复造轮子。
2. DB commit前不允许signal外部系统或发外部消息——必须先写business state+outbox在同一事务，commit后（AFTER_COMMIT）才触发下游。
3. 审批必须绑定具体action/version/actor/time，不能是模糊的"批准了"，要能追溯到批准的是哪个版本的动作。
4. 同一outbox事件不能因dispatcher重启而重复触发副作用（幂等）。
5. **高风险动作的审批人必须是真人，不允许AI或纯规则引擎代替人类做最终批准决定**（2026-09-02，见架构原则第42条#10；欧盟AI法案第14条对高风险AI系统的人工监督是硬性法定要求，不是Matbox自选的产品偏好，不可因为"效率"或"审批人不在线"而降级）。

### 1.1 风险等级对应审批人规则（2026-09-02补充，落实第1节第5条，此前只有P0骨架）

审批人要求随F-ACTION-001已定义的`riskLevel`（0-5，blast-radius风险半径检查产出）分级，不是所有审批都要求真人，但高风险区间没有例外：

| riskLevel区间 | 审批人要求 | 说明 |
|---|---|---|
| 0-1（低风险） | 可配置为自动通过或规则引擎审批 | 如只读查询、租户内部低影响操作，不强制走人工审批队列，由租户在AIEMP-F001 permissionPolicy里自行配置是否需要审批 |
| 2-3（中风险） | 默认真人审批，租户可自行决定是否降级为规则引擎 | 企业可根据自身风险偏好调整，但降级决定本身需要留痕（关联AIEMP-F004配置审计），不能默认静默降级 |
| 4-5（高风险） | **强制真人审批，不可配置、不可降级** | 对应欧盟AI法案第14条人工监督要求，AiApproval记录的`decidedBy`在riskLevel 4-5时必须是真实人类用户ID，不允许系统账号/AI身份/纯规则引擎自动决定 |

## 2｜全球调研结论

本模块的核心模式是Transactional Outbox（事务性发件箱）——2026年分布式系统处理"数据库状态变更"与"触发外部副作用"一致性问题的成熟标准模式（避免双写不一致），不是需要独立验证厂商选型的问题，而是标准架构模式的正确落地。技术底座（Flowable BPM、Temporal）均已在架构原则第31条完成独立验证，本模块直接复用，不重复调研。

## 3｜Own / Reuse / Must Not Rebuild

| 类型 | 对象 | 说明 |
|---|---|---|
| OWN | ApprovalBridge/OutboxDispatcher、ai_approval映射、businessKey契约 | Matbox自己的审批-动作桥接业务规则 |
| REUSE | RuoYi Flowable BPM发布器、Temporal signal机制（与F-QUEUE-001/F-TASK-001共用基础设施） | 不重新造BPM引擎和持久化工作流 |
| MUST NOT REBUILD | Spring ApplicationEvent的同步事件机制不可直接用于外部side effect | 必须走outbox异步dispatch，不允许同步触发 |

## 4｜Feature Register

| FeatureID | 名称 | 说明 |
|---|---|---|
| APPROVAL-F001 | ai_approval映射 | 高风险ProposedAction与Flowable审批实例的businessKey绑定 |
| APPROVAL-F002 | Transactional Outbox | 同事务写business state+outbox_event，AFTER_COMMIT才dispatch |
| APPROVAL-F003 | Outbox Dispatcher | retry/DLQ/向Temporal发signal恢复durable workflow |
| APPROVAL-F004 | 审批操作集 | approve/reject/timeout/withdraw，含mobile审批入口 |

### APPROVAL-F001 · ai_approval映射
- **目标**：高风险AI Action触发审批时，创建ai_approval记录并绑定Flowable的businessKey，二者一一对应可追溯。
- **验收标准**：审批记录绑定具体action的版本号和发起人/时间，不是模糊引用。

### APPROVAL-F002 · Transactional Outbox
- **目标**：business state变更（如审批状态更新）与outbox_event写入在同一DB事务完成，不在commit前触发任何外部信号。
- **验收标准**：人为让事务在写outbox后、commit前crash，验证不会有外部信号被误发出。

### APPROVAL-F003 · Outbox Dispatcher
- **目标**：dispatcher异步消费outbox_event，向Temporal发送signal恢复对应的durable workflow；dispatcher重启后不重复触发已成功的signal。
- **验收标准**：dispatcher崩溃重启后，未完成的outbox事件被重新处理且不产生重复signal（幂等）。

### APPROVAL-F004 · 审批操作集
- **目标**：approve/reject/timeout/withdraw四种操作，均可通过PC和mobile发起。
- **验收标准**：timeout自动触发（审批超时未响应按预设策略处理），withdraw允许发起人主动撤回未处理的审批请求。

## 5｜核心数据 Contract（逻辑模型，可直接建表/建接口）

**AiApproval**（2026-08-30补充requestedPayloadHash/decisionReason/expiresAt字段，源自AI员工底层`approval`表；2026-09-02补充riskLevel/approverType字段；2026-09-04放宽actionId引用范围）
approvalId, actionId(关联F-ACTION-001的ProposedAction **或** F-QUEUE-001 QUEUE-F010的ActionInterceptDecision **或** F-TASK-001 TASK-F008的AiTaskStep——2026-09-04场景模拟发现QUEUE-F010、TASK-F008的"转人工"此前都没有真正调用本模块，只改了个状态字段；本字段改为按`actionSourceType`区分来源，不新建第二套审批状态机去分别服务），**actionSourceType**(ACTION_GATEWAY|IMPLEMENTER_INTERCEPT|TASK_SELFCORRECTION，2026-09-04新增/补充第3类，分别对应F-ACTION-001的AI员工业务动作、F-QUEUE-001的Implementer AI施工动作、F-TASK-001任务内自我纠错触碰硬上限), businessKey(关联Flowable流程实例), actionType, riskLevel(0-5，ACTION_GATEWAY来源取自F-ACTION-001 blast-radius检查结果；IMPLEMENTER_INTERCEPT来源取自架构原则第59条四级分类映射；TASK_SELFCORRECTION来源默认按中风险(2-3)处理，具体规则Stage10细化), status(PENDING|APPROVED|REJECTED|TIMEOUT|WITHDRAWN), requestedPayloadHash（防止审批通过后payload被偷换）, requestedBy, decidedBy?, **decidedByType(HUMAN|RULE_ENGINE，riskLevel 4-5时此字段建库时即约束只能为HUMAN)**, decisionReason?, expiresAt?, decidedAt?, createdAt

**OutboxEvent**
eventId, aggregateType(如AiApproval), aggregateId, eventType(APPROVED|REJECTED|TIMEOUT|WITHDRAWN), payload, dispatched(bool), dispatchAttempts, createdAt

**API 端点（最小集合）**
- `POST /approval` — （2026-09-04补，此前遗漏创建端点）创建一条AiApproval，调用方传入`actionSourceType`+对应来源的actionId/decisionId+riskLevel，F-ACTION-001和F-QUEUE-001（QUEUE-F010）都调用这一个端点，不各自实现一套
- `POST /approval/{approvalId}/approve` — 批准（写business state+outbox同事务）
- `POST /approval/{approvalId}/reject` — 拒绝
- `POST /approval/{approvalId}/withdraw` — 发起人撤回
- `GET /approval/pending` — 查询待审批列表（PC/mobile共用）

## 6｜P0 冻结规则

1. DB commit前触发外部signal或消息：不允许。
2. dispatcher重启导致重复signal（幂等失败）：不允许。
3. 审批记录不绑定具体action版本/actor/time：不允许。
4. riskLevel 4-5的AiApproval，`decidedByType`为RULE_ENGINE或`decidedBy`为非真人身份：不可降级P0（欧盟AI法案第14条硬性要求，见1.1节）。

## 7｜当前唯一继续断点

Stage 10（真实接入Flowable、真实Temporal signal联调）尚未开始。下一步：把 APPROVAL-F001~F004 转成 WorkPackage，需与F-ACTION-001、F-TASK-001的Temporal部署计划协调。

## 附录｜来源

- 内容来源：《Matbox_多端平台_CURRENT_正式开发文档_V3.0》F-APPROVAL-001 章节（2026-08-30核对确认）
- 技术底座依据（架构原则第31条已确认）：RuoYi Flowable BPM、Temporal Java SDK
- **字段补充依据（2026-08-30）**：《Matbox_AI_Employee_System_V6.3_Final_Frozen》底层包`04_Domain_Schema/migrations/003_runtime.sql`（approval表）
- **风险等级对应审批人规则依据（2026-09-02）**：[Matbox_架构设计原则.md](Matbox_架构设计原则.md)第42条#10（27道产品/商业定义问题确认记录，欧盟AI法案第14条人工监督硬性要求）
