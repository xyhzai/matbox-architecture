# Matbox 中央编排层 / Orchestrator（"大脑"）（F-ORCHESTRATOR-001）

正式开发文档 · V1.0-RC · 2026-08-30

## 当前定位

本专项解决"用户在任何界面说一句话，谁/什么机制决定该找哪个AI员工处理、要不要拆解成多步、要不要多个员工协作"的问题——这是本会话"AI员工能力缺口调研清单"里定性为**"没有它其他都是空谈"的P0前提**（详见[Matbox_AI员工能力缺口调研清单_2026-08-30.md](Matbox_AI员工能力缺口调研清单_2026-08-30.md)#1）。

**这不是一个新增的可选功能，是补齐已建成模块本来就需要的入口**：F-TASK-001（任务运行时）、F-ACTION-001（工具网关）、F-DELEGATION-001（委派）、F-PROVIDER-001（模型网关）这4份正式文档各自内部逻辑完整，但目前都要求调用方已经知道`employeeId`/该走哪条链路——本模块补上"用户一句话进来，怎么知道该调用谁"这一层。10次沙盘推演（见调研清单）里4次直接卡死在这个缺口上。

**是否现在设计的论证（2026-08-30，用户已确认执行）**：本模块的核心结构（Registry+Classifier+Coordinator）不依赖真实生产流量就能设计对——员工目录已有（F-AIEMP-001），路由架构是算法设计问题不是"要看数据才知道"的问题。真正依赖真实流量的只是"具体路由阈值怎么精调"这类调优细节，不是整体架构，标注在第7节继续断点里，不影响本模块现在整体成型。

**DocID**: MATBOX-ORCHESTRATOR-20260830-V1.0-RC
**状态**: DRAFT_RESEARCH_COMPLETE（内容级核查通过，未进入 Stage 10 真实施工）
**依赖方（已知阻塞）**：F-AIEMP-001（Registry来源，已建成）、F-TASK-001（Classifier判断后创建的任务，已建成）、F-DELEGATION-001（Coordinator的fan-out/fan-in执行层，已建成）、F-COST-001（编排器自身开销的独立预算线，已建成）

## 1｜不可变原则

1. 编排器自己的LLM调用开销（拆解+汇总）必须独立计入F-COST-001成本模型，不允许算作worker/AI员工的成本，避免"测试时几毛钱、规模化后账单失控却查不出原因"。
2. 相同输入的路由决策应当保持确定性——不允许纯LLM现场判断"这次该找谁"，避免同一句话跑两次被路由到不同AI员工。
3. 编排器不得成为无监控的单点故障——必须有容灾/降级路径，编排器不可用时不能让全平台的AI员工调用全部停摆。
4. 编排器持有的上下文（任务描述+中间结果）必须有明确的窗口管理策略，不允许假设"上下文可以无限增长"。
5. 任何委派/重试都必须有硬性次数上限——不允许无界循环、无界委派链。

## 2｜全球调研结论（2026-08-30，两轮深度调研）

### 2.1 多家独立实现互相印证的收敛结构——不是单一厂商说法

Salesforce Atlas Reasoning Engine、Microsoft Agent Framework（WorkflowBuilder）、Google Agentspace/Gemini Enterprise、开源LangGraph/AutoGen/CrewAI，全部收敛到同一个行业标准结构，业内正式名称叫**"Handoff Orchestration"**（也叫routing/triage/transfer/dispatch）：
- **Registry**（Agent发现/生命周期管理）——本模块不重复存储，直接查询F-AIEMP-001的EmployeeTemplate/EmployeeInstance
- **Classifier**（意图路由）——决定这次请求该匹配哪个/哪些AI员工
- **Coordinator**（fan-out并行/fan-in汇总/顺序链）——对接F-DELEGATION-001实际执行委派链

Microsoft的WorkflowBuilder明确支持fan-out（并行分支）、fan-in（等待所有分支汇总）、顺序链三种模式，这是Coordinator组件的具体形态参照。

### 2.2 路由技术选型——有真实生产数据支撑，不是原则性描述

- **Embedding路由**：成本<$0.01/次查询，比LLM路由便宜约65倍，生产环境把路由延迟从5000ms压到100ms，迭代优化后精度92-96%——但处理不了没见过的新意图/需要组合推理的复杂请求
- **LLM路由**：适应性强，能处理复杂/新颖请求，但慢且贵
- **结论：混合模式**——常见/明确请求走embedding快速路径，模糊/复合/新颖请求才落到LLM推理兜底

### 2.3 真实设计陷阱——AutoGen已经暴露的问题

AutoGen的GroupChatManager"下一个该谁发言"是纯LLM预测，**同一句话跑两次可能路由到不同Agent**，因为LLM每次判断可能不同——这是选择混合模式而非纯LLM路由的关键理由之一，不只是为了省钱，是为了路由结果的确定性和可复现性。

### 2.4 必须显式防住的5类真实生产失败模式（40%多Agent试点6个月内在生产失败）

1. **单点故障**——编排器挂了全系统停摆，误分类的错误会在规模化后复合放大，需要容灾设计
2. **吞吐瓶颈**——真实案例：编排器单次LLM调用3秒+20个worker等待分配，吞吐上限只有6.7任务/秒，编排器自己会成为全系统的天花板
3. **成本失控**——真实案例：测试时$0.5的工作流，10万次执行后可能到月付$5万，因为编排器的"拆解+汇总"LLM调用叠加在每个worker成本之上（对应不可变原则第1条）
4. **上下文窗口溢出**——中间结果超过50个，128k上下文的模型也装不下
5. **8条根因清单**（生产环境40%失败率的直接原因）：隐藏状态、竞态条件、无界循环、工具权限范围过宽、幂等性缺失、循环内阻塞调用、朴素重试策略、单线程编排器在真实流量下变瓶颈——设计时逐条对照排除

### 2.5 真实案例验证（第二轮，用户要求"已经成功的公司+真实用户评价"）

Salesforce Agentforce（Atlas引擎的真实产品）G2真实评价：正面"intelligent routing帮着减少人工干预、提升响应速度"；差评"**如果数据混乱、有重复记录，路由/整体表现会受影响**"——揭示了一个关键点：**"大脑"路由准不准，很大程度取决于EmployeeTemplate角色定义/任务描述够不够结构化，不是纯路由算法问题**，跟PIM结构化数据要求（见调研清单#30）是同一个前提的两个应用场景。

## 3｜Own / Reuse / Must Not Rebuild

| 类型 | 对象 | 说明 |
|---|---|---|
| OWN | RoutingClassifier业务规则、Coordinator编排逻辑、失败模式防护（容灾/吞吐监控/成本隔离/上下文管理/循环检测） | Matbox自己的路由/编排业务规则 |
| REUSE | Embedding模型（供应商能力，经F-PROVIDER-001 Model Gateway调用）、LLM推理兜底（同样经F-PROVIDER-001） | 不重新造Embedding/LLM推理能力本身 |
| MUST NOT REBUILD | F-AIEMP-001的Registry存储、F-DELEGATION-001的委派执行、F-TASK-001的任务运行时 | 本模块只做路由决策和协调，不重复实现这些已有模块的职责 |

## 4｜Feature Register

| FeatureID | 名称 | 说明 |
|---|---|---|
| ORCHESTRATOR-F001 | Registry接入 | 查询F-AIEMP-001的EmployeeTemplate/EmployeeInstance，不重复存储 |
| ORCHESTRATOR-F002 | 混合路由（Classifier） | Embedding主路径+LLM兜底，按请求复杂度自动选择 |
| ORCHESTRATOR-F003 | Coordinator | fan-out并行/fan-in汇总/顺序链，对接F-DELEGATION-001实际执行 |
| ORCHESTRATOR-F004 | 失败模式防护 | 容灾/吞吐监控/独立成本建模/上下文窗口管理/循环与重试上限 |
| ORCHESTRATOR-F005 | 路由确定性与可追溯 | 相同输入保持一致路由结果（非AB实验场景下），路由决策留痕可查询 |

### ORCHESTRATOR-F001 · Registry接入
- **目标**：路由决策前先查询F-AIEMP-001当前可用的AI员工清单（含角色定义、技能范围、状态），不在本模块另存一份。
- **验收标准**：F-AIEMP-001新增/停用一个AI员工，路由结果立即感知变化，不需要重启或手动同步。

### ORCHESTRATOR-F002 · 混合路由（Classifier）
- **目标**：常见请求（历史已见过的意图模式）走Embedding快速匹配到对应AI员工；模糊/复合/新颖请求落到LLM推理，判断是否需要拆解成多步或委派给多个员工协作。用户在雇佣中心/日常交互中已明确手动指定AI员工时（`RoutingRequest.manualEmployeeId`不为空），直接跳过Embedding/LLM匹配，走权限/租户边界校验后直接命中，不重新做语义路由判断（2026-09-02补强，落实架构原则第41条）。
- **验收标准**：Embedding路径的P95延迟<200ms；LLM兜底路径必须给出可解释的匹配理由，不是黑箱输出一个employeeId；手动指定路径必须仍然做租户/权限校验，不能因为"用户手动选的"就跳过安全检查。

### ORCHESTRATOR-F003 · Coordinator
- **目标**：路由决策确认需要多员工协作时，通过F-DELEGATION-001发起实际的fan-out/fan-in/顺序链执行；单员工可处理的请求直接创建F-TASK-001任务。
- **验收标准**：fan-out的并行分支必须全部返回或超时才能fan-in，不允许部分分支丢失结果却继续汇总。
- **范围边界，2026-09-04补（自查发现F-AIEMP-001曾错误引用本组件后加）**：本Coordinator管的是**员工与员工之间**要不要协作、怎么协作，不管**一个员工内部、Subagent与Subagent之间**怎么路由/交接——后者属于F-AIEMP-001的AIEMP-F006范围，由员工内部专职的路由型Subagent自己承担，不经本模块。两个层级不要混用，本条只做澄清，不改变本模块已有设计。

### ORCHESTRATOR-F004 · 失败模式防护
- **目标**：显式防住2.4节列出的5类失败模式——独立部署可容灾、吞吐有监控告警、成本独立建模到F-COST-001、上下文超阈值有截断/摘要降级策略、任何循环/委派链有硬性次数上限。
- **验收标准**：人为构造编排器实例宕机，验证有容灾切换；人为构造循环委派场景，验证在达到上限时被强制终止并留痕，不是无限跑下去。

### ORCHESTRATOR-F005 · 路由确定性与可追溯
- **目标**：非AB实验场景下，相同输入应产生一致的路由结果；每次路由决策留下可查询的记录（匹配了谁、用了哪种路由方式、置信度多少）。
- **验收标准**：同一句话在无AI员工配置变更的情况下重复提交，路由结果一致；任意一次路由决策可以查到具体理由。

## 5｜核心数据 Contract（逻辑模型，可直接建表/建接口）

**RoutingRequest**（2026-09-02补强，落实架构原则第41条+专项00f发现的缺口）
requestId, tenantId, actorId（发起请求的人类用户或系统）, rawInput（自然语言原文）, attachments[]?（新增，如参考图片/尺寸文档等多模态附件的StorageRef列表，此前完全没有字段承载，设计师上传参考图无处可放）, manualEmployeeId?（新增，用户手动指定要哪个AI员工时使用，跳过Classifier的语义匹配，直接命中；为空时走正常混合路由）, channel（PC|MOBILE|独立站匿名入口等，关联多端调用场景）, context{}, createdAt

**RoutingDecision**
decisionId, requestId, routingMethod(EMBEDDING|LLM_FALLBACK), matchedEmployeeIds[], confidence, needsCoordination(bool), planSteps[]?（若需要拆解成多步/多员工协作）, decisionReason, createdAt

**OrchestratorCostRecord**（不可变原则第1条落地，独立于worker成本）
costRecordId, decisionId, llmCallType(DECOMPOSE|AGGREGATE), tokensUsed, costUsd, occurredAt

**FailsafeEvent**（失败模式防护留痕）
eventId, eventType(TIMEOUT|LOOP_LIMIT_HIT|CONTEXT_OVERFLOW|FAILOVER_TRIGGERED), relatedRequestId?, details, occurredAt

**API 端点（最小集合）**
- `POST /orchestrator/route` — 提交自然语言请求，返回路由决策（匹配的AI员工、是否需要协作、置信度）
- `GET /orchestrator/route/{decisionId}` — 查询某次路由决策的详细理由
- `GET /orchestrator/health` — 查询编排器自身健康状态（供容灾切换判断）

## 6｜P0 冻结规则

1. 编排器自身LLM调用开销未独立计入成本模型：不可降级P0。
2. 编排器单点故障无容灾/降级路径：不可降级P0。
3. 相同输入在非AB实验场景下路由结果不一致：不允许。
4. 委派链/重试无硬性次数上限（无界循环风险）：不可降级P0。
5. 上下文超过阈值时没有降级策略、直接报错或截断关键信息：不允许。

## 7｜当前唯一继续断点

Stage 10（真实部署、接入真实Embedding模型、真实调优路由阈值）尚未开始。**明确区分**：本模块的整体架构（Registry+Classifier+Coordinator+失败模式防护）现在已经设计完整，可以转WorkPackage；**只有"Embedding相似度阈值具体设多少""哪些意图归为同一路由类别"这类需要真实用户请求数据才能精调的参数**，留到Stage 10接入真实流量后再迭代，不影响本模块现在整体成型。

## 附录｜来源

- **架构模式依据**：[Inside the Orchestrator: The Brain Behind Every Multi-Agent AI System](https://medium.com/@krunalkamble215/inside-the-orchestrator-the-brain-behind-every-multi-agent-ai-system-d76701e70e1f)、[Atlas Reasoning Engine](https://engineering.salesforce.com/inside-the-brain-of-agentforce-revealing-the-atlas-reasoning-engine/)、[Multi-agent Reference Architecture - Microsoft](https://microsoft.github.io/multi-agent-reference-architecture/docs/reference-architecture/Reference-Architecture.html)
- **路由技术选型依据**：[Top 5 Semantic Routing Platforms](https://www.getmaxim.ai/articles/top-5-semantic-routing-platforms-for-llm-applications/)、[The Intent Classification Layer Most Agent Routers Skip](https://tianpan.co/blog/2026-04-16-intent-classification-agent-routers)
- **失败模式依据**：[6 Multi-Agent Orchestration Patterns for Production](https://beam.ai/agentic-insights/multi-agent-orchestration-patterns-production)、[Multi-Agent System Reliability: Failure Patterns, Root Causes](https://www.getmaxim.ai/articles/multi-agent-system-reliability-failure-patterns-root-causes-and-production-validation-strategies/)
- **调研清单/沙盘推演依据**：[Matbox_AI员工能力缺口调研清单_2026-08-30.md](Matbox_AI员工能力缺口调研清单_2026-08-30.md)#1
- **RoutingRequest.attachments/manualEmployeeId补强依据（2026-09-02）**：[Matbox_专项00f_AI员工指令交互流程设计_2026-09-02.md](技术选型报告/Matbox_专项00f_AI员工指令交互流程设计_2026-09-02.md)；架构原则第41条
