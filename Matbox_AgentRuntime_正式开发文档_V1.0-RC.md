# Matbox Agent Runtime / AI 执行运行时（F-RUNTIME-001）

> 本文档由 [专项28技术选型与开发交接报告](技术选型报告/Matbox_专项28_AgentRuntime_技术选型与开发交接报告_2026-08-30.md) 整理而成，是"能直接开工写代码"的精简版；完整的8候选调研过程、真实事故案例、逐条查证来源，以专项28原文为准，不在本文档重复。**2026-09-05建立**（用户要求排查遗留项时发现：Feature Register长期把本模块标注为"专项28已完成技术选型审查"，但一直没有对应的正式开发文档本体，跟AIEMP-001/ACTION-001等"选型+正式文档"两步都走完的模块不是同一进度，本文档补齐这一步）。

## 当前定位

AI员工被F-ORCHESTRATOR-001路由到、F-TASK-001创建`ai_task`/`ai_task_step`之后，**谁、用什么机制真正执行"调用模型→模型决定要不要用工具→派发工具→把工具结果喂回模型→再判断要不要继续"这个多轮推理循环本身**——这是此前所有已建成文档都还没写清楚的一层，由本模块补齐。

**不是什么**（避免与相邻模块重复设计，详见专项28第1节）：
- 不是F-TASK-001——不拥有`ai_task`/`ai_task_step`生命周期状态机、不拥有Checkpoint/Resume/Kill Task持久化语义，本模块只是被F-TASK-001的Workflow在RUNNING状态下调用来执行一个具体step的执行体。
- 不是F-ORCHESTRATOR-001——不做路由决策，拿到的输入已经是确定的`employeeId`+`goal`。
- 不是F-ACTION-001——不做工具的权限/风险/预算/审批判定，只负责把模型的工具调用请求正确转发给F-ACTION-001的10步Enforcement Pipeline。
- 不是F-PROVIDER-001——不直连任何AI供应商SDK，一次模型调用永远经过F-PROVIDER-001的`invoke()`统一接口。
- 不是F-MEM-001——只管"这一次task step执行期间"的短期上下文窗口管理，跨会话长期记忆检索是F-MEM-001的职责（F-MEM-001检索链路建成前，本模块先用自己的短期上下文机制独立跑通，RUNTIME-F001留一个显式的"记忆检索结果注入点"）。

## 1｜技术选型结论（复用专项28已确认结论，不重新打开）

**整体执行引擎：Matbox自研（Java，Temporal Workflow/Activity承载推理循环），不整体采纳任何现成Agent框架。**

专项28真实核查了8个候选（Claude Agent SDK、OpenAI Agents SDK、LangGraph、CrewAI、Microsoft Agent Framework、Google ADK、Vercel AI SDK、Temporal原生模式），Top-3是 **#1 Matbox自研 > #2 Google ADK for Java > #3 LangGraph（需跨语言桥接）**。胜出理由是**架构一致性，不是能力强弱**：Matbox已经在F-ACTION-001（10步Enforcement Pipeline）和F-TASK-001（Temporal Checkpoint/Resume/Kill语义）冻结了具体的工具执行安全模型和持久化模型，任何"整体采纳一个自带循环控制+自带工具执行+自带状态持久化"的现成框架都会产生**两个竞争的执行/持久化真相源**，这是结构性冲突，不是多花时间集成能解决的量级问题。Google ADK（唯一官方Java一等公民支持）和LangGraph（生产证据最强，约400家企业含Klarna/Uber/JPMorgan）均认真评估过，分别因"自带Runner/Session状态模型与Temporal冲突"和"Python-only违反架构原则第33条Java单语言栈"未整体采纳，降级为长期能力监控项。完整的8候选逐一核查、真实安全事故（Google ADK 2026-08 prompt injection提权事故）、License风险表，见专项28第3/6/8/9节。

**关键技术依据**：Temporal官方有《Basic agentic loop with Claude and tool calling》Cookbook + 《Spring AI integration》官方Java集成文档，且Temporal Activity原生心跳机制（`Activity.getExecutionContext().heartbeat()`）与架构原则第28条"心跳必须从循环内部发出、连续漏2次才报警"高度吻合——"Java原生Agent Runtime"是Temporal官方认证的推荐模式，不是Matbox闭门造车（专项28第3.4/7节）。

**RUNTIME-F004上下文窗口管理子能力**：混合方案 = Anthropic Context Editing API（Claude专属，REUSE，官方数据29-84% token节省需独立验证）+ Matbox自研通用裁剪/摘要兜底（非Claude供应商场景）。击败LangMem（深度绑定LangGraph生态）、Mem0（定位是跨会话长期记忆，属F-MEM-001范围非本模块）。

## 2｜Own / Reuse / Must Not Rebuild

- **OWN**：ReasoningLoopController循环控制流与终止条件判断、PromptAssembler组装规则、ToolCallDispatcher与F-ACTION-001的桥接映射、CallLevelRetryHandler重试/退避策略、HeartbeatEmitter/KillSwitchResponder的Matbox业务语义（频率/报警阈值/安全终止点选择）、非Claude供应商的上下文裁剪/摘要兜底。
- **REUSE**：Temporal Workflow/Activity引擎本身（含原生Heartbeat/Cancellation机制，与F-TASK-001/F-QUEUE-001共用同一套集群，不新建第二套持久化工作流系统）；F-PROVIDER-001的`invoke()`统一模型调用接口；F-ACTION-001的10步Enforcement Pipeline；F-AIEMP-001的EmployeeTemplate只读查询；Anthropic Context Editing API + Memory Tool；错误码规范17个跨模块错误码；REL-F006的Flyway迁移工具+TENANT-F004共享表模式。
- **MUST NOT REBUILD**：模型推理能力本身（F-PROVIDER-001已封装）、Temporal自身的crash恢复/replay/幂等去重机制、MCP Gateway工具调用安全治理层（F-ACTION-001已REUSE）、跨AI员工委派链路防护算法（F-DELEGATION-001已冻结）。

## 3｜Feature Register

| FeatureID | 名称 | 技术路线 |
|---|---|---|
| RUNTIME-F001 | PromptAssembler | Matbox自研 |
| RUNTIME-F002 | ReasoningLoopController | Matbox自研（Java，Temporal Workflow/Activity） |
| RUNTIME-F003 | ToolCallDispatcher | Matbox自研（协议层REUSE ACTION-F005/PROVIDER-F006契约） |
| RUNTIME-F004 | ContextWindowManager | 混合方案（Claude Context Editing API REUSE + 自研通用兜底） |
| RUNTIME-F005 | CallLevelRetryHandler | Matbox自研（复用错误码规范） |
| RUNTIME-F006 | HeartbeatEmitter | REUSE Temporal Activity原生心跳 + 自研业务语义层 |
| RUNTIME-F007 | KillSwitchResponder | REUSE Temporal Activity Cancellation机制 + 自研安全终止点判断 |
| RUNTIME-F008 | StreamingProgressBridge | API接入（复用F-TASK-001 Task API事件序列） |

### RUNTIME-F001 · PromptAssembler
读EmployeeTemplate的角色定义/目标/工具清单 + AiTaskStep.description + 历史轮次，组装成一次LLM调用的message列表。**验收标准**：组装结果必须可追溯每个字段的来源模块（不允许硬编码/凭空拼接）；为F-MEM-001预留显式的"记忆检索结果注入点"字段位。

### RUNTIME-F002 · ReasoningLoopController
Temporal Workflow代码承载的确定性循环控制流：调模型→响应含tool_use?→是则派发工具→回填结果标记不可信→回到循环，否则判断终止条件结束。**验收标准**：`agent-runtime/loop`目录下的Workflow代码必须满足Temporal确定性约束（不直接调用非确定性API，所有外部调用经`activities/*`封装）——这是Temporal编程模型硬性要求，违反会导致Workflow replay行为不一致，见RT-T001。

### RUNTIME-F003 · ToolCallDispatcher
把模型返回的`tool_use`转译成F-ACTION-001的`ProposedAction`，调用`propose→execute`，执行结果标记为不可信内容后回填。**验收标准**：不存在绕过F-ACTION-001网关的工具调用（RT-T001/RT-T007）；委派权限不放大，必须原样携带发起本次AiTask的AgentIdentity（不允许在循环内部临时提升权限范围）。

### RUNTIME-F004 · ContextWindowManager
Claude场景走Context Editing API自动裁剪；非Claude供应商走Matbox自研通用裁剪/摘要兜底。**验收标准**：超长多轮对话裁剪后任务仍能产出正确结果，不能裁掉关键信息导致任务失败（RT-T003）；`ContextStats`必须可查询当前上下文占用/裁剪历史（直接回应Claude Agent SDK Issue #507指出的"无法按类别细分上下文用量"缺口）。

### RUNTIME-F005 · CallLevelRetryHandler
场景化应用错误码规范已定义的17个码，区分可重试（`PROVIDER_TIMEOUT`/`RATE_LIMITED`/`TOOL_TIMEOUT`）与不可重试（`TOOL_POLICY_DENIED`/`BUDGET_EXCEEDED`）。**验收标准**：`RATE_LIMITED`触发Workflow层指数退避重试该轮LLM调用，不是重跑整个task导致丢失已进行到一半的多轮上下文（RT-T004）。

### RUNTIME-F006 · HeartbeatEmitter
循环内部每2-3分钟调用一次`Activity.getExecutionContext().heartbeat(payload)`，`source`字段固定标注`LOOP_INTERNAL`（架构原则第28条要求：必须证明心跳来自循环内部，不是进程存活检查）。**验收标准**：连续漏2次心跳，F-OBS-001（OBS-F004）在约定时间窗口内触发告警（RT-T006）；心跳payload不携带敏感数据（Prompt原文/工具参数可能含租户业务机密），只带最小必要进度标识。

### RUNTIME-F007 · KillSwitchResponder
Temporal Cancellation信号随心跳一起投递（源码级证据，非Matbox假设）——**心跳间隔本身就是Kill信号的最大响应延迟上限**，架构原则第28条定的心跳频率同时决定Kill Switch响应及时性，Stage 10调参须一并考虑。**验收标准**：Kill信号下发后，Agent Runtime在下一次心跳内确认收到并在当前工具调用完成后的安全点终止，不是mid-flight强行杀死导致工具执行状态不一致（RT-T005）。

### RUNTIME-F008 · StreamingProgressBridge
不新建WebSocket/SSE通道，模型流式片段/中间工具调用结果经F-TASK-001已有Task API事件序列（`AiTaskEvent`）异步落库，前端走TASK-F004断线重连补齐机制读取。**验收标准**：不直接写client response（遵守TASK-F001 P0规则1）。

## 4｜核心数据 Contract（逻辑模型，可直接建表/建接口）

```yaml
ReasoningTurn:
  turnId: uuid
  taskId: string          # 关联 F-TASK-001 ai_task.task_id
  stepId: string          # 关联 F-TASK-001 ai_task_step.step_id
  turnIndex: integer
  role: MODEL_CALL | TOOL_CALL
  modelInvocationRef: string?   # 关联 F-PROVIDER-001 ModelInvocation.invocationId
  actionExecutionRefs: string[] # 关联 F-ACTION-001 ActionExecution.executionId，一轮可能有多个并行工具调用
  stopReason: CONTINUE | END_TURN | MAX_TURNS_REACHED | SELF_CORRECTION_TRIGGERED | KILLED | ERROR
  untrustedContentFlags: string[]  # 标记本轮工具/网页输出中被判定为不可信内容的片段引用，供审计
  createdAt: datetime

HeartbeatEvent:
  heartbeatId: uuid
  taskId: string
  stepId: string?
  temporalActivityId: string?
  sequenceNo: integer
  emittedAt: datetime
  source: LOOP_INTERNAL   # 架构原则第28条要求：必须标注心跳来自循环内部

KillAcknowledgement:
  taskId: string
  stepId: string?
  acknowledgedAt: datetime
  safePointReached: boolean   # 是否在当前工具调用完成后的安全点终止，而非mid-flight强杀
  compensationTriggeredRef: string?  # 关联TASK-F005补偿动作引用

ContextStats:
  taskId: string
  stepId: string
  currentTokens: integer
  maxWindowTokens: integer
  trimEventsCount: integer
  claudeContextEditingApplied: boolean
```

**数据库**：沿用REL-F006的Flyway迁移+TENANT-F004共享表模式，4张表（`runtime_reasoning_turn`/`runtime_heartbeat_event`/`runtime_kill_acknowledgement`/`runtime_context_snapshot`），均含`tenant_id`字段，完整DDL见专项28第20节。`ai_task`/`model_invocation`/`action_execution`本身表结构不在本模块重复定义。

## 5｜API 端点（仅运维/调试用途，主体不对外暴露HTTP服务）

Agent Runtime主要以Temporal Workflow/Activity代码形式存在，被F-TASK-001的Workflow直接调用（同进程Activity调度，非HTTP）。仅暴露只读运维端点，统一前缀`/runtime`：

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/runtime/reasoning-turns/{taskId}/{stepId}` | 查询某AiTaskStep内部推理轮次明细 |
| GET | `/runtime/heartbeats/{taskId}` | 查询心跳事件序列（人工排查用，正式告警走OBS-F004） |
| POST | `/runtime/kill-ack` | Kill信号确认回执（供TASK-F005验证Kill真正生效，非人工直接调用） |
| GET | `/runtime/context-stats/{taskId}/{stepId}` | 查询上下文窗口占用/裁剪历史 |

鉴权：不新建平行体系，走与`/dq/*`、`/task/*`同一套JWT校验（`Operator`及以上角色），多租户隔离复用TENANT-F004"共享表+租户ID字段"模式。完整OpenAPI 3.0文档见专项28第15节。

## 6｜P0 冻结规则

1. **循环内部不判断工具执行权限**——权限判断完全交给F-ACTION-001的10步Enforcement Pipeline（ACTION-F005第③步），Agent Runtime只转发已附带AgentIdentity上下文的ProposedAction，自己不裁决"能不能执行"。
2. **工具/网页输出必须当作不可信内容处理**（ACTION-F005验收标准+架构原则第10条）——回填工具结果时必须显式标记来源不可信，不能让模型把工具输出误判为系统指令（Google ADK 2026-08真实prompt injection提权事故是反面教材）。
3. **委派权限不得放大**——组装ProposedAction时必须原样携带发起本次AiTask的AgentIdentity，不允许在推理循环内部临时提升权限范围。
4. **心跳必须证明来自循环内部**（`source=LOOP_INTERNAL`），不能只是进程存活检查——这是架构原则第28条的字面要求，不是抽象满足。
5. **任何模型调用/工具调用错误不允许静默吞掉继续假装成功**（fail-closed，与F-ACTION-001/DQ系列一致）。
6. **TASK-F008自我纠错达到硬上限必须转人工审批，不允许无限重试**（复用DELEGATION-F005"硬上限防重试风暴"同一原则，2025年7月保险公司84.7万次API调用死循环真实事故是这条要求的依据）。
7. **心跳payload不得携带敏感数据**——Prompt原文/工具调用参数可能含租户业务机密，只携带最小必要的进度标识字段。
8. **`agent-runtime/loop`目录下的Workflow代码必须保持Temporal确定性约束**——所有真正的外部调用、随机性、系统时间读取必须封装进`activities/*`，这是Temporal编程模型本身的硬性要求，不是Matbox自定规则。

## 7｜当前唯一真实协调缺口（不是本模块单方面能关闭的项）

**F-PROVIDER-001的Provider Adapter响应schema尚未定义跨供应商统一的`normalized_tool_calls[]`字段**——Claude的`tool_use`、OpenAI的`function_call`、Gemini的`function_call`三者字段名/结构不同，Agent Runtime现阶段只能自己解析各Provider Adapter的原始响应格式提取工具调用。**这条已向F-PROVIDER-001 Owner登记协调需求**，建议Stage 10前在PROVIDER-F006补一个跨供应商归一化字段，避免Agent Runtime里散落供应商专属解析逻辑。不阻塞P0链路开工（WP-RUNTIME-01/02可先用自行解析的方式跑通）。

## 8｜验收标准（Stage 10绑定真实Repo+真实Temporal集群后）

RT-T001~RT-T008（8项测试场景，专项28第23节新建，Agent Runtime此前无任何既有验收基线）+ 第2节Own/Reuse边界核查 + 第6节P0规则全部通过，且：
1. 推理循环每一次工具调用均可在审计记录里追溯到对应的F-ACTION-001 ActionExecution；
2. 心跳事件确认从循环内部发出，而非仅依赖进程存活检查；
3. TASK-F008自我纠错硬上限、DELEGATION-F005式重试风暴防护在本模块同样生效。

未通过任一项，Feature不得进入RC5 ACCEPTED流程。工作量估算约38-59人天（不含Stage 10真实调参缓冲），详见专项28第25节WP-RUNTIME-01~07拆分。

## 附录｜来源

完整8候选逐一核查、真实生产证据/事故案例、License审查、逐条外部URL来源，见 [专项28技术选型与开发交接报告](技术选型报告/Matbox_专项28_AgentRuntime_技术选型与开发交接报告_2026-08-30.md) 全文（含附录来源汇总）。本文档依赖的其他已建成正式文档：`Matbox_中央编排层_正式开发文档_V1.0-RC.md`、`Matbox_AI任务运行时_正式开发文档_V1.0-RC.md`、`Matbox_Action网关_正式开发文档_V1.0-RC.md`、`Matbox_Provider_Router_正式开发文档_V1.0-RC.md`、`Matbox_AI员工身份_正式开发文档_V1.0-RC.md`、`Matbox_证据审计与监控_正式开发文档_V1.0-RC.md`、`Matbox_错误码规范_正式开发文档_V1.0-RC.md`。
