# Matbox 证据审计与AI员工监控（F-OBS-001）

正式开发文档 · V1.0-RC · 2026-08-29

## 当前定位

本专项解决两件不同但都紧迫的事：
1. **防篡改证据记录**——质检 Gate 的判定结果（GateDecision）、审核记录，一旦写入不能被偷改，事后能证明"当时确实是这么定的"。
2. **AI 员工行为监控**——团队只有2个人，没精力一个个盯着每个 AI 员工在干嘛，需要工具自动发现异常（烧钱死循环、编造信息、悄悄跳步骤）并报警。

这两件事很多项目会混成一个"日志系统"，但性质不同（一个要"防改"，一个要"实时看"），本文档分开设计，共用底层管道。

是 Platform Core 的共享能力，被 F-DQ-001/002/010/013、CRED-F006 直接依赖。

**DocID**: MATBOX-OBS-GATE-20260829-V1.0-RC
**状态**: DRAFT_RESEARCH_COMPLETE（已完成全球选型调研，未进入 Stage 10 真实施工）
**2026-08-30 核对AI员工底层包**：底层包的Quality Gate & Evidence（WP-009）和Observability & Agent Map（WP-011）方向跟本模块一致（OTel Trace/Metric + 证据留痕），`quality_result`表(gate_code/evaluator/score/threshold/evidence_ref)和`audit_event`表(actor_type/actor_id/before_hash/after_hash)的字段已并入EvidenceBundle的type扩展（见第5节），不需要新建平行的证据/审计系统。底层包的Threat Model文档（10类威胁：跨租户/prompt injection/凭证泄漏/委派提权/重放/恶意MCP server/供应链/数据泄露/失控成本/审计篡改）比本项目现有任何文档都更集中，Matbox目前没有独立的威胁清单文档，这是一处可以直接吸收的缺口，暂记录在此，待Stage 10前统一整理成正式威胁模型文档。

**2026-08-30 补充（重要架构变更）**：新增 OBS-F006（AI Evaluation，评测框架）。《Matbox_多端平台_CURRENT_正式开发文档_V3.0》F-OBS-001 章节把"AI评测"直接放进了证据审计里；用户确认按新文档为准，**评测框架不再是独立的、architecture底层里"尚未开始设计"的模块，而是并入本模块，现在就可以开始设计**——这推翻了架构原则第6条"评测框架现在不启动设计"的原判断，第6条和第28条相应部分已更新，架构依赖图的"内部持续评测框架"占位模块已移除（详见架构原则第31条）。

## 1｜不可变原则

1. 证据类记录（GateDecision、SourceReviewRecord、AcceptanceRun）一旦写入不得修改或删除，只能追加新记录。
2. AI 员工监控数据（token消耗、工具调用、异常）与证据类记录物理/逻辑分开存放，不能混为一谈——监控数据可以滚动清理，证据数据不行。
3. 告警必须"可行动"——发出来的每一条报警都得有人能处理，处理不了的不发，避免"狼来了"。
4. 优先用官方原生支持的标准，不额外造轮子。

## 2｜全球调研结论（2026-08-29）

### 2.1 关键发现：Anthropic 官方已原生支持标准化监控

Claude Code / Claude Agent SDK 在 2026 年已经**官方原生支持 OpenTelemetry**（业界公认的厂商中立监控标准，不是 Anthropic 专属），可以零改造直接拿到：token消耗、预估成本、工具调用记录、会话健康度。官方还提供现成的 Docker Compose + Grafana 模板。这与"不绑定单一供应商"的原则不冲突——OpenTelemetry 本身就是跨厂商标准，换别的 AI 模型一样能用。

**结论：AI 员工监控直接用 OpenTelemetry 做采集标准，不用另外造/接第三方监控协议。**

### 2.2 看板/存储工具选型

| 候选 | 说明 | 结论 |
|---|---|---|
| SigNoz | 自建、OpenTelemetry原生、日志+指标+链路一体 | **采用**——自建单二进制，够小团队用 |
| OpenObserve | 类似定位，也是2026年热门开源选项 | 备选，功能接近 |
| Uptrace | 用 ClickHouse 做存储，天然不可改历史数据 | 备选，存储层更硬核但部署更重 |

### 2.3 防篡改证据存储选型

| 候选 | 说明 | 结论 |
|---|---|---|
| **immudb** | 开源，每条记录进入密码学可验证的链条，改了/删了都能被发现 | **采用** |

### 2.4 告警原则（2026年共识）

只设置"高信号"告警——每一条报警都必须是能处理的，处理不了的不发，避免因为报警太多导致人麻木不管。AI 员工监控要重点抓：token 异常消耗（死循环烧钱）、连续失败、行为偏离历史基准（drift）。

### 2.5 九家供应商的证据保留期实测：没有一家能承担 Matbox 的业务证据责任（2026-09-08新增，专项00r收敛⑥）

本会话对九家供应商报告做 100% 通读 + 数字回查后，逐家查到的 Provider 侧保留期：

| 供应商 | Provider 保留期 | 证据强度 |
|---|---|---|
| **Zapier** | Action Run 结果 **仅 7 天**（官方原文：`Action Runs are stateless: data is retained briefly (7 days) for processing and troubleshooting, then automatically deleted.`） | ✅ 官方逐字命中 |
| **Activepieces** | 执行数据 **30 天**（官方 limits 页） | ✅ 官方逐字命中 |
| **Workato** | Job/trigger/report **30–90 天**（Activity audit 默认 1 年，外部 streaming 连续失败 7 天后标记 failed） | 📄 报告内容 |
| **Microsoft** | Evaluation 结果约 **89 天** | 📄 报告内容 |
| **Fin / Intercom** | 删除请求后 ≤30 天；合同终止后未请求则 180 天自动删除，备份再 +14 天 | 📄 报告内容 |

**这不是个别厂商的短板，是五家一致的行业常态。** 收敛结论：**Provider 的执行日志只能作为 Evidence 的来源之一，绝不能作为 Matbox 的 Evidence SoT。**

**对本模块的直接含义**：OBS-F003（防篡改证据账本）与 OBS-F008（分层存储）的定位因此被九家独立验证——不是"锦上添花的审计功能"，而是**业务证据能否在 Provider 保留期之后仍然存在**的唯一保障。任何一次外部 Action 的证据，在 Provider 侧最短 7 天就会消失。

**同时补一条 Workato 查到的坑**：外部 Audit Log Streaming 失败会进入持久缓存并指数退避，但**连续 7 天仍未成功后会被标记为 failed 事件**——即"日志已经流出去了"这个假设本身会静默失效。Matbox 对外部日志流必须做 delivery ack + 缺口扫描 + 补拉告警，不能只发不管。

## 3｜Own / Reuse / Must Not Rebuild

| 类型 | 对象 | 说明 |
|---|---|---|
| OWN | EvidenceBundle、GateDecision存证规则、告警规则 | Matbox 自己的证据/告警业务逻辑 |
| REUSE | OpenTelemetry采集、SigNoz存储展示、immudb防篡改存储 | 直接用现成开源实现 |
| MUST NOT REBUILD | OTel SDK本身、密码学验证算法 | 不自己写监控协议或加密验证逻辑 |

## 4｜Feature Register

| FeatureID | 名称 | 说明 |
|---|---|---|
| OBS-F001 | OpenTelemetry 采集层 | 接入 Claude Agent SDK 原生 OTel 输出 + Matbox 后端自身埋点 |
| OBS-F002 | 自建监控看板 | SigNoz 自建部署，AI员工行为看板（token/工具调用/异常） |
| OBS-F003 | 防篡改证据账本 | immudb 存储 GateDecision/SourceReviewRecord/AcceptanceRun |
| OBS-F004 | 高信号告警规则 | token异常/连续失败/行为drift 的可执行报警 |
| OBS-F005 | 统一证据查询接口 | 供 F-DQ-002/010/013、CRED-F006 等模块查询证据 |
| OBS-F006 | AI Evaluation（评测框架） | 离线Golden/Challenge Set评测+线上eval运行，2026-08-30从多端平台文档并入，原架构原则第6条"暂不启动"已改 |
| OBS-F007 | 生产环境持续质量漂移监测 | 拿OBS-F006 Golden Set当基线，持续监测生产输出质量有没有偏移，区别于OBS-F006的"上线前测一次" |
| OBS-F008 | 证据/审计日志分层存储 | 热存(近期，immudb)+冷归档(旧数据，低成本存储)，满足EU AI Act留存要求且控制成本 |

### OBS-F001 · OpenTelemetry 采集层
- **目标**：Claude Agent SDK 的原生 OTel 数据（traces/metrics/log events）接入 Matbox 自己的管道；Matbox 后端服务自身也按 OTel 标准埋点，保证以后换AI供应商时监控体系不用重做。
- **验收标准**：AI员工每次任务的 token 消耗、工具调用链路可查询。

### OBS-F002 · 自建监控看板
- **目标**：自建 SigNoz，展示 AI 员工行为看板（谁在干活、烧了多少 token、有没有循环报错）。
- **验收标准**：团队两人任一人打开看板，5分钟内能看出"现在有没有 AI 员工在异常运行"。

### OBS-F003 · 防篡改证据账本
- **目标**：GateDecision、SourceReviewRecord、AcceptanceRun 等证据类记录写入 immudb，任何后续修改/删除企图都能被检测到。
- **验收标准**：对已写入记录做任意篡改测试，系统必须能检测并报告不一致。

### OBS-F004 · 高信号告警规则
- **目标**：只对"团队真能处理"的异常报警——token异常消耗、连续失败超过阈值、行为明显偏离历史基准。
- **验收标准**：告警误报率可追踪；连续出现无效告警需要有清理/调整机制，不能放任不管变成噪音。
- **2026-09-04新增职责（场景模拟[Matbox_发布与基线系统](Matbox_发布与基线系统_正式开发文档_V1.0-RC.md)REL-F007时发现，此前遗漏）**：也负责评估REL-F007的`RolloutThreshold`（灰度发布的关键指标阈值），突破时直接调用REL-F007的`POST /release/deploys/{deployId}:rollback`触发自动回滚——REL-F007自己不实现指标采集/评估逻辑，复用本模块已有的OpenTelemetry+SigNoz管线，不重复建设。
- **2026-09-04再新增职责（场景模拟[Matbox_AI任务运行时](Matbox_AI任务运行时_正式开发文档_V1.0-RC.md)TASK-F006时发现）**：TASK-F006检测到长任务执行偏离原计划超过阈值时，调用本模块生成告警（本条原话"行为偏离历史基准（drift）"本来就覆盖这个场景），TASK-F006自己不建通知机制。
- **2026-09-04第三次新增职责（场景推演"运行中"R1-R4自身指标时发现，比前两处更基础）**：DQ质检系统自己的核心运行指标（BLOCKED_MANUAL占比、scanner_error_rate、工具升级回归检出率下降等，定义见DQ正式文档第17节/F-DQ-013）异常时，同样必须调用本模块生成可行动告警，不能只在DQ自己的运行看板上被动展示、指望有人自己想起来去看——DQ原文档F-DQ-013的"目标"原话是"让Quality Owner能看到"，只写了展示，没写通知，是本条覆盖范围里最容易被忽略的一处，因为它是DQ自己的地基指标，不像REL-F007/TASK-F006那样是"外部模块来找OBS-F004"，这次是反过来发现DQ自己都没接。

### OBS-F005 · 统一证据查询接口
- **目标**：F-DQ-002/010/013、CRED-F006 等模块都通过这一层查询证据，不各自直连存储。
- **验收标准**：新增模块要用证据数据时，只能走这层接口，不能绕过。

### OBS-F006 · AI Evaluation（评测框架，2026-08-30新增，架构变更）
- **目标**：任何关键人工/AI动作可追到actor/resource/action/version/result/cost/approval/evidence——这条本身跟OBS-F001~F005一致；新增的是评测本身：跑Golden/Challenge Set、记录eval结果，判断AI员工/模型的输出质量有没有下降。
- **In Scope**：trace IDs；结构化审计；model/prompt/tool/policy版本；EvidenceBundle；eval运行；指标。
- **Out of Scope**：不把普通web访问日志当AI审计。
- **上游输入**：来自所有Feature的事件。
- **下游输出**：可查询的审计/证据/eval指标。
- **页面/入口**：`/ops/audit`；`/ops/evals`；任务时间线
- **依赖**：与OBS-F001~F005共用同一套OpenTelemetry采集管道，不新建第二套。
- **验收标准（按七层施工面，原样保留自多端平台文档，未做删减）**：
  - Frontend/UI：审计/证据时间线/eval结果可见，敏感原文默认隐藏/脱敏；关键事件可定位source/version。
  - Backend/API/Service：Audit/Evidence/Eval服务；不允许每个Feature自建日志schema；审计写入失败策略明确，不能吞掉P0事件。
  - Data/DB/Migration：追加式审计/证据/eval结果引用；secret/敏感全文不得无控制保存；留存/导出/版本测试。
  - Async/Runtime：异步指标/eval作业；不阻塞主事务做重计算；事件丢失/重复的指标测试。
  - Provider：OpenTelemetry/log/metric/eval适配器；不把provider遥测当唯一事实源；跨服务trace连续性。
  - Infra/Config：采集器/留存/脱敏/告警配置；不暴露公开日志；P95/失败工具/provider/审批拒绝指标。
  - Tests/Observability：审计完整性/eval回归测试；Golden/Challenge Set版本化；证据可追溯性。

**2026-08-30 深度核实后补强**：多端平台文档原文对"Golden/Challenge Set"只有笼统提法，没有具体结构。查证2026年LLM/Agent评测的成熟做法后确认，评测集必须覆盖以下**4类**，缺一类都不算完整（不能只有其中一两类就自称"建了评测集"）：
1. **真实生产流量抽样**——从真实运行中的请求里按比例抽样，不是纯人工编的题目
2. **对抗性测试库**——专门构造用来诱导AI员工犯错/被绕过的案例
3. **人为构造的边界情况**——覆盖率不够但真实可能发生的边角场景
4. **过去真实出过问题的案例重放**——线上出过的真实故障，固化成回归用例，防止同一个问题再犯

每次评测运行应记录覆盖了这4类里的哪些、各类占比，而不是只报一个笼统的"通过率"。

**工具选型（2026-08-30深度核实新增，之前完全没点名具体工具）**：按Matbox一贯"自建开源优先"原则（同CRED的Infisical、COST的Langfuse、OBS其余功能的SigNoz+immudb），确定用**DeepEval**（开源MIT，Python，能直接嵌进pytest跑CI/CD评测，覆盖"真实生产流量抽样"+"过去问题重放"这两类）配合**Promptfoo**（开源MIT，专长生成/运行对抗性用例——prompt注入、越狱、PII泄露、工具滥用，正好对应"对抗性测试库"这一类）。Promptfoo虽然2026年被OpenAI收购，但官方确认继续保持开源MIT协议，不影响自建使用。避免CI跑分不稳定的做法：用容差区间而不是精确阈值判断通过，固定评判用的模型版本。

**评测集4类结构与工具映射**：

| 类别 | 内容 | 承接工具 |
|---|---|---|
| 真实生产流量抽样 | 从线上请求按比例抽样 | DeepEval |
| 对抗性测试库 | prompt注入/越狱/PII泄露/工具滥用 | Promptfoo |
| 人为构造边界情况 | 覆盖率不够但真实可能发生的场景 | DeepEval |
| 历史故障重放 | 线上真实出过的问题固化成回归用例 | DeepEval |

**重要说明（跟架构原则第6/28条的关系）**：原先"评测框架现在不启动设计"的判断，是基于"Matbox现在没有真实部署，离线/线上评测都做不出真正有用的东西"这个前提。现在评测框架被并入本模块（OBS-F001~F005已经READY_FOR_STAGE10_BINDING），意味着评测框架的设计工作现在就可以跟着OBS一起开始，不用再等Stage 10——具体多快真正投入使用（跑真实评测数据），仍然受限于"有没有真实系统在跑"这个客观条件，这一点没有变。

### OBS-F007 · 生产环境持续质量漂移监测（2026-08-30从"AI员工能力缺口调研清单"#5并入）
- **目标**：区别于OBS-F006"上线前/版本升级前测一次"，本Feature拿OBS-F006的Golden Set结果当基线，**持续**监测生产环境的实际输出质量有没有偏移——查证到2026年共识是团队常见错误是"开发阶段猛加监控，上生产反而为了性能扒掉"，实际相反，生产环境才是最需要持续监控的阶段；未持续监控的团队常在30-60天内出现质量悄悄下降却不自知的情况。
- **验收标准**：质量分数滚动窗口下降超过阈值（参照行业常见做法：6小时滚动窗口下降>15%）触发告警；告警需要能区分"真实质量下降"和"正常波动"，不能一有风吹草动就报警变噪音（同OBS-F004"高信号告警"原则）。
- **2026-09-04新增职责（场景推演DQ"运行中"R4"人工审核通过率趋势"指标时发现）**：该指标的异常形状是"悄悄涨"的缓慢漂移，不是单点突变，形状跟本Feature的滚动窗口对比基线机制一致，跟OBS-F004的"超过阈值就报"不是一回事——直接套OBS-F004会等到通过率已经明显失控才报警，滚动窗口才能在早期趋势阶段就发现。本Feature机制上不天然只服务AI员工，只是`QualityDriftCheck`现有字段（`employeeId`+关联OBS-F006 Golden Set基线）目前只覆盖了AI员工这一种用法；人工审核员不是AI员工也没有Golden Set可比，需要为"人工审核通过率"这类人的行为漂移指标开一条不依赖Golden Set基线的轻量分支（基线取自身历史滚动窗口即可，不需要另建评测框架），复用的是本Feature的"滚动窗口vs基线"机制本身，不是复用AI专属字段，也不新建第二个漂移检测模块。

### OBS-F008 · 证据/审计日志分层存储（2026-08-30从"AI员工能力缺口调研清单"#11并入）
- **目标**：immudb（OBS-F003）继续作为近期热数据的防篡改存储；超过热存周期（默认90天，可配置）的记录归档到低成本冷存储，归档后仍保持防篡改特性（链式哈希校验不失效），满足EU AI Act"至少留存6个月"的硬性要求且控制长期存储成本。
- **验收标准**：归档到冷存储的记录仍可被校验完整性（不因为迁移存储介质就失去防篡改能力）；查询跨热存/冷存的证据链时对使用方透明，不需要区分"这条记录存在哪"。
- **证据强度说明**：这条只确认了immudb"仅追加不可篡改"这一技术特性的适配性，"分层存储成本优化"这个细分点没有查到同等扎实的真实客户案例，证据强度弱于本文档其余条目，Stage 10真实接入云存储时需要重新核实归档存储的具体产品选型。

## 5｜核心数据 Contract（逻辑模型，可直接建表/建接口）

**EvidenceBundle**（沿用质检文档已有命名，immudb存储，防篡改主表——不是新概念，是给已有的 EvidenceBundle/evidenceBundleRef 补充具体字段结构；2026-08-30核对AI员工底层包`quality_result`/`audit_event`表后确认type枚举可直接扩展覆盖，不需要新建平行的证据表）
evidenceBundleId, type(GateDecision|SourceReviewRecord|AcceptanceRun|CredentialAccessEvent|PolicyDecision|QualityResult|AgentAuditEvent等), refId（指向原始业务对象，如qualityRunId/gateDecisionId）, tenantId, contentHash, prevHash（链式防篡改）, beforeHash?/afterHash?（type=AgentAuditEvent时使用，记录变更前后状态哈希，源自AI员工底层audit_event表字段）, storageTier(HOT|ARCHIVED)（OBS-F008，2026-08-30新增，超过热存周期后归档标记）, payload(jsonb), writtenAt, writtenBy

**QualityDriftCheck**（OBS-F007，2026-08-30新增）
checkId, tenantId, employeeId?, baselineEvalRunId（关联OBS-F006的EvalRun作为基线）, windowStart, windowEnd, currentScore, baselineScore, driftPercent, alertTriggered(bool), checkedAt

**AgentTraceEvent**（OpenTelemetry Span，存SigNoz）
traceId, spanId, parentSpanId?, agentId, workPackageId, model, provider, tokensIn, tokensOut, costUsd（关联F-COST-001）, latencyMs, status(OK|ERROR|TIMEOUT), startedAt, finishedAt

**AlertRule**
ruleId, metricName（如token_burn_rate, consecutive_failures）, threshold, windowMinutes, severity(P0|P1), notifyChannel, status(ACTIVE|MUTED|EXPIRED)（对应"高信号告警"原则，避免狼来了）

**AlertEvent**
alertEventId, ruleId, triggeredAt, resolvedAt?, acknowledgedBy?, falsePositive(bool)（用于统计误报率、调整规则）

**EvalRun**（OBS-F006，评测运行记录，2026-08-30新增，字段在多端平台文档基础上补充了bucketCoverage）
evalRunId, goldenSetVersion, modelRef, promptVersion, resultSummary(jsonb), passRate, bucketCoverage(jsonb)（记录production_sample/adversarial/edge_case/replayed_failure四类各自的用例数与通过率，2026-08-30深度核实后补充，避免笼统通过率掩盖某一类完全没覆盖）, executedAt

**API 端点（最小集合）**
- `POST /obs/evidence-bundles` — 写入EvidenceBundle（内部服务调用，仅追加不可改）
- `GET /obs/evidence-bundles?refId=` — 按业务对象ID查询证据链
- `POST /obs/verify/{evidenceBundleId}` — 校验某条记录是否被篡改（返回校验结果+hash链）
- `GET /obs/agent-trace/{agentId}` — 查询某AI员工的行为轨迹
- `POST /obs/evals/run` — 触发一次评测运行（OBS-F006）
- `GET /obs/evals/{evalRunId}` — 查询某次评测的结果详情
- `GET /obs/drift-checks?employeeId=` — 查询某AI员工的持续质量漂移监测结果（OBS-F007）
- `POST /obs/evidence-bundles/{evidenceBundleId}/archive` — 手动/自动触发归档（OBS-F008，超过热存周期自动触发）

## 6｜P0 冻结规则

1. 证据类记录（GateDecision等）被直接修改或删除且无痕迹：不可降级 P0。
2. 监控数据和证据数据混存导致证据被监控数据的清理策略误删：不可降级 P0。
3. 告警长期无效未处理导致团队对报警麻木（狼来了效应）：视为设计缺陷，需要重新调整告警规则。
4. 证据归档到冷存储后防篡改特性失效（无法再校验完整性）：不可降级P0。
5. 生产环境质量漂移超阈值未触发告警（静默劣化）：不允许。
6. **把外部 Provider 的执行日志当作 Matbox 的 Evidence SoT：不可降级P0**（2026-09-08新增，专项00r收敛⑥，见2.5节）。五家实测保留期为 7 天 / 30 天 / 30–90 天 / 89 天 / 180 天，**最短的 Zapier Action Run 只有 7 天**。每一次外部动作的证据必须在 Provider 保留期内完成向 Matbox 证据账本的持久化，Provider 侧记录只保留为 `provider_evidence_ref` 外部引用。
7. **外部 Audit Log Streaming 只发不校：不允许**（2026-09-08新增）。必须有 delivery ack、周期性缺口扫描、失败补拉与告警——Workato 实测其 streaming 连续失败 7 天后会把事件标记为 failed，届时缺口已不可恢复。

## 7｜当前唯一继续断点

Stage 10（真实部署 SigNoz + immudb，接入真实 Claude Agent SDK OTel 数据）尚未开始。下一步：实际部署这两个工具、验证 OTel 数据真实可采集、把 OBS-F001~F008 转成 WorkPackage。OBS-F008的冷存储具体产品选型待Stage 10真实接入云存储时核实。

## 附录｜来源

- [Claude Code Observability with OpenInference and OpenTelemetry in 2026](https://futureagi.com/blog/claude-code-observability-openinference-opentelemetry-2026/)
- [Claude Agent SDK Observability with OpenTelemetry (2026)](https://openobserve.ai/blog/claude-agent-sdk-observability-opentelemetry/)
- [Monitor Claude Cowork activity with OpenTelemetry - Anthropic Help Center](https://support.claude.com/en/articles/14477985-monitor-claude-cowork-activity-with-opentelemetry)
- [Agent observability: The complete guide for 2026 - Braintrust](https://www.braintrust.dev/articles/agent-observability-complete-guide-2026)
- [Beyond Syslog: Building a Tamper-Proof Audit Trail with immudb](https://fossforce.com/2026/08/beyond-syslog-building-a-tamper-proof-e-commerce-audit-trail-with-immudb/)
- [Best Open-Source Observability Platforms in 2026 (SigNoz/OpenObserve)](https://www.parseable.com/blog/ten-best-open-source-observability-platforms-2026)
- [Monitoring for Startups: Set Up Reliability Before Your First 1,000 Users](https://web-alert.io/blog/monitoring-for-startups-reliability-before-scale)
- OBS-F006 内容来源：《Matbox_多端平台_CURRENT_正式开发文档_V3.0》F-OBS-001 章节（2026-08-30 核对合并，架构变更详见架构原则第31条）
- **EvidenceBundle类型扩展/Threat Model依据（2026-08-30）**：《Matbox_AI_Employee_System_V6.3_Final_Frozen》底层包`04_Domain_Schema/migrations/005_artifact_quality_cost_audit.sql`（quality_result/audit_event表）、`08_质量安全成本/security/threat_model.md`、WP-009/WP-011定义
- OBS-F006 评测集4类结构补强依据：[LLM Eval Golden Set Design: A 2026 Engineering Guide](https://futureagi.com/blog/llm-eval-golden-set-design-2026/)（2026-08-30深度核实，原多端平台文档的"Golden/Challenge Set"提法偏笼统，按此依据补充为4类结构）
- OBS-F006 工具选型依据（DeepEval+Promptfoo，2026-08-30，按12条完整核对表执行）：[Top 5 LLM Evaluation Frameworks in 2026, Compared — DeepEval](https://deepeval.com/blog/top-5-llm-evaluation-frameworks)、[DeepEval alternatives (2026) — Braintrust](https://www.braintrust.dev/articles/deepeval-alternatives-2026)
- **OBS-F007/F008依据（2026-08-30）**：[Matbox_AI员工能力缺口调研清单_2026-08-30.md](Matbox_AI员工能力缺口调研清单_2026-08-30.md)#5#11；Arize/Galileo/Confident AI真实市场数据（模型监控品类市场份额23.9%/6.6%）；immudb"仅追加不可篡改"技术特性确认
