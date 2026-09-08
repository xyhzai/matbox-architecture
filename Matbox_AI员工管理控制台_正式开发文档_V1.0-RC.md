# Matbox AI员工管理控制台（F-CONSOLE-001）

正式开发文档 · V1.0-RC · 2026-08-30

## 当前定位

本专项解决企业管理员登进 Matbox 后台后，实际怎么管好自己雇的这批 AI 员工——从"该雇哪个"到"怎么训练它""它做得好不好""还能花多少钱""所有信息汇总在哪一眼看清"的完整闭环。这是面向租户管理员的第一方产品体验层，本身**不重新造能力**，绝大部分是已建成后端能力（F-AIEMP-001模板/F-COST-001账本/F-OBS-001证据与质量漂移/F-SUPERVISOR-001 Monitor发现/F-ORCHESTRATOR-001路由记录）的自助式聚合呈现，加少量新增的"训练反馈"编排逻辑。

**这是"AI员工能力缺口调研清单"#13(雇佣中心)/#14(训练中心)/#15(质检/评分中心)/#16(成本+预算中心)/#18(统一控制台)定性为🟠(现在就该做)后的正式设计**。#17(AI Value/ROI追踪)在调研清单中仍为🟡（跟成本中心不是一回事，需要真实业务价值数据才能设计具体算法），本文档只在Control Tower里预留扩展位，不现在设计具体实现。

**DocID**: MATBOX-CONSOLE-GATE-20260830-V1.0-RC
**状态**: DRAFT_RESEARCH_COMPLETE

## 1｜不可变原则

1. 本模块不重新存一份AI员工的业务数据（模板/成本/质量/审批记录），全部通过已有模块的API聚合展示，禁止"两份真相"——任何字段如果已经在F-AIEMP-001/F-COST-001/F-OBS-001里有唯一事实源，本模块只做投影，不复制存储。
2. 业务人员在控制台里对AI员工做的任何有实际效果的操作（训练反馈生效、预算调整、Pause/Suspend/Retire等）都必须走已有的审批/审计通道（F-APPROVAL-001/F-OBS-001/AIEMP-F004），不允许控制台自己开一条绕过审计的后门。
3. 成本预测是"参考建议"，不能变成"自动阻断业务执行"——延续F-COST-001已确认的"80%/100%软性提醒、不硬阻断"原则，除非用户本人/产品明确决定升级为硬阻断并留痕。
4. 质检评分必须带证据链（evidenceBundleRef），不允许只给一个分数不给依据。

## 2｜全球调研结论（2026-08-30，全部来自"AI员工能力缺口调研清单"已完成的第二轮真实案例验证，本节做架构化提炼）

### 2.1 雇佣中心（Hiring Center）——参照Salesforce Agentforce，避免同一个坑

真实数据：Agentforce正面反馈是"案件处理时间最多降40%、低代码Builder减轻管理员负担"；差评是"对平台生态不熟的人学习曲线陡、中小企业觉得贵"。**结论**：雇佣中心的核心设计目标是"业务人员自助可用"，浏览/对比/智能匹配的交互复杂度必须压得比工程师工具低一个档次，这跟#14训练中心是同一条硬要求，不是可选的体验优化。

### 2.2 训练中心（Training Center）——业务人员自助反馈，不能靠工单

**结论**：训练中心存在的意义是让业务人员自己能改AI员工的行为，不用每次都提工单等工程师改配置——这是企业能不能真正用起来的硬要求。但"自助"不等于"绕过审计"：反馈提交后是否生效、怎么生效，仍要走AIEMP-F004的配置版本审计，只是审批链路要比工程师改代码短、快。

### 2.3 质检/评分中心（QC & Scoring Center）——参照Medallia，警惕"大而全"

背景数据：57%的企业AI已上生产，但32%把"质量"列为头号阻碍，这是真实规模化痛点。真实案例Medallia（G2 4.5分）核心优势是"质检数据能接入产品策略/政策决策/高管看板，不只是一张打分报表"；差评是"实施是个大工程、不如专用QA工具灵活"。**结论**：质检中心第一版只做"评分卡+证据链下钻+接入现有OBS-F007质量漂移告警"，不做Medallia式的全公司策略决策中枢，避免重蹈"大而全导致实施笨重"的坑。

### 2.4 成本+预算中心产品化——从后端账本到自助体验，新增预测能力

F-COST-001已有完整的记账+预算告警后端能力（COST-F001~F005），本模块要做的是把它变成租户管理员能自己看、自己配置预警线的自助界面，并新增此前完全没有的**成本预测**能力（不是只回顾"花了多少"，还要回答"照这个趋势下去这个月/这个季度大概要花多少"）。

### 2.5 统一控制台（Control Tower）——ServiceNow五支柱模式，ROI留扩展位

真实具名客户案例（ServiceNow AI Control Tower）：罗利市政府IT服务台成本降66%、霍尼韦尔合规认证提速75%、Avalara每月省800小时。诚实结论：**这类平台投不投得划算，不取决于AI多炫，取决于客户会不会持续扩大合同**——因为平台让"自主工作更安全、更高产"这件事本身可衡量、可追责。组织框架采纳Gartner AI Governance Platform MQ的Discover/Observe/Govern/Secure/Measure五支柱，与本模块CONSOLE-F001~F004及已有的F-ORCHESTRATOR-001/F-SUPERVISOR-001/F-TENANT-001分别对应。**Measure支柱下预留#17(AI Value/ROI追踪)的扩展位**——IBM在Gartner报告里强调这是核心差异化能力（"值不值"而非"花了多少"），但具体算法需要真实业务结果数据（如AI员工促成的实际业务成交额）才能设计，现在只占位不实现。

## 3｜Own / Reuse / Must Not Rebuild

| 类型 | 对象 | 说明 |
|---|---|---|
| OWN | 控制台聚合视图逻辑、TrainingFeedback的接收与路由规则、成本预测的趋势推算逻辑 | Matbox自己的管理台业务规则 |
| REUSE | F-AIEMP-001模板/实例数据、F-COST-001账本与预算告警、F-OBS-001证据与质量漂移检测、F-SUPERVISOR-001 Monitor发现、F-ORCHESTRATOR-001路由记录 | 全部投影读取，不复制存储 |
| MUST NOT REBUILD | 审批引擎、审计日志系统、成本记账系统 | 复用F-APPROVAL-001/F-OBS-001/F-COST-001，不新建第二套 |

## 4｜Feature Register

| FeatureID | 名称 | 说明 |
|---|---|---|
| CONSOLE-F001 | 雇佣中心（Hiring Center） | 浏览/对比/智能匹配EmployeeTemplate，业务人员自助可用 |
| CONSOLE-F002 | 训练中心（Training Center） | 业务人员自助提交行为修正反馈，经AIEMP-F004审计生效 |
| CONSOLE-F003 | 质检/评分中心（QC & Scoring Center） | 评分卡+证据链下钻，接入OBS-F007质量漂移告警，不做全公司策略中枢 |
| CONSOLE-F004 | 成本+预算中心（含成本预测） | F-COST-001的自助体验层，新增趋势预测能力 |
| CONSOLE-F005 | 统一控制台（Control Tower） | Discover/Observe/Govern/Secure/Measure五支柱聚合，Measure下预留ROI扩展位 |

### CONSOLE-F001 · 雇佣中心（Hiring Center）
- **目标**：企业管理员能浏览/对比已发布的EmployeeTemplate（F-AIEMP-001），输入业务需求描述获得推荐匹配，交互复杂度对标"业务人员自助可用"而非工程师工具。**同时支持两种雇佣路径**（2026-09-02，见架构原则第42条#1）：①**模板雇佣**（默认路径，多数用户使用）——从F-AIEMP-001已发布的EmployeeTemplate直接雇佣或按需微调；②**从零自建**（面向高级用户/有复杂定制需求的租户）——从空白开始定义role/skills/sop_ref等EmployeeTemplate字段，走AIEMP-F001完整的Draft→Validated→Active校验流程，不因为是"自建"就绕过Golden Set验收。
- **依赖**：F-AIEMP-001（AIEMP-F001模板Registry）。
- **已知交叉依赖（不是本条独立缺陷）**：智能匹配的准确度依赖需求描述的结构化程度——这跟调研清单#1真实案例验证中发现的"Agentforce路由准不准取决于角色定义/任务描述够不够结构化"是同一个前提，也跟#30(PIM结构化数据)相关，需要一起看。
- **Out of Scope（Stage 10前不实现）**：具体匹配算法的打分权重；"从零自建"路径的引导式Builder UI具体交互设计。
- **验收标准**：管理员输入一段业务需求描述，能拿到按相关性排序的模板推荐列表，且能看到"为什么推荐这个"的可解释依据，不是黑盒打分；选择"从零自建"的管理员，创建出的EmployeeTemplate必须和模板库来源的Template走同一套校验/审计标准，不允许自建路径产出未经验证就能直接上生产的AI员工。

### CONSOLE-F002 · 训练中心（Training Center）
- **目标**：业务人员对AI员工某次产出不满意时，能直接提交修正反馈（如"这类问题应该这样处理"），反馈进入审核队列，经AIEMP-F004配置版本审计确认后才实际生效，不能工程师改工单才能改。**业务流配置的人工介入分两档**（2026-09-02，见架构原则第42条#25）：①**简单场景走自助**——本条描述的TrainingFeedback自助提交/审计生效路径，租户自己就能完成；②**复杂场景可付费请Matbox顾问介入**——当业务流配置复杂度超出自助UI能覆盖的范围（如涉及跨多个AI员工的SOP联动、非标准审批链设计），租户可发起"顾问介入请求"，由Matbox方人工顾问协助完成配置，该动作走独立的商务/定价流程（非本文档技术架构范围，具体定价/流程由业务侧另行确定），但产出的配置变更同样必须经AIEMP-F004审计，不能因为是"顾问代做"就绕过留痕。
- **依赖**：F-AIEMP-001（AIEMP-F004配置版本与审计）、F-APPROVAL-001（涉及policy变更时的审批）。
- **Out of Scope（Stage 10前不实现）**：顾问介入请求的具体商务流程/定价页面（业务层范畴，非技术架构）。
- **验收标准**：提交的反馈必须有明确的生效/驳回状态可查；反馈被采纳后，对应EmployeeInstance的配置变更必须留下可追溯的diff记录，不能"悄悄改了但查不到"；顾问介入产生的配置变更在审计记录里必须能区分"租户自助提交"与"顾问代为配置"两种来源，不能混为一谈。

### CONSOLE-F003 · 质检/评分中心（QC & Scoring Center）
- **目标**：管理员能查看某个AI员工实例的质量评分卡，评分卡数据来自F-OBS-001已有的OBS-F007（生产质量漂移检测）和F-SUPERVISOR-001的MonitorReview，点开任意一项能下钻到具体的证据（evidenceBundleRef），不是只给一个数字。**评分标准归属**（2026-09-02，见架构原则第42条#2）：Matbox提供默认评分rubric（覆盖准确性/合规性/效率等通用维度），企业可在默认标准基础上调整权重或新增自定义维度，不强制企业从零定义评分标准，也不锁死只能用Matbox默认值。**训练前后对比视图**（2026-09-02，见架构原则第42条#21）：管理员提交训练反馈（CONSOLE-F002）并生效后，本中心需展示"训练前基线分数 vs 训练后当前分数"的对比视图，复用OBS-F007已有的基线快照与当前分数数据，不需要为对比视图单独新建一套评分存储。
- **依赖**：F-OBS-001（OBS-F007）、F-SUPERVISOR-001（MonitorReview）、CONSOLE-F002（训练反馈生效事件，用于触发前后对比）。
- **Out of Scope（Stage 10前不实现）**：具体评分rubric的权重设计、跨企业策略决策/高管看板这类"大而全"功能——参照Medallia真实差评，第一版只做评分卡+下钻；自定义评分维度的具体UI编辑器交互设计。
- **验收标准**：任意一条评分卡上的分数，管理员必须能一键查到支撑这个分数的原始证据，不允许"黑盒打分"；企业调整过的自定义评分标准必须与Matbox默认标准区分存储，租户间自定义标准互不可见；训练前后对比视图必须明确标注基线快照的生成时间点，不能拿两个不同口径的分数直接比较。

### CONSOLE-F004 · 成本+预算中心（含成本预测）
- **目标**：把F-COST-001已有的账本+预算告警能力（COST-F001~F005）做成租户管理员能自助查看、自助配置预警线的界面；新增成本预测能力——基于历史用量趋势给出"照当前趋势本月/本季度预计花费"的参考值。
- **依赖**：F-COST-001（全部）。
- **Out of Scope（Stage 10前不实现）**：预测模型的具体算法参数（先用简单趋势外推占位，具体模型精度调优需要真实用量数据）。
- **验收标准**：预测结果必须明确标注"参考预测，非承诺值"；预测结果不得触发任何自动阻断业务执行的动作，只能触发提醒（复用F-COST-001已有的软性提醒机制）。

### CONSOLE-F005 · 统一控制台（Control Tower）
- **目标**：把CONSOLE-F001~F004以及F-ORCHESTRATOR-001（路由健康）、F-SUPERVISOR-001（输出治理）、F-TENANT-001（权限/身份）的关键指标聚合到一个页面，按Discover（发现有哪些AI员工/哪些在跑）/Observe（观测运行状态）/Govern（雇佣/训练/审批治理）/Secure（权限/凭据安全态势）/Measure（成本+质量，预留ROI扩展位）五支柱组织。
- **依赖**：CONSOLE-F001~F004、F-ORCHESTRATOR-001、F-SUPERVISOR-001、F-TENANT-001（均已建成或本文档同步建成）。
- **Out of Scope（Stage 10前不实现）**：Measure支柱下的ROI/Value具体算法（调研清单#17，仍为🟡，需要真实业务结果数据）。
- **验收标准**：管理员打开控制台首页，五支柱各自至少有一个可点击下钻的真实数据来源入口，不是静态占位截图。

## 5｜核心数据 Contract（逻辑模型，可直接建表/建接口）

**（不新建模板/成本/质量数据存储）** 模板数据以F-AIEMP-001的EmployeeTemplate/EmployeeInstance为唯一事实源，成本数据以F-COST-001的UsageLedgerEntry为唯一事实源，质量数据以F-OBS-001的QualityDriftCheck/EvidenceBundle为唯一事实源，本模块只做投影查询，不复制。

**TrainingFeedback**（CONSOLE-F002，新增，唯一新增的持久化实体）
feedbackId, tenantId, employeeInstanceId, submittedBy(userId), feedbackType(BEHAVIOR_CORRECTION|POLICY_ADJUST_REQUEST), content, status(PENDING_REVIEW|APPLIED|REJECTED), appliedViaConfigVersionId?（关联AIEMP-F004的配置版本记录）, appliedViaApprovalId?（若触发审批，关联F-APPROVAL-001）, createdAt, resolvedAt?

**BudgetForecast**（CONSOLE-F004，投影计算结果，可缓存不必持久化）
forecastId, tenantId, employeeInstanceId?（为空代表整租户级预测）, method(TRAILING_TREND，占位，Stage 10定具体模型), windowDays, projectedUsage, projectedCost, generatedAt, disclaimerText（固定标注"参考预测，非承诺值"）

**API 端点（最小集合）**
- `GET /console/hiring/templates?query=` — 浏览/搜索EmployeeTemplate（投影自AIEMP-F001）
- `POST /console/hiring/match` — 输入业务需求描述，返回推荐模板列表+可解释依据
- `POST /console/training/feedback` — 提交训练反馈（对应CONSOLE-F002）
- `GET /console/training/feedback?employeeInstanceId=` — 查看某AI员工的反馈历史与生效状态
- `GET /console/qc/scorecard/{employeeInstanceId}` — 质检评分卡（投影自OBS-F007/MonitorReview，含evidenceBundleRef下钻）
- `GET /console/cost/budget/{tenantId}` — 预算自助视图（投影自F-COST-001）
- `GET /console/cost/forecast/{tenantId}` — 成本预测（CONSOLE-F004）
- `GET /console/control-tower/digest/{tenantId}` — 五支柱聚合摘要（CONSOLE-F005）

## 6｜P0 冻结规则（不可降级）

1. TrainingFeedback被静默应用而未经AIEMP-F004配置审计留痕：不可降级 P0。
2. 成本预测结果被用于自动阻断AI员工执行任务（而非软性提醒）：不允许，除非用户本人明确决定并留痕。
3. 质检评分卡展示分数却查不到对应的evidenceBundleRef证据：不允许。

## 7｜当前唯一继续断点

Stage 10（真实实现聚合查询、接入真实前端）尚未开始。下一步：把 CONSOLE-F001~F005 转成 WorkPackage；CONSOLE-F001智能匹配算法、CONSOLE-F003评分rubric、CONSOLE-F004预测模型的具体参数均需要真实使用数据才能精调，现在只完成结构设计。CONSOLE-F005的Measure支柱ROI扩展位待调研清单#17从🟡转正后再实现。

## 附录｜来源

- **依据（2026-08-30）**：[Matbox_AI员工能力缺口调研清单_2026-08-30.md](Matbox_AI员工能力缺口调研清单_2026-08-30.md)#13#14#15#16#17#18（第二轮真实案例验证：Salesforce Agentforce G2真实评价、Medallia G2 4.5分真实评价、ServiceNow AI Control Tower具名客户案例——罗利市政府/霍尼韦尔/Avalara、Gartner首份AI Governance Platform Magic Quadrant的Discover/Observe/Govern/Secure/Measure五支柱框架）
- **雇佣路径/评分标准归属/训练前后对比/顾问介入依据（2026-09-02）**：[Matbox_架构设计原则.md](Matbox_架构设计原则.md)第42条#1/#2/#21/#25（27道产品/商业定义问题确认记录）
