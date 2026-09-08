# Matbox 成本控制（F-COST-001）

正式开发文档 · V1.0-RC · 2026-08-29

## 当前定位

本专项解决"AI 员工花了多少钱、有没有超预算、谁在烧钱"的问题。是 Platform Core 的共享能力，被 F-DQ-012（AI Code Review）等模块依赖，也是 Provider Router（架构原则第9条分级路由）做"按成本选模型"决策的数据来源。

**与 Provider Router 的关系：** 两者不合并成一个模块。Provider Router 负责"怎么路由/切换模型"，F-COST-001 负责"花了多少钱、超没超预算"，各自独立、通过接口互通。原因见下方调研结论。

**DocID**: MATBOX-COST-GATE-20260829-V1.0-RC
**状态**: DRAFT_RESEARCH_COMPLETE
**2026-08-30 补充**：新增 COST-F005（企业套餐用量账本/预算/权益），来自《Matbox_多端平台_CURRENT_正式开发文档_V3.0》F-COST-001 章节——该文档也用了 F-COST-001 这个编号，但管的是"企业订阅套餐扣费额度"，跟COST-F001~F004管的"AI调用花了多少钱"是两件相关但不同的事。核对后确认是真实缺口，并入本文档当新Feature，不单独占用编号（详见架构原则第31条）。

**2026-08-30 核对AI员工底层包**：`cost_ledger`表要求append-only+最小归因到tenant/employee/task/provider/model-tool/timestamp，跟本文档"源头span/trace打租户标签，不靠账单事后反推"的原则方向一致，无冲突；`cost_model.csv`列出9个成本维度（llm_input/output/image/video/gpu/browser/storage/human_review/retry_waste），比本文档原先的usageType枚举更完整，已并入UsageLedgerEntry（见第5节）；`budget_policy`表的"预算检查在昂贵调用前+高风险副作用前各查一次"跟COST-F005的reserve→execute→commit/release模式是同一个思路的两种表述，不冲突。

## 1｜不可变原则

1. 每一次 AI 调用的花费必须可追溯到具体是哪个 AI 员工、哪个任务、哪次 WorkPackage 花的，不能只有一个总账数字。
2. 预算告警必须是"软性提醒"而不是自动断电式硬阻断（除非用户明确要求硬限制）——避免任务跑到一半突然被切断导致数据不一致。
3. 不为了省成本，把任务悄悄换成更便宜但效果不够的模型而不留痕迹——降级选择必须可追溯，配合第6条评测框架验证效果没有下降。

## 2｜全球调研结论（2026-08-29）

### 2.1 关键决策：成本控制不与 Provider Router 合并

调研初期倾向"用 LiteLLM 一个工具同时做路由+成本控制"，但深入查证后否决：

- LiteLLM 自带的预算管理"层级比专门的成本工具更扁平"，团队级预算强制执行等治理功能在开源版中被阉割（需付费企业版）。
- 自建 LiteLLM 网关需要额外部署 Redis（缓存/限流）+ PostgreSQL（费用记录存储），不是轻量接入，是新增两块基础设施的维护负担。
- 真实案例显示自建这套东西的实际月度总拥有成本（TCO）在中低请求量下反而高于直接使用其他方案。

**结论：Provider Router 的技术选型（是否用LiteLLM）留到该模块单独设计时再定；F-COST-001 现在先独立展开，不因为"顺便"而绑定 LiteLLM。**

### 2.2 成本追踪工具选型

| 候选 | 说明 | 结论 |
|---|---|---|
| **Langfuse** | 开源，成本记录直接嵌在调用链路（trace）里，精确到每个AI员工每一步；对多智能体场景友好 | **采用** |
| Finout / Mavvrik / Amnic | 商业SaaS，企业级FinOps平台 | 不用——团队规模不需要，且是托管服务，与自建优先原则冲突 |

### 2.3 预算告警模式（2026年小团队常见做法）

**"软性配额+提醒"**：给团队设一个月度预算，花到80%在协作工具（如 Slack）提醒一次，花到100%再提醒一次，通知到负责人；不做"一超预算就断电"式硬阻断，避免任务跑一半被强制中断。

## 3｜Own / Reuse / Must Not Rebuild

| 类型 | 对象 | 说明 |
|---|---|---|
| OWN | 预算规则、告警阈值、成本归因到WorkPackage/AI员工的业务逻辑 | Matbox 自己的成本治理规则 |
| REUSE | Langfuse 的调用链路成本记录能力 | 不重新造 token 计价/追踪逻辑 |
| MUST NOT REBUILD | 各 AI 供应商的计价规则本身 | 直接读供应商官方定价，不自己维护一套费率表还要手动更新 |

## 4｜Feature Register

| FeatureID | 名称 | 说明 |
|---|---|---|
| COST-F001 | Langfuse 成本追踪接入 | 记录每次AI调用的token/费用，关联到WorkPackage/AI员工身份 |
| COST-F002 | 预算规则与阈值配置 | 月度/项目预算设置 |
| COST-F003 | 软性配额告警 | 80%/100%提醒，通知负责人 |
| COST-F004 | 成本归因查询接口 | 供 Provider Router 分级路由、F-DQ-012 等模块查询 |
| COST-F005 | 企业套餐用量账本/预算/权益（Usage Ledger/Budget/Entitlement） | 企业订阅套餐扣费与额度管理，2026-08-30从多端平台文档并入 |

### COST-F001 · Langfuse 成本追踪接入
- **目标**：所有 AI 调用（无论走哪个供应商）的花费都记录下来，精确到具体 WorkPackage 和 AI 员工身份。
- **依赖**：F-CRED-001（AI员工身份识别）、F-OBS-001（trace数据来源）。
- **验收标准**：任意一次AI调用能查到花了多少钱、是谁花的、为了什么任务。

### COST-F002 · 预算规则与阈值配置
- **目标**：能设置月度总预算、按项目/模块的预算上限。
- **验收标准**：预算规则可配置、可修改，修改留痕。

### COST-F003 · 软性配额告警
- **目标**：花费到80%/100%阈值时自动通知负责人，不硬性掐断正在进行的任务。
- **验收标准**：告警触发准确、及时，不误报不漏报。

### COST-F004 · 成本归因查询接口
- **目标**：其他模块（尤其是 Provider Router 做分级路由决策时）能查询"这类任务历史平均花多少钱"，辅助路由决策。
- **验收标准**：查询接口返回数据与 Langfuse 原始记录一致。

### COST-F005 · 企业套餐用量账本/预算/权益（Usage Ledger/Budget/Entitlement，2026-08-30新增；2026-09-02补充具体计费模式，见架构原则第42条#5/#6）
- **目标**：统一记录LLM/图片/视频/Tool/API成本，并限制企业套餐/预算——这是"企业订阅套餐扣费"逻辑，跟COST-F001~F004的"AI调用花了多少钱"是两件相关但不同的事：F001~F004回答"这次任务花了多少钱"，F005回答"这个企业套餐额度还剩多少、能不能继续用"。
- **计费模式（2026-09-02确认）**：**混合模式**——基础订阅费包含一定用量额度（entitlement），超出额度部分另计费（走UsageLedger按实际用量结算），不是纯订阅制（额度用不完不退，超了不能用）也不是纯按量付费。**大模型成本转嫁方式**：额度内的部分模型调用成本已打包进订阅费定价（企业感知不到底层模型单价波动），超出额度的部分按接近实际provider成本价透传给企业（不在超额部分上加价牟利，超额定价单独维护一份`overagePricingVersion`，与订阅套餐定价版本分开管理，防止provider调价时需要同步改两份不相关的定价）。
- **In Scope**：usage ledger（只追加账本）；provider usage归一化；预算预留/提交（reserve→execute→commit/release）；quota；权益(entitlement)；多币种；**订阅额度+超额透传的双轨计费逻辑**。
- **Out of Scope**：不靠前端隐藏套餐信息假装限制；不让provider账单直接变成内部事实源。
- **上游输入**：task/action/provider usage事件。
- **下游输出**：账本条目 + 预算/额度判定。
- **页面/入口**：`/settings/billing-usage`；任务成本面板
- **依赖**：无前置阻塞，逻辑上依赖COST-F001已有的Langfuse trace数据作为usage事件来源。
- **验收标准（按七层施工面，原样保留自多端平台文档，未做删减）**：
  - Frontend/UI：用量/预算/额度/拒绝原因可见，不暴露provider密价合同；quota界面与后端一致。
  - Backend/API/Service：UsageLedger/Budget/Entitlement检查；Action/Provider不得自建计费逻辑；reserve→execute→commit/release契约；并发预算不超支，commit时二次校验。
  - Data/DB/Migration：账本只追加不可静默覆盖；可对账(reconciliation)。
  - Async/Runtime：provider用量对账/告警；重复callback不重复记账。
  - Provider：provider用量/成本适配器；业务不得直接解析provider发票；provider切换不影响账本连续性。
  - Infra/Config：定价/版本配置+功能开关；不硬编码价格在UI里；baseline记录定价版本。
  - Tests/Observability：并发/重试/重复callback/多币种测试；同一幂等键只记一次被接受的成本。

## 5｜核心数据 Contract（逻辑模型，可直接建表/建接口）

**CostEvent**（Langfuse trace中记录，本模块只做归因与查询）
costEventId, traceId（关联F-OBS-001的AgentTraceEvent）, agentId, workPackageId, tenantId, provider, model, tokensIn, tokensOut, costUsd, timestamp

**BudgetRule**（2026-09-02新增`hardCapEnabled`字段，落实架构原则第39条）
budgetId, scope(tenant|project|workPackageType|employeeId), periodType(monthly), limitUsd, alertThresholds[](默认[80,100]), currentSpendUsd, hardCapEnabled(bool，默认false，租户管理员可对单个AI员工/单个预算规则单独开启"硬性自动暂停"，参照Google Gemini Enterprise 2026年8月上线的真实做法), updatedAt

**BudgetAlertEvent**
alertId, budgetId, thresholdHit(80|100), notifiedAt, notifyChannel, acknowledged(bool)

**UsageLedgerEntry**（COST-F005，append-only账本，2026-08-30新增，原样保留自多端平台文档的字段定义；2026-08-30核对AI员工底层包`cost_model.csv`+`cost_ledger`表后补强usageType枚举与最小归因字段）
ledgerEntryId, tenantId, employeeId?（关联F-AIEMP-001的EmployeeInstance）, workPackageId?, usageType(llm_input|llm_output|image|video|gpu|browser|storage|human_review|retry_waste|tool|api), unit（token|generation|second|gb_month|minute等，随usageType变化）, quantity, unitCost, costUsd, provider?, idempotencyKey, recordedAt
（说明：底层包`cost_ledger`表明确"append-only"+"最少归因到tenant/employee/task/provider/model-tool/timestamp"，本表字段已满足；`retry_waste`维度此前遗漏，专门统计重试浪费的成本，2026-08-30补上）

**BudgetReservation**（COST-F005，reserve→execute→commit/release模式）
reservationId, tenantId, entitlementId, reservedAmountUsd, status(RESERVED|COMMITTED|RELEASED), createdAt, resolvedAt?

**Entitlement**（COST-F005，企业套餐权益；2026-09-02补充计费模式字段）
entitlementId, tenantId, planType, quotaLimitUsd, quotaUsedUsd, periodStart, periodEnd, **overagePricingVersion**（超额部分定价版本号，与`planType`对应的订阅定价版本分开维护，provider调价只需更新此版本不影响订阅套餐定价）, **overageBillingMode**（固定值`NEAR_COST_PASSTHROUGH`，超额部分按接近provider实际成本价透传，不加价牟利）

**API 端点（最小集合）**
- `GET /cost/summary?workPackageId=` — 查询某任务花费
- `GET /cost/summary?agentId=&period=` — 查询某AI员工周期花费
- `POST /cost/budgets` — 设置预算规则
- `GET /cost/route-hint?taskType=` — 供Provider Router查询"这类任务历史平均花费"，辅助分级路由决策
- `POST /cost/reservations` — 预留一笔预算额度（COST-F005，reserve阶段）
- `POST /cost/reservations/{reservationId}/commit` — 提交预留，正式扣费
- `POST /cost/reservations/{reservationId}/release` — 释放预留（任务取消/失败）
- `GET /cost/entitlements/{tenantId}` — 查询企业套餐当前额度/用量

## 6｜P0 冻结规则

1. 成本数据被静默丢失或不归因到具体AI员工/任务：视为设计缺陷。
2. 为省钱擅自降级模型且不留痕迹、不经评测框架验证效果：不允许。
3. **预算/额度检查服务不可用时必须fail-closed（直接拒绝执行），不允许fail-open（放行）**：2026-08-30深度核实新增。查证分布式系统真实故障模式发现，"降级时优先保证请求成功"这类看似合理的工程决策，是授权类事故最常见的真实成因——COST-F005的reserve阶段如果查不到额度状态，必须按"拒绝"处理，不能因为"检查服务挂了就别管了、先放行"。

## 7｜当前唯一继续断点

Stage 10（真实部署 Langfuse，接通真实 AI 调用数据）尚未开始，且依赖 F-CRED-001（AI员工身份）和 F-OBS-001（trace数据）先落地。下一步：把 COST-F001~F005 转成 WorkPackage。

## 附录｜来源

- [Best LLM Cost Tracking Tools in 2026](https://www.getmaxim.ai/articles/best-llm-cost-tracking-tools-in-2026/)
- [LiteLLM Review 2026: Features, Pricing, Pros and Cons](https://www.truefoundry.com/blog/a-detailed-litellm-review-features-pricing-pros-and-cons-2026)
- [LiteLLM Pricing 2026: Open-Source & Enterprise Cost Breakdown](https://www.truefoundry.com/blog/litellm-pricing-guide)
- [Top 5 AI Gateways for Cost-Aware LLM Routing in 2026](https://www.getmaxim.ai/articles/top-5-ai-gateways-for-cost-aware-llm-routing-in-2026/)
- [AI Cost Visibility in 2026: Strategies, Tools, and Best Practices](https://www.finout.io/blog/ai-cost-visibility-in-2026-strategies-tools-and-best-practices)
- COST-F005 内容来源：《Matbox_多端平台_CURRENT_正式开发文档_V3.0》F-COST-001 章节（2026-08-30 核对合并，详见架构原则第31条）
- COST-F005 设计独立核实（2026-08-30，按12条完整核对表执行，非单次搜索）："reserve→execute→commit/release"经查证是支付行业标准的"预授权→扣款/撤销"模式（Authorization Hold→Capture/Void）搬到AI用量计费上，加上幂等键防重复扣费，与2026年LLM计费成熟做法一致；补充核实真实分布式系统失败模式后，新增P0规则6.3条（预算检查服务不可用必须fail-closed）——[How Do You Meter LLM Token Usage for Billing?](https://flexprice.io/blog/how-to-meter-llm-tokens-usage-for-billing)、[PayPal Authorization and Capture](https://developer.paypal.com/api/nvp-soap/paypal-payments-pro/integration-guide/authorizations/)、[Handling failures in distributed systems: Patterns and anti-patterns](https://www.statsig.com/perspectives/handling-failures-in-distributed-systems-patterns-and-anti-patterns)
- **成本维度/归因字段核对依据（2026-08-30）**：《Matbox_AI_Employee_System_V6.3_Final_Frozen》底层包`08_质量安全成本/cost/cost_model.csv`、`04_Domain_Schema/migrations/005_artifact_quality_cost_audit.sql`（cost_ledger/budget_policy表）、`06_API_Contract/contracts/billing_admin_contract.md`
- **BudgetRule.hardCapEnabled依据（2026-09-02，架构原则第39条）**：[Flexible billing and cost controls for agents on Google Cloud — Google Cloud Blog](https://cloud.google.com/blog/products/ai-machine-learning/flexible-billing-and-cost-controls-for-agents-on-google-cloud)——Gemini Enterprise 2026年8月26日上线真实硬性预算上限功能，官方同时提醒需权衡"中途暂停打断关键业务流程"的风险
- **计费模式（订阅+超额透传）依据（2026-09-02）**：[Matbox_架构设计原则.md](Matbox_架构设计原则.md)第42条#5/#6（27道产品/商业定义问题确认记录）
