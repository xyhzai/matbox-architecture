# Matbox Action 网关 / Action Gateway（F-ACTION-001）

正式开发文档 · V1.0-RC · 2026-08-30

## 当前定位

本专项解决"所有Tool/MCP/内部/第三方**工具与动作**调用的唯一受控执行入口"的问题——AI员工不能裸调生产API或绕过domain自建权限，所有有副作用的动作必须经本模块统一做权限/资源范围/风险/可逆性/预算/审批/幂等/commit时重新鉴权/审计。

**这是核查《Matbox_多端平台_CURRENT_正式开发文档_V3.0》F-ACTION-001章节后确认的模块**，2026-08-30核对《AI_Employee_System_V6.3_Final_Frozen》底层包后做了一处**结构性修正**：底层包把"调用AI模型供应商"和"调用工具/执行动作"设计成两个平级网关——Model Gateway（WP-006，对应本项目已建成的F-PROVIDER-001）和MCP/Tool Gateway（WP-007，对应本模块），各自有独立SQL表（`model_invocation` vs `tool_invocation`）、独立contract文档、独立service目录，不是一个网关内部的分支。**本模块因此收窄为专职工具/动作调用（不再包含"若为AI供应商调用则走Provider Router"这条分支，AI模型调用完全由F-PROVIDER-001单独处理）**。调用链改为：**F-ACTION-001（工具/动作） → Registry状态检查 → 租户边界检查 → Identity/RBAC/ABAC检查 → 风险半径检查 → 审批要求检查 → 预算检查 → 取凭证（F-CRED-001） → 限流/熔断检查 → 执行 → 结果规范化+审计+成本+trace**（10步enforcement顺序，源自底层包`mcp_tool_gateway_contract.md`），出站URL安全校验（F-EGRESS-001）作为所有出站请求的基础设施层防护，不分网关统一适用，不算在这10步业务顺序里。

**DocID**: MATBOX-ACTION-GATEWAY-20260830-V1.0-RC（2026-08-30二次修订，收窄为Tool/MCP Gateway）
**状态**: DRAFT_RESEARCH_COMPLETE（内容级核查通过，未进入 Stage 10 真实施工）
**依赖方（已知阻塞）**：F-PLAT-001、F-CRED-001（已建成）、F-COST-001（已建成）、F-OBS-001（已建成）、[F-EGRESS-001](Matbox_出站请求安全_正式开发文档_V1.0-RC.md)（本轮同步建成）

## 1｜不可变原则

1. 模型不得裸调生产API——所有工具/第三方调用必须经Action Gateway，不允许domain自建权限绕过统一校验。
2. commit-time重新鉴权是P0——execute前的权限判断不能当作执行时刻仍然有效的唯一依据，必须在真正提交副作用前重新校验permission/entitlement/budget/approval。
3. 高风险动作必须明确展示风险/可逆性给用户确认，不能隐藏在无感知的自动执行里，且不能在预览中暴露secret。
4. 幂等是强制要求——重试不能重复产生外部副作用（如重复扣款、重复发消息）。

## 2｜全球调研结论（复用本会话已完成的MCP Gateway生态调研 + AI员工底层包核对）

本会话此前已针对"Tool调用安全网关怎么做"这个问题调研过：2026年MCP（Model Context Protocol）Gateway生态已经成熟——Obot、ContextForge、MCPX/Lunar等开源方案，2026年已有Linux Foundation治理、97M+下载量、13K+已注册MCP server，是行业公认的Tool调用安全治理基础设施，不需要从零自建工具调用安全层。

**2026-08-30核对AI员工底层包`mcp_tool_gateway_contract.md`补强**：该文档给出了比本文档此前更细的两处内容，已采纳：
1. **Registration Contract字段**：每个工具/MCP server注册时必须登记`tool_id/tenant_scope/owner/type/version/endpoint_ref/secret_ref/capabilities/allowed_actions/risk_level/data_classes/rate_limit/timeout_ms/healthcheck/status`——比本文档原先的ProposedAction更完整地定义了"工具本身"的注册信息，不只是"一次调用"的信息。
2. **10步enforcement顺序**：Registry状态检查→租户边界检查→Identity/RBAC/ABAC检查→blast-radius(风险半径)检查→审批要求检查→预算检查→Secret解析→限流/熔断检查→执行→结果规范化+审计+成本+trace。这比本文档此前"取凭证→校验URL→执行"的简化顺序更完整，本文档采纳这个顺序，其中"Secret解析"对应F-CRED-001，出站URL安全校验（F-EGRESS-001）作为基础设施层防护应用于"执行"这一步，不单独占enforcement顺序里的一个位置。

**结论**：Action Gateway的Provider层（Tool/MCP adapter部分）基于MCP Gateway生态搭建（REUSE），业务层的权限/风险/预算/审批判定逻辑是Matbox自己的（OWN），enforcement顺序采用AI员工底层包已验证过的10步版本。

### 2.1 缺"确定性 Workflow 当作一个整体工具调用"这一层（2026-09-04，深度调研ServiceNow/Salesforce/UiPath三家真实做法后新增，用户直接要求解决）

**查证结论**：本文档ACTION-F001~F005管的都是**单个动作**（一次ProposedAction对应一个toolId）的权限/风险/幂等/审计，这部分设计是对的。但查证ServiceNow真实案例发现，"provision user"这类常见业务操作，真实做法不是让AI每次临时想"先建AD账号、再报HR、再走审批"这几步分别调用，而是把整条流程预先封装、测试好，AI一次调用整条流程；Salesforce把这个原则叫Hybrid Reasoning——确定性任务（价格计算、库存扣减、退款、审批路由）走预先定义的Flow/Apex，不确定性任务（总结、生成、判断意图）才交给模型临时推理。ServiceNow原话警告："Competitors expose system APIs, forcing agents to orchestrate these steps on every invocation...probabilistic orchestration introduces variance"——让AI每次临时拼多步操作的顺序，会在token压力下漏步骤、编造不存在的旧阈值、生成违反合规的顺序。

UiPath的真实产品Maestro提供了具体、可直接采纳的实现路径：用**BPMN**（Business Process Model and Notation，公开的国际流程图标准，非私有格式）定义流程步骤顺序，用**DMN**（Decision Model and Notation，配套的决策规则标准）定义确定性判断逻辑，两者都是成熟、有多个开源实现的标准，不需要Matbox自己发明一套流程定义格式。

**确认的方向（已落地为ACTION-F006，见下方）**：新增Workflow概念，用BPMN定义步骤顺序、DMN定义分支决策，一个Workflow内部由多个ProposedAction组成，AI员工一次调用整个Workflow，而不是分别调用每一步。**这不是绕过或降低ACTION-F001~F005已有的单动作治理**——Workflow内部每一步仍然各自完整走一遍10步Enforcement Pipeline，Workflow只是把"AI员工每次要不要临时拼这几步、该拼成什么顺序"这个决策，提前搬到设计时做完、测试好、冻结，运行时AI员工只管"要不要调用这个已验证的Workflow"，不再临时编排步骤顺序本身。

### 2.2 缺"按业务平台划分的具名Connector目录"这一层（2026-09-05，用户指出底层架构没考虑Connector生态后新增查证）

**查证结论**：ACTION-F002的`ToolRegistration`是单个工具/MCP server级别的注册（一个toolId对应一个具体API端点），这个粒度对，但缺一层更上面的、面向业务的分组——用户真正要接入的是"微信客服""Shopify店铺""酷家乐"这类**完整业务平台**，一个平台通常包含多个相关工具/端点、共享同一套OAuth/凭证。深度复核Salesforce/ServiceNow/UiPath三家真实做法后确认这不是本文档特有的疏漏，是三家独立收敛到的同一层：

- **Salesforce**：2018年以65亿美元收购MuleSoft买下Anypoint Platform，当时Agentforce尚未存在——是先建通用集成能力，2026年才成为"Agentic时代的骨干"，技术上是Control-Plane/Data-Plane分离+Agent Registry+Gateway模式，且已用MCP协议对接外部工具，与本文档ACTION-F001~F005的Gateway+Policy思路互相印证。
- **ServiceNow**：一个"Spoke"= 一组打包好的Actions（类型化输入输出）+ 一个Connection & Credential**别名**（流程/Agent只认别名、从不直接接触真实凭证）+ 示例流程，通过ServiceNow Store分发，AI Agent运行时动态挑选合适的Spoke执行。
- **UiPath**：Integration Service是连通层，Marketplace是明确的连接器分发/变现渠道（第三方建连接器上架、UiPath代收款分成，2021年数据已有1300+上架，同一套连接器同时服务传统自动化和Agent）。

**结论**：Matbox已经有的F-ACTION-001（Gateway+10步Pipeline）和F-CRED-001（credentialRef别名机制）已经覆盖了三家模式里"Gateway/Policy层"和"凭证别名层"，**不需要重建**；真正缺的是三家都有、Matbox没有的"具名业务Connector目录"这一层，新增ACTION-F007补齐，架在ACTION-F002之上，不是平行/竞争系统——一个Connector下面挂多个ToolRegistration，共享一个凭证作用域。

## 3｜Own / Reuse / Must Not Rebuild

| 类型 | 对象 | 说明 |
|---|---|---|
| OWN | ActionGateway/Policy/Risk评估/Reauth/Idempotency、ProposedAction schema | Matbox自己的动作权限/风险判定业务规则 |
| REUSE | MCP Gateway生态（Obot/ContextForge/MCPX类方案）做Tool/MCP adapter层 | 不重新造MCP协议层工具调用安全治理 |
| MUST NOT REBUILD | 模型直接SDK调用能力 | 禁止绕过Gateway，所有调用必须经ToolAdapter |

## 4｜Feature Register

| FeatureID | 名称 | 说明 |
|---|---|---|
| ACTION-F001 | ActionGateway核心 | Policy/Risk/Reauth/Idempotency，ProposedAction schema校验 |
| ACTION-F002 | Tool/MCP注册与Adapter层 | 工具/MCP server注册（tool_id/capabilities/risk_level/rate_limit等），基于MCP Gateway生态接入 |
| ACTION-F003 | Action预览与确认 | 高风险动作preview/diff/risk展示，不暴露secret，用户明确确认 |
| ACTION-F004 | 幂等与可逆性 | idempotency key去重，reversibility/compensation引用记录 |
| ACTION-F005 | 10步Enforcement Pipeline | Registry→租户边界→RBAC/ABAC→风险半径→审批→预算→取凭证→限流→执行→审计，源自AI员工底层包 |
| ACTION-F006 | Workflow Registry（确定性多步流程） | ⚠️**2026-09-08标注**：本设计的参照对象 UiPath Maestro Business Rules，其官方页面标题至今仍标 `(preview)`（支持 DMN v1.3）。设计方向不因此推翻——BPMN+DMN 是 OMG 国际标准、五家供应商独立收敛于「确定性骨架+LLM适应」（专项00r收敛②）——但**不得以「UiPath 已经这么做了」作为成熟度依据**；收口时若 Workato/Composio 有更成熟的决策表实现，参照对象可换。用BPMN定顺序、DMN定决策规则，多个ProposedAction组合成一次整体调用，内部每步仍走完整10步Pipeline，不降级单动作治理 |
| ACTION-F007 | Connector Registry（具名业务连接器目录） | 按业务平台分组ToolRegistration（微信/抖音/小红书/Shopify/酷家乐等），共享凭证作用域，供F-CONSOLE-001雇佣/配置AI员工时勾选启用 |

### ACTION-F001 · ActionGateway核心
- **目标**：所有ProposedAction（含employee+AuthContext+resource version）经统一Policy/Risk/Reauth判定后才允许执行。
- **验收标准**：commit前重新校验permission/entitlement/budget/approval，不信任execute请求发起时刻的旧判断。

### ACTION-F002 · Tool/MCP注册与Adapter层（复用MCP Gateway生态，2026-08-30补强注册字段）
- **目标**：每个工具/MCP server先注册（tool_id/tenant_scope/owner/type/version/endpoint_ref/secret_ref/capabilities/allowed_actions/risk_level/data_classes/rate_limit/timeout_ms/healthcheck/status），未注册的工具一律拒绝调用；已注册工具的调用统一经ToolAdapter。
- **验收标准**：未授权/未注册工具被拒绝且留审计；调用链任一环节失败都要有明确denyReason，不是裸的执行失败。

### ACTION-F003 · Action预览与确认
- **目标**：高风险动作在执行前向用户展示可解释的风险/影响范围/diff，用户明确确认后才提交。
- **验收标准**：预览界面不显示任何secret；risk/scope的解释与实际执行范围一致。

### ACTION-F004 · 幂等与可逆性
- **目标**：Activity执行通过worker/outbox完成（不让请求线程无限等待），retry不重复产生外部副作用；记录reversibility/compensation引用供人工或自动回滚。
- **验收标准**：同一idempotencyKey的重复请求只产生一次真实副作用。

### ACTION-F005 · 10步Enforcement Pipeline（2026-08-30从AI员工底层包并入）
- **目标**：每次工具/动作调用严格按顺序经过：①Registry状态检查②租户边界检查③Identity/RBAC/ABAC检查④blast-radius风险半径检查⑤审批要求检查⑥预算检查⑦Secret解析（F-CRED-001）⑧限流/熔断检查⑨执行（F-EGRESS-001出站URL防护在此步生效）⑩结果规范化+审计+成本+trace。
- **验收标准**：委派权限不得放大（delegated agent权限不能超过源Agent本次授权范围）；Web/browser/tool输出必须当作不可信内容处理；高风险副作用在真正执行前必须有第二次policy评估。

### ACTION-F006 · Workflow Registry（确定性多步流程，2026-09-04新增，见2.1节查证结论）
- **目标**：用BPMN定义一个Workflow内部多个动作的执行顺序/分支/并行，用DMN定义纯规则型判断（比如"金额超过X走审批、否则直接执行"），Workflow由多个已注册的ProposedAction步骤组成；AI员工调用Workflow整体，不需要在运行时临时决定这几步的顺序。Workflow定义本身走版本化+测试后才能上线，跟ACTION-F002工具注册是同一套"先注册测试、再允许调用"的纪律。
- **验收标准**：Workflow内部每一步仍然各自完整经过10步Enforcement Pipeline，不能因为"已经是Workflow的一部分"就跳过任何一步（尤其是commit时重新鉴权，ACTION-F001的P0原则同样适用于Workflow内部的每一步）；给定一个已上线Workflow，人为构造中途某一步权限被收回的场景，验证该步仍然被正确拒绝，不会因为是"预先设计好的流程"就被默认放行；Workflow版本变更不影响已经在执行中的旧版本实例。

### ACTION-F007 · Connector Registry（具名业务连接器目录，2026-09-05新增，见2.2节查证结论）
- **目标**：把面向具体业务平台（微信/抖音/小红书/Shopify/酷家乐等）的一组相关ToolRegistration打包成一个具名Connector，共享同一个凭证作用域（对应F-CRED-001一次OAuth授权，不是每个工具各自单独授权一遍）；Connector在F-CONSOLE-001的雇佣/配置界面里以业务名称展示供租户勾选启用，而不是让租户逐个工具去理解技术细节。**初始目录覆盖Matbox两条目标客户线**（家居制造/设计行业，见交接文档第0节"必须严格遵守"）：家居制造+电商侧（微信客服/微信小程序/抖音/小红书/Shopify），设计行业侧（酷家乐等设计工具，具体清单待缺口③业务对象调研确认后补齐，不在此处预先编造）。
- **验收标准**：一个Connector下的多个ToolRegistration必须共享同一个`credentialScopeRef`，不允许同一业务平台下的不同工具各自持有互相独立、未关联的凭证（防止授权碎片化、租户重复走OAuth流程）；Connector被禁用（DISABLED/DEPRECATED）时，其下所有ToolRegistration必须同步不可调用，不能只改Connector状态不联动工具状态；Connector目录变更（新增/下线）必须同步反映在F-CONSOLE-001的可选连接器列表里，不能有Connector在Registry里存在但控制台不可见（或反之）。

### 2.3 三条来自九家横向收口的实现级约束（2026-09-08新增，见专项00r）

#### 2.3.1 两套验签机制不能写成一套

同一家供应商（Zapier）对两类回调用的是**完全不同的验签方式**，混用即生产事故：

| 回调类型 | 验签方式 | 关键细节 |
|---|---|---|
| **Action Run Callback** | `Zapier-Callback-Signature` = **JWT，用 Zapier JWKS 公钥验 RS256** | 含 iat/exp，约 **5 分钟**有效；5xx/网络错误指数退避**最多 3 次**，**4xx 不重试**；按 run_id 幂等；callback 失败仍可 GET 结果兜底 |
| **Connection Webhook** | **Standard Webhooks 规范，HMAC-SHA256** | **必须用 raw body 验签**（先 parse 再序列化会失败）；签名内容 = `webhook-id` + `webhook-timestamp` + raw body；常量时间比较；`whsec_*` secret 仅创建时返回一次，丢失需删掉重建 |

**冻结**：Matbox 的 Provider Adapter 必须为这两类分别实现，禁止抽象成一个通用 `verifySignature()`。（专项00q §1.2）

#### 2.3.2 Canonical Timeout Policy：同一个动作在不同入口有不同 timeout 语义

Workato 实测——**同一个外部动作**，走不同入口的超时上限完全不同：

| 入口 | timeout |
|---|---|
| Recipe 标准 job | **90 分钟**（long pause/action 累计最长 732 天） |
| API Platform | 默认 **30 秒**，最大 **240 秒** |
| Connector SDK runtime HTTP | **3 分钟** |
| OPA 私网请求 | **500 秒** |
| Embedded API | **40 秒** |

Zapier 侧同样：Integration Builder runtime 是 **30 秒**，但 White Label Action Run 存在「>45 秒动作最终完成后仍触发 callback」的描述——**两类运行面必须分别建 SLO，不得用一个 timeout 常量覆盖全部**。

**冻结**：`ActionExecution` 记录必须携带 `entrySurface` 与该 surface 的 `timeoutBudgetMs`；Provider 的 timeout 统一映射成 Matbox 的 `EXECUTION_UNKNOWN`（不可逆动作）或 `TOOL_TIMEOUT`（可安全重试动作），**禁止两者共用一个码**。（专项00q §9.2、§1.1）

#### 2.3.3 若采用 default-deny 的 Connector Policy，必须带两个前提

微软 Advanced Connector Policies 是九家里唯一做到 default-deny 的，但官方文档同时写明两条限制——**抄结论不抄前提，就是把营销口径当能力**：

1. **只覆盖 Certified Connector。** 官方原文：`Advanced connector policies currently apply to certified connectors only. Custom connectors and HTTP connectors aren't yet supported.` 自定义与 HTTP 连接器今天仍归 classic Data Policy 管。
2. **只在 Managed Environment 上能全封。** 非托管环境里 nonblockable connectors **仍然封不掉**。
3. 附带：**MCP 只能整站封，不能封单个 Tool**（`granular control over individual MCP tools ... isn't available`）——Matbox 若要做到 MCP Tool 级 allowlist，这一层必须自建，不能指望 Provider。

**冻结**：Matbox 的 Connector Policy 可以采用 default-deny，但**必须自己做到 Action 级与 MCP Tool 级**，不得因为"微软也是 default-deny"就假定 Provider 层已经覆盖。（专项00q §2.1）

## 5｜核心数据 Contract（逻辑模型，可直接建表/建接口）

**ToolRegistration**（2026-08-30从AI员工底层包`tool_registration`表并入）
toolId, version, tenantScope?, name, type, endpointRef, secretRef?, capabilities[], allowedActions[], riskLevel(0-5), dataClasses[], status(ACTIVE|DISABLED), createdAt

**ProposedAction**
actionId, tenantId, employeeId, toolId+toolVersion（关联ToolRegistration）, resourceScope[], risk(LOW|MEDIUM|HIGH), reversibility(REVERSIBLE|IRREVERSIBLE), budgetRef, status(PROPOSED|APPROVED|EXECUTING|SUCCEEDED|FAILED|DENIED), idempotencyKey, createdAt

**ActionExecution**
executionId, actionId, egressValidationRef（关联F-EGRESS-001校验记录，执行步生效）, compensationRef?, executedAt, resultStatus, costRef（关联F-COST-001）
（说明：AI供应商调用不再经本模块，走F-PROVIDER-001独立的Model Gateway，故本实体不再关联ProviderCallEvent）

**ActionAuditRecord**
recordId, actionId, decision(ALLOWED|DENIED), denyReason?, reauthCheckedAt, actorId

**WorkflowDefinition**（2026-09-04新增，ACTION-F006）
workflowId+version, name, bpmnRef（BPMN流程定义文件引用）, dmnRefs[]（关联的DMN决策表引用，可为空）, stepActionRefs[]（关联的ProposedAction/ToolRegistration步骤序列）, status(DRAFT|VALIDATED|ACTIVE|RETIRED), testManifest{}

**WorkflowRun**（2026-09-04新增，ACTION-F006，一次Workflow整体调用的执行记录）
runId, workflowId+workflowVersion, employeeId, currentStepIndex, stepExecutionRefs[]（关联各步骤对应的ActionExecution）, status(RUNNING|SUCCEEDED|FAILED|PARTIALLY_FAILED), startedAt, completedAt?

**ConnectorDefinition**（2026-09-05新增，ACTION-F007；**2026-09-08按专项00r九家横向收口补强**）
connectorId, name（业务名称，如"微信客服"）, platformCategory(SOCIAL|ECOMMERCE|DESIGN_TOOL|OTHER), **version（语义化版本，2026-09-08新增）**, **tenantId（租户绑定，2026-09-08新增；跨租户引用同一connectorId必须403，见P0规则11）**, toolRegistrationRefs[]（关联的ToolRegistration.toolId列表）, credentialScopeRef（关联F-CRED-001，同一Connector下所有工具共享此凭证作用域）, status(ACTIVE|BETA|DISABLED|DEPRECATED), **lifecycleState(PRIVATE|PROMOTED|AVAILABLE|LEGACY|DEPRECATING|DEPRECATED，2026-09-08新增)**, sourceType(MATBOX_CORE|THIRD_PARTY，**当前阶段仅MATBOX_CORE，THIRD_PARTY字段预留但不在本轮设计第三方接入/审核/分成流程，避免为不存在的场景过度设计**), createdAt

**ConnectorAction**（2026-09-08新增，ACTION-F007；专项00r收敛⑦"连接器数量≠能力"，九家供应商全部主动否定自己的连接器数字）
actionKey（**Matbox稳定业务键**，如`inventory.get_stock`／`customer.send_email`；AI员工与Workflow只认这个，永不写provider侧ID）, connectorId+connectorVersion, **providerActionKey（供应商侧稳定key）**, **providerActionId（供应商侧易变id，可能每次discovery都变，禁止持久化为业务契约）**, canonicalInputSchema, canonicalOutputSchema, readWrite(READ|WRITE|DELETE), riskLevel(0-5), requiredScopes[], approvalPolicyRef?, costEstimate?, lastVerifiedAt, status
（**为什么必须拆两个provider字段**：Zapier官方要求每次`POST /v2/action-runs/`前重新Get Actions取新id，旧id不能持久化；Composio #4253证明"有某Connector"≠"该Connector所有动作可做"（managed OAuth缺scope时邻近工具仍被返回）。见专项00q §1.2、§10.2。）

**ConnectorHealth**（2026-09-08新增，ACTION-F007；专项00r收敛④"Provider报的状态不可信"，四家独立到达）
connectorId+connectorVersion, **catalogHealth**（目录里是否存在）, **searchHealth**（能否被能力检索召回）, **schemaHealth**（schema能否加载且跨provider转换不失真）, **executeHealth**（真实调用成功率/p95/错误分类）, lastProbeAt, degradedReason?
（**四态必须独立**：Composio #3776实测——混合auth/no-auth toolkit时`session.search`会漏掉工具，但`execute`照样能跑。**"Search无结果"不等于"能力不存在"**，把四者合并成一个"可用/不可用"必然误判。）

**ConnectionVerification**（2026-09-08新增；专项00r收敛④）
connectionRef（关联F-CRED-001）, providerReportedStatus（供应商说的，如ACTIVE）, **matboxVerifiedStatus(UNVERIFIED|VERIFIED|FAILED)**, lastVerifiedAt, probeEvidenceRef
（**Provider的ACTIVE不等于凭据有效**：Composio GitHub #4120——填入垃圾API Key仍可创建`status=ACTIVE`的Connected Account，26/26复现。首次执行写动作前必须做一次安全的credential probe，probe结果才是Matbox的事实。）

**TriggerAttempt**（2026-09-08新增；专项00r收敛⑤"Webhook不是可靠消息队列"，三家独立到达）
attemptId, tenantId, connectorId, providerEventId, receivedAt, **verifyResult(SIGNATURE_OK|SIGNATURE_FAIL|AUTH_REJECTED)**, persistedAt?, routedRunRef?（**可为空**）, status(RECEIVED|VERIFIED|PERSISTED|ROUTED|FAILED|DEAD_LETTER)
（**必须独立于Run存在**：Activepieces GitHub #14328/#14808实测——若Connection刷新失败或Webhook鉴权拒绝发生在正式Run创建**之前**，就没有Run可供告警系统捕获，调用方还可能收到HTTP 200。若TriggerAttempt挂在Run下面，这类静默失败永远看不见。）

**API 端点（最小集合）**
- `POST /action/registry/tools` — 注册工具/MCP server（对应AI员工底层`/v1/registry/tools`）
- `POST /action/propose` — 提交一个ProposedAction，返回预览（risk/diff/scope）
- `POST /action/{actionId}/execute` — commit时重新鉴权后按10步Enforcement Pipeline真正执行
- `GET /action/{actionId}` — 查询动作状态/审计记录
- `POST /action/{actionId}/compensate` — 触发可逆动作的补偿/回滚（仅reversibility=REVERSIBLE适用）
- `POST /action/workflows` — 注册一个Workflow定义（BPMN+DMN引用+步骤序列），需先VALIDATED才能ACTIVE（2026-09-04新增，ACTION-F006）
- `POST /action/workflows/{workflowId}/run` — 调用一个已上线Workflow，内部按BPMN定义顺序逐步执行，每步仍走完整10步Pipeline（2026-09-04新增，ACTION-F006）
- `GET /action/workflow-runs/{runId}` — 查询一次Workflow整体执行的进度/状态（2026-09-04新增，ACTION-F006）
- `POST /action/connectors` — 注册一个Connector定义（业务名称+关联的ToolRegistration列表+凭证作用域）（2026-09-05新增，ACTION-F007）
- `GET /action/connectors` — 查询可用Connector目录（供F-CONSOLE-001雇佣/配置界面展示）（2026-09-05新增，ACTION-F007）
- `POST /action/connectors/{connectorId}/disable` — 禁用一个Connector，联动其下所有ToolRegistration不可调用（2026-09-05新增，ACTION-F007）
- `GET /action/connectors/{connectorId}/actions` — 按租户/员工可见范围返回Action级能力清单（**不是返回整个Connector**）（2026-09-08新增，ACTION-F007）
- `POST /action/connectors/{connectorId}/health-probe` — 触发四态Health探测（catalog/search/schema/execute）（2026-09-08新增）
- `POST /action/connections/{connectionRef}/verify` — 对Provider报的ACTIVE做独立credential probe，写入ConnectionVerification（2026-09-08新增）
- `GET /action/trigger-attempts` — 查询TriggerAttempt（含尚未产生Run的失败尝试）（2026-09-08新增）
- `POST /action/connector-versions/{connectorId}/compatibility-check` — 升版本前做破坏性变更检测（2026-09-08新增）

## 6｜P0 冻结规则

1. 模型/业务代码绕过ActionGateway直接调用第三方API或工具side effect：不允许。
2. 未注册工具被调用：不允许（对应AI员工底层威胁模型"malicious MCP/tool server"）。
3. commit时不重新校验permission/entitlement/budget/approval：不可降级P0。
4. 高风险动作预览暴露secret：不允许。
5. 重试产生重复副作用（幂等失败）：不允许。
6. 委派权限被放大（delegated agent权限超过源Agent授权范围）：不可降级P0。
7. Workflow内部任一步骤跳过完整10步Enforcement Pipeline（因为"已经是预先设计好的流程"就默认放行）：不可降级P0（2026-09-04新增，ACTION-F006，见2.1节）。
8. 同一Connector下的多个ToolRegistration使用互相独立、未关联的凭证（凭证作用域碎片化）：不允许（2026-09-05新增，ACTION-F007，见2.2节ServiceNow"别名"教训）。
9. **以Connector为单位验收"已接入"**：不允许（2026-09-08新增，专项00r收敛⑦，九家一致）。验收单位必须是 `Connector + Action + 输入输出 + Scope + Risk + 真实成功Test`。Salesforce原文：「一个 Connector 不是一个能力。比如 Shopify Connector 下面还要继续拆 Product、Inventory、Order、Customer、Refund 等动作；真正给 AI 员工的是动作，不是整个 Connector。」
10. **把Provider返回的易变action id持久化为业务契约、或让AI员工直接调用provider-specific action id**：不允许（2026-09-08新增）。AI员工只认Matbox的`actionKey`；provider侧id每次discovery重取。
11. **跨租户引用同一个connectorId/connectionRef**：不允许，必须403+安全审计（2026-09-08新增，补齐ACTION-F007原设计中缺失的租户级凭据隔离）。
12. **把Provider报的连接状态（如ACTIVE）直接当作"凭据已验证"**：不允许（2026-09-08新增，专项00r收敛④）。必须有独立的`matboxVerifiedStatus`，首次写动作前probe。
13. **TriggerAttempt依附于Run存在**：不允许（2026-09-08新增，专项00r收敛⑤）。事件必须先验签→持久化→去重→再路由；未能产生Run的失败尝试同样必须可见可告警。
14. **把 Action Run Callback 与 Connection Webhook 抽象成同一个验签实现**：不允许（2026-09-08新增，见2.3.1）。前者是 JWT/JWKS RS256、5 分钟有效、4xx 不重试；后者是 Standard Webhooks HMAC + raw body。
15. **用单一 timeout 常量覆盖所有执行入口**：不允许（2026-09-08新增，见2.3.2）。`ActionExecution` 必须记录 `entrySurface` 与对应 `timeoutBudgetMs`；不可逆动作超时必须落 `EXECUTION_UNKNOWN` 而非 `TOOL_TIMEOUT`。

## 7｜当前唯一继续断点

Stage 10（真实接入MCP Gateway、真实Tool/第三方API adapter、真实与F-EGRESS-001联调）尚未开始。下一步：把 ACTION-F001~F005 转成 WorkPackage，对应AI员工底层WP-007，需与F-EGRESS-001、F-CRED-001协调部署顺序（本模块依赖两者已就绪）。

## 附录｜来源

- 内容来源：《Matbox_多端平台_CURRENT_正式开发文档_V3.0》F-ACTION-001 章节（2026-08-30核对确认）
- 调用链依据：架构原则第32条（2026-08-30预先记录）
- 技术选型依据：MCP Gateway生态（2026年Linux Foundation治理、97M+下载、13K+已注册server；Obot/ContextForge/MCPX/Lunar为代表方案）
- **结构性修正依据（2026-08-30）**：《Matbox_AI_Employee_System_V6.3_Final_Frozen》底层包 `06_API_Contract/contracts/mcp_tool_gateway_contract.md`、`04_Domain_Schema/migrations/004_registry_invocation.sql`（tool_registration/tool_invocation表）、WP-007定义
- **ACTION-F006 Workflow Registry依据（2026-09-04）**：用户提供ServiceNow官方33页Blueprint+ServiceNow→Matbox映射母文档+2份Salesforce Agentforce深度调研（原文见`docs/技术选型报告/参考资料_AI员工竞品原始文档_2026-09-04/`），本会话补查UiPath Maestro真实产品（[UiPath Maestro](https://www.uipath.com/product/maestro)：BPMN engine+DMN decision engine作为Orchestration Layer核心）；详见架构原则第72条
- **ACTION-F007 Connector Registry依据（2026-09-05）**：[Agentforce MuleSoft](https://www.mulesoft.com/platform/agentforce)、[Extending Agentforce with External MCP Tools via MuleSoft](https://developer.salesforce.com/blogs/2026/08/extending-agentforce-with-external-mcp-tools-via-mulesoft)、[Salesforce MuleSoft $6.5B acquisition rationale](https://www.techtarget.com/it-infrastructure/news/252437506/Salesforces-MuleSoft-acquisition-shows-API-management-appeal)、[ServiceNow Integration Hub](https://www.servicenow.com/products/integration-hub.html)、[ServiceNow Spoke Development Best Practices](https://github.com/ServiceNowDevProgram/SpoketoberfestResources/blob/master/SpokeDevelopmentBestPracticesPublic.md)、[UiPath Integration Service](https://www.uipath.com/product/integration-service)、[UiPath Marketplace Monetization](https://ir.uipath.com/news/detail/200/uipath-marketplace-unveils-monetization-of-automation-content-opening-new-revenue-stream-for-partners-and-creating-faster-delivery-of-automation-projects)
