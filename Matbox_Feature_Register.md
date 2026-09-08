# Matbox Feature Register


> 按 RC5 标准定义的"唯一当前事实源"——记录目前已知的所有 Feature 及其状态。持续更新，不批量攒批。
> 状态定义详见 [Matbox_架构设计原则.md](Matbox_架构设计原则.md) 第13条（RC5标准）。

## 状态图例

| 状态 | 含义 |
|---|---|
| ✅ READY_FOR_STAGE10_BINDING | 设计文档已完成，等待绑定真实 Repo 施工（真实 Repo 已就绪：`xyhzai/matbox`） |
| ❌ MISSING | 被其他模块依赖，但目前找不到对应开发文档，需要重新做 |
| 🔵 CONFIRMED | 前端页面，设计中，已同步进本仓库 |
| ⚪ NOT_STARTED | 尚未开始 |

## Platform Core Quality / DevCodeQuality（代码持续质检与安全自检）

来源文档：[Matbox_代码持续质检与安全自检_正式开发文档_V1.1-RC_CURRENT_Stage9内容级重验版_2026-08-19.docx](Matbox_代码持续质检与安全自检_正式开发文档_V1.1-RC_CURRENT_Stage9内容级重验版_2026-08-19.docx)（审核记录见架构原则文档）

| FeatureID | 名称 | 状态 | 依赖 |
|---|---|---|---|
| F-DQ-001 | Dev Quality Run Orchestrator | ✅ READY_FOR_STAGE10_BINDING | F-OBS-001, F-RELEASE-001, **F-APPROVAL-001**（2026-09-04场景模拟发现：BLOCKED_MANUAL状态原文只写"Source Reviewer/Acceptance Owner处理"，全文零处提通知机制，已补上必须调用F-APPROVAL-001创建待办，这是DQ自己核心状态机里的坑，不是新功能才有的问题）；**QUEUE-F008**（2026-09-04用户直接要求解决"审核产能瓶颈"卡点：三个Gate全PASS后新增风险分级判断，命中低风险四条标准可跳过独立Review直接进受控Merge，复用QUEUE-F008 Overlap Zone Registry作为风险信号之一，GateDecision新增riskTier/reviewRoute/auditSampled/auditOutcome字段，详见架构原则第68条） |
| F-DQ-002 | Evidence Normalizer / Finding Mapper | ✅ READY_FOR_STAGE10_BINDING | F-OBS-001 |
| F-DQ-003 | SonarQube Code Quality Adapter | ✅ READY_FOR_STAGE10_BINDING | F-DQ-001/002, F-CRED-001 |
| F-DQ-004 | OpenGrep SAST Adapter + Matbox RulePack | ✅ READY_FOR_STAGE10_BINDING | F-DQ-001/002 |
| F-DQ-005 | Betterleaks Secret Detection Adapter | ✅ READY_FOR_STAGE10_BINDING | F-DQ-001/002, F-CRED-001 |
| F-DQ-006 | Trivy Dependency/Container/IaC/SBOM Adapter | ✅ READY_FOR_STAGE10_BINDING | F-RELEASE-001 |
| F-DQ-007 | Matbox Architecture/Contract/Schema Guard | ✅ READY_FOR_STAGE10_BINDING | RC5 Canonical Registry |
| F-DQ-008 | OPA GatePolicy Evaluator | ✅ READY_FOR_STAGE10_BINDING | F-DQ-001~007（2026-09-04用户直接要求解决"DQ自己判断逻辑没有独立核查"存疑事项：本模块早就定义了PolicyChallengeSet这个Contract但从未接上规则，已补上opa test强制跑通才能合并+新增用例必须经非本次Implementer的人过一遍+复用第15节Technology Watch季度节奏定期重跑防漂移，详见架构原则第69条） |
| F-DQ-009 | Auto Repair / Revalidation Controller | ✅ READY_FOR_STAGE10_BINDING | F-DQ-001~008 |
| F-DQ-010 | Suppression / False Positive / Waiver Governance | ✅ READY_FOR_STAGE10_BINDING | F-OBS-001 |
| F-DQ-011 | SCM / PR / Merge / Release Quality Integration | ✅ READY_FOR_STAGE10_BINDING | F-RELEASE-001 |
| F-DQ-012 | AI Code Review Supplemental Evidence Adapter | 🟡 OPTIONAL（成本/区域可选启用） | Provider Router, F-CRED-001（2026-09-04用户追问"审核AI能不能多布置、专门AI审专门程序"后扩展：从单一AI review拆成2个专门AI并行预审（安全向/架构合规向），只标重点不下结论，仅作用于GateDecision.reviewRoute=INDEPENDENT_REVIEW的WorkPackage，不改变谁需要人工审这道闸门，只让人工这一步更快；成本沿用本模块已有的检索式喂上下文+低成本模型先判的规则，详见架构原则第70条） |
| F-DQ-013 | Dev Quality Ops / Tool Health / Regression Harness | ✅ READY_FOR_STAGE10_BINDING | F-OBS-001（2026-09-04场景模拟发现：本模块"人工审核通过率趋势"指标是缓慢漂移型，不是阈值突变型，直接照抄BLOCKED_MANUAL那次的"调用OBS-F004"会接错检测机制，已改为复用OBS-F007的滚动窗口漂移检测，OBS-F007同步扩展） |

**待补充要求复查结果**（2026-08-29）：
- **SLSA Provenance 构建签名**：已解决，无需改动质检文档本体。核对原文档发现，Codex 原文档在 F-DQ-001 的 Own/Reuse 表里已经把"provenance"列为 REUSE 项、明确指向"F-RELEASE-001"（原文档早已预留这个模块名占位）。现在 F-RELEASE-001 正式文档已建成（REL-F003·SLSA构建溯源签名，目标Level 2，含provenanceRef字段+P0规则），正好填上原文档预留的空位，不需要再改质检文档。
- **AI 员工执行过程安全防护**：**2026-09-05已补齐，不再是挂账项**。此前卡在依赖上——F-DQ-009（自动修复控制器）依赖的"Shared Agent Runtime"当时只有专项28技术选型报告、没有正式设计。Agent Runtime正式开发文档已建立（[Matbox_AgentRuntime_正式开发文档_V1.0-RC.md](Matbox_AgentRuntime_正式开发文档_V1.0-RC.md)），质检文档第16节"安全与隐私边界"已补上第7条，把F-DQ-009驱动的Implementer AI repair job纳入Agent Runtime的P0冻结规则约束（不可信内容处理/心跳监控/委派权限不放大/自我纠错硬上限转人工）。

## 代码问题定位与人工修复台（质检系统之上的只读可视化层，独立文档不合并）

来源文档：[Matbox_代码问题定位与人工修复台_独立专项开发文档_V1.0.docx](代码问题定位与人工修复台/Matbox_代码问题定位与人工修复台_Codex独立开发包_V1.0/Matbox_代码问题定位与人工修复台_独立专项开发文档_V1.0.docx)（用户提供，2026-08-29，审核记录见架构原则文档第22-23条）。F-VIZ-005修复闭环的具体步骤见「流程演示图」[viz_repair_loop_flow.html](viz_repair_loop_flow.html)（架构原则第26条）。**2026-08-30深度排查发现：源文档自己明确写着"文档状态：开发指导版"、"尚未达到Codex Ready或最终验收"，Stage 8真实POC要等Matbox源码仓库和Base Commit才能执行——这是比其余8个模块（都卡在同一个"Stage 10真实施工未开始"）更早一步的阻塞点，之前用"✅ DESIGN_COMPLETE"跟其他已就绪模块同等标注，容易让人误以为VIZ和DQ等模块处于同一就绪程度，下面status改成区分标注。**

**2026-09-05复核（用户要求排查遗留项触发）：上面"等Matbox源码仓库"这条阻塞理由已经不成立，需要更正**——查`git log`确认真实仓库`xyhzai/matbox`最早提交日期是2026-08-29，比这条阻塞说明本身写下的日期（2026-08-30）还早一天，也就是写下这条说明的时候仓库其实已经就绪，"等仓库"这部分从一开始就不该成立。"等Base Commit"这部分仍然成立，但这跟其余8个模块共同卡住的"Stage 10真实施工未开始/BaselineID未生成"是同一件事（见`docs/Matbox_开发总账.md`每个Feature都有的`G-STAGE10-REPO-001`阻塞标记）——**VIZ现在不再比其他模块更早卡一步，不需要跟其他DRAFT_RESEARCH_COMPLETE模块区分标注**，下面status统一即可，不用再单独强调"比其余8个模块更早阻塞"。

| FeatureID | 名称 | 状态 | 依赖 |
|---|---|---|---|
| F-VIZ-001 | View Contract | 🟡 DESIGN_COMPLETE_POC_PENDING | 字段/状态/置信度/降级规则冻结 |
| F-VIZ-002 | Projection API | 🟡 DESIGN_COMPLETE_POC_PENDING | 只读投影，复用F-DQ-002/F-OBS-001/F-TENANT-001权限与证据 |
| F-VIZ-003 | Finding UI | 🟡 DESIGN_COMPLETE_POC_PENDING | 问题总览、代码定位、证据抽屉 |
| F-VIZ-004 | Relation UI | 🟡 DESIGN_COMPLETE_POC_PENDING | 直接/传递/未知影响关系图 |
| F-VIZ-005 | Repair UX | 🟡 DESIGN_COMPLETE_POC_PENDING | 隔离修复、审批、补丁预览、复检；依赖F-DQ-009，提交新commit创建QualityRun这一步复用F-DQ-001（见[VIZ修复闭环流程演示图](viz_repair_loop_flow.html)） |
| F-VIZ-006 | Realtime | 🟡 DESIGN_COMPLETE_POC_PENDING | 事件订阅，复用F-QUEUE-001，不新建第二套队列 |
| F-VIZ-007 | Security/QA | 🟡 DESIGN_COMPLETE_POC_PENDING | 权限脱敏审计，依赖F-TENANT-001 |

**审核追加要求**（2026-08-29，见架构原则第22-23条）：代码解析明确为"Tree-sitter主力+SCIP兜底"混合方案；AI解释/修复调用必须把源代码内容当不可信数据处理，且该AI调用本身不具备工具执行能力。**已写回正式文档本体**（2026-08-29，直接编辑docx第9节"技术实现建议"，经XSD schema校验通过）。

## 地基模块（被大量依赖）

| FeatureID | 名称 | 状态 | 说明 |
|---|---|---|---|
| F-OBS-001 | Evidence / Audit / Trace 共享事实系统 | 🟢 DRAFT_RESEARCH_COMPLETE | 正式开发文档已完成：[Matbox_证据审计与监控_正式开发文档_V1.0-RC.md](Matbox_证据审计与监控_正式开发文档_V1.0-RC.md)（OpenTelemetry采集 + SigNoz看板 + immudb防篡改，拆出 OBS-F001~F006）。被 F-DQ-001/002/010/013、CRED-F006 依赖。**流程图检查结论（架构原则第26条验收标准）：无真实顺序流程，保持摘要卡片**。**2026-08-30新增OBS-F006 AI Evaluation（评测框架）**：从《多端平台V3.0》并入，推翻了架构原则第6/28条"评测框架现在不启动设计"的原判断，评测框架现在跟着OBS一起设计（详见架构原则第31条），架构依赖图的独立占位模块已标记已并入。**2026-08-30核对AI员工底层包（架构原则第33条）**：quality_result/audit_event表已并入EvidenceBundle的type扩展，无需新建平行证据系统；底层包威胁模型文档(10类威胁)是Matbox目前缺的一处集中清单，已记录待整理。**2026-08-30新增OBS-F007(生产环境持续质量漂移监测)+OBS-F008(证据日志分层存储)**（调研清单#5#11）。**2026-09-04场景模拟REL-F007发现并补上**：OBS-F004新增职责，负责评估REL-F007灰度发布的RolloutThreshold阈值并在突破时调用REL-F007的自动回滚接口——此前REL-F007"自动回滚"里"自动"这部分没有指定执行者。同一轮又发现并接上TASK-F006（AI任务运行时"中途漂移检测"）的告警职责，原描述"触发人工Takeover"没写怎么通知到人 |
| F-RELEASE-001 | ReleaseArtifact / Baseline / SBOM 系统 | 🟢 DRAFT_RESEARCH_COMPLETE | 正式开发文档已完成：[Matbox_发布与基线系统_正式开发文档_V1.0-RC.md](Matbox_发布与基线系统_正式开发文档_V1.0-RC.md)（Harbor仓库 + 复用F-DQ-006的SBOM + SLSA签名，拆出 REL-F001~F006）。被 F-DQ-001/006/011 依赖。**流程图检查结论（架构原则第26条验收标准）：✅有真实顺序流程**（"Merge Commit→依赖快照→构建记录→产物摘要→ReleaseArtifactID→部署记录"追溯链条），**专属流程演示图已制作**：[release_traceability_flow.html](release_traceability_flow.html)，原样嵌入架构依赖图弹窗。**2026-08-30新增REL-F006数据库迁移追溯（Flyway）**：从《多端平台V3.0》并入。**2026-09-04新增REL-F007灰度发布+自动回滚**：核对"运行中"设计时发现的真实缺口——此前只有`DeployRecord.rollbackOf`这个事后人工回滚指针，没有灰度放量+指标自动触发机制，同一次自查还发现并补上了F-QUEUE-001的QUEUE-F010(架构原则第58/59/61/62条)。**2026-09-04场景模拟REL-F007发现真实断点**：原设计没写谁来实时评估RolloutThreshold阈值，"自动回滚"的"自动"是空的——已接上F-OBS-001的OBS-F004；同时补上AUTO_THRESHOLD触发的回滚必须回填为DQ回归测试用例，不能因为发生在生产环境就不算"逃逸" |
| F-COST-001 | 成本控制系统 | 🟢 DRAFT_RESEARCH_COMPLETE | 正式开发文档已完成：[Matbox_成本控制_正式开发文档_V1.0-RC.md](Matbox_成本控制_正式开发文档_V1.0-RC.md)（**2026-09-02更正**：Langfuse此前记录的"REUSE"结论已推翻，改为Matbox自研聚合层消费F-OBS-001/F-PROVIDER-001数据，Langfuse降级为可选调试工具，详见专项21e，独立于Provider Router，拆出 COST-F001~F005）。被 F-DQ-012、Provider Router 依赖。**流程图检查结论（架构原则第26条验收标准）：✅有真实顺序流程**（2.3节"预算告警模式"：设预算→80%提醒→100%再提醒通知负责人→软性提醒不硬阻断），**专属流程演示图已制作**：[budget_alert_flow.html](budget_alert_flow.html)，原样嵌入架构依赖图弹窗。**成本归因做法已确认并含一处自我纠正（架构原则第28条，2026-08-29）**：不是靠Langfuse"Environment"功能（该说法不准确，已更正），是在AI员工每次调用的源头span/trace打上租户标签，跟着调用记录一起存；明确禁止靠月底账单事后反推。**2026-08-30新增COST-F005企业套餐用量账本/预算/权益**：从《多端平台V3.0》并入，reserve→execute→commit/release模式。**2026-08-30核对AI员工底层包（架构原则第33条）**：cost_ledger的append-only+归因要求与本模块原则一致，UsageLedgerEntry补齐9个成本维度(含此前遗漏的retry_waste)，无冲突。**2026-09-02新增`hardCapEnabled`硬性预算暂停开关**（架构原则第39条，参照Google Gemini Enterprise 2026-08真实功能）+**回填架构原则第42条#5/#6计费模式**：混合模式（订阅额度+超额近成本价透传），Entitlement新增`overagePricingVersion`/`overageBillingMode`字段 |
| F-TENANT-001 | 租户与权限体系（Tenant/RBAC） | 🟢 DRAFT_RESEARCH_COMPLETE | 正式开发文档已完成：[Matbox_租户与权限体系_正式开发文档_V1.0-RC.md](Matbox_租户与权限体系_正式开发文档_V1.0-RC.md)（复用OPA + 简单RBAC + 数据隔离，拆出 TENANT-F001~F005）。P0安全红线。**流程图检查结论（架构原则第26条验收标准）：✅有真实顺序流程，与F-CRED-001共享同一条**（2.4节"AI 员工授权模式"鉴权/收回端 + CRED-F003签发端，是同一条"AI员工临时授权生命周期"的两端），**专属流程演示图已制作**：[cred_tenant_auth_lifecycle_flow.html](cred_tenant_auth_lifecycle_flow.html)，原样嵌入架构依赖图弹窗（cred/tenant两个节点共享同一张图）。**2026-08-30与《多端平台V3.0》F-PLAT-001分工确认**：F-TENANT-001管AI员工鉴权(OPA)+数据隔离，F-PLAT-001管人类登录/会话安全(MFA/SSO/设备)——查证2026年AuthN/AuthZ分离最佳实践后确认两个都保留、不合并（详见架构原则第31条）。**2026-08-30核对AI员工底层包（架构原则第33条）**：人类角色定义补强为7个具名角色(TenantOwner/TenantAdmin/EmployeeOwner/Operator/Reviewer/Viewer/PlatformAdmin)，新增ABAC属性集合和4条强制DENY规则。**2026-08-30新增TENANT-F006匿名访客身份**（调研清单#9，仅身份/权限层）：新增AnonymousVisitor principalType，会话级+默认零信任+只读allowlist，参照Auth0 2026年Anonymous Sessions模式；独立站具体页面/渠道设计明确不在本次范围（等用户"独立站"业务包） |
| F-QUEUE-001 | 任务队列 | 🟢 DRAFT_RESEARCH_COMPLETE | 正式开发文档已完成：[Matbox_任务队列_正式开发文档_V1.0-RC.md](Matbox_任务队列_正式开发文档_V1.0-RC.md)（**2026-08-30引擎从Hatchet改为Temporal**——Hatchet无官方Java SDK跟多端平台文档定的Java/RuoYi技术栈不契合，且跟F-TASK-001共用同一套Temporal，拆出 QUEUE-F001~F004；**2026-09-04新增QUEUE-F005~F010**——自认领机制/Worktree隔离派工/运行时资源队列/高风险公共文件强制转人工/派发附带架构决定摘要/施工期间实时动作拦截，源自架构原则第58/59/61/62条查证，原计划另立"调度器"模块，核查后发现与本模块重叠，改为并入本模块而非新建；QUEUE-F010是核对"开发中是否做完"时发现的真实空白——此前误以为DQ的Gate已覆盖实时拦截，核查后确认没有；**2026-09-04实际场景模拟QUEUE-F010那条链后补了4处接口断点**：转人工改为真正调用F-APPROVAL-001创建审批记录；FILE_WRITE命中QUEUE-F008高风险清单时提前打`willRequireManualReview`标记而非等合并前才发现；QueueRun状态字段此前误借用F-TASK-001状态，已改为专属`AWAITING_APPROVAL`；补齐审批被拒绝/超时/撤回三条此前没写的路径该转到哪。**换场景模拟QUEUE-F007运行时资源锁又发现1处更严重的断点**：原设计的锁没有租约/过期时间，持有方一旦崩溃锁会被永久占住导致真实死锁，已补`leaseExpiresAt`租约机制+`AWAITING_RESOURCE`专属状态）。**流程图检查结论（架构原则第26条验收标准）：✅有真实顺序流程**（QUEUE-F004"失败恢复与重试策略"：中断→从断点恢复→按RepairPolicy重试→超限转NEEDS_MANUAL_INTERVENTION；此前误判为无流程，2026-08-29重新通读后纠正），**专属流程演示图已制作**：[queue_retry_escalation_flow.html](queue_retry_escalation_flow.html)，原样嵌入架构依赖图弹窗 |
| F-STORAGE-001 | 对象存储 | 🟢 DRAFT_RESEARCH_COMPLETE | 正式开发文档已完成：[Matbox_对象存储_正式开发文档_V1.0-RC.md](Matbox_对象存储_正式开发文档_V1.0-RC.md)（SeaweedFS，拆出 STORAGE-F001~F006）。**2026-08-30新增STORAGE-F004~F006**：签名上传下载/病毒扫描隔离/资产生命周期状态机，从《多端平台V3.0》F-ASSET-001并入，不单独立项。**流程图检查结论（2026-09-02重新核实修正）：STORAGE-F006是真实状态机（UPLOADING→QUARANTINED→SCANNING→READY/REJECTED→DELETED_SOFT→PURGED），此前"无真实顺序流程"的判断过期，✅已补建专属流程演示图**：[storage_asset_lifecycle_flow.html](storage_asset_lifecycle_flow.html)，已嵌入架构依赖图弹窗。**⚠ 2026-09-02二次核查发现并修正真实缺口**：制作流程图时发现验收标准承诺"软删除后可恢复"，但状态机只画单向箭头到PURGED、API也没有restore端点——已修正为DELETED_SOFT保留期内可恢复回READY，补齐`deletedAt`/`purgeScheduledAt`字段+`POST .../restore`端点 |
| F-PROVIDER-001 | Provider Router / 模型接入层 | 🟢 DRAFT_RESEARCH_COMPLETE | **2026-08-30新建正式开发文档**：[Matbox_Provider_Router_正式开发文档_V1.0-RC.md](Matbox_Provider_Router_正式开发文档_V1.0-RC.md)——原架构底层⚪NOT_STARTED占位模块，核对《多端平台V3.0》F-PROVIDER-001章节后确认就是本模块的正式设计，拆出PROVIDER-F001~F005，按租户限流方案（架构原则第28条）正式写入PROVIDER-F004（详见架构原则第31条）。**2026-08-30核对AI员工底层包（架构原则第33条）**：边界确认为"只处理AI模型调用"（对应底层包Model Gateway/WP-006），新增PROVIDER-F006 Provider Adapter标准接口。**2026-08-30细化PROVIDER-F002 PIPL跨境传输触发点**（调研清单#6）：MCP/API调用海外LLM可能构成PIPL跨境传输，ModelInvocation新增piplCrossBorderTriggered字段留痕。**流程图检查结论（2026-09-02重新核实修正）：PROVIDER-F003健康检查/熔断/故障转移此前从未配流程图，✅已补建**：[provider_failover_flow.html](provider_failover_flow.html)，已嵌入架构依赖图弹窗 |
| F-CRED-001 | Secret / Credential 管理系统 | 🟢 DRAFT_RESEARCH_COMPLETE | 正式开发文档已完成：[Matbox_密钥管理_正式开发文档_V1.0-RC.md](Matbox_密钥管理_正式开发文档_V1.0-RC.md)（工具选型 Infisical，拆出 CRED-F001~F007）。Stage 10 真实施工未开始，解开 F-DQ-003/005/012 的依赖。**流程图检查结论（架构原则第26条验收标准）：✅有真实顺序流程，与F-TENANT-001共享同一条**（CRED-F003签发端 + TENANT 2.4节鉴权/收回端），**专属流程演示图已制作**：[cred_tenant_auth_lifecycle_flow.html](cred_tenant_auth_lifecycle_flow.html)，原样嵌入架构依赖图弹窗（cred/tenant两个节点共享同一张图）。**2026-08-30新增CRED-F007企业第三方集成凭证**：从《多端平台V3.0》并入，跟原CRED-F001~F006（AI员工临时Token）是两类不同的密钥使用场景。**2026-08-30新增CRED-F008 AgentIdentity持久身份层（架构原则第33条）**：从AI员工底层包并入，明确"员工级持久身份"（CRED-F008）与"任务级临时Grant"（CRED-F003）是两层不同粒度，不合并。**2026-08-30新增CRED-F009匿名访客会话身份**（调研清单#9）：与F-TENANT-001 TENANT-F006配套，AnonymousVisitorSession可升级关联正式Contact身份 |
| F-SUPERVISOR-001 | 输出监督层 / Supervisor+Monitor | 🟢 DRAFT_RESEARCH_COMPLETE | **2026-08-30新建正式开发文档**：[Matbox_输出监督层_正式开发文档_V1.0-RC.md](Matbox_输出监督层_正式开发文档_V1.0-RC.md)——"AI员工能力缺口调研清单"#3，补齐"AI员工说的话本身"完全没有治理的安全空白，是#9(独立站匿名访客场景)能否上生产的前提。Sierra双层架构参照(Supervisor实时+Monitor异步)，拆出SUPERVISOR-F001~F004，Supervisor子层现在设计完整，Monitor子层判断阈值留到Stage 10真实数据精调。依赖F-AIEMP-001/F-OBS-001/F-EGRESS-001（均已建成）。**2026-08-30新增SUPERVISOR-F005 AI身份披露检查**（调研清单#25，用户确认欧盟是目标市场后执行）：EU AI Act Article 50透明度义务2026-08-02已生效未被Digital Omnibus推迟，与Annex III高风险系统完整合规义务（已推迟至2027-12-02，且留待法务正式分类）是两件不同的事，更正了#25原"截止日已过"的判断 |
| F-ORCHESTRATOR-001 | 中央编排层("大脑") | 🟢 DRAFT_RESEARCH_COMPLETE | **2026-08-30新建正式开发文档**：[Matbox_中央编排层_正式开发文档_V1.0-RC.md](Matbox_中央编排层_正式开发文档_V1.0-RC.md)——"AI员工能力缺口调研清单"#1定性为P0前提("没有它其他都是空谈")，用户论证确认后执行。Registry(接F-AIEMP-001)+Classifier(混合路由)+Coordinator(接F-DELEGATION-001)三组件，拆出ORCHESTRATOR-F001~F005，显式防住5类真实生产失败模式(单点故障/吞吐瓶颈/成本失控/上下文溢出/8条根因清单) |
| F-TASK-001 | AI 任务运行时 / Durable AI Task Runtime | 🟢 DRAFT_RESEARCH_COMPLETE | **2026-08-30新建正式开发文档**：[Matbox_AI任务运行时_正式开发文档_V1.0-RC.md](Matbox_AI任务运行时_正式开发文档_V1.0-RC.md)——核查《多端平台V3.0》F-TASK-001章节后确认，此前与F-QUEUE-001的Temporal/Hatchet引擎冲突已解决（共用同一套Temporal实例，业务逻辑分开），拆出TASK-F001~F004（详见架构原则第31条）。**2026-08-30核对AI员工底层包（架构原则第33条）**：状态机升级为CREATED→VALIDATED→QUEUED→RUNNING→WAITING_APPROVAL/WAITING_DEPENDENCY→SUCCEEDED/FAILED/CANCELLED，新增TASK-F005 Kill/Checkpoint/Resume（解决架构原则第28条Kill Switch挂账项），确认不引入NATS JetStream，任务分发全部用Temporal原生能力。**2026-08-30新增TASK-F006(中途漂移检测)+TASK-F007(Continue-As-New，Temporal官方推荐做法防Event History溢出)**（调研清单#4#8）。**2026-08-30新增TASK-F008任务内自我纠错（Reflexion式）**（调研清单#12，仅单次任务内部分）：生成→自我批判→修正闭环，硬上限复用DELEGATION-F005同一原则；跨任务长期进化不在本条范围。**流程图检查结论（2026-09-02重新核实修正，架构原则第26条原判断"无真实顺序流程"已过期）：TASK-F008生成→自我批判→修正是真实Reflexion式闭环，✅已补建专属流程演示图**：[task_self_correction_flow.html](task_self_correction_flow.html)，已嵌入架构依赖图弹窗。**2026-09-04场景模拟TASK-F006发现真实断点**：原描述"触发人工Takeover"没写怎么真正通知到人，已接上F-OBS-001的OBS-F004告警机制（"行为偏离历史基准"本来就是它管的场景），不新建通知逻辑 |
| **F-LOC-001** | 全球多语言与本地化 / Global Localization | 🟢 DRAFT_RESEARCH_COMPLETE | **2026-09-08新建正式开发文档**：[Matbox_全球多语言与本地化_正式开发文档_V1.0-RC.md](Matbox_全球多语言与本地化_正式开发文档_V1.0-RC.md)。**定位：基础层公共能力，不是AI员工下属模块**——被平台/独立站/小程序/App/iPad/AI员工/在线聊天共同消费。来源：用户侧交接包 `语言包.zip`（Stage 9 PASS，DEV.docx 2,028段 + 4个JSON + 可运行POC），拆出 **LOC-F001~F020** + AC-LOC-001~040。**本会话独立核验**：MANIFEST SHA-256 8/8一致；**实跑 poc.py 确认 12/12 PASS**；三个锁定commit经GitHub API核实全部真实且与版本精确对应。**选型已调整（升至上游latest）**：vue-i18n 9.1.9(2021-10发布，官方已EOL)→**11.4.10**；next-intl 4.13.7→**4.14.2**；Tolgee 3.218.3→**v3.221.0**。废止包中「禁止升v11」规则——核查 `@dcloudio/uni-app` 各dist-tag依赖树，**uni-app根本不依赖vue-i18n**（自带`@dcloudio/uni-i18n`），其「锁定DCloud版本线」的事实前提不成立；且Matbox本地化尚无存量代码，v11破坏性改动成本为零。**新增5个Matbox侧Gate**：G-LOC-MATBOX-001（Product Master Owner缺失阻塞LOC-F008/F009的product类目）、**-002（Messaging Owner在本Register中不存在，阻塞P0的LOC-F020）**、-003（交接包未记录任何被淘汰候选，违反开发包标准第9条，须补TMS/Web i18n/翻译Provider三组对比）、-004（12/12里有2条是同义反复，零依赖空环境下仍PASS，AC-LOC-008/009不得计入已验证）、-005（`canonicalize()`把en-IN抹成en，language与locale归一必须拆两个函数）。**与专项00r交叉印证**：C-LOC-013/015/011 三条已关闭冲突与九家横向收口的收敛⑧①③独立撞上，同向加强。**流程图检查结论：待检查**（含Translation状态机 pending→translated→review_required→reviewed→released + outdated 分支，属真实顺序流程，收口后评估是否单独出图） |

## AI 员工执行体系（源自《Matbox_多端平台_CURRENT_正式开发文档_V3.0》，2026-08-30正式加入）

来源文档：《Matbox_多端平台_CURRENT_正式开发文档_V3.0》（审核记录见架构原则第31-32条）。用户此前提出的"10个干净模块"整理计划已完成前置核查（F-TASK-001独立文档、F-ASSET-001悬空引用核查、F-ACTION-001调用链），本轮正式建立以下5个模块的开发文档。

| FeatureID | 名称 | 状态 | 依赖 |
|---|---|---|---|
| F-EGRESS-001 | 出站请求安全 / SSRF Policy | 🟢 DRAFT_RESEARCH_COMPLETE | 正式开发文档：[Matbox_出站请求安全_正式开发文档_V1.0-RC.md](Matbox_出站请求安全_正式开发文档_V1.0-RC.md)（无阻塞，可独立先行），拆出 EGRESS-F001~F003。被F-ACTION-001依赖。**流程图检查结论（架构原则第26条）：已检查，无真实顺序流程，摘要卡片** |
| F-AIEMP-001 | AI 员工身份 | 🟢 DRAFT_RESEARCH_COMPLETE | 正式开发文档：[Matbox_AI员工身份_正式开发文档_V1.0-RC.md](Matbox_AI员工身份_正式开发文档_V1.0-RC.md)（纯业务schema，复用Provider Router/F-COST-001），拆出 AIEMP-F001~F004。依赖F-CRED-001/F-COST-001/F-OBS-001（均已建成）。**2026-08-30核对AI员工底层包大幅补强（架构原则第33条）**：采纳EmployeeTemplate/EmployeeInstance/AgentIdentity三层分离模型（取代原单表设计），拆出AIEMP-F001~F005，新增岗位生命周期(Draft→Validated→Active→Paused/Suspended→Retired)、初始岗位族、岗位最小验收集。**2026-08-30新增P0规则7**：KPI优化/AB实验不得覆盖或绕过policy/审批检查（源自OpenAI自己Agent群体攻破Hugging Face生产系统的真实事故，见调研清单#7），被F-ORCHESTRATOR-001的Registry引用。**2026-09-02回填架构原则第42条#3/#4/#18/#11**：EmployeeTemplate新增`visibilityScope`（TENANT_PRIVATE\|PLATFORM_PUBLIC）归属字段+`contributedFromTenantId`溯源，明确同租户多AI员工可复用同一SOP/PolicyBundle；AIEMP-F005补充辞退流程对租户管理员完整可见。**流程图检查结论（2026-09-02重新核实修正，此前"无真实顺序流程"的判断已过期）：AIEMP-F005生命周期与Kill Switch（Draft→Validated→Active→Paused/Suspended/Revoked/Retired）是真实流程，✅已补建专属流程演示图**：[aiemp_lifecycle_killswitch_flow.html](aiemp_lifecycle_killswitch_flow.html)，已嵌入架构依赖图弹窗。**⚠ 2026-09-02二次核查发现并修正真实缺口**：Retire的定义此前未提Grant撤销，与验收标准"辞退时间线须显示Grant失效时间点"自相矛盾——已修正为Retire必须原子性级联触发Revoke，新增P0规则6.1，补齐`revokedAt`/`retiredAt`等缺失字段，补齐`:suspend`/`:revoke`两个此前遗漏的API端点。**2026-09-04深度调研ServiceNow/Salesforce/UiPath三家真实做法后新增AIEMP-F006 Subagent分工层**：原有Skill实体只是"能力清单"，不是"独立推理子单元"，参照ServiceNow T2 SOC/Salesforce Sales Account Management真实拆法，在EmployeeTemplate与Skill之间插入Subagent层（各自model_policy/evaluation_profile，经AgentBinding显式绑定），详见架构原则第72条 |
| F-ACTION-001 | Action 网关 | 🟢 DRAFT_RESEARCH_COMPLETE | 正式开发文档：[Matbox_Action网关_正式开发文档_V1.0-RC.md](Matbox_Action网关_正式开发文档_V1.0-RC.md)（Tool/MCP Adapter层基于MCP Gateway生态），拆出 ACTION-F001~F004。调用链见架构原则第32条：F-ACTION-001→F-CRED-001+F-EGRESS-001+F-PROVIDER-001。**流程图检查结论：✅有真实顺序流程**（propose→风险预览确认→commit时重新鉴权→执行→幂等审计，5环节），**专属流程演示图已制作**：[action_gateway_flow.html](action_gateway_flow.html)，已嵌入架构依赖图弹窗。**2026-08-30结构性修正（架构原则第33条）**：核对AI员工底层包后确认应拆成Model Gateway(F-PROVIDER-001)+Tool Gateway(本模块)两个平级网关，本模块收窄为只处理工具/动作调用，采纳底层包10步enforcement顺序，新增ACTION-F005。**2026-09-04深度调研ServiceNow/Salesforce/UiPath三家真实做法后新增ACTION-F006 Workflow Registry**：原有ACTION-F001~F005管的都是单个动作，没有"预先把几步串成一条测试过的确定性流程、AI一次调用整条流程"这一层，参照UiPath Maestro真实做法采用BPMN定顺序+DMN定决策规则（公开国际标准，非私有格式），Workflow内部每步仍完整走10步Enforcement Pipeline不降级，详见架构原则第72条。**2026-09-05用户指出底层架构没考虑Connector生态，深度复核Salesforce(MuleSoft)/ServiceNow(Spoke)/UiPath(Marketplace)三家真实商业与技术架构后新增ACTION-F007 Connector Registry**：ACTION-F002的ToolRegistration只到单个工具粒度，缺一层按业务平台分组的具名Connector目录（微信/抖音/小红书/Shopify/酷家乐等），三家的Gateway+凭证别名层Matbox已经有（F-ACTION-001+F-CRED-001），新增的只是目录分组层，架在ACTION-F002之上非平行系统，详见架构原则第73条。**流程图检查结论**：已检查，ACTION-F007本身是目录/分组概念（注册Connector→挂工具→共享凭证→禁用联动），不是真实顺序流程，摘要卡片即可，不需要单独制作流程演示图 |
| F-APPROVAL-001 | AI 动作审批 + Transactional Outbox | 🟢 DRAFT_RESEARCH_COMPLETE | 正式开发文档：[Matbox_AI动作审批_正式开发文档_V1.0-RC.md](Matbox_AI动作审批_正式开发文档_V1.0-RC.md)（复用RuoYi Flowable BPM+Temporal signal），拆出 APPROVAL-F001~F004。依赖F-ACTION-001、F-QUEUE-001/F-TASK-001的Temporal基础设施。**流程图检查结论：✅有真实顺序流程**（Transactional Outbox模式：同事务写state+outbox→commit→dispatcher消费→Temporal signal→workflow恢复，5环节），**专属流程演示图已制作**：[approval_outbox_flow.html](approval_outbox_flow.html)，已嵌入架构依赖图弹窗。**2026-08-30核对AI员工底层包（架构原则第33条）**：确认底层包未指定具体BPM引擎，RuoYi Flowable是我们补齐的实现细节非冲突；补充requestedPayloadHash/decisionReason/expiresAt字段。**2026-09-02回填架构原则第42条#10**：新增1.1节风险等级对应审批人规则表，`riskLevel`4-5强制真人审批列为不可降级P0（欧盟AI法案第14条硬性要求），AiApproval新增`riskLevel`/`decidedByType`字段。**2026-09-04场景模拟发现并补上的接口断点**：QUEUE-F010（Implementer AI施工期间实时拦截）此前"转人工"只改状态字段没真正调用本模块，现已打通——AiApproval新增`actionSourceType`区分来源（ACTION_GATEWAY/IMPLEMENTER_INTERCEPT），补了此前遗漏的`POST /approval`创建端点，两类高风险动作共用同一套审批流程，不新建第二套 |
| F-NOTIFY-001 | 通知中心 / Channel Matrix | 🟢 DRAFT_RESEARCH_COMPLETE | 正式开发文档：[Matbox_通知中心_正式开发文档_V1.0-RC.md](Matbox_通知中心_正式开发文档_V1.0-RC.md)（Novu核心+自建微信Adapter，Novu无原生微信支持），拆出 NOTIFY-F001~F004。依赖F-PLAT-001、F-OBS-001（已建成）。**流程图检查结论：已检查，无真实顺序流程，摘要卡片**。**2026-08-30确认与AI员工底层包Webhook Contract不冲突（架构原则第33条）**：Webhook管系统集成事件分发（B2B），本模块管终端用户通知，两个不同层，不合并 |
| F-DELEGATION-001 | AI 员工委派 / Delegation Service | 🟢 DRAFT_RESEARCH_COMPLETE | **2026-08-30新建正式开发文档**：[Matbox_AI员工委派_正式开发文档_V1.0-RC.md](Matbox_AI员工委派_正式开发文档_V1.0-RC.md)——从AI员工底层包核对后确认的全新模块，之前任何文档都没有对应设计，拆出DELEGATION-F001~F004。内部自建Delegation Contract为真相，预留A2A协议（2026年Linux Foundation治理的Agent互操作事实标准）适配接口但不现在绑定。依赖F-AIEMP-001/F-CRED-001/F-TASK-001（均已建成）（详见架构原则第33条）。**2026-08-30新增DELEGATION-F005失败模式防护（调研清单#2）**：委派深度硬上限+数学可判定循环检测+上游产出可信度标记，防重试风暴/循环委派/幻觉级联，源自2025年7月真实生产事故（84.7万次API调用死循环，6.3万美元账单） |
| （跨模块契约，无FeatureID） | 错误码规范 / Error Code Specification | 🟢 DRAFT_RESEARCH_COMPLETE | **2026-08-30新建正式开发文档**：[Matbox_错误码规范_正式开发文档_V1.0-RC.md](Matbox_错误码规范_正式开发文档_V1.0-RC.md)——从AI员工底层包直接采纳17个错误码，不是某个FeatureID的功能模块，是所有模块共同遵守的跨模块契约（类比evidenceBundleRef字段统一），此前Matbox没有任何文档统一定义过错误码，是真实缺口（详见架构原则第33条）。**2026-09-02补充技术选型审查（[专项20](技术选型报告/Matbox_专项20_错误码规范_技术选型与开发交接报告_2026-09-02.md)）**：对比RFC 9457/Google API错误模型/Stripe/GitHub/Twilio真实错误响应格式后确认，结论REFERENCE——现有短枚举命名风格已与行业实践一致，不需整体照搬RFC；`message`拆分为`title`/`detail`两字段，`details`补充参照Google `FieldViolation`的最小结构化schema。**关键新发现**：Matbox后端底座（yudao-cloud）默认"HTTP永远200、错误码放响应体"与本规范"真实HTTP状态码"设计冲突，已裁决覆盖框架默认行为，Stage 10前需在GlobalExceptionHandler层面显式处理 |
| F-CONSOLE-001 | AI员工管理控制台（Hiring/Training/QC/Cost/Control Tower） | 🟢 DRAFT_RESEARCH_COMPLETE | **2026-08-30新建正式开发文档**：[Matbox_AI员工管理控制台_正式开发文档_V1.0-RC.md](Matbox_AI员工管理控制台_正式开发文档_V1.0-RC.md)——"AI员工能力缺口调研清单"#13/#14/#15/#16/#18定性为🟠(现在就该做)后的正式设计，面向租户管理员的产品体验层，绝大部分是F-AIEMP-001/F-COST-001/F-OBS-001/F-SUPERVISOR-001/F-ORCHESTRATOR-001已有能力的自助聚合投影，不复制存储，拆出CONSOLE-F001~F005。Control Tower按Gartner AI Governance Platform MQ的Discover/Observe/Govern/Secure/Measure五支柱组织，Measure下预留#17(ROI追踪，仍🟡)扩展位。依赖F-AIEMP-001/F-COST-001/F-OBS-001/F-SUPERVISOR-001/F-ORCHESTRATOR-001/F-APPROVAL-001（均已建成）。**2026-09-01五个子中心已完成独立技术选型审查（[专项21a](技术选型报告/Matbox_专项21a_AI员工训练中心_技术选型与开发交接报告_2026-09-01.md)训练中心/[21b](技术选型报告/Matbox_专项21b_企业业务流配置AI员工_技术选型与开发交接报告_2026-09-01.md)业务流配置/[21c](技术选型报告/Matbox_专项21c_雇佣中心_技术选型与开发交接报告_2026-09-01.md)雇佣中心/[21d](技术选型报告/Matbox_专项21d_质检评分中心_技术选型与开发交接报告_2026-09-01.md)质检评分中心/[21e](技术选型报告/Matbox_专项21e_成本预算中心与控制台_技术选型与开发交接报告_2026-09-01.md)成本预算中心）**，明确CONSOLE-F001与ORCHESTRATOR-F002的边界（雇佣期模板匹配 vs 运行期路由，需独立TemplateMatcher组件不得直接调用`/orchestrator/route`）。**2026-09-02回填架构原则第42条#1/#2/#21/#25**：CONSOLE-F001新增"模板雇佣+从零自建"两条路径；CONSOLE-F003补充默认评分标准+企业可调整机制、训练前后对比视图；CONSOLE-F002补充简单场景自助+复杂场景付费顾问介入两档 |

## 多端渲染与内容分发体系（源自《Matbox_多端平台_CURRENT_正式开发文档_V3.0》，2026-08-30正式加入）

来源文档：同上。

| FeatureID | 名称 | 状态 | 依赖 |
|---|---|---|---|
| F-PAGE-001 | 页面内容 Schema | 🟢 DRAFT_RESEARCH_COMPLETE | 正式开发文档：[Matbox_页面内容Schema_正式开发文档_V1.0-RC.md](Matbox_页面内容Schema_正式开发文档_V1.0-RC.md)（纯业务schema，框架无关），拆出 PAGE-F001~F004。依赖F-STORAGE-001（已建成）、F-MULTIEND-001。**流程图检查结论：已检查，无真实顺序流程（Draft/Published是状态转换非因果流程，与F-STORAGE-001资产生命周期同等判断），摘要卡片** |
| F-MOBILE-001 | 移动端 Shell / Auth / Progress / Offline Sync | 🟢 DRAFT_RESEARCH_COMPLETE | 正式开发文档：[Matbox_移动端Shell_正式开发文档_V1.0-RC.md](Matbox_移动端Shell_正式开发文档_V1.0-RC.md)（复用已验证的yudao-ui-admin-uniapp），拆出 MOBILE-F001~F004。**流程图检查结论：已检查，无真实顺序流程，摘要卡片** |
| F-MULTIEND-001 | 多端渲染 + Client Capability Registry | 🟢 DRAFT_RESEARCH_COMPLETE | 正式开发文档：[Matbox_多端渲染与能力注册_正式开发文档_V1.0-RC.md](Matbox_多端渲染与能力注册_正式开发文档_V1.0-RC.md)（Next.js Web端SSR/SEO + uni-app移动端），拆出 MULTIEND-F001~F004。依赖F-PAGE-001。**流程图检查结论：已检查，PublishGuard只是单条if-then规则（2环节），不够格算流程，摘要卡片** |
| F-HANDOFF-001 | PC → 手机交接 | 🟢 DRAFT_RESEARCH_COMPLETE | 正式开发文档：[Matbox_PC转手机交接_正式开发文档_V1.0-RC.md](Matbox_PC转手机交接_正式开发文档_V1.0-RC.md)（一次性opaque code，纯安全模式设计），拆出 HANDOFF-F001~F004。依赖F-MOBILE-001。**流程图检查结论：✅有真实顺序流程**（创建交接码→扫码claim→重新鉴权→跳转资源→presence更新→过期撤销，5环节），**专属流程演示图已制作**：[handoff_claim_flow.html](handoff_claim_flow.html)，已嵌入架构依赖图弹窗 |
| F-CHANNEL-001 | 租户渠道实例 / Brand / Theme / Template / Domain / App Identity | 🟢 DRAFT_RESEARCH_COMPLETE | 正式开发文档：[Matbox_租户渠道实例_正式开发文档_V1.0-RC.md](Matbox_租户渠道实例_正式开发文档_V1.0-RC.md)（复用F-CRED-001/F-RELEASE-001/F-TENANT-001），拆出 CHANNEL-F001~F004。依赖F-PAGE-001、F-MULTIEND-001。**流程图检查结论：已检查，无真实顺序流程，摘要卡片**。**2026-09-02回填架构原则第42条#22**：新增4.2.1节明确区分客户端渠道品牌定制（CHANNEL-F002，完整白标）与管理控制台品牌定制（新增，仅登录页/导航栏Logo配色，非完整白标，属F-CONSOLE-001范畴登记于此避免与客户端白标能力混淆） |

**暂不加入，等待用户后续提供的3份外部包**：F-INTERVIEW-001、F-EXTERNALVIEW-001、F-SYNDICATION-001（依赖Conversation/Data Acquisition引擎、Communication Runtime & Meeting、Product Core，用户确认这些包存在但尚未整理发送）。


### 被正式文档引用、但在上面各表里没有登记行的编号（2026-09-08 全仓审计补录）

用脚本把全部正式开发文档里出现的 `F-XXX-NNN` 与本文件的登记行做差集，查出 8 个"被引用却查不到登记行"的编号。**其中 6 个是已知的、有原因的，2 个此前从没记录过**。列全在这里，免得下一个人（或下一个 AI）以为它们不存在。

| 编号 | 被几份正式文档引用 | 实况 | 是不是缺口 |
|---|---|---|---|
| **F-PLAT-001** | **9 份**（AI员工身份、Action网关、租户与权限体系、租户渠道实例、移动端Shell、通知中心、页面内容Schema、开发总账、架构设计原则） | **不是 Matbox 自己的模块**——它定义在上游《Matbox_多端平台_CURRENT_正式开发文档_V3.0》里；2026-08-30 已与 F-TENANT-001 做过分工确认（见租户与权限体系文档开头）。F-NOTIFY-001 把它列为「依赖方（已知阻塞）：人类登录会话」 | **否**（外部上游模块），但**此前从没在本登记表里说明过**——9 份文档依赖一个查不到出处的编号，现补记 |
| **F-MEM-001** | 3 份（AgentRuntime、架构设计原则、AI员工能力缺口调研清单） | 知识库/记忆系统。[专项27](技术选型报告/Matbox_专项27_知识库记忆系统_技术选型与开发交接报告_2026-08-30.md) 已完成技术选型调研；[架构原则第438条](Matbox_架构设计原则.md)明确决定「保持部分设计现状，**不现在锁定向量库方案**」。F-RUNTIME-001 用它来划边界（"跨会话长期记忆是 F-MEM-001 的职责，不是我的"） | **否**（有意暂缓，理由已记录），但**此前从没在本登记表里出现过**，现补记 |
| F-RUNTIME-001 | 3 份 | **已在册**，只是登记行把编号和名字写在同一个单元格（`F-RUNTIME-001 Agent Runtime`），与其余行的格式不一致，机器扫不到 | 否（格式问题，非缺口） |
| F-ASSET-001 | 4 份 | 见本文件既有说明：并入其他模块 | 否 |
| F-COLLAB-001 | 1 份 | 见本文件既有说明：仍是提案 | 否 |
| F-INTERVIEW-001 | 1 份 | 等待用户后续提供的外部包 | 否 |
| F-EXTERNALVIEW-001 | 1 份 | 等待用户后续提供的外部包 | 否 |
| F-SYNDICATION-001 | 1 份 | 等待用户后续提供的外部包 | 否 |

**这次审计还接上了一条此前断开的线**：上面「暂不加入，等待用户后续提供的3份外部包」那条写着它们依赖 **Communication Runtime**；而 [F-LOC-001](Matbox_全球多语言与本地化_正式开发文档_V1.0-RC.md) 的 **G-LOC-MATBOX-002** 卡的正是同一个东西（`Shared Messaging / Communication Runtime`，Message/Thread/Delivery State）。**LOC-F020（P0）不是一个孤立的 LOC 问题，它和那 3 个功能在等同一样东西**——四个功能一条队。已在 F-LOC-001 文档里补上交叉引用。

**本项已固化为机器检查**：`python docs/_check_docs_consistency.py` 的 C6 会持续比对"被引用的编号"与"有登记行的编号"，出现新的无说明孤儿就报出来，不再依赖谁记得去查。

## 横向行业调研（专项00系列，不产生新FeatureID，验证/回填已有模块）

来源目录：[docs/技术选型报告/](技术选型报告/)。这批报告不是"某个模块该怎么做"的技术选型，而是持续横向核查全球AI员工/AI Agent平台生态，验证Matbox已有设计、发现契约缺口、提供外部佐证。方法论教训：搜索必须用"AI coworker/同事Skill"这类真实高热度候选聚集的通俗用语，不能只用"AI employee platform"这类企业register用语，否则会系统性漏掉2026年最高热度的候选（详见专项00第10节）。

| 专项 | 对象 | 核心结论 | 对Matbox的影响 |
|---|---|---|---|
| [00](技术选型报告/Matbox_专项00_完整AI员工平台横向调研_2026-09-01.md) | 完整横向调研+第二轮补充 | 建立方法论：不能只看star数/名人背书，要看真实源码/issue/第三方讨论 | 后续00b-00n均沿用此标准 |
| [00b](技术选型报告/Matbox_专项00b_agency-agents-zh专项评估_2026-09-01.md) | jnMetaCode/agency-agents-zh | 267角色prompt库+真实TS编排引擎，单用户非多租户 | 不采纳，架构参考价值有限 |
| [00c](技术选型报告/Matbox_专项00c_agency-agents原版专项评估_2026-09-01.md) | msitarzewski/agency-agents | 纯prompt模板库，无真实编排运行时 | 不采纳 |
| [00d](技术选型报告/Matbox_专项00d_Paperclip专项评估_2026-09-02.md) | paperclipai/paperclip | 真实org-chart/预算自动暂停机制，但CVE-2026-41679含CVSS 10.0未鉴权RCE | REJECT代码/架构，CVE已作为F-ACTION-001 P0规则外部佐证 |
| [00e](技术选型报告/Matbox_专项00e_AI员工呈现方式与cumora专项评估_2026-09-02.md) | yetone/cumora | TS技术栈冲突+BCG研究证明"具名员工"呈现削弱人类监督 | 只采纳"具名+头像+状态"安全一半，见架构原则第43条 |
| [00f](技术选型报告/Matbox_专项00f_AI员工指令交互流程设计_2026-09-02.md) | 指令交互流程设计提案 | 纯聊天框是结构性失败模式，需"目标→任务→子任务"看板层 | 发现RoutingRequest/AiTask 5处契约缺口，已回填F-ORCHESTRATOR-001/F-TASK-001 |
| [00g](技术选型报告/Matbox_专项00g_目标客户规模策略调研_2026-09-02.md) | 目标客户规模 | 中国"规上"家具企业仅0.5%，EU家具SME占70%+增加值 | 支撑"中小企业优先"确认决定（架构原则42#24） |
| [00h](技术选型报告/Matbox_专项00h_竞争对手深度调研_2026-09-02.md) | 三维家/尚品宅配/酷家乐/Lateua | 真实竞对数据核实（三维家17000+企业客户等） | 竞对格局记录，回填架构原则42#23 |
| [00i](技术选型报告/Matbox_专项00i_OpenWorker专项评估_2026-09-02.md) | andrewyng/openworker | 真实工程但审批fail-open(#520)/幂等缺陷(#443)未修复 | REJECT代码/架构，2条参考回填00f，2条反面案例回填专项16 |
| [00j](技术选型报告/Matbox_专项00j_Distilly与AgentTeams专项评估_2026-09-02.md) | titanwings/distilly、agentscope-ai/AgentTeams | Distilly治理风险大(单人133 commits)+缺同意机制；AgentTeams阿里背书健康 | 确认不做"同事数字分身"功能（架构原则第44条） |
| [00k](技术选型报告/Matbox_专项00k_多AI员工协同场景与AgentTeams对接方案_2026-09-02.md) | 多AI员工协同场景（首轮，仅家具制造） | 家具订单是接力式流程，委派机制够用 | 提出F-COLLAB-001方案，复用现有SSE/WS机制，不引入Matrix协议（Java无成熟SDK） |
| [00l](技术选型报告/Matbox_专项00l_TabTin与munder-difflin真实评价核查_2026-09-02.md) | TabTin、munder-difflin | TabTin公开仅10天证据不足但上海团队刚获6000万融资，munder-difflin面向编程Agent关联度低 | 均不深挖，TabTin列入观察名单 |
| [00m](技术选型报告/Matbox_专项00m_ConductorOSS专项评估_2026-09-02.md) | conductor-oss/conductor | 与Temporal同类，验证Temporal选型仍是更优解 | REFERENCE-ONLY，回填专项28候选清单 |
| [00n](技术选型报告/Matbox_专项00n_多AI员工协同场景补充核查_设计服务行业_2026-09-02.md) | 多AI员工协同场景（补充，室内/建筑/景观） | 单一设计工种也是接力式，但建筑"多专业协同设计"(BIM协调员角色)是目前最贴近AgentTeams模式的真实场景 | 00k的REFERENCE证据强度从"自编示例"升级为"真实第三方案例"，F-COLLAB-001技术方案不变 |
| [00p](技术选型报告/Matbox_专项00p_七家AI员工平台12维度横向调研_2026-09-05.md) | 七家AI员工平台（ServiceNow/Salesforce/Microsoft/UiPath/Zapier/Intercom·Fin/Workato）× 12维度 | **本文档只是调研的一半**——按2026-09-05分工，用户侧用GPT做官方一手资料穷举，本会话负责独立负面证据+核实数字+翻译成Matbox字段；**跨公司总结待两边合并后再做，本文不下总结**。已浮现待验证的现象：连接器"被上游逼停"出现3次、跨区能力差异出现2次、官方与独立质量数字最大落差是Fin（67% vs 38%）、Fin证明"不自建连接器生态"也能跑通（MCP+蹭Zapier） | 尚未回填任何模块。ACTION-F007已识别3处待修（动作粒度、版本字段、凭证租户级隔离），详见本报告Salesforce一节 |

## 前端页面

| 名称 | 状态 | 说明 |
|---|---|---|
| Lumora 首页 | 🔵 CONFIRMED（设计中） | 家居产品展示首页，详见 [Matbox_前端页面追踪清单.md](Matbox_前端页面追踪清单.md) |

## 架构底层（技术选型审查已完成，见专项27/28）

| 模块 | 状态 | 说明 |
|---|---|---|
| 商家与产品档案（Catalog/PIM，暂定FeatureID待定） | ⚪ NOT_STARTED（2026-09-05识别，有意暂缓，不并入AI员工深化） | 用户明确要求"专心弄完AI员工，不要一而再再而三分心"，本条只做记录、不展开设计。**背景**：讨论AI员工Connector Registry时，用户指出"商家档案"和"产品档案"这类业务数据现有架构里没有归属，最初以为属于AI员工范围（交接文档"缺口③"），后用户当场纠正——这是独立的公共数据层，被平台店铺/独立站/移动端/AI员工调用/AI作图/视频/详情图等多方共同消费，不是AI员工专属，不挂在AIEMP/ACTION下面。**已查证的初步方向（未展开设计）**：PIM（产品信息管理）是真实、成熟的软件品类（"Golden Record"模式：每SKU一份权威主记录，各渠道呈现从主记录派生，headless+API-first架构）；多租户SaaS惯例是"商家档案"（业务数据）与"权限RBAC"（F-TENANT-001已有）分层处理，不合并；Shopify真实架构印证此分法。**已知未处理项**：用户提到还有一份用Codex测试产出的相关资料未提供给本会话，尚未核对是否与此重复/冲突。**下一步**：等AI员工这条线彻底收尾后再回来展开，不在本轮处理 |
| 知识库 / 记忆系统 | 🟡 有意保持不锁定（专项27已完成技术选型审查，2026-08-30） | 数据保留原则已定（架构原则第7条）；MEM-F001的ACL/来源/TTL/撤销传播权限控制层已设计完整。**专项27结论（[技术选型报告](技术选型报告/Matbox_专项27_知识库记忆系统_技术选型与开发交接报告_2026-08-30.md)）：不是遗漏未做，是调研完毕后确认"现在不锁定后端厂商"本身就是正确判断**——Mem0/Zep(Graphiti)/Letta/pgvector自建之间没有绝对赢家，胜负取决于Matbox真实对话量级/查询模式等目前不存在的场景数据。**现在就能做的具体动作（成本几乎为零）**：把MEM-F001的ACL契约做成后端无关的`MemoryStore`适配器接口，用已在用的PostgreSQL+pgvector做最小参考后端验证接口设计，不代表选定pgvector为正式引擎。**新发现需更正旧记录**：Zep已于2025年4月停运自托管社区版，只剩纯SaaS的Zep Cloud，直接影响"以后要不要用Zep"这条此前调研清单#23记录的判断，需更新 |
| F-RUNTIME-001 Agent Runtime | 🟢 DRAFT_RESEARCH_COMPLETE | **2026-09-05建立正式开发文档**：[Matbox_AgentRuntime_正式开发文档_V1.0-RC.md](Matbox_AgentRuntime_正式开发文档_V1.0-RC.md)——用户要求排查遗留项时发现，此前长期只有专项28技术选型报告，没有对应正式文档本体，跟AIEMP-001/ACTION-001等"选型+正式文档"两步都走完的模块不是同一进度，现已补齐，拆出RUNTIME-F001~F008。需吸收"AI员工执行安全"要求（架构原则第10条）+ Kill Switch紧急停止机制（架构原则第28条，2026-08-29确认）。心跳检测2-3分钟一次、必须从工作循环内部主动发出、连续漏2次才报警；进度表30分钟一次给用户看summary；两件独立的事。**技术选型结论（[专项28](技术选型报告/Matbox_专项28_AgentRuntime_技术选型与开发交接报告_2026-08-30.md)）：自研（Java+Temporal），明确否决LangGraph/CrewAI/AutoGen/OpenAI Agents SDK等全部Python-only候选**（语言栈与架构原则第33条Java单语言栈冲突），Google ADK Java版评为Top-3但因需要削足适履改造未整体采纳。**2026-09-02专项00m事后核查conductor-oss/conductor（原Netflix Conductor）作为验证性候选，非否决非采纳**——同属durable execution引擎赛道，但Temporal的"代码即workflow"模式对TASK-F008自我纠错这类复杂条件分支场景更合适，不构成推翻本选型的理由，完整核查记录见[专项00m](技术选型报告/Matbox_专项00m_ConductorOSS专项评估_2026-09-02.md)。**唯一真实协调缺口**：F-PROVIDER-001响应schema尚未定义跨供应商统一的`normalized_tool_calls[]`字段，已登记协调需求，不阻塞P0开工 |

## 专项00r 横向收口回改落地（2026-09-08）

九家供应商报告 100% 通读 + 数字回查完成后，[专项00r](技术选型报告/Matbox_专项00r_九家供应商横向收口_2026-09-08.md) §7 列出 11 项会回改正式文档的事项。**本日已全部落地**，不再是待办：

| 优先级 | 事项 | 落到哪 | 依据（几家独立收敛） |
|---|---|---|---|
| P0 | `executionIdentityPolicy` 成 AI 员工一等字段 + Sponsor 必填 | F-AIEMP-001 新增 §2.5 + AgentIdentity 补 3 字段 + P0规则8/9 | **4 家**（Workato 产品级限制最硬：VUA skills 跑不了自治 orchestration） |
| P0 | Provider 的 ACTIVE ≠ 已验证；Catalog/Search/Schema/Execute 四态 Health | F-ACTION-001 新增 `ConnectorHealth`、`ConnectionVerification` 契约 + P0规则12 | **4 家**（Composio #4120 垃圾 key 也 ACTIVE，26/26 复现） |
| P0 | TriggerAttempt 必须独立于 Run 记录 | F-ACTION-001 新增 `TriggerAttempt` 契约 + P0规则13 + 端点 | **3 家**（Activepieces #14328/#14808 静默失败还回 200） |
| P0 | Evidence 长期保存归 Matbox，Provider 日志仅作来源 | F-OBS-001 新增 §2.5 + P0规则6/7 | **5 家保留期实测**：7天/30天/30–90天/89天/180天 |
| P0 | Connector 验收单位改为 Action 级 | F-ACTION-001 新增 `ConnectorAction` 契约 + P0规则9/10 + 端点 | **9 家一致**（全部主动否定自己的连接器数字） |
| P1 | ACTION-F007 三处挂账：action 粒度 / version 字段 / 租户级凭据隔离 | `ConnectorDefinition` 补 version/tenantId/lifecycleState + P0规则11 | 原始出处已定位到 Salesforce §9 第6条 |
| P1 | 统一 Error Taxonomy | 错误码规范新增 §4.1，**15 个新错误码 + 3 条使用规则** | Microsoft 九码 + Activepieces 十一态 + UiPath `Faulted≠可重试` 归一 |
| P1 | 两套验签机制必须分开实现 | F-ACTION-001 新增 §2.3.1 + P0规则14 | Zapier 同一家两套：JWT/JWKS RS256 vs Standard Webhooks HMAC(raw body) |
| P1 | Canonical Timeout Policy | F-ACTION-001 新增 §2.3.2 + P0规则15 | Workato 实测同一动作五个入口五种 timeout（30s/40s/3min/90min/500s） |
| P2 | default-deny 必须带两个前提 | F-ACTION-001 新增 §2.3.3 | 微软 ACP 官方：仅 Certified Connector + 仅 Managed Environment；MCP 只能整站封 |
| P2 | ACTION-F006 的 BPMN+DMN 参照对象仍是 preview | ACTION-F006 行内标注 | UiPath Maestro Business Rules 页面至今标 `(preview)` |

**新增 P0 冻结规则合计 9 条**：F-ACTION-001 的 9~15（7条）、F-AIEMP-001 的 8~9（2条）、F-OBS-001 的 6~7（2条）。

## 下一步优先级

**已完成正式开发文档且已补充精确数据结构（可直接建表/建接口）**：F-CRED-001、F-OBS-001、F-RELEASE-001、F-COST-001、F-TENANT-001、F-QUEUE-001、F-STORAGE-001（均 2026-08-29）+ F-PROVIDER-001、F-TASK-001、F-EGRESS-001、F-AIEMP-001、F-ACTION-001、F-APPROVAL-001、F-NOTIFY-001、F-PAGE-001、F-MOBILE-001、F-MULTIEND-001、F-HANDOFF-001、F-CHANNEL-001（均 2026-08-30新建，源自《多端平台V3.0》）。用户明确要求"文档必须精确到一旦开工就能直接写代码，不只是整理规划"，全部19份文档均已补上核心数据Contract（字段级schema）+ 最小API端点集合，不再只是概念性描述。

**2026-08-29 自我复查发现新缺口**（不是用户提出，是重新审视架构原则+RC5文档后自己找出来的）：F-COST-001、F-TENANT-001、F-QUEUE-001、F-STORAGE-001 全部已完成正式文档。至此，本次自我复查发现的全部缺口都已补上正式文档。

**2026-08-29 用户要求"全面排查"数据Contract一致性，已完成**：逐份跨文档核对7个模块新增的字段级schema，与原质检文档/RC5文档/彼此之间比对，发现并修复4处真实问题（EvidenceBundle命名统一、AgentGrant重复建表去重、WorkPackage状态与QueueRun技术状态混用、dependencySnapshotRef字段名对齐源文档）。详见 [Matbox_架构设计原则.md](Matbox_架构设计原则.md) 第24条。

下一步是 Stage 10：确定服务器/部署方式（架构原则第40条已确认中国区+欧盟区混合架构大方向，具体落地仍在Stage 10范围）。**此前记录的4处遗留写回项现已全部完成**（2026-09-05核对）：质检文档"AI员工执行过程安全防护"（2026-09-05补齐）+"SLSA Provenance"（已确认无需改动本体）；人工修复台文档"Tree-sitter+SCIP混合方案"+"源代码当不可信数据处理"（2026-08-29已写回，见上方VIZ小节）。

**2026-09-02：build-vs-buy技术选型审查（对1-28个专项逐一做"自研/复用/接入/二开"审查，不默认全部自研）批次5完成6个（21a-21e、20），累计22/28。剩余#22/24/25/26四个明确卡在"独立站"业务包未提供（用户已确认，非遗漏），暂不推进；用户明确指示先把AI员工整块做扎实**：架构原则第42条27道产品/商业定义问题的9项待回填全部完成（#1/#2/#3/#4/#5/#6/#10/#11/#18/#21/#22/#25，仅剩#16数据导入归属需要新范围界定非机械回填），横向调研00-series扩展到00n（14份报告，见上方"横向行业调研"表格）。

**2026-09-02：流程图覆盖率复查完成**——用户当面指出这是第4次出现"该有流程图但没做"的遗漏，全量重新核实全部模块后确认4处真实缺口（TASK-F008/STORAGE-F006/PROVIDER-F003/AIEMP-F005），4张专属流程演示图已全部补建并接线进架构依赖图，本地server下逐一验证通过。根因（Feature Register的"流程图检查结论"标注是一次性判断，模块内容后续增长时未重新核查）已写入自查规则第7条（Flow-Diagram Coverage Check），要求今后任何模块新增Feature时都必须重新核对是否产生了新的真实顺序流程，不再只信旧标注。

**2026-09-02：制图后二次核查（用户追问"确定全部弄完了吗"触发）**——不满足于"流程图能打开"就算完成，逐一核对4张新流程图对应的正式文档acceptance criteria与实际API/数据字段是否自洽。TASK-F008、PROVIDER-F003核查后确认内部逻辑自洽、字段真实存在，无遗漏；AIEMP-F005（Retire未级联Revoke）、STORAGE-F006（软删除承诺可恢复但无restore端点）两处发现真实契约缺口并已修正，详见各自表格行。这次复查同时发现Feature Register的HTML网页版发布早于本轮4张流程图完工，内容已过期（仍显示"补建中"），已重新生成republish，与本文件同步。
