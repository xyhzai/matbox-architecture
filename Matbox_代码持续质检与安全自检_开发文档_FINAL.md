# Matbox 代码持续质检与安全自检 Gate · 开发文档 FINAL

**FeatureID**：F-DQ-001 ~ F-DQ-013（13 个功能，同一份文档统一定义）  
**归属**：Platform Core Quality / DevCodeQuality  
**生成于**：2026-09-09 15:23（仓库 a13b2d8）  
**生成方式**：`python docs/_build_dq_final_doc.py`，内容从源头逐条抽取，不重新表述  
**来源指纹（两个源，任一改动本文档即过期）**  

- `Matbox_代码持续质检与安全自检_正式开发文档_V1.1-RC_CURRENT_Stage9内容级重验版_2026-08-19.docx` sha256 `fa1d5a65431d37ff95ce9440c870ee197959aa8c3ea6f9bc3961b4d0fd9f4372`  
- `Matbox_专项01_代码持续质检与安全自检_技术选型与开发交接报告_2026-08-30.md` sha256 `f772814db0559f767b5b358457baab918e413689887bae657860e9c6e2e5037a`

> 最后一行不是装饰。本文档是**生成物**，源文件一改它就过期，而过期是没有提示的——这正是今天查出一堆矛盾的根因。一致性检查器 C8 会比对这个指纹，对不上当场 FAIL。改了源文件请重跑生成器。

---

## 0｜这份文档是什么，以及它跟其他文档的关系

### 0.1 它是唯一权威

DQ 的决定此前散在 6 个地方：正式文档 `.docx`、样板 `quality_gate_flow.html`、架构设计原则、开发总账、Feature Register、专项01 交接报告。谁也不是全的，而且 2026-09-08 一天内就查出 4 处互相矛盾（总账 10 处过期 MISSING 标记、同一道 Gate 两个编号、写 6 道 Gate 实为 7 道、同一模块 4 个名字）。**这些不是巧合，是「没有唯一真相」必然长出来的东西。**

**从本文档起，DQ 的内容以本文件为准。** 其余文件的角色：

| 文件 | 新角色 |
|---|---|
| `..._V1.1-RC_..._2026-08-19.docx` | **历史存档**。它是本文档的主要来源，但已被改过 13 次、不再是用户交付的原版（原版在 git `edd6951`）。今后不再单独维护 |
| `quality_gate_flow.html`（样板） | **标准与范例**。它定义「一个功能的开发资料要齐全到什么程度」这 12 块结构，并作为其余约 200 个功能的模板。它展示本文档的内容，不再是内容的沉淀地 |
| `Matbox_架构设计原则.md` | **跨模块规则**。凡是不只管 DQ 一家的规则（调度器、AI 何时问人、审核机制…）留在那里，本文档引用不复制 |
| `Matbox_开发总账.md` | **RC5 31 项字段台账**，派工用，不重复本文档内容 |
| 其他模块正式文档 | 灰度/回滚在 `F-RELEASE-001`、自认领/worktree 在 `F-TASK-001`/`F-QUEUE-001`、指标告警在 `F-OBS-001`——**这些故意不放在 DQ**，本文档只引用 |

### 0.2 怎么用（目标：直接 AI 开发，秒对接）

- **派活给一个 AI**：不要甩整份。从 `docs/工作包/DQ/` 取它自己那一份（Scope + 依赖 + 它那 7 行施工面 + 相关验收标准 + 派工字段）
- **人工审核准备度**：看「开发前」12 块，缺哪块一眼可见
- **每一句都能反查出处**：每块结尾标了它来自 `.docx` 哪一节 / 专项01 哪一节 / 样板 / 架构原则第几条。**指不出出处的内容不许进本文档**

### 0.3 「可直接开发」验收清单 —— 交付前逐条验，不靠感觉

用户定的标准是**「达不到就自己补资料，直到可以秒开发」**。

> **这张清单存在本身就是一次教训的产物。** 第一版 FINAL 只读了 `.docx`，把 1069 行的《专项01 技术选型与开发交接报告》当成「讲选哪个工具的」跳过了——**只凭文件名判断内容**。实际它装着 API 端点清单、真 SQL DDL、源码目录树、OpenAPI、鉴权、错误码、测试集、工作量估算，也就是「能不能直接写代码」缺的全部东西。根子上的毛病是：我验的是「我这一步做完没有」，不是「这东西够不够开工」——两个不同的问题。所以把标准变成一张能勾的清单，动笔前列出来、交付前逐条验，不靠自觉。

**当前：24 / 24 项齐备，0 项部分，0 项缺**

| | 项 | 状态 | 在哪 / 缺什么 |
|---|---|---|---|
| 1 | 技术栈定死（语言/框架/DB/迁移工具） | ✅ | FINAL §4.18.1：Java/Spring Boot（RuoYi-Vue-Pro 基座）+ PostgreSQL + Flyway + 共享表 tenant_id。**2026-09-09 补上出处**：此前写了「已核实 RuoYi 支持 PostgreSQL」却没给来源，等于没验。现已查证——官方仓库有专门的 sql/postgresql/ruoyi-vue-pro.sql，官方支持 MySQL/Oracle/PostgreSQL/SQLServer/MariaDB/达梦/TiDB（github.com/YunaiV/ruoyi-vue-pro）。结论成立。 |
| 2 | 源码目录结构 + 依赖方向铁律 | ✅ | 专项01 §22 |
| 3 | API 端点清单（方法/路径/幂等键/对应 Feature） | ✅ | 专项01 §13：20 个端点，统一前缀 /dq |
| 4 | Request / Response Schema | ✅ | 专项01 §14 |
| 5 | OpenAPI 3.0 文档 | ✅ | 专项01 §15 |
| 6 | 鉴权 / 权限 / 多租户规范 | ✅ | 专项01 §16 |
| 7 | 数据库 DDL + Migration | ✅ | 专项01 §20：真 SQL，dq_quality_run 等表逐字段 |
| 8 | Provider Adapter 接口规范 | ✅ | 专项01 §17：含 5 个 Adapter 各自差异化处理点 |
| 9 | Webhook / 回调 / 异步任务规范 | ✅ | 专项01 §18 |
| 10 | 错误码 / 重试 / 超时 / 降级 | ✅ | 专项01 §19 + 《Matbox_错误码规范》 |
| 11 | 测试集 / Golden Set / 验收脚本 | ✅ | 专项01 §23 |
| 12 | 前后端开发任务拆分 | ✅ | 专项01 §21：FE-01~FE-06 |
| 13 | 成本 / 性能 / 并发 / 安全要求 | ✅ | 专项01 §24 |
| 14 | 开发阶段 / 优先级 / 工作量估算 | ✅ | 专项01 §25 |
| 15 | 风险 / 阻塞项 / 备用方案 | ✅ | 专项01 §26 |
| 16 | 给未来 AI 开发者的完整执行说明 | ✅ | 专项01 §28 |
| 17 | 七类施工面逐条核实（RC5 硬条件） | ✅ | .docx §10：91 条一条不落 |
| 18 | 验收标准写成 Given-When-Then | ✅ | .docx §13：24 条 |
| 19 | 允许 / 禁止修改的具体路径（可机检） | ✅ | dq_protected_scope.yml。**跨模块全局高风险清单不在此**——QUEUE-F008 原文写明其路径待 Stage 10 填充，那份归 F-QUEUE-001 管 |
| 20 | 工具版本锁到完整 40 位哈希（第15节第6条） | ✅ | 2026-09-08 当天补齐。查出 Betterleaks/Trivy/OPA 只锁了 10 位短哈希，用 GitHub API 逐个展开写回 .docx 表2 与附录A，5 个工具现全部 40 位。**我原本误判这条『必须开工后才能补』，实际当场就做完了** |
| 21 | 本地环境怎么跑起来（几条命令、多久） | ✅ | 2026-09-09 由 CI 实测证实，不再是纸面规格。四步：① clone → ② 准备 PostgreSQL（CI 用 postgres:16 service；本地连接串走 MATBOX_DB_URL/USER/PASSWORD 环境变量）→ ③ `cd backend && mvn -B verify` → ④ 看到 `Successfully applied 1 migration` 与 `BUILD SUCCESS` 即环境就绪。**真实耗时：干净机器上 65 秒（含 JDK 安装与依赖下载），其中 Maven 本身 23.6 秒。**步骤写在 backend/README.md。 |
| 22 | Implementer 指派 | ✅ | 2026-09-09 用户指定：**opencode**。13 个功能的 Implementer 全部落实，RC5 第19条「所有施工面必须有人负责」满足。此前 UNASSIGNED_STAGE10 的状态解除。 |
| 23 | 项目骨架已初始化（可以 clone 下来就跑） | ✅ | 2026-09-09 建成并**真跑通**。分支 stage10-skeleton → CI 绿 → 已合入 main (a9abd652)。CI 日志实证：Flyway `Successfully applied 1 migration to schema "public", now at version v1`，`Tests run: 2, Failures: 0`，`BUILD SUCCESS`，Total time 23.6s。含 backend/pom.xml（Spring Boot 3.3.5 / Java 17）、modules/dev-quality、V1__dq_core_tables.sql（8 表 7 索引，专项01 §20 原文）、GitHub Actions（起真 postgres:16 跑迁移并回查建表结果）。**判定标准不是文件建好了，是 CI 那个绿。** |
| 24 | SCM 平台已定（F-DQ-011 依赖） | ✅ | 专项01 §25 WP-DQ-08 备注写着「依赖 SCM 平台最终选型（尚未确定 GitHub/GitLab）」，但 2026-09-09 核实：真实仓库 xyhzai/matbox 就在 GitHub 上，默认分支 main，已有 3 个分支。**事实上已定，文档那句话过期了**，F-DQ-011 按 GitHub 实现即可。 |

**结论以本表为准，不由我口头判断**：两项 ❌ 之中，「Implementer 指派」只有用户能定；「本地环境怎么跑起来」是真空白，且它不需要等真代码库——这是当前最该补的一项。

---

# 一、开发前 · Ready-to-Build Package（12 块）

> 这一段回答的不是「这个模块怎么跑」，而是「**要开发这个模块，资料必须齐全到什么程度**」。结构 = RC5 Work Package 模板 + 全球调研后确认要补强的 3 点（验收标准写成 Given-When-Then、存疑必须显式标注、安全敏感功能加 STRIDE 检查）。**这是唯一一个做完整的范例，其余约 200 个功能按同一份模板执行。**

## ① 身份与状态　<sub>✅ 已备齐</sub>

- **DocID**：MATBOX-DEVQUALITY-GATE-20260819-V1.1-RC
- **版本**：V1.1-RC · CURRENT Stage 9 内容级重验版 · 2026-08-19
- **状态**：STAGE9_CONTENT_AUDIT_PASS · READY_FOR_STAGE10_BINDING（Formal RC5 ParallelReadiness 尚未派生）
- **唯一执行标准**：00_当前唯一入口_CURRENT_Matbox_新专项开发_前期深调研到Codex验收_一比一执行标准_2026-08-18.docx
- **Stage 1-8**：PASS；Stage 8 无需虚假 POC，真实 Repo/CI 验证下沉为 Stage 10/11 Gate
- **Stage 10 前置**：必须绑定真实 Matbox Repo、Base Commit、WorkPackageID、Worktree/PR、Allowed/Protected Scope
- **不可降级原则**：需求/开发文档 → Implementer AI 开发 → 代码质检 Gate → 安全质检 Gate → 自动测试 Gate → 不合格自动返修 → 新 commit → 代码质检+安全质检+测试全部重跑 → 独立 Review → 受控合并 → 合并后代码/安全/测试/Contract/Regression 重验 → ReleaseArtifact/Baseline → 最终 Acceptance

> 出处：`.docx` 第1节 + 文档头表

## ② Scope In / Out　<sub>✅ 已备齐</sub>

### In Scope — 13 个子功能

| FeatureID | 名称 | 归属 | Stage9 Status | 主要依赖/Gate |
|---|---|---|---|---|
| F-DQ-001 | Dev Quality Run Orchestrator | Platform Core Quality / DevCodeQuality | READY_FOR_STAGE10_BINDING | G-STAGE10-REPO-001 |
| F-DQ-002 | Evidence Normalizer / Finding Mapper | Platform Core Quality / DevCodeQuality | READY_FOR_STAGE10_BINDING | G-STAGE10-REPO-001 |
| F-DQ-003 | SonarQube Code Quality Adapter | Platform Core Quality / DevCodeQuality | READY_FOR_STAGE10_BINDING | G-STAGE10-REPO-001 + license/component inventory at binding |
| F-DQ-004 | OpenGrep SAST Adapter + Matbox RulePack | Platform Core Quality / DevCodeQuality | READY_FOR_STAGE10_BINDING | G-STAGE10-REPO-001；真实 repo rule tuning required before hardening custom rules |
| F-DQ-005 | Betterleaks Secret Detection Adapter | Platform Core Quality / DevCodeQuality | READY_FOR_STAGE10_BINDING | G-STAGE10-REPO-001 |
| F-DQ-006 | Trivy Dependency / Container / IaC / SBOM Adapter | Platform Core Quality / DevCodeQuality | READY_FOR_STAGE10_BINDING | G-STAGE10-REPO-001 |
| F-DQ-007 | Matbox Architecture / Contract / Schema Guard | Platform Core Quality / DevCodeQuality | READY_FOR_STAGE10_BINDING | G-STAGE10-REPO-001 + G-STAGE10-CONFLICT-001 |
| F-DQ-008 | OPA GatePolicy Evaluator | Platform Core Quality / DevCodeQuality | READY_FOR_STAGE10_BINDING | G-STAGE10-REPO-001 |
| F-DQ-009 | Auto Repair / Revalidation Controller | Platform Core Quality / DevCodeQuality | READY_FOR_STAGE10_BINDING | G-STAGE10-REPO-001 |
| F-DQ-010 | Suppression / False Positive / Waiver Governance | Platform Core Quality / DevCodeQuality | READY_FOR_STAGE10_BINDING | G-STAGE10-REPO-001 |
| F-DQ-011 | SCM / PR / Merge / Release Quality Integration | Platform Core Quality / DevCodeQuality | READY_FOR_STAGE10_BINDING | G-STAGE10-REPO-001 |
| F-DQ-012 | AI Code Review Supplemental Evidence Adapter | Platform Core Quality / DevCodeQuality | OPTIONAL_B_PROVIDER · Stage10 可按成本/区域启用 | NONE for P0 core；启用时绑定 provider policy |
| F-DQ-013 | Dev Quality Ops / Tool Health / Regression Harness | Platform Core Quality / DevCodeQuality | READY_FOR_STAGE10_BINDING | G-STAGE10-REPO-001 |

> 出处：`.docx` 第9节 Feature Register（表14）

### 每个功能自己的 In / Out Scope

**F-DQ-001 · 质检调度器**（Dev Quality Run Orchestrator）

- 目标：把每个 WorkPackage 的开发节点转成可追溯 QualityRun，并派生 required checks；任何 Gate 结果绑定具体 Baseline/Commit/Scope。
- In Scope：trigger plan、check applicability、run lifecycle、retry budget、impact expansion、quality status check。
- Out of Scope：不拥有 WorkPackage/PR/Merge/Release truth；不自建 CI 平台。
- 入口/Route：Backend + /ops/dev-quality/runs

**F-DQ-002 · 证据归一化**（Evidence Normalizer / Finding Mapper）

- 目标：把各工具异构结果转换成统一 Finding/Error/Evidence 结构，同时保留不可变 raw report。
- In Scope：SARIF/JSON/JUnit/API response parser、fingerprint/dedupe、severity/category mapping、partial/error detection。
- Out of Scope：不把 provider-specific schema 写进 Domain；不删除原始证据。
- 入口/Route：Backend only；/ops/dev-quality/findings 通过共享 Evidence Query 展示

**F-DQ-003 · SonarQube 适配器**（SonarQube Code Quality Adapter）

- 目标：使用 SonarQube 作为持续代码质量/覆盖/复杂度/重复/Quality Gate 引擎，并正确处理异步 CE 任务。
- In Scope：analysis submit、CE task poll、Quality Gate fetch、new-code measures、raw evidence。
- Out of Scope：不让 Sonar Project/Issue/QualityGate 成为 Matbox SoT；不只看 scanner CLI exit。
- 入口/Route：Backend adapter；Sonar server internal

**F-DQ-004 · OpenGrep 适配器 + 自有规则包**（OpenGrep SAST Adapter + Matbox RulePack）

- 目标：提供 SAST、差异扫描和 Matbox 自定义静态/语义规则；把核心错误与 findings 分离。
- In Scope：rule pack、target scope、baseline/diff、JSON/SARIF、strict/error mapping、timeout。
- Out of Scope：不把 OpenGrep 当唯一 security truth；不在无证据时把所有 warning 设为 Hard Gate。
- 入口/Route：CI runner + rule repository

**F-DQ-005 · Betterleaks 密钥检测适配器**（Betterleaks Secret Detection Adapter）

- 目标：在 staged/diff/current tree/release scope 检测 secrets，并对 partial scan、validation、redaction 做安全边界。
- In Scope：git diff/staged/full scope、baseline ignore、JSON/SARIF/JUnit、redaction、confidence、scan error aggregation。
- Out of Scope：P0 默认不启用 live secret validation；不自动把发现的 secret 发送到第三方验证。
- 入口/Route：CI runner；pre-commit 可选加速

**F-DQ-006 · Trivy 供应链适配器**（Trivy Dependency / Container / IaC / SBOM Adapter）

- 目标：对 lockfile、filesystem、container image、IaC 和 ReleaseArtifact 生成漏洞/配置/SBOM Evidence。
- In Scope：fs/image/config scan、SBOM、vuln DB snapshot、exit mapping、EOL metadata、timeout/cache/db errors。
- Out of Scope：不把 Trivy DB 当 Matbox 业务 SoT；不因 scanner timeout 误判 clean。
- 入口/Route：CI runner + release pipeline

**F-DQ-007 · 架构/契约/Schema 守卫**（Matbox Architecture / Contract / Schema Guard）

- 目标：补足通用扫描器解决不了的 Matbox 语义规则：Protected Scope、Contract/Schema/Migration、Shared Capability、Provider/Secret 边界。
- In Scope：manifest/registry diff、API schema、DB migration ownership、queue/worker/shared config/lockfile、forbidden dependency rules。
- Out of Scope：不替代 RC5 派发前语义冲突检查；不重建业务 Domain SoT。
- 入口/Route：CI backend；rule/manifest repository

**F-DQ-008 · OPA 策略裁决**（OPA GatePolicy Evaluator）

- 目标：把完整 Evidence 转换成一致、可版本化、fail-closed 的 GateDecision；明确 DENY 与 POLICY_ERROR。
- In Scope：policy bundle、input schema、decision reason、strict builtin errors、policy version/hash。
- Out of Scope：OPA 不拥有 Finding/WorkPackage/Release facts；不以 OPA server 作为第二业务数据库。
- 入口/Route：CI/local evaluator；P0 优先 CLI/embedded ephemeral，不新增常驻业务服务

**F-DQ-009 · 自动返修与重验**（Auto Repair / Revalidation Controller）

- 目标：把可修问题自动交给 deterministic fixer 或 Implementer AI 返修，并保证每次修复都重新检查且不能自我批准。
- In Scope：repair eligibility、attempt policy、patch isolation、impact expansion、same+affected checks rerun、manual escalation。
- Out of Scope：不自动批准 waiver；不自动改高风险权限/迁移/加密/secret/production policy。
- 入口/Route：Backend + Implementer/agent integration

**F-DQ-010 · 误报与豁免治理**（Suppression / False Positive / Waiver Governance）

- 目标：允许证据化处理误报与非 P0 风险，但禁止“为了过 CI”静默忽略。
- In Scope：fingerprint suppression、owner/reviewer、scope、expiry、reason、evidence、revalidation。
- Out of Scope：不可降级 P0 不允许 accepted-risk bypass；AI/Implementer 不能单独批准。
- 入口/Route：/ops/dev-quality/suppressions

**F-DQ-011 · SCM/合并/发布集成**（SCM / PR / Merge / Release Quality Integration）

- 目标：把 DevQuality status check 嵌入 PR、merge queue、Integration Commit 和 ReleaseArtifact 验收，不复制 SCM/Release SoT。
- In Scope：status/check API、latest-main rebase trigger、merge blocking、post-merge run、release evidence link。
- Out of Scope：不自建 Git/PR/Merge Queue；不直接标最终 ACCEPTED。
- 入口/Route：SCM checks + release pipeline

**F-DQ-012 · AI 代码审查补充证据**（AI Code Review Supplemental Evidence Adapter）

- 目标：接 Qodo/CodeRabbit/其他 AI Review 作为补充 Review Evidence，发现跨文件逻辑/可维护性问题，但不作为唯一 Hard Gate。检查范围明确包含语义级代码重复检测（同功能不同写法的 Type-4 semantic clone，SonarQube 的文本级查重抱不住，2026-09-04补，架构原则第62条）。
- In Scope：provider adapter、comment/findings normalization、privacy/region policy、model/version evidence。
- Out of Scope：AI reviewer 不批准自己的代码；不因 AI 说“LGTM”绕过 deterministic/security tests。
- 入口/Route：PR review + /ops/dev-quality/findings

**F-DQ-013 · 工具健康与回归台**（Dev Quality Ops / Tool Health / Regression Harness）

- 目标：让 Quality Owner 能看到扫描器健康、运行趋势、失败分布、返修次数和 Gate Evidence，并用固定 challenge set 防工具升级回退。
2026-09-04实测发现（场景推演：生产环境 Gate 判定分布中 BLOCKED_MANUAL 占比突然从平时 5% 飙升到 40%，这件事从“仪表盘数字变了”到“真的有人去处理”这条链路推不下去）：本条目标原文只写了“让 Quality Owner 能看到”，动词是“看到”，不是“被通知”——与 F-QUEUE-001 QUEUE-F010、F-TASK-001 TASK-F006 最初犯的是同一类错，只是这次发生在 DQ 自己的运行指标层面。当前没有任何机制保证 BLOCKED_MANUAL 占比/scanner_error_rate 等异常会主动推送给任何人，完全依赖某个人自己想起来去看这个页面。
修正：本条关键运行指标（BLOCKED_MANUAL占比、scanner_error_rate、工具升级回归检出率下降等）异常时，必须调用 F-OBS-001 的 OBS-F004（高信号告警规则）生成可行动告警，不能只是在本看板上被动展示。
- In Scope：ops dashboard、tool health、metrics、Golden/Challenge set、upgrade canary、rollback evidence。
- Out of Scope：不重建 F-OBS dashboard/metrics backend；不把生产业务 Quality 与 DevCodeQuality 混为同一指标。
- 入口/Route：/ops/dev-quality；复用 /ops/audit /ops/evals

> 出处：`.docx` 第9节各 Feature 小节（表15–27）

## ③ Own / Reuse / Must Not Rebuild　<sub>✅ 已备齐</sub>

| 类型 | 对象/能力 | Owner / SoT | 规则 |
|---|---|---|---|
| OWN | DevQualityRun / ScannerRun / NormalizedFinding / GateDecision / RepairAttempt / SuppressionRef | Platform Core Quality · DevCodeQuality | 只拥有开发代码质量域状态；所有外部 scanner id 仅作 ref。 |
| OWN | DevQuality GatePolicy / RulePack binding / applicability matrix | Platform Core Quality | PolicyVersion 必须版本化并进入 Baseline/Evidence。 |
| REUSE | EvidenceBundle / trace / audit / eval result | F-OBS-001 | 所有 raw report、normalized finding、decision、repair evidence 写共享 Evidence；不自建第二 audit store。 |
| REUSE | ReleaseArtifact / Baseline / SBOM / provenance / deploy relation | F-RELEASE-001 | DevQuality 只引用；不得创建 CodeRelease/CodeBaseline 第二事实源。 |
| REUSE | FeatureID / WorkPackageID / Base Commit / Worktree / PR / Protected Scope / Merge | RC5 Canonical Registry | DevQualityRun 必须绑定具体 WorkPackage/Baseline；Base/Contract 变化触发 revalidation。 |
| REUSE | Tenant/RBAC/Secret/Provider/Cost/Infra/Queue/Object Storage | Platform Core shared owner | 通过现有 Contract 调用，不复制表、权限、secret store、worker 系统。 |
| MUST NOT REBUILD | SAST、Secrets、Vulnerability DB、通用 Code Quality、Policy Language | 外部 A 类工具 | Matbox 编排/标准化/裁决，不重写成熟扫描引擎。 |
| MUST NOT REBUILD | AI Review 平台与 SCM/Merge Queue | SCM/B 类 Provider | 只做 Adapter，禁止 Vendor schema 成为 Matbox SoT。 |

> 出处：`.docx` 第4节 Stage 7 架构冻结（表4）

## ④ 依赖 & 冻结 Contract　<sub>✅ 已备齐</sub>

六个 Own 数据模型的字段，**一旦施工开始不得随意改，改要走 Change Register**：

**QualityRun**

```
qualityRunId, triggerType, phase(CODE_QUALITY|SECURITY|AUTOMATED_TEST|RECHECK|POST_MERGE), FeatureID, WorkPackageID, BaselineID, baseCommit, headCommit/integrationCommit, ReleaseArtifactRef, requiredCheckSetVersion, policyVersion, parentQualityRunId, impactScope, status, createdAt/startedAt/finishedAt, triggeredBy, evidenceBundleRef
```

**ScannerRun**

```
scannerRunId, qualityRunId, adapterType, toolVersion, toolCommit/digest, configDigest, targetScope, status, exitCode, errorClass, startedAt, completedAt, rawEvidenceRef, normalizedFindingCount
```

**NormalizedFinding**

```
findingId, qualityRunId, sourceScanner, ruleId, category, severity, confidence, file/path/location, fingerprint, introducedByRef, isNew, remediationClass, suppressionRef?, evidenceRef
```

**GateDecision**

```
gateDecisionId, qualityRunId, policyVersion, decisionState, blockingFindingRefs[], incompleteCheckRefs[], reasonCodes[], evaluatorVersion, evidenceBundleRef, decidedAt, riskTier(LOW|STANDARD)?, reviewRoute(AUTO_APPROVED|INDEPENDENT_REVIEW), auditSampled(bool)?, auditOutcome(PENDING|CONFIRMED|REVERSED)?
```

**RepairAttempt**

```
repairAttemptId, parentQualityRunId, WorkPackageID, attemptNo, strategy(deterministic|codex|manual), sourceFindingRefs[], patchCommit/diffRef, impactedScopeRef, resultQualityRunId, evidenceRef
```

**SuppressionRef**

```
suppressionId, type(false_positive|accepted_risk), fingerprint/rule/scope, reason, owner, independentReviewer, createdAt, expiresAt, evidenceRef; non-degradable P0 仅允许“证据化 false positive”，不得 accepted-risk bypass
```

> 出处：`.docx` 第7节 核心数据 Contract（表7–12）

**上游依赖**：`F-OBS-001`（Evidence/Audit/Trace）、`F-RELEASE-001`（ReleaseArtifact/Baseline/SBOM）、`F-CRED-001`（凭据注入）、RC5 Canonical Registry（FeatureID/WorkPackageID/Base Commit/Worktree/PR）

## ⑤ 允许 / 禁止修改范围　<sub>✅ 已备齐</sub>

- 11.1 可自动返修（默认候选）
- 格式化、lint、确定性静态规则可安全机械修复。
- 明确的 import/unused/简单 null/typing 等低风险修复；必须由测试和重新扫描证明。
- 依赖 patch/minor 修复仅在 lockfile、build、unit/integration、安全扫描全部通过且不触发 Protected Scope 时可候选。
- Implementer AI 根据 Finding 生成 patch，但写入隔离 Worktree/Branch；每个 patch 都是新的 evidence-bearing attempt。
- 11.2 默认禁止全自动修改
- 认证、授权、Tenant/RBAC、Secret/KMS、加密算法与证书策略。
- 破坏性 DB Migration、核心 Schema/Contract、跨域 Shared Capability Owner。
- 生产网络/Egress、Release/branch protection、GatePolicy 本身。
- 删除/屏蔽安全 finding、扩大 suppression、修改测试去“适配”错误实现（2026-09-04明确：这条同样适用于 Implementer AI 的第一次实现，不只是 RepairController 的返修环节——WorkPackage 的验收标准必须在写代码前锁定，不允许同一次实现里边写代码边改验收测试去凑过关，架构原则第62条）。
- 任何由同一 Implementer 自己给自己最终 Source Review/Acceptance。
- RepairAttempt 最大次数不得在代码里写死；由 RepairPolicyVersion 配置。超过策略预算或连续两次未缩小 blocking set 时建议进入 BLOCKED_MANUAL，但最终数值在 Stage10 结合真实 CI/团队成本绑定。

> 出处：`.docx` 第11节 自动返修策略

- 1. P0 开源 Scanner 优先在 Matbox 控制的 runner/self-host 环境执行；源码不因方便默认发送到第三方云。
- 2. AI Review B 类 Provider 仅在 Tenant/Repo policy、地域、数据保留、成本与凭据条件满足时启用；默认不是硬依赖。
- 3. Betterleaks live validation 默认关闭；开启前必须经 Egress、Credential、Security policy，且 Evidence 不保存明文 secret。
- 4. Scanner/Parser 进程以最小权限运行；报告、规则、Git 内容均视为不可信输入，限制文件/报告大小、CPU、内存、时间、网络。
- 5. 所有 tokens/SCM credentials/Sonar tokens 走 F-CRED-001 credentialRef/runtime injection，禁止出现在 prompt、日志、DB 普通字段、Artifact。
- 6. 发往 B 类 Provider（如 F-DQ-012 用到的 AI Review 服务）的代码范围，必须受一份显式白名单约束，由负责人决定哪些仓库/路径允许发出，不得因追求判断准确率而无限制扩大发送范围（2026-09-04 补）。7. AI 员工执行过程安全防护（原挂账项，2026-09-05 补齐）：此前本条一直空着，是因为依赖的 Agent Runtime 模块只有技术选型报告、没有正式设计（第9节 F-DQ-009 对"Shared Agent Runtime"的依赖标注即此处）。Agent Runtime 正式开发文档已于 2026-09-05 建立（Matbox_AgentRuntime_正式开发文档_V1.0-RC.md），本条据此补齐：F-DQ-009 驱动的 Implementer AI repair job 必须遵守该文档 P0 冻结规则——工具/网页输出一律当作不可信内容处理，不因 repair job 更"内部"而放宽（架构原则第10条）；心跳必须从循环内部发出，连续漏2次触发 F-OBS-001 告警，repair job 卡死不允许无声挂起；心跳 payload 不得携带敏感数据（可能含被修复代码/工具调用参数）；委派权限不放大，repair job 不得在执行中临时提升自身权限范围；达到自我纠错硬上限必须转人工审批，不允许对同一个修复任务无限重试（防止 DQ 自己的自动修复被滥用成重试放大器）。

> 出处：`.docx` 第16节 安全与隐私边界

### ⑤附 · 机器可读版：[`dq_protected_scope.yml`](dq_protected_scope.yml)（2026-09-08 补）

上面这些是给人读的散文，**机器读不了**——而 RC5 的 PARALLEL_READY 硬条件要求「允许修改的代码/资产范围明确，禁止修改边界明确」，散文满足不了「明确」。已把它落成 glob 形式：

| 内容 | 条数 |
|---|---|
| 13 个功能各自的写入范围 | 13 |
| 依赖方向铁律（含 adapters 之间禁止互相依赖） | 3 |
| 只读的上游客户端（RC5/OBS/RELEASE/CRED/TENANT） | 5 |
| 冻结 Contract（改要走 Change Register） | 1 |
| Must Not Rebuild（命中即违规） | 3 类 |
| 自动返修默认禁改类别 | 6 类 |

**消费方**：F-DQ-007 施工时校验越界、QUEUE-F008 命中强制转人工、WorkPackage 派发时抽出该功能自己那一段随材料交给 Implementer AI。

⚠️ **两件老实话，写在 yml 的 `open:` 段里**：

1. **跨模块的「高风险公共文件」全局清单不在这个文件里**。QUEUE-F008 原文：「具体路径待 Stage10 真实 Repo 确定后填充」——那份归 F-QUEUE-001 维护，DQ 不替它做决定，只声明自己会命中的类别。
2. **上面所有路径仍是设计约定，还没跟真实 Repo 目录对照过**（Matbox 真代码库还没有第一行代码）。Stage 10 绑定 `G-STAGE10-REPO-001` 时必须逐条核对，对不上以真实目录为准并回填该文件。

## ⑥ Implementation Surface · 七类施工面（13 × 7 = 91 条，一条不落）　<sub>✅ 已备齐</sub>

> RC5 硬条件：**少一个施工面，不能派发 AI**。七类 = Frontend/UI、Backend/API/Service、Data/DB/Migration、Async/Runtime、External Integration/Provider、Infra/Config、Tests/Observability。

### F-DQ-001 · 质检调度器

<sub>Dev Quality Run Orchestrator</sub>


**Frontend/UI｜Applicable · Ops FE**
- Allowed / N/A：run/timeline/status/retry link
- Protected：不做第二 audit UI
- Contract / Dependency：Evidence query + QualityRun API
- Acceptance / Test / Evidence：同 WorkPackage 可看每次 run、状态原因与 evidence。

**Backend/API/Service｜Applicable · Platform Quality**
- Allowed / N/A：QualityRunService/CheckPlanResolver/GateTriggerService
- Protected：禁止自行改 RC5/Release 状态
- Contract / Dependency：WorkPackageRef + BaselineRef + CheckSetVersion
- Acceptance / Test / Evidence：trigger 幂等；同 event 重放不重复创建有效 run。
- Transaction / Idempotency / Retry / Recovery：QualityRun 创建以 WorkPackageID+BaselineID+trigger/phase 形成幂等键；先提交 run 记录再经既有 Outbox/Job 派发 Scanner；重复 trigger/callback 不产生第二有效 run；retry 有上限；进程崩溃后从持久化 run/scanner 状态恢复。

**Data/DB/Migration｜Applicable · Quality BE**
- Allowed / N/A：quality_run/scanner_run 逻辑记录或现有 shared schema extension
- Protected：不复制 Feature/PR/Baseline 主表
- Contract / Dependency：refs only + optimistic/version guard
- Acceptance / Test / Evidence：migration 可升级/回滚；所有 refs 可追溯。

**Async/Runtime｜Applicable · Shared Reliable Runtime**
- Allowed / N/A：并发派发 scanner jobs、timeout/retry/cancel
- Protected：不建第二 queue/worker system
- Contract / Dependency：Job/Outbox contract
- Acceptance / Test / Evidence：crash/retry 不丢 run；重复 callback 幂等。

**Provider/External｜Applicable · Adapter Registry**
- Allowed / N/A：选择 required adapters
- Protected：Provider ID 不成为 core status
- Contract / Dependency：ScannerAdapter interface
- Acceptance / Test / Evidence：missing adapter => INCOMPLETE，不可 PASS。

**Infra/Config｜Applicable · Platform Infra**
- Allowed / N/A：timeout/concurrency/feature flag/check-set config
- Protected：禁止 hardcode prod bypass
- Contract / Dependency：versioned CheckSet config
- Acceptance / Test / Evidence：配置变化触发 REVALIDATION_REQUIRED。

**Tests/Observability｜Applicable · QA**
- Allowed / N/A：orchestrator unit/integration/failure injection
- Protected：禁止 mock-only 冒充最终验收
- Contract / Dependency：Golden run fixtures
- Acceptance / Test / Evidence：重复事件、超时、缺 scanner、重启均可复现。

### F-DQ-002 · 证据归一化

<sub>Evidence Normalizer / Finding Mapper</sub>


**Frontend/UI｜N/A**
- Allowed / N/A：无独立 UI；由 F001/F012 消费
- Protected：N/A
- Contract / Dependency：N/A
- Acceptance / Test / Evidence：N/A

**Backend/API/Service｜Applicable · Quality BE**
- Allowed / N/A：NormalizerRegistry/Parser/Mapper
- Protected：不得吞 scanner error 或把 no-result 当 0 findings
- Contract / Dependency：NormalizedFinding v1 + ScannerError v1
- Acceptance / Test / Evidence：同一固定 fixture 可稳定映射；未知字段 forward-compatible。
- Transaction / Idempotency / Retry / Recovery：Parser/Mapper 本身不在业务 DB 事务内执行；rawEvidenceRef 成功取得后再通过 F-OBS 受控写入 normalized refs；以 raw report hash + tool/version + finding fingerprint 幂等；解析失败不重写为 0 findings，返回 SCANNER_ERROR/INCOMPLETE；无网络型 retry，修复 parser/config 后重跑。

**Data/DB/Migration｜Applicable · Obs/Quality**
- Allowed / N/A：只保存 normalized refs + rawEvidenceRef
- Protected：不保存明文 secret/source 全文到普通表
- Contract / Dependency：EvidenceRef contract
- Acceptance / Test / Evidence：敏感字段 redaction；Evidence hash 可复核。

**Async/Runtime｜Applicable · Shared Runtime**
- Allowed / N/A：异步大报告 parse 可 job 化
- Protected：不能影响原 scanner exit status
- Contract / Dependency：parse job contract
- Acceptance / Test / Evidence：parse fail => SCANNER_ERROR/INCOMPLETE。

**Provider/External｜Applicable · Scanner Adapters**
- Allowed / N/A：每 adapter 自带 parser version
- Protected：provider result 不能直接变 GateDecision
- Contract / Dependency：AdapterResult contract
- Acceptance / Test / Evidence：adapter contract tests 100% 固定 fixtures。

**Infra/Config｜Applicable · Security/Infra**
- Allowed / N/A：max report size、schema validation、redaction
- Protected：不信任 SARIF/JSON 内容
- Contract / Dependency：parser limits config
- Acceptance / Test / Evidence：malformed/oversized report 不造成 RCE/DoS，返回受控错误。

**Tests/Observability｜Applicable · QA/Security**
- Allowed / N/A：golden parser fixtures + malicious report corpus
- Protected：无
- Contract / Dependency：fixture bundle version
- Acceptance / Test / Evidence：同输入同映射；secret 0 泄漏到日志。
- Acceptance / Test / Evidence（2026-09-04补）：severity/category 映射应引入可达性（reachability）判断——该发现路径在当前代码里是否真的可能被触发——作为排序依据之一，不是所有静态命中同等优先级；真实案例显示这样能大幅减少无意义提醒。

### F-DQ-003 · SonarQube 适配器

<sub>SonarQube Code Quality Adapter</sub>


**Frontend/UI｜N/A**
- Allowed / N/A：使用共享 Ops UI
- Protected：N/A
- Contract / Dependency：N/A
- Acceptance / Test / Evidence：N/A

**Backend/API/Service｜Applicable · SonarAdapter Owner**
- Allowed / N/A：submit/poll CE/fetch gate/measures
- Protected：不得 CE pending 就 PASS
- Contract / Dependency：SonarAdapterResult
- Acceptance / Test / Evidence：CE success + gate OK 才可 tool-level pass；NO_VALUE 不等于 OK。
- Transaction / Idempotency / Retry / Recovery：不复制 Sonar 数据事务；analysis submit 以 QualityRun/commit/project ref 去重；CE task polling 为有界 retry/backoff；pending 可恢复继续轮询，CE fail/cancel/timeout 映射为非 PASS；服务重启后凭 ceTaskId 恢复。

**Data/DB/Migration｜N/A**
- Allowed / N/A：外部 Sonar 数据不复制为主表
- Protected：不得复制 Sonar project issue store
- Contract / Dependency：只存 refs/evidence
- Acceptance / Test / Evidence：N/A

**Async/Runtime｜Applicable · Shared Runtime**
- Allowed / N/A：CE polling/backoff/timeout
- Protected：禁止无限 poll/同步阻塞业务 thread
- Contract / Dependency：async polling contract
- Acceptance / Test / Evidence：CE fail/cancel/timeout 映射受控状态。

**Provider/External｜Applicable · Sonar external**
- Allowed / N/A：pinned server/analyzer versions
- Protected：不把独立 analyzer license 忽略
- Contract / Dependency：provider version snapshot
- Acceptance / Test / Evidence：tool/analyzer versions 进入 Evidence。

**Infra/Config｜Applicable · Infra**
- Allowed / N/A：self-host URL/token/TLS/project-key mapping
- Protected：token 不进日志
- Contract / Dependency：F-CRED credentialRef
- Acceptance / Test / Evidence：health check + version pin；升级可回滚。

**Tests/Observability｜Applicable · QA**
- Allowed / N/A：CE pending/fail/no-value/gate-error fixtures
- Protected：无
- Contract / Dependency：contract + integration test
- Acceptance / Test / Evidence：四类状态不可互相混淆。

### F-DQ-004 · OpenGrep 适配器 + 自有规则包

<sub>OpenGrep SAST Adapter + Matbox RulePack</sub>


**Frontend/UI｜N/A**
- Allowed / N/A：无独立 UI
- Protected：N/A
- Contract / Dependency：N/A
- Acceptance / Test / Evidence：N/A

**Backend/API/Service｜Applicable · OpenGrepAdapter**
- Allowed / N/A：scan changed/affected target + rule config
- Protected：不得把 fatal core error 映射 0 findings
- Contract / Dependency：OpenGrepAdapterResult
- Acceptance / Test / Evidence：core/parser/config error 与 finding blocking 分离。
- Transaction / Idempotency / Retry / Recovery：扫描过程无 Matbox 业务 DB 事务；结果写 Evidence 前绑定 commit+rulepack/config digest；同一 run 重放按 fingerprint 幂等去重；timeout/engine/config/baseline worktree error 受控重试或 BLOCKED；恢复必须重新确认 target/baseline 未漂移。

**Data/DB/Migration｜N/A**
- Allowed / N/A：规则版本引用；finding 落共享 evidence
- Protected：不复制源码
- Contract / Dependency：RulePackVersion + EvidenceRef
- Acceptance / Test / Evidence：N/A

**Async/Runtime｜Applicable · Runner**
- Allowed / N/A：parallel file scan/timeouts/diff worktree
- Protected：baseline/worktree failure不能 PASS
- Contract / Dependency：runner contract
- Acceptance / Test / Evidence：baseline checkout/normalize failure => SCANNER_ERROR。

**Provider/External｜Applicable · OpenGrep binary/rules**
- Allowed / N/A：pinned binary + internal rule pack
- Protected：外部 registry 网络依赖默认关闭/受控
- Contract / Dependency：ScannerArtifactRef
- Acceptance / Test / Evidence：离线/镜像可复现。

**Infra/Config｜Applicable · Security Infra**
- Allowed / N/A：container digest/cpu/mem/timeout
- Protected：禁止 unpinned latest
- Contract / Dependency：tool manifest
- Acceptance / Test / Evidence：checksum/digest + rollback。

**Tests/Observability｜Applicable · AppSec QA**
- Allowed / N/A：known-vuln fixtures + false-positive corpus + rule tests
- Protected：无
- Contract / Dependency：RuleTestSetVersion
- Acceptance / Test / Evidence：P0 rules 100% 检出固定 challenge；误报经 evidence 化 suppression。

### F-DQ-005 · Betterleaks 密钥检测适配器

<sub>Betterleaks Secret Detection Adapter</sub>


**Frontend/UI｜N/A**
- Allowed / N/A：无独立 UI
- Protected：N/A
- Contract / Dependency：N/A
- Acceptance / Test / Evidence：N/A

**Backend/API/Service｜Applicable · BetterleaksAdapter**
- Allowed / N/A：run git/directory scan，读取 finding + scan errors
- Protected：findings 存在时也不能忽略 scanErrs
- Contract / Dependency：SecretScanResult
- Acceptance / Test / Evidence：任一 required partition error => INCOMPLETE/SCANNER_ERROR。
- Transaction / Idempotency / Retry / Recovery：Secret 扫描不在业务 DB 事务中；Finding/Evidence 以 commit+rule+location/fingerprint 幂等；Git/source partial error 不因已有 findings 被吞掉；transient source error 可有限重试，重试后仍有缺口则 INCOMPLETE/SCANNER_ERROR；恢复不得泄露原 Secret。

**Data/DB/Migration｜N/A**
- Allowed / N/A：只存 redacted finding fingerprint/ref
- Protected：绝不保存可复用明文 secret
- Contract / Dependency：Evidence redaction contract
- Acceptance / Test / Evidence：Evidence/log/export 0 usable secret。

**Async/Runtime｜Applicable · Runner**
- Allowed / N/A：partition/full history 可异步；timeout
- Protected：不无限 full-history 每 PR
- Contract / Dependency：scan scope policy
- Acceptance / Test / Evidence：PR 快速范围 + release/full baseline 策略可配置。

**Provider/External｜Applicable · Betterleaks binary**
- Allowed / N/A：pinned MIT binary；validation disabled default
- Protected：禁止 uncontrolled external validation
- Contract / Dependency：adapter config
- Acceptance / Test / Evidence：validation 开启必须走 Egress/Secret policy 并单独审批。

**Infra/Config｜Applicable · Security Infra**
- Allowed / N/A：redact=100、timeout、max-target、network deny default
- Protected：禁止 debug 输出 secret
- Contract / Dependency：security runner profile
- Acceptance / Test / Evidence：runner 无公网也可完成 P0 static secret scan。

**Tests/Observability｜Applicable · Security QA**
- Allowed / N/A：fake-secret fixtures + partial-error + malformed git history
- Protected：无
- Contract / Dependency：SecretChallengeSet
- Acceptance / Test / Evidence：fake secret 必拦；partial scan 不能 PASS；日志 0 泄漏。

### F-DQ-006 · Trivy 供应链适配器

<sub>Trivy Dependency / Container / IaC / SBOM Adapter</sub>


**Frontend/UI｜N/A**
- Allowed / N/A：无独立 UI
- Protected：N/A
- Contract / Dependency：N/A
- Acceptance / Test / Evidence：N/A

**Backend/API/Service｜Applicable · TrivyAdapter**
- Allowed / N/A：scan target/report/exit/error mapping
- Protected：finding exit 与 engine error 不得混淆
- Contract / Dependency：TrivyAdapterResult
- Acceptance / Test / Evidence：timeout/cache lock/db download error => SCANNER_ERROR/TIMEOUT。
- Transaction / Idempotency / Retry / Recovery：Trivy 不拥有 Matbox 业务事务；DB/check bundle 更新与扫描分离；ReleaseArtifact+DB snapshot+config digest 确定幂等扫描身份；DB/cache lock、download/timeout 可有界 retry；重启后重新校验 DB snapshot 与 artifact digest，不沿用不完整扫描结果。

**Data/DB/Migration｜Applicable · Release/Obs**
- Allowed / N/A：SBOM/DB snapshot digest refs
- Protected：不复制 CVE DB
- Contract / Dependency：DependencySnapshotRef/SBOMRef
- Acceptance / Test / Evidence：ReleaseArtifact 能追到对应 SBOM+DB version。

**Async/Runtime｜Applicable · Runner**
- Allowed / N/A：DB update/cache lock/retry
- Protected：禁止 scanner DB 锁导致 silent pass
- Contract / Dependency：job + cache lock contract
- Acceptance / Test / Evidence：并发扫描、DB 更新冲突可恢复。

**Provider/External｜Applicable · Trivy artifact/DB**
- Allowed / N/A：pinned CLI/container + controlled DB source
- Protected：禁止 latest/action floating tag
- Contract / Dependency：ScannerArtifactRef + DBRef
- Acceptance / Test / Evidence：artifact digest、DB digest/version 均入 Evidence。

**Infra/Config｜Applicable · SupplyChain Infra**
- Allowed / N/A：tool mirror/signature/checksum/canary/rollback
- Protected：扫描器供应链自身不可信默认
- Contract / Dependency：tool update policy
- Acceptance / Test / Evidence：升级先 canary，旧版本可回滚。

**Tests/Observability｜Applicable · QA/Sec**
- Allowed / N/A：vulnerable lock/image/IaC fixtures + timeout/db failure
- Protected：无
- Contract / Dependency：SupplyChainChallengeSet
- Acceptance / Test / Evidence：已知 fixture 检出；engine failure 0 false pass。

### F-DQ-007 · 架构/契约/Schema 守卫

<sub>Matbox Architecture / Contract / Schema Guard</sub>


**Frontend/UI｜N/A**
- Allowed / N/A：无独立用户 UI
- Protected：N/A
- Contract / Dependency：N/A
- Acceptance / Test / Evidence：N/A

**Backend/API/Service｜Applicable · Architecture Guard**
- Allowed / N/A：read WorkPackage allowed/protected scope + repo diff；运行 rules/checkers
- Protected：不得自行修改 Registry 纠正冲突
- Contract / Dependency：ArchitectureCheckRequest/Result
- Acceptance / Test / Evidence：越 Protected Scope、重复 API/table/migration/worker/shared capability 必阻断。
- Transaction / Idempotency / Retry / Recovery：Guard 默认只读 Canonical Registry/Repo snapshot，不创建第二业务事务；规则结果以 commit+registry revision+rulepack digest 幂等；Registry/Schema/manifest 缺失或漂移直接 ERROR/REVALIDATION_REQUIRED；修复依赖后从冻结 snapshot 重跑，不用旧结果恢复。

**Data/DB/Migration｜Applicable · Architecture Owner**
- Allowed / N/A：只读取 Canonical Registry refs；必要 checker cache
- Protected：不能建立第二 registry/table owner
- Contract / Dependency：RegistryRef + schema digest
- Acceptance / Test / Evidence：schema/contract/migration digest 可复核。

**Async/Runtime｜Applicable · Shared Runtime**
- Allowed / N/A：大 schema graph diff 可异步
- Protected：不能和 RC5 冲突检查形成双写状态
- Contract / Dependency：read-only check job
- Acceptance / Test / Evidence：same inputs deterministic；错误 fail-closed。

**Provider/External｜Applicable · OpenGrep + native checkers**
- Allowed / N/A：静态规则可调用 OpenGrep；结构规则用 deterministic parser
- Protected：禁止 LLM 做 Hard Gate 唯一判定
- Contract / Dependency：CheckerAdapter contract
- Acceptance / Test / Evidence：确定性规则不依赖 AI。

**Infra/Config｜Applicable · Platform Config**
- Allowed / N/A：protected namespaces、owners、rule pack version
- Protected：禁止每 Feature 自定义绕过
- Contract / Dependency：ArchitecturePolicyVersion
- Acceptance / Test / Evidence：变化触发旧 PASS 失效。

**Tests/Observability｜Applicable · Architecture QA**
- Allowed / N/A：duplicate API/table/migration、direct Provider SDK、raw secret、forbidden queue fixtures
- Protected：无
- Contract / Dependency：ArchitectureChallengeSet
- Acceptance / Test / Evidence：全部固定冲突 100% 阻断。

### F-DQ-008 · OPA 策略裁决

<sub>OPA GatePolicy Evaluator</sub>


**Frontend/UI｜N/A**
- Allowed / N/A：共享 Ops UI 只展示 decision/reason
- Protected：N/A
- Contract / Dependency：N/A
- Acceptance / Test / Evidence：N/A

**Backend/API/Service｜Applicable · GatePolicy Owner**
- Allowed / N/A：build policy input → opa eval/check → normalized decision
- Protected：policy eval error 绝不能当 allow
- Contract / Dependency：GatePolicyInput/Decision v1
- Acceptance / Test / Evidence：deny=DENY；rego/eval error=POLICY_ERROR；undefined/empty 按 policy schema 明确。
- Transaction / Idempotency / Retry / Recovery：OPA evaluator 作为 stateless/ephemeral policy eval，不写第二业务数据库；decision 以 qualityRunId+policy bundle digest+input hash 幂等；仅进程级 transient invocation 可有限重试；Rego compile/eval/builtin error 一律 POLICY_ERROR，恢复必须加载同一或明确新版本 policy 后生成新 Decision。

**Data/DB/Migration｜N/A**
- Allowed / N/A：policy bundle 版本/Hash 存 Registry/Evidence ref
- Protected：不在 OPA 保存业务数据
- Contract / Dependency：PolicyVersionRef
- Acceptance / Test / Evidence：N/A

**Async/Runtime｜Applicable · Runner**
- Allowed / N/A：timeout/retry
- Protected：禁止 fail-open
- Contract / Dependency：evaluation job
- Acceptance / Test / Evidence：timeout => TIMEOUT；重试超限 => BLOCKED。

**Provider/External｜Applicable · OPA binary**
- Allowed / N/A：pinned Apache-2.0 artifact
- Protected：禁止 remote dynamic bundle 未验证直入
- Contract / Dependency：OPAArtifactRef
- Acceptance / Test / Evidence：binary/policy digest 进入 Baseline。

**Infra/Config｜Applicable · Security Infra**
- Allowed / N/A：no-network default、strict builtin errors、bundle signature/hash
- Protected：禁止 unversioned policy hot-edit
- Contract / Dependency：policy deployment config
- Acceptance / Test / Evidence：政策升级有 canary/regression/rollback。

**Tests/Observability｜Applicable · QA/Security**
- Allowed / N/A：allow/deny/undefined/compile-error/runtime-error fixtures
- Protected：无
- Contract / Dependency：PolicyChallengeSet
- Acceptance / Test / Evidence：每类状态精确映射，不出现 false PASS。
- 2026-09-04用户直接要求解决（存疑事项：DQ自己的判断逻辑没有独立核查）：查证确认OPA原生自带策略单元测试框架opa test——对Rego规则跑table-driven用例、有覆盖率报告、可直接接入CI，这是真实且成熟的现有能力，不是要新造一套。本节Tests/Observability行其实已经定义了PolicyChallengeSet这个Contract，但"Protected：无"，且没有任何规则要求它必须什么时候跑、谁来维护用例——名字定了，机制从来没被真正接上，这正是「存疑事项」指出的缺口所在。
- 修正三条，同时解决"有没有测"和用户真正在意的"是不是自己审自己"：①F-DQ-008的Rego策略每次改动，必须先经opa test跑通PolicyChallengeSet里的table-driven用例（已知diff→已知期望PASS/DENY/POLICY_ERROR），不过不能合并，本行"Protected"从"无"改为"策略变更未过PolicyChallengeSet禁止合并"；②PolicyChallengeSet新增/修改用例，不能由当次改动策略的同一个人/AI闭环拍板，至少要经一位非本次Implementer的人过一遍，防止自己出题自己判自己对；③复用第15节Technology Watch的季度节奏，PolicyChallengeSet不只在策略改动时跑，还要按同样节奏定期把当前生产策略重新跑一遍固定用例，抓的是"策略代码本身没变，但OPA运行时/依赖升级等外部因素导致判断结果悄悄漂移"这种情况——跟"运行中"R4刚发现的"缓慢漂移不是靠单点阈值能防住"是同一个道理，此处也是漂移场景，不是靠一次性测试能保证长期正确。

### F-DQ-009 · 自动返修与重验

<sub>Auto Repair / Revalidation Controller</sub>


**Frontend/UI｜Applicable · Ops FE**
- Allowed / N/A：显示 repair attempt、diff、blocked reason
- Protected：不提供“一键无审跳过 P0”
- Contract / Dependency：Repair API
- Acceptance / Test / Evidence：每次 attempt 可追到 source finding/patch/result run。

**Backend/API/Service｜Applicable · Repair Owner**
- Allowed / N/A：RepairPlanner/Controller；创建新 patch/commit/ref
- Protected：修复者不得写 final approval
- Contract / Dependency：RepairRequest/RepairResult
- Acceptance / Test / Evidence：repair 后必创建新 QualityRun；旧 PASS 不复用。
- Transaction / Idempotency / Retry / Recovery：每次 RepairAttempt 绑定 parentQualityRun+finding set+attemptNo，重复调度不得生成并行自相矛盾修复；patch 只在隔离 Worktree 应用，成功后形成新 commit；失败/冲突可回滚 worktree；retry 有上限，超限进入 BLOCKED_MANUAL；新 commit 必须从三个 Gate 第一关重跑。

**Data/DB/Migration｜Applicable · Quality BE**
- Allowed / N/A：repair attempt refs
- Protected：不复制 git patch/PR truth
- Contract / Dependency：patchCommit/diffRef
- Acceptance / Test / Evidence：attempt 序号幂等、不可覆盖历史。

**Async/Runtime｜Applicable · Shared Agent Runtime**
- Allowed / N/A：Implementer AI repair job、retry/timeout/cancel
- Protected：不建第二 AI task runtime
- Contract / Dependency：Task/WorkPackage ref
- Acceptance / Test / Evidence：agent crash 可恢复；重复提交不重复 patch。

**Provider/External｜Applicable · Implementer/SCM Adapter**
- Allowed / N/A：deterministic fixer or Implementer AI patch
- Protected：禁止 provider 直接 merge/main write
- Contract / Dependency：RepairProvider contract
- Acceptance / Test / Evidence：只在 isolated worktree/branch 写。

**Infra/Config｜Applicable · Quality Config**
- Allowed / N/A：repairable class、attempt limit、high-risk denylist
- Protected：禁止硬编码无限自动循环
- Contract / Dependency：RepairPolicyVersion
- Acceptance / Test / Evidence：attempt 超限 → BLOCKED_MANUAL。

**Tests/Observability｜Applicable · QA**
- Allowed / N/A：fix success/fix fails/fix introduces new issue/base changed fixtures
- Protected：无
- Contract / Dependency：RepairChallengeSet
- Acceptance / Test / Evidence：新问题能阻断；修复不越 Protected Scope。

### F-DQ-010 · 误报与豁免治理

<sub>Suppression / False Positive / Waiver Governance</sub>


**Frontend/UI｜Applicable · Ops FE**
- Allowed / N/A：request/review/expiry/list
- Protected：不显示敏感 secret payload
- Contract / Dependency：Suppression API
- Acceptance / Test / Evidence：权限、到期、scope 清楚。

**Backend/API/Service｜Applicable · Quality/Security**
- Allowed / N/A：validate suppression against finding fingerprint/scope
- Protected：禁止 wildcard 永久忽略
- Contract / Dependency：Suppression contract
- Acceptance / Test / Evidence：expired/stale suppression 自动失效并 revalidate。
- Transaction / Idempotency / Retry / Recovery：Suppression/Waiver 写入走现有受控事务/optimistic revision；fingerprint+scope+policyVersion 防重复；批准动作必须独立 Reviewer，重复请求幂等；到期/撤销立即失效并触发 revalidation；写入失败不得让 finding 静默消失。

**Data/DB/Migration｜Applicable · Quality BE**
- Allowed / N/A：suppression metadata + EvidenceRef
- Protected：不保存明文 secret
- Contract / Dependency：immutable audit refs
- Acceptance / Test / Evidence：修改产生新 version，不覆盖原决定。

**Async/Runtime｜Applicable · Shared Runtime**
- Allowed / N/A：expiry/revalidation events
- Protected：不建第二 scheduler
- Contract / Dependency：shared scheduled event
- Acceptance / Test / Evidence：到期后 affected Baseline 标 revalidation。

**Provider/External｜N/A**
- Allowed / N/A：无外部 provider
- Protected：N/A
- Contract / Dependency：N/A
- Acceptance / Test / Evidence：N/A

**Infra/Config｜Applicable · Security Config**
- Allowed / N/A：RBAC、max expiry、P0 policy
- Protected：禁止 config 允许 self-approval
- Contract / Dependency：SuppressionPolicy
- Acceptance / Test / Evidence：P0 false-positive 必须独立 Security Reviewer + evidence。

**Tests/Observability｜Applicable · QA/Security**
- Allowed / N/A：expired/wildcard/self-approval/P0 bypass tests
- Protected：无
- Contract / Dependency：SuppressionChallengeSet
- Acceptance / Test / Evidence：四类违规 100% 阻断。

### F-DQ-011 · SCM/合并/发布集成

<sub>SCM / PR / Merge / Release Quality Integration</sub>


**Frontend/UI｜Applicable · SCM/Ops FE**
- Allowed / N/A：check status/link to evidence
- Protected：不让 UI override hard gate
- Contract / Dependency：status check contract
- Acceptance / Test / Evidence：PR 明确显示 blocker reason。

**Backend/API/Service｜Applicable · Dev Platform**
- Allowed / N/A：publish check; merge hook; post-merge trigger
- Protected：禁止 direct main bypass
- Contract / Dependency：SCMCheck + ReleaseRef
- Acceptance / Test / Evidence：merge 前 latest base 有效；merge 后自动新 run。
- Transaction / Idempotency / Retry / Recovery：SCM status/check、post-merge trigger 以 repo+commit+check name/qualityRun 幂等；不自建 Merge/Release 事务；SCM/API transient error 可有界 retry，失败时 merge 保持 blocked；服务恢复后重新读取最新 main/head/merge commit，发现漂移即 REVALIDATION_REQUIRED。

**Data/DB/Migration｜N/A**
- Allowed / N/A：PR/merge/release truth 外部/共享 owner
- Protected：不复制 PR/master table
- Contract / Dependency：refs only
- Acceptance / Test / Evidence：N/A

**Async/Runtime｜Applicable · Shared Runtime**
- Allowed / N/A：webhook/event/outbox
- Protected：不丢 merge event
- Contract / Dependency：idempotent event contract
- Acceptance / Test / Evidence：duplicate webhook 不重复 acceptance；lost event 可 reconciliation。

**Provider/External｜Applicable · SCM Adapter**
- Allowed / N/A：GitHub/GitLab 等
- Protected：SCM schema 不进 core
- Contract / Dependency：ScmAdapter
- Acceptance / Test / Evidence：provider swap 不改 Gate domain。

**Infra/Config｜Applicable · Release Infra**
- Allowed / N/A：required checks/branch protection/merge queue
- Protected：禁止 admin bypass 无审计
- Contract / Dependency：branch policy + release config
- Acceptance / Test / Evidence：生产策略启动断言；bypass 有审计且 P0 禁止。

**Tests/Observability｜Applicable · QA/Release**
- Allowed / N/A：PR pass→base change→revalidate；merge→new baseline→rerun
- Protected：无
- Contract / Dependency：E2E release fixture
- Acceptance / Test / Evidence：分支 PASS 不可直接推出 ACCEPTED。

### F-DQ-012 · AI 代码审查补充证据

<sub>AI Code Review Supplemental Evidence Adapter</sub>


**Frontend/UI｜Applicable · SCM FE**
- Allowed / N/A：PR comments/summary/link
- Protected：不展示未脱敏 private source 到非授权用户
- Contract / Dependency：review evidence UI
- Acceptance / Test / Evidence：AI advice 与 hard finding 明确区分。

**Backend/API/Service｜Applicable · AIReviewAdapter**
- Allowed / N/A：submit diff/context/read result
- Protected：禁止直接 write/merge/waive
- Contract / Dependency：AIReviewRequest/Result
- Acceptance / Test / Evidence：provider error 不影响 deterministic gate 的真实性，但 required AI Review 配置时标 INCOMPLETE。
- Transaction / Idempotency / Retry / Recovery：AI Review Provider 调用不在 Matbox 业务事务内；request 绑定 repo/commit/diff/model/version 并使用 provider idempotency（如支持）或本地 request key 去重；限流/网络错误可有限重试；超时/裁剪/partial response 标 INCOMPLETE，不得用旧“LGTM”恢复为 PASS。

**Data/DB/Migration｜N/A**
- Allowed / N/A：只存 EvidenceRef/normalized finding
- Protected：provider conversation 不作 SoT
- Contract / Dependency：EvidenceRef
- Acceptance / Test / Evidence：N/A

**Async/Runtime｜Applicable · Shared Runtime**
- Allowed / N/A：rate limit/retry/cancel
- Protected：不无限重试产生费用
- Contract / Dependency：provider job contract
- Acceptance / Test / Evidence：429/timeout 映射清楚。

**Provider/External｜Applicable · B-class provider**
- Allowed / N/A：Qodo/CodeRabbit/etc
- Protected：provider-specific schema/secret 不泄露
- Contract / Dependency：AIReviewAdapter
- Acceptance / Test / Evidence：version/region/cost/retention 记录。

**Infra/Config｜Applicable · Provider/Security**
- Allowed / N/A：data minimization、region、retention、budget
- Protected：禁止默认把全私有仓库发云端
- Contract / Dependency：ProviderPolicy
- Acceptance / Test / Evidence：未批准 region/provider 时功能关闭。

**Tests/Observability｜Applicable · QA/Sec**
- Allowed / N/A：deterministic fail + AI pass；AI fail + deterministic pass；large diff truncation
- Protected：无
- Contract / Dependency：AIReviewChallengeSet
- Acceptance / Test / Evidence：AI 不得覆盖 Hard Gate；截断必须标 incomplete/context-limited。
- Allowed / N/A（2026-09-04补）：喂给该 Provider 的代码应通过检索方式给相关上下文（调用关系等），不整仓库塞入——真实数据显示上下文过大反而降低准确率；判断成本控制上采用"低成本模型先判，低置信度才升级"，不默认多模型并行（多模型并行真实成本会涨 4 倍以上）；发送范围受第16节 Provider 白名单约束。
- 2026-09-04用户直接要求解决（承接「并行调度」卡片卡点①的风险分级方案，用户追问"审核AI能不能多布置、专门AI审专门程序"）：查证2026年真实数据——AI代码审查在识别已知模式的安全漏洞、性能瓶颈、风格问题上已经比较可靠，但对需要理解业务背景、需要"全局"架构判断的问题仍明显弱于人类，现有实践一致认为AI审查会长期是"辅助"而非"替代"人工判断；同时查到真实的多专门AI并行审查案例——Cloudflare生产系统用最多7个专门AI（各自只看一个维度：安全/性能/架构合规）并行审查同一份diff，互不干扰，因为"不同专门AI的盲点不一样"，45秒内出结果。
- 修正：F-DQ-012从"单一AI review"扩展为"多个专门AI并行预审"，仅适用于GateDecision.reviewRoute=INDEPENDENT_REVIEW的WorkPackage（即未命中低风险自动批准、原本就要走独立Review的那部分，不改变谁需要人工审核这道闸门）——至少拆成安全向、架构合规向两个独立视角并行跑，各自只产出简短的重点标注（问题位置+一句话原因），不产出PASS/DENY结论，附加在diff上供Source Reviewer参考，人的最终判断权不变。模型/成本沿用本节已有规则（检索式喂上下文、低成本模型先判低置信度才升级、禁止默认多模型全量并行），不新定义第二套成本纪律。如实标注一个新的小尾巴：这层专门AI预审本身也是AI在做判断，谁来核查这几个专门AI标的重点标得准不准，现在没有答案——沿用本节已有的AIReviewChallengeSet思路即可覆盖，不需要另建机制，但具体节奏现在不定，等这层实际跑起来有真实数据后再补，不能没有数据先编。

### F-DQ-013 · 工具健康与回归台

<sub>Dev Quality Ops / Tool Health / Regression Harness</sub>


**Frontend/UI｜Applicable · Ops FE**
- Allowed / N/A：runs/findings/tool health/policy/version/repair trend
- Protected：不复制 audit store UI backend
- Contract / Dependency：Evidence query APIs
- Acceptance / Test / Evidence：从 FeatureID/WorkPackageID 一跳追到 QualityRun/Evidence。

**Backend/API/Service｜Applicable · Obs/Quality**
- Allowed / N/A：metrics aggregation/health/status
- Protected：不修改 scanner truth
- Contract / Dependency：metrics contract
- Acceptance / Test / Evidence：scanner unavailable/slow/error rate 可告警。
- Transaction / Idempotency / Retry / Recovery：Ops/metrics 不拥有 Quality/Evidence SoT；聚合写入以 event/run id 幂等，使用 F-OBS/outbox 既有可靠路径；metric/dashboard 失败不反向修改 GateDecision；challenge run 可重试但必须保留失败 Evidence；恢复后按 immutable Evidence 重建视图。

**Data/DB/Migration｜N/A**
- Allowed / N/A：metrics/evidence 存 F-OBS shared
- Protected：不建 local observability DB
- Contract / Dependency：Evidence/Metric refs
- Acceptance / Test / Evidence：N/A

**Async/Runtime｜Applicable · Shared Runtime**
- Allowed / N/A：scheduled canary/nightly regression
- Protected：不建第二 scheduler
- Contract / Dependency：scheduled task ref
- Acceptance / Test / Evidence：任务失败可见且不静默。

**Provider/External｜Applicable · All tool adapters**
- Allowed / N/A：version health probe
- Protected：不自动升级 latest
- Contract / Dependency：ToolManifest
- Acceptance / Test / Evidence：每次升级先固定 challenge set 再推广。

**Infra/Config｜Applicable · Infra/Obs**
- Allowed / N/A：alerts/retention/redaction/tool mirrors
- Protected：禁止公网 dashboard/secret logs
- Contract / Dependency：observability config
- Acceptance / Test / Evidence：P95、error、timeout、queue backlog 有阈值配置。

**Tests/Observability｜Applicable · QA**
- Allowed / N/A：20+ fixed failure tests + tool upgrade regression
- Protected：无
- Contract / Dependency：DevQualityChallengeSetVersion
- Acceptance / Test / Evidence：candidate tool/version 不低于 previous stable 的 hard-gate recall；失败可 rollback。

> 出处：`.docx` 第10节（原文逐条抽取，一字未改）

## ⑦ 验收标准 · Given-When-Then（24 条全部转完）　<sub>✅ 已备齐</sub>

| TestID | 场景 | PASS 标准 |
|---|---|---|
| DQ-T001 | 正常 WorkPackage：required checks 全完成且无 blocking finding | GateDecision=PASS；只允许进入下一开发关，不标 ACCEPTED。 |
| DQ-T002 | OpenGrep fatal config/core error | SCANNER_ERROR；即使 JSON/SARIF 存在也不 PASS。 |
| DQ-T003 | Betterleaks 部分文件扫描失败但仍产出 findings | INCOMPLETE/SCANNER_ERROR；补跑后才可决定。 |
| DQ-T004 | Trivy scan timeout / cache-db lock timeout | TIMEOUT/SCANNER_ERROR；可受控 retry，不得 clean pass。 |
| DQ-T005 | OPA policy result deny | DENY，ReasonCode 可追溯。 |
| DQ-T006 | OPA Rego compile/eval error | POLICY_ERROR，fail-closed。 |
| DQ-T007 | Sonar CE pending/fail/cancel/no-value | 不得 PASS；分别映射 RUNNING/SCANNER_ERROR/INCOMPLETE。 |
| DQ-T008 | Fake secret fixture | DENY；Evidence 已 redacted，日志无可用 secret。 |
| DQ-T009 | Fixable lint/static finding → Implementer AI repair | 生成新 RepairAttempt+patch；重跑后才能 PASS。 |
| DQ-T010 | 修复 A 时引入新 vulnerable dependency | Trivy/affected checks 发现并 DENY。 |
| DQ-T011 | WorkPackage Base Commit 变化 | 旧 Quality PASS 失效，REVALIDATION_REQUIRED。 |
| DQ-T012 | PR PASS 后 merge 形成 Integration Commit | 强制创建 post-merge QualityRun；旧 PR PASS 不可直接继承。 |
| DQ-T013 | Expired suppression | suppression 失效；finding 重新参与 Gate。 |
| DQ-T014 | Scanner binary missing/adapter unavailable | INCOMPLETE/SCANNER_ERROR；fail-closed。 |
| DQ-T015 | AI reviewer LGTM，但 deterministic SAST/secret/test fail | 最终 Gate 仍 DENY。 |
| DQ-T016 | P0 high-risk code由 Implementer自己 Review | ACCEPTANCE_PENDING/BLOCKED；必须独立 Reviewer。 |
| DQ-T017 | Malformed/oversized SARIF/JSON | parser 安全失败；不 crash 整体平台，不 false pass。 |
| DQ-T018 | Evidence export/logging | 0 usable secret；敏感源码按 RBAC/redaction。 |
| DQ-T019 | ReleaseArtifact build | 可追到 DependencySnapshot/SBOM/tool versions/config/policy + merged commit。 |
| DQ-T020 | Tool/RulePack/Policy 升级 | 固定 Challenge Set 回归；候选回退则不升级，Previous Stable 可恢复。 |
| DQ-T021 | 代码质检 Gate 命中 blocking defect | CODE_QUALITY_GATE=DENY；不得跳过为“总体 PASS”；返修后生成新 commit，并从代码质检重新开始。 |
| DQ-T022 | 代码质检 PASS，但安全质检发现 Secret/SAST/SCA/P0 架构风险 | SECURITY_GATE=DENY；不得因为前一 Gate PASS 或后续测试通过而合并；返修后代码/安全/测试全部重跑。 |
| DQ-T023 | 代码与安全均 PASS，但 unit/contract/integration/regression 任一 required test FAIL | AUTOMATED_TEST_GATE=DENY；返修后从 CODE_QUALITY_GATE 起重新执行三 Gate，不能只重跑失败测试。 |
| DQ-T024 | PR 三 Gate 全 PASS 后完成受控 Merge | 必须基于新 Integration Commit/ReleaseArtifact/Baseline 创建 POST_MERGE QualityRun，并重跑受影响代码质检、安全质检、自动测试及 Contract/Integration/Regression；旧 PR PASS 不可直接继承。 |

> 出处：`.docx` 第13节 Acceptance Test Matrix（表28）

## ⑧ 存疑 / 待确认事项 —— 不脑补，显式标注　<sub>✅ 已备齐</sub>

> **这一块存在本身就是标准的一部分**：全球调研后确认的三项补强之一就是「存疑必须显式标注，而不是让 AI 自己脑补」。

### 等真实 Repo 才能填的（现在写就是编造）

**7 道 Stage 10/11 Gate 尚未关闭**（2026-09-08 更正：此前写 6 道，漏列了 `G-STAGE10-CONFLICT-001`）：

- `G-STAGE10-REPO-001`｜绑定真实 repository、target branch、Base Commit、WorkPackageID、Worktree/PR；无真实值不得声称该 WorkPackage 的质检已跑通。
- `G-STAGE10-CONFLICT-001`｜扫描真实 Router/Service/DB/Migration/Queue/Worker/Shared Config/lockfile，确认物理代码中不存在重复 API/表/Migration/Worker/Queue/lockfile 冲突；Stage 9 只完成设计/文档层去重，物理层必须在此关闭。
- `G-DQ-ST10-CI-002`｜在真实 CI runner 验证 5 个 A 类 pinned artifact、network/secret/permissions、cache/timeout；记录真实运行时间与资源。
- `G-DQ-ST10-RULE-003`｜用当前 Matbox 真实 code diff + challenge fixtures 校准 OpenGrep/Architecture RulePack；P0 rule 必须先有 fixed fixture，再成为 Hard Gate。
- `G-DQ-ST10-EVIDENCE-004`｜验证 Raw Report → NormalizedFinding → GateDecision → EvidenceBundle → WorkPackage/PR 的可追溯链。
- `G-DQ-ST10-REPAIR-005`｜真实演练“不合格 → Implementer AI 修 → 新 commit → same+affected recheck”；不得仅文档描述。
- `G-DQ-ST11-MERGE-006`｜真实 merge 后建立 Integration Commit/ReleaseArtifact/Baseline，并重跑 affected quality/security/contract/regression。

> 出处：`.docx` 第14节

**只有第 1 道是开工那一刻的门，其余 6 道都要先有代码才关得掉**（CI-002 要真跑一次、RULE-003 要真实 diff、REPAIR-005 要真演练返修、ST11-MERGE-006 干脆是合并之后）。文档第14节原话：「平台没有开发完不是阻塞。本 Gate 在每个真正准备施工的 Feature/WorkPackage 上**按需绑定**真实 Repo/Base Commit。」——**所以不存在「跑完这几道再开发」，动手那一刻这几道就开始跑了。**

### 跟真实 Repo 无关、但现在也答不了的

- **RC5 正式 ParallelReadiness 尚未派生**。13 个功能到底是 `PARALLEL_READY` 还是 `BLOCKED_BY_DEPENDENCY`，目前没有正式结论。RC5 第22节要求它必须由 Base Commit 有效性等规则化派生，**禁止人工随意填写**；开发总账现值为「不适用（Stage 10 未启动，禁止提前派生）」
- **13 个功能的 Implementer 全部 `UNASSIGNED_STAGE10`**（Feature Owner / Source Reviewer / Acceptance Owner 已填好，唯独干活的人空着）。RC5 第19条硬条件：所有适用施工面必须全部有人负责，少一个不能派发 AI
- **「环境多快能跑起来」这一维度完全空白**。上面 12 块回答的都是「要做什么、边界在哪」，没有一块回答「AI/人接到任务后，敲几个命令、多久能有个能跑的开发环境」
- **顶部准备度摘要没有强制力**。标 🟡 的项没有任何机制拦着不让派发；查证的全球真实做法是靠机器人卡住「资料没填满不许进下一步」，这要等 Stage 10 真 CI 才能装
- **DQ 自己写的判断逻辑，没有独立于自己的核查**。5 个外部工具互相独立，但 DQ 自己的调度逻辑和 OPA 里 Matbox 自写的策略是「自己判自己」。2026-09-04 已给出方案并落地为 F-DQ-008 新规则（`opa test` + PolicyChallengeSet + 用例不得由改策略的同一人闭环拍板 + 季度重跑）

> 出处：`.docx` 第14/20节 + 样板「存疑事项」卡片 + 架构原则

## ⑨ 安全威胁检查（STRIDE-lite）　<sub>✅ 已备齐</sub>

> DQ 处理 Secret 扫描与质检判定，属安全敏感功能。下面是把文档已有规则按 STRIDE 六类重新归类，**不是新发明**。

- 1. P0 开源 Scanner 优先在 Matbox 控制的 runner/self-host 环境执行；源码不因方便默认发送到第三方云。
- 2. AI Review B 类 Provider 仅在 Tenant/Repo policy、地域、数据保留、成本与凭据条件满足时启用；默认不是硬依赖。
- 3. Betterleaks live validation 默认关闭；开启前必须经 Egress、Credential、Security policy，且 Evidence 不保存明文 secret。
- 4. Scanner/Parser 进程以最小权限运行；报告、规则、Git 内容均视为不可信输入，限制文件/报告大小、CPU、内存、时间、网络。
- 5. 所有 tokens/SCM credentials/Sonar tokens 走 F-CRED-001 credentialRef/runtime injection，禁止出现在 prompt、日志、DB 普通字段、Artifact。
- 6. 发往 B 类 Provider（如 F-DQ-012 用到的 AI Review 服务）的代码范围，必须受一份显式白名单约束，由负责人决定哪些仓库/路径允许发出，不得因追求判断准确率而无限制扩大发送范围（2026-09-04 补）。7. AI 员工执行过程安全防护（原挂账项，2026-09-05 补齐）：此前本条一直空着，是因为依赖的 Agent Runtime 模块只有技术选型报告、没有正式设计（第9节 F-DQ-009 对"Shared Agent Runtime"的依赖标注即此处）。Agent Runtime 正式开发文档已于 2026-09-05 建立（Matbox_AgentRuntime_正式开发文档_V1.0-RC.md），本条据此补齐：F-DQ-009 驱动的 Implementer AI repair job 必须遵守该文档 P0 冻结规则——工具/网页输出一律当作不可信内容处理，不因 repair job 更"内部"而放宽（架构原则第10条）；心跳必须从循环内部发出，连续漏2次触发 F-OBS-001 告警，repair job 卡死不允许无声挂起；心跳 payload 不得携带敏感数据（可能含被修复代码/工具调用参数）；委派权限不放大，repair job 不得在执行中临时提升自身权限范围；达到自我纠错硬上限必须转人工审批，不允许对同一个修复任务无限重试（防止 DQ 自己的自动修复被滥用成重试放大器）。

**真事，不是假设**：2026-03-19，DQ 选用的 Trivy 官方发布的 v0.69.4 被供应链攻击，恶意代码塞进正式发布包，连配套的 trivy-action / setup-trivy 两个 GitHub 脚本一起中招，能偷 CI 密钥、埋后门、蠕虫式扩散。**这不是「万一」，是 DQ 选用的 5 个工具之一真的出过事。**对应防护：第15节第6条要求锁到完整 40 位提交哈希，不能只锁版本标签。

> 出处：`.docx` 第15/16节 + 样板卡片⑨

## ⑩ 责任角色　<sub>✅ 已备齐</sub>

| FeatureID | Feature Owner | Implementer | Source Reviewer | Acceptance Owner | Release Owner |
|---|---|---|---|---|---|
| F-DQ-001 | Platform Quality Owner | UNASSIGNED_STAGE10 | Source/Security Owner | QA Owner | Release Owner |
| F-DQ-002 | Platform Quality Owner | UNASSIGNED_STAGE10 | Source/Security Owner | QA Owner |  |
| F-DQ-003 | Platform Quality Owner | UNASSIGNED_STAGE10 | Source/Security Owner | QA Owner |  |
| F-DQ-004 | AppSec/Quality Owner | UNASSIGNED_STAGE10 | Security Reviewer | QA Owner |  |
| F-DQ-005 | Security Owner | UNASSIGNED_STAGE10 | Security Reviewer | QA Owner |  |
| F-DQ-006 | Supply Chain Security Owner | UNASSIGNED_STAGE10 | Security Reviewer | QA Owner |  |
| F-DQ-007 | Platform Architecture Owner | UNASSIGNED_STAGE10 | Architecture + Security Reviewer | QA Owner |  |
| F-DQ-008 | Platform Quality/Security Owner | UNASSIGNED_STAGE10 | Security Reviewer | QA Owner |  |
| F-DQ-009 | Dev Productivity/Quality Owner | UNASSIGNED_STAGE10 | independent Source/Security Reviewer | QA Owner |  |
| F-DQ-010 | Security/Quality Owner | UNASSIGNED_STAGE10 | independent reviewer | QA Owner |  |
| F-DQ-011 | Dev Platform + Release Owner | UNASSIGNED_STAGE10 | Source/Security Owner | QA/Release Owner |  |
| F-DQ-012 | Source Review Owner | UNASSIGNED_STAGE10 | independent human/AI policy | QA Owner |  |
| F-DQ-013 | Quality/Observability Owner | UNASSIGNED_STAGE10 | Source/Security Owner | QA Owner |  |

> 出处：`.docx` 第9节各 Feature 的 Owner/Review 行（表15–27）

⚠️ **Implementer 一栏全部 `UNASSIGNED_STAGE10`** —— 这是 RC5 PARALLEL_READY 的硬条件缺口，不是漏填。按架构原则第58条，派工方式已定为**自认领式**（可派发的 WorkPackage 进共享清单，Implementer AI 主动认领），对应能力是 `F-QUEUE-001` 的 QUEUE-F005~F010，不由 DQ 自建。

## ⑪ 并行调度　<sub>✅ 已备齐</sub>

| 建议 WP | Feature | 目标 |
|---|---|---|
| WP-DQ-01 | F001 + F002 | 先建立 QualityRun/ScannerRun/NormalizedFinding/GateDecision contract 与 F-OBS evidence 接口。 |
| WP-DQ-02 | F003 | Sonar async CE adapter。 |
| WP-DQ-03 | F004 + F007 | OpenGrep adapter + Matbox architecture/contract guard。 |
| WP-DQ-04 | F005 | Betterleaks secret adapter + redaction/partial error。 |
| WP-DQ-05 | F006 | Trivy supply-chain/SBOM adapter。 |
| WP-DQ-06 | F008 | OPA policy evaluator + fail-closed decision。 |
| WP-DQ-07 | F009 + F010 | repair/revalidation + suppression governance。 |
| WP-DQ-08 | F011 | SCM/merge/release integration。 |
| WP-DQ-09 | F012 | AI Review optional adapter。 |
| WP-DQ-10 | F013 | Ops/tool health/challenge regression。 |

> 出处：`.docx` 第18节 Implementer 施工顺序（表30）

**并行数量不设固定上限**（RC5 第15条）：真正可调度的 AI 数量 = 当前 `PARALLEL_READY` 且写入资源互不冲突的活动 WorkPackage 数量，同时受 Reviewer/Test/基础设施容量约束。

**支撑能力不在 DQ**：自认领机制、worktree 隔离派工、运行时资源队列、高风险公共文件强制转人工、派发附带架构决定摘要、施工期间实时动作拦截——全部是 `F-QUEUE-001` 的 QUEUE-F005~F010（架构原则第58/62条确认「不新建调度器模块，并入已有的 F-QUEUE-001」）。

## ⑫ 验收交付清单 —— 通过时必须交出什么　<sub>✅ 已备齐</sub>

RC5 14 项字段之一，2026-09-03 补齐（此前漏整理，材料本来就在文档里）：

- **代码质检结果**：QualityRun + 各 ScannerRun 记录（第7节数据模型）
- **安全质检结果**：同上，含 Secret / 依赖 / 容器 / IaC / SBOM 证据
- **自动测试结果**：对应的 QualityRun + ScannerRun 记录
- **Evidence 包**：NormalizedFinding / GateDecision，绑定 EvidenceBundleID，**不可变**
- **返修记录（如涉及）**：RepairAttempt，绑定父 QualityRun + 第几次尝试
- **最终验收结论**：AcceptanceRunID（Evidence 类型 `MANUAL_ACCEPTANCE`），由独立 Acceptance Owner 出具

> 出处：样板卡片⑫（材料来自 `.docx` 第7/12/13节）

---

# 二、开发中 · 三道 Gate 不可跳过

## 2.1 不可降级的闭环

2026-09-04补：上面这张图画的是原始默认路径——"三个Gate全PASS→必经独立Review"。审核产能瓶颈问题解决后（详见架构原则第68条），这条路径已经分叉：同时满足风险分级四条硬标准的WorkPackage，会跳过独立Review直接进Controlled Merge，改由抽样机制事后复核；不满足任一条的，仍走图中这条路径不变。这张图暂不重画，分叉判定字段（riskTier/reviewRoute）的权威定义见第7节GateDecision。

> 出处：`.docx` 第5节 整体开发闭环与触发点

## 2.2 统一状态机（10 种状态，Fail-Closed）

> ⚠️ **这张表是跨模块契约**：`F-VIZ-001~007`（代码问题定位与人工修复台）的界面必须完整支持这 10 种状态，不得自行裁剪成更短的枚举、也不得把 `SCANNER_ERROR` 与 `POLICY_ERROR` 合并成一个笼统的 ERROR（两者处置方式完全不同，DQ-T007 明确要求不能混为一谈）。

| 状态 | 含义 | 是否允许进入下一关 | 必须动作 |
|---|---|---|---|
| CREATED | QualityRun 已创建，尚未开始 | 否 | 校验 WorkPackage/Baseline/PolicyVersion/required scanners。 |
| RUNNING | 必需 Scanner/Test 正在执行 | 否 | 持续记录 ScannerRun/Evidence。 |
| PASS | 所有 required evidence 完整且 GatePolicy 允许 | 是，仅进入下一开发关；不等于 ACCEPTED | 冻结 GateDecision + EvidenceRef。 |
| DENY | Findings/Tests/Policy 触发阻断 | 否 | 生成 RepairPlan 或转人工。（2026-09-04实测补：判断依据是第11.2节已定义的默认禁止全自动修改类别——命中则直接转人工（进入 BLOCKED_MANUAL，已接通 F-APPROVAL-001 通知），否则生成 RepairPlan 走自动返修。此前这两处内容存在但没有互相引用。） |
| INCOMPLETE | 扫描只完成部分范围或 required evidence 缺失 | 否 | 补跑/重跑；禁止把已有结果当全量 PASS。 |
| SCANNER_ERROR | Scanner/config/parser/runtime 错误 | 否 | 按错误分类 Retry；超限后 BLOCKED。 |
| POLICY_ERROR | OPA/Rego/Policy bundle 编译或 eval 错误 | 否 | Security/Quality Owner 修复 Policy；禁止降级绕过。 |
| TIMEOUT | Scanner/Test/CE 等超时 | 否 | 受控重试或拆 scope；仍超时则 BLOCKED。 |
| REVALIDATION_REQUIRED | Base Commit/Contract/Schema/lockfile/config/policy/evidence 变化使旧 PASS 失效 | 否 | 对影响面生成新 QualityRun。 |
| BLOCKED_MANUAL | 重复返修失败、冲突或高风险需人工决定 | 否 | Source Reviewer / Acceptance Owner 处理。 |

> 出处：`.docx` 第6节 统一状态机与 Fail-Closed 规则（表6）

## 2.3 检查适用性矩阵

| 变化类型 | Sonar | OpenGrep | Betterleaks | Trivy | Contract/Schema Guard | OPA | Tests |
|---|---|---|---|---|---|---|---|
| 业务源码 | Required | Required | Required | Lockfile/dep 变更时 | Applicable | Required final | Unit/contract + impacted integration |
| API/Contract/Schema | Applicable | Required | Required | Applicable | Required | Required final | Contract/schema/regression |
| DB/Migration | Applicable | Required rules | Required | Dependency/IaC applicable | Required | Required final | Migration/rollback/idempotency |
| Docker/IaC/CI | N/A或Applicable | Applicable | Required | Required | Config/CI guard | Required final | Build/deploy/security |
| Dependency/Lockfile | Applicable | Applicable | Required | Required | Lockfile ownership guard | Required final | Build + smoke + regression |
| Docs/Prompt-only | N/A（写原因） | 按文件类型 | Required 防 secret | N/A | 版本/Hash guard | Required final | Doc/hash checks |
| Post-merge Integration | Required affected scope | Required | Required | Required if artifact/deps | Required | Required final | Affected integration/regression |
| ReleaseArtifact | Required baseline policy | Required release scope | Required | Required + SBOM/image | Required | Required final | Release smoke/regression |

> 出处：`.docx` 第8节 检查适用性矩阵（表13）

## 2.4 P0 GatePolicy 冻结规则

- 1. Required scanner/test 缺失、部分完成、超时、引擎错误、报告解析错误：一律不可 PASS。
- 2. Confirmed/高置信 Secret finding：DENY；若可能为真实凭证，修复必须包含删除/轮换/审计方案，不能只删字符串。
- 3. Sonar Quality Gate ERROR：DENY；NO_VALUE/CE pending/fail 不得当 OK。
- 4. OpenGrep/Matbox Architecture Guard 命中不可降级 P0（权限、Secret、跨租户、Protected SoT、重复 Contract/Schema/Migration/Queue/Shared Capability 等）：DENY。
- 5. Trivy 新增的 blocking vulnerability/misconfiguration 由版本化策略决定；scanner DB/timeout/error 本身先阻断为 SCANNER_ERROR/TIMEOUT。
- 6. OPA DENY：DENY；OPA compile/eval error：POLICY_ERROR；都不得 fail-open。
- 7. Automated Test/Contract/Migration/Security/Regression 任一 required test fail：DENY。
- 8. Base Commit、Contract/Schema、lockfile、tool/config/policy version、ReleaseArtifact 任一关键输入变化：旧 PASS 失效 → REVALIDATION_REQUIRED。
- 9. AI Review PASS 不能覆盖 deterministic/security failure；AI Review finding 作为 supplemental Evidence。

> 出处：`.docx` 第12节

## 2.5 工具 / 规则 / 策略的升级与回滚

- 1. 所有 Scanner/RulePack/Policy 必须固定 version/commit/container digest/config digest；禁止 `latest` 进入 production gate。
- 2. Candidate 版本先跑固定 Challenge Set，再在非生产/受控 PR 做 canary；只有 Hard Gate recall 不回退、误报可接受、性能未越预算才升级。
- 3. Previous Stable 必须可立即回滚；升级失败不得为了“保持最新”强制切换。
- 4. Vulnerability DB / Rule registry 也属于 Baseline 输入；关键 DB/rule 变化使旧 Quality PASS 不可无条件复用。
- 5. 工具供应链本身按不可信输入处理：镜像/二进制校验、最小权限、network deny/default、无生产 Secret。
- 6. 真实案例（2026-09-04补）：2026年3月19日，DQ选用的Trivy官方发布的v0.69.4版本被供应链攻击——恶意代码被塞进正式发布包，连配套的trivy-action、setup-trivy两个GitHub Action也一起中招，可窃取CI密钥、植入后门、像蠕虫一样扩散。本节第1条"锁定version/commit/digest"要求必须精确到完整40位提交哈希，不能只锁版本标签（如@v0.28.0这种可变引用）——这是那次真实攻击得手的关键漏洞点。
- 7. 技术盯梢（Technology Watch）节奏分三层，不是同一个节奏（2026-09-04补，查证5轮真实做法后定）：①安全漏洞类——不定时，官方漏洞库一有新记录立刻响应，不等下次例行检查；②版本老化/停止维护类——定时查，常见每天或每周；③"是否有更好的替代品出现"这类战略判断——季度评审一次（不是传统的半年一次，2026年AI工具迭代速度更快，真实做法是"现在最好的工具3个月后可能被超越"）。

> 出处：`.docx` 第15节

## 2.6 三条跨模块规则（不在本文档，只引用）

2026-09-04 讨论产生、当天即搬迁到架构设计原则的三条——因为它们**不只管 DQ 一家，所有模块开发时都要用**：

- **调度器要提前建好待命**，不等真要用了才现搭 → 架构原则第58条（落地为 `F-QUEUE-001` 的 QUEUE-F005~F010）
- **AI 该不该停下来问人，按「动作后果」四级分类**，不按 AI 自报的把握度 → 架构原则第59条
- **开发中的审核 = 实时拦截 + 事后抽查两层并行** → 架构原则第60/62条

> 出处：架构原则第58/59/60/62条（搬迁记录见 git `118f3ad`）

---

# 三、运行中 · 上线之后健不健康

> **这一整个阶段是 2026-09-04 讨论产生的，此前不在 `.docx`（它是 08-19 的 Stage 9 版本）。本次收口一并纳入。**

## 3.1 为什么三道 Gate 全过了还要单独盯运行中

不是重复保险，是必需的。2026 年真实统计：**72%** 的团队报告过至少一次AI 生成代码导致的生产事故；**74%** 的 AI 生成代码有至少四分之一在上线后需要返工；很多问题上线 **30 天以后**才冒出来（真实叫法 quality drift）。更扎心的是，多数团队 review 那一刻觉得 AI 代码质量比人写的还好，**一旦真跑到生产环境，这个观感会崩掉**。

**结论**：①②③ Gate 能保证的是「这次改动没有已知问题」，保证不了「这个东西在真实世界里长期没事」。运行中这一块防的正是这个真空区。

## 3.2 老实说清楚现在处于哪一级成熟度

查证到的真实 AI 生产事故处理成熟度路径：

1. **只读洞察**（只看数据，不建议不执行）
2. 建议动作
3. 批准式补救（AI 提议、人批准、AI 执行、没效果自动回滚 + 升级）
4. 窄范围自主

**R1–R5 这一整块，现在的真实定位就是最初级的第 1 级「只读洞察」**——给人看数据，不会自己建议、更不会自己动手。往上走要先具备三根支柱：执行时的策略边界（DQ 已有 OPA）、不可篡改的审计账本（已有 immudb/OBS-F003）、每个 AI 动作的信任分数（**Matbox 现在完全没有**，见架构原则第65条）。**少一根都不能往自主化走。如实记录现状，不跳级。**

## 3.3 R1–R5 五块

| 编号 | 内容 | 数据来源 | 现状 |
|---|---|---|---|
| **R1** | 当前部署状态（Baseline / ReleaseArtifact / 上次部署时间 / 灰度进度 / 自动回滚阈值） | 第7节 ReleaseArtifact/Baseline 逻辑模型 | 待接入真实数据。灰度+自动回滚已落地为 `F-RELEASE-001` 的 **REL-F007**，不停在这张卡片上 |
| **R2** | Gate 判定分布（10 种状态占比 + reviewRoute + auditOutcome） | 第6节状态机 + GateDecision 的 riskTier/reviewRoute/auditSampled/auditOutcome 字段（架构原则第68条） | 待接入。**核心指标异常必须调 `OBS-F004` 生成可送达告警**，不能只是「让 Quality Owner 能看到」 |
| **R3** | 核心运行指标 | 第17节 Observability/SLO 指标，一字未改 | 待接入 |
| **R4** | 人工审核通过率趋势 | 抽样复核结果 | 待接入 |
| **R5** | 技术盯梢（5 个工具的最新版本与安全公告） | GitHub 公开数据 | **已接真实数据**——这张表查的是 GitHub 公开信息，不需要 Matbox 自己的系统跑起来 |

> 出处：`.docx` 第17节 + 样板「运行中」面板（2026-09-04 补强部分）

**R1–R4 现在真的没有数据，老实标「待接入真实数据」，不填假数字装样子。**等 Stage 10 真系统跑起来，直接把真实遥测接进这些已经定好的坑里，不用重新设计。

---

# 四、怎么建 · Implementation Blueprint

> 前三部分回答「要做什么、边界在哪、怎么验收」。**这一部分回答「代码怎么写」**——技术栈、目录结构、端点、Schema、建表、鉴权、错误码、测试、工作量。
>
> 全部来自《专项01 技术选型与开发交接报告》（1069 行）。**第一版 FINAL 漏掉了整个这一部分**，见 §0.3 的教训说明。

## 4.1 系统架构与数据流

```
┌─────────────────────────────────────────────────────────────────────┐
│                         RC5 WorkPackage / Codex Worktree               │
└───────────────────────────────────┬───────────────────────────────────┘
                                     │ ① trigger (push/PR/manual)
                                     ▼
                        ┌────────────────────────┐
                        │  F-DQ-001 Run Orchestrator │──reads──▶ RC5 Registry
                        │  (QualityRun lifecycle)   │           (WorkPackage/BaseCommit/
                        └────────────┬────────────┘            Protected Scope)
                                     │ ② resolve CheckSet + dispatch
        ┌────────────────────────────┼────────────────────────────┐
        ▼                            ▼                            ▼
┌───────────────┐          ┌───────────────────┐         ┌───────────────────┐
│ CODE_QUALITY   │          │  SECURITY_GATE     │         │ AUTOMATED_TEST_GATE│
│ GATE           │  PASS──▶ │  (安全质检)        │ PASS──▶ │  (unit/contract/    │
│ SonarQube      │          │  OpenGrep(sec)      │         │  integration/       │
│ Adapter        │          │  Betterleaks+       │         │  security/regress)  │
│ (F-DQ-003)      │          │  Gitleaks并行(F005)  │         │                     │
│ OpenGrep(quality│         │  Trivy (F-DQ-006)    │         │                     │
│ rules)(F-DQ-004) │         │  Architecture Guard  │         │                     │
│                │          │  (F-DQ-007)          │         │                     │
└───────┬────────┘          └──────────┬──────────┘         └──────────┬──────────┘
        │  raw report                  │  raw report                    │
        ▼                              ▼                                ▼
                    ┌──────────────────────────────────────┐
                    │  F-DQ-002 Evidence Normalizer           │
                    │  (SARIF/JSON/JUnit → NormalizedFinding)│
                    └───────────────────┬────────────────────┘
                                        │
                                        ▼
                    ┌──────────────────────────────────────┐
                    │  F-DQ-008 OPA GatePolicy Evaluator      │──reads suppression──▶ F-DQ-010
                    │  (fail-closed GateDecision)            │                      Suppression
                    └───────────────────┬────────────────────┘                      Governance
                          DENY │                    │ PASS
                                ▼                    ▼
              ┌──────────────────────┐   独立Source Review → Controlled Merge
              │ F-DQ-009 Auto Repair /  │                              │
              │ Revalidation Controller│                              ▼
              │ (Codex/Temporal patch, │                     New Integration Commit
              │  isolated worktree)    │                              │
              └───────────┬────────────┘                              ▼
                          │ new commit                        POST_MERGE_REVALIDATION
                          └──────────────▶ 回到 ① 从CODE_QUALITY_GATE重新开始      │
                                                                        ▼
                                                              ReleaseArtifact / Baseline
                                                              (F-RELEASE-001, 消费F-DQ-006 SBOM)

  所有ScannerRun/NormalizedFinding/GateDecision/RepairAttempt结果 ──写入──▶ F-OBS-001
  EvidenceBundle（immudb防篡改）；F-DQ-011把GateDecision状态回写SCM PR Status Check；
  F-DQ-013从F-OBS-001读取指标渲染到复用的SigNoz/Ops看板，不新建第二套可观测性后端。
```

> 出处：专项01 第12节（原文逐字收录，未改写）

## 4.2 源码目录、模块与依赖关系

```
backend/
  modules/
    dev-quality/
      orchestrator/         # F-DQ-001：QualityRunService, CheckPlanResolver, GateTriggerService
      normalizer/            # F-DQ-002：ParserRegistry, FindingMapper（依赖adapters/*的AdapterResult）
      adapters/
        sonar/               # F-DQ-003
        opengrep/             # F-DQ-004（含 rulepacks/ 子目录，Matbox自定义规则）
        secrets/              # F-DQ-005：betterleaks/, gitleaks/（过渡期并行）, merge/（并集判定）
        trivy/                # F-DQ-006
        architecture-guard/   # F-DQ-007（依赖 rc5-registry-client）
        opa/                  # F-DQ-008（含 policies/ 子目录，Rego bundle）
        ai-review/            # F-DQ-012（可选模块，独立可关闭）
      repair/                 # F-DQ-009（依赖 shared/agent-runtime-client 即 F-TASK-001客户端）
      suppression/            # F-DQ-010
      scm-integration/        # F-DQ-011
      ops/                    # F-DQ-013（依赖 shared/obs-client 即 F-OBS-001客户端）
      shared/
        contracts/            # QualityRun/Finding/GateDecision等DTO，供adapters/*、ops/共用
        errors/                # 复用 Matbox_错误码规范 的统一ErrorResponse
    shared-clients/            # 跨模块共享的Contract客户端（不属于dev-quality私有）
      rc5-registry-client/
      obs-client/              # F-OBS-001
      release-client/           # F-RELEASE-001
      cred-client/               # F-CRED-001
      tenant-client/             # F-TENANT-001
frontend/
  apps/ops-console/
    features/dev-quality/       # 对应FE-01~FE-06
```

**依赖方向铁律**（对应Own/Reuse/Must Not Rebuild）：`dev-quality/*` 只允许依赖 `shared-clients/*` 和自己内部子模块，不允许反向被 `rc5-registry-client`等基础设施客户端依赖；`adapters/*` 之间禁止互相依赖（每个Adapter独立可插拔，移除任一Adapter不影响其余Adapter运行，只影响CheckSet适用性矩阵判定）。

> 出处：专项01 第22节（原文逐字收录，未改写）

## 4.3 API 接口清单

统一前缀 `/dq`（对内Ops界面路由沿用原设计已定路由 `/ops/dev-quality/*`，两者指向同一后端服务，`/ops/dev-quality/*` 为前端友好别名）。鉴权规范见第16节，错误码规范见第19节。

| 方法 | 路径 | 说明 | 对应Feature |
|---|---|---|---|
| POST | `/dq/quality-runs` | 创建QualityRun（幂等键：WorkPackageID+BaselineID+trigger/phase） | F-DQ-001 |
| GET | `/dq/quality-runs/{qualityRunId}` | 查询QualityRun详情+状态 | F-DQ-001 |
| POST | `/dq/quality-runs/{qualityRunId}/cancel` | 取消进行中的QualityRun | F-DQ-001 |
| GET | `/dq/quality-runs/{qualityRunId}/scanner-runs` | 查询该Run下所有ScannerRun | F-DQ-002 |
| GET | `/dq/quality-runs/{qualityRunId}/findings` | 查询该Run的NormalizedFinding列表 | F-DQ-002 |
| GET | `/dq/quality-runs/{qualityRunId}/gate-decision` | 查询该Run最终GateDecision | F-DQ-008 |
| GET | `/dq/findings` | 按workPackageId/ruleId/severity/isNew等条件查询Finding（供VIZ模块只读投影调用） | F-DQ-002 |
| POST | `/dq/repair-attempts` | 触发一次RepairAttempt（内部服务调用，由GateDecision=DENY自动触发或F-VIZ-005手动触发） | F-DQ-009 |
| GET | `/dq/repair-attempts/{repairAttemptId}` | 查询修复尝试详情+resultQualityRunId | F-DQ-009 |
| POST | `/dq/suppressions` | 提交Suppression/Waiver申请 | F-DQ-010 |
| PUT | `/dq/suppressions/{suppressionId}/approve` | 独立Reviewer批准（禁止自批准，鉴权层校验reviewer≠requester） | F-DQ-010 |
| PUT | `/dq/suppressions/{suppressionId}/revoke` | 撤销/使其失效 | F-DQ-010 |
| GET | `/dq/suppressions` | 查询Suppression列表（按status/scope/expiry过滤） | F-DQ-010 |
| POST | `/dq/scm/webhooks/{provider}` | SCM Webhook入口（PR opened/synchronize/merged），provider=github\|gitlab | F-DQ-011 |
| GET | `/dq/scm/checks/{provider}/{commitSha}` | 查询某commit的DQ Status Check聚合状态 | F-DQ-011 |
| GET | `/dq/tool-health` | 工具健康看板数据（含各Adapter最近成功率/P95耗时/OPA上游社区节奏等观察指标） | F-DQ-013 |
| POST | `/dq/challenge-runs` | 触发一次固定Challenge Set回归（工具/规则/策略升级前必跑） | F-DQ-013 |
| GET | `/dq/challenge-runs/{challengeRunId}` | 查询Challenge回归结果，PASS/REGRESSED | F-DQ-013 |
| POST | `/dq/ai-review` | 触发AI Code Review补充证据（仅F-DQ-012启用时可调用） | F-DQ-012 |

> 出处：专项01 第13节（原文逐字收录，未改写）

## 4.4 Request / Response Schema

```yaml
# 以下为核心对象的JSON Schema（简化版，完整版随OpenAPI文档维护）

QualityRun:
  type: object
  required: [qualityRunId, phase, featureId, workPackageId, baselineId, baseCommit, status]
  properties:
    qualityRunId: {type: string, format: uuid}
    triggerType: {type: string, enum: [PUSH, PR_OPEN, PR_SYNC, MANUAL, POST_MERGE, REVALIDATION]}
    phase: {type: string, enum: [CODE_QUALITY, SECURITY, AUTOMATED_TEST, RECHECK, POST_MERGE]}
    featureId: {type: string}
    workPackageId: {type: string}
    baselineId: {type: string, nullable: true}
    baseCommit: {type: string}
    headCommit: {type: string, nullable: true}
    releaseArtifactRef: {type: string, nullable: true}
    requiredCheckSetVersion: {type: string}
    policyVersion: {type: string}
    parentQualityRunId: {type: string, nullable: true}
    impactScope: {type: object}
    status: {type: string, enum: [CREATED, RUNNING, PASS, DENY, INCOMPLETE, SCANNER_ERROR, POLICY_ERROR, TIMEOUT, REVALIDATION_REQUIRED, BLOCKED_MANUAL]}
    tenantId: {type: string}
    createdAt: {type: string, format: date-time}
    startedAt: {type: string, format: date-time, nullable: true}
    finishedAt: {type: string, format: date-time, nullable: true}
    triggeredBy: {type: string}
    evidenceBundleRef: {type: string, nullable: true}

NormalizedFinding:
  type: object
  required: [findingId, qualityRunId, sourceScanner, ruleId, category, severity, fingerprint]
  properties:
    findingId: {type: string, format: uuid}
    qualityRunId: {type: string}
    sourceScanner: {type: string, enum: [SONARQUBE, OPENGREP, BETTERLEAKS, GITLEAKS, TRIVY, ARCH_GUARD, AI_REVIEW]}
    ruleId: {type: string}
    category: {type: string}
    severity: {type: string, enum: [BLOCKER, CRITICAL, MAJOR, MINOR, INFO]}
    confidence: {type: string, enum: [HIGH, MEDIUM, LOW]}
    filePath: {type: string}
    location: {type: object}
    fingerprint: {type: string}
    introducedByRef: {type: string, nullable: true}
    isNew: {type: boolean}
    remediationClass: {type: string, enum: [AUTO_FIXABLE, MANUAL_REQUIRED, HIGH_RISK_NO_AUTO]}
    suppressionRef: {type: string, nullable: true}
    evidenceRef: {type: string}

GateDecision:
  type: object
  required: [gateDecisionId, qualityRunId, decisionState, policyVersion]
  properties:
    gateDecisionId: {type: string, format: uuid}
    qualityRunId: {type: string}
    policyVersion: {type: string}
    decisionState: {type: string, enum: [PASS, DENY, POLICY_ERROR, INCOMPLETE]}
    blockingFindingRefs: {type: array, items: {type: string}}
    incompleteCheckRefs: {type: array, items: {type: string}}
    reasonCodes: {type: array, items: {type: string}}
    evaluatorVersion: {type: string}
    evidenceBundleRef: {type: string}
    decidedAt: {type: string, format: date-time}
```

> 出处：专项01 第14节（原文逐字收录，未改写）

## 4.5 OpenAPI 3.0 文档

```yaml
openapi: 3.0.3
info:
  title: Matbox DevCodeQuality API
  version: "1.0.0"
  description: >
    代码持续质检与安全自检（F-DQ-001~013）对外暴露的最小API集合。
    鉴权见第16节，错误码统一使用 Matbox_错误码规范_正式开发文档_V1.0-RC.md。
servers:
  - url: https://internal.matbox.local/dq
paths:
  /quality-runs:
    post:
      operationId: createQualityRun
      summary: 创建一次QualityRun（幂等：WorkPackageID+BaselineID+trigger/phase）
      security: [{ bearerAuth: [] }]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [featureId, workPackageId, baseCommit, phase, triggerType]
              properties:
                featureId: { type: string }
                workPackageId: { type: string }
                baselineId: { type: string, nullable: true }
                baseCommit: { type: string }
                phase: { type: string, enum: [CODE_QUALITY, SECURITY, AUTOMATED_TEST, RECHECK, POST_MERGE] }
                triggerType: { type: string, enum: [PUSH, PR_OPEN, PR_SYNC, MANUAL, POST_MERGE, REVALIDATION] }
                idempotencyKey: { type: string }
      responses:
        "201":
          description: 已创建
          content:
            application/json:
              schema: { $ref: "#/components/schemas/QualityRun" }
        "409":
          description: IDEMPOTENCY_CONFLICT（同idempotencyKey但payload不同）
        "402":
          description: BUDGET_EXCEEDED（如启用F-DQ-012且成本预算触发）
  /quality-runs/{qualityRunId}:
    get:
      operationId: getQualityRun
      security: [{ bearerAuth: [] }]
      parameters:
        - { name: qualityRunId, in: path, required: true, schema: { type: string } }
      responses:
        "200":
          description: OK
          content:
            application/json:
              schema: { $ref: "#/components/schemas/QualityRun" }
        "404":
          description: RESOURCE_NOT_FOUND
  /quality-runs/{qualityRunId}/gate-decision:
    get:
      operationId: getGateDecision
      security: [{ bearerAuth: [] }]
      parameters:
        - { name: qualityRunId, in: path, required: true, schema: { type: string } }
      responses:
        "200":
          description: OK
          content:
            application/json:
              schema: { $ref: "#/components/schemas/GateDecision" }
  /findings:
    get:
      operationId: listFindings
      security: [{ bearerAuth: [] }]
      parameters:
        - { name: workPackageId, in: query, schema: { type: string } }
        - { name: severity, in: query, schema: { type: string } }
        - { name: isNew, in: query, schema: { type: boolean } }
      responses:
        "200":
          description: OK
          content:
            application/json:
              schema:
                type: array
                items: { $ref: "#/components/schemas/NormalizedFinding" }
  /suppressions:
    post:
      operationId: createSuppression
      security: [{ bearerAuth: [] }]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [type, fingerprint, reason]
              properties:
                type: { type: string, enum: [false_positive, accepted_risk] }
                fingerprint: { type: string }
                reason: { type: string }
                expiresAt: { type: string, format: date-time }
      responses:
        "201": { description: 已创建，待独立Reviewer批准 }
        "403": { description: AUTH_FORBIDDEN（P0规则不可申请accepted_risk） }
  /suppressions/{suppressionId}/approve:
    put:
      operationId: approveSuppression
      security: [{ bearerAuth: [] }]
      parameters:
        - { name: suppressionId, in: path, required: true, schema: { type: string } }
      responses:
        "200": { description: 已批准 }
        "403": { description: AUTH_FORBIDDEN（批准者=申请者时拒绝，禁止自批准） }
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT（携带tenantId claim，见第16节）
  schemas:
    QualityRun:
      $ref: "#/components/schemas/QualityRunFull"
    QualityRunFull:
      type: object
      description: 见第14节完整定义
    GateDecision:
      type: object
      description: 见第14节完整定义
    NormalizedFinding:
      type: object
      description: 见第14节完整定义
```

> 出处：专项01 第15节（原文逐字收录，未改写）

## 4.6 鉴权、权限与多租户规范

**不新建平行鉴权体系**——完全复用 F-TENANT-001（TENANT-F001~F006）与 F-CRED-001（CRED-F001~F009）已冻结的模式：

1. **人类用户访问**：走 `POST /tenant/sessions` 登录获得带 `tenantId` claim 的 JWT；DQ模块所有 `/dq/*` 端点用同一套 JWT 校验，不单独发一套 DQ token。角色沿用 TENANT-F002 已定义的7个具名角色（TenantOwner/TenantAdmin/EmployeeOwner/Operator/Reviewer/Viewer/PlatformAdmin）——F-DQ-010 的 Suppression 批准动作要求操作者角色为 `Reviewer` 且 `reviewerId != requesterId`（禁止自批准，对应原设计不可变原则）。
2. **AI员工（Codex/Claude）访问**：F-DQ-009 Auto Repair Controller 触发的每次Codex修复任务，必须先经 `POST /cred/agent-grants` 领取本次WorkPackage范围的短期Token（CRED-F003），DQ模块内部调用 `POST /tenant/authz/check` 做ABAC判断，`resource_type=dev_quality_run`, `action=repair`；权限范围不得超过当前WorkPackage的Allowed/Protected Scope。修复完成/超时后授权立即失效，不残留"僵尸权限"（TENANT-F003强制拒绝规则第4条）。
3. **多租户隔离**：所有DQ表（第20节）强制带 `tenant_id` 字段，遵循 TENANT-F004 "共享表+租户ID字段"模式，查询层禁止绕过租户过滤（数据层拦截，不能只靠应用层"记得加条件"）。QualityRun/Finding/GateDecision 全部继承触发它的 WorkPackage 所属租户。
4. **凭据（Sonar Token/Betterleaks live-validation凭据/AI Review Provider Key）**：一律通过 `GET /cred/secrets/{secretRefId}` 走 CRED-F001 Infisical适配层读取，运行时代理注入，禁止出现在DQ模块自己的配置文件、日志、Prompt中（CRED-F004"运行时代理注入"原则）。
5. **PlatformAdmin访问租户DQ数据**：必须走 TENANT-F002 定义的 break-glass 流程（时限+理由+不可篡改审计），不能用平台管理员身份静默查看某租户的Finding/GateDecision详情（Finding可能包含敏感代码片段/文件路径）。
6. **F-DQ-010批准闭环的强制拒绝**：与TENANT-F003强制拒绝规则第3条（"Risk 4/5的有副作用动作没有Approval默认DENY"）对齐——P0类false-positive suppression本身被视为高风险有副作用操作，必须双人（申请人+独立Reviewer）才能生效，符合口径。

> 出处：专项01 第16节（原文逐字收录，未改写）

## 4.7 Provider Adapter 接口规范

所有5个外部工具（及F-DQ-005过渡期新增的Gitleaks并行适配器）统一实现同一个 `ScannerAdapter` 接口，禁止让任何一个工具的原生schema渗透进Matbox Domain（Own/Reuse/Must Not Rebuild第65行原则）：

```yaml
ScannerAdapter接口（伪代码/逻辑契约，非某语言绑定）:
  submit(target: ScanTarget, config: AdapterConfig, idempotencyKey: string) -> AdapterRunHandle
    # target: {commit, diffScope|fullScope, workPackageId}
    # config: {toolVersion固定版本, configDigest, timeoutMs}
    # 返回句柄，不阻塞等待结果

  poll(handle: AdapterRunHandle) -> AdapterStatus
    # enum: SUBMITTED | RUNNING | COMPLETED | SCANNER_ERROR | TIMEOUT
    # SonarQube场景专用：额外区分 CE_PENDING | CE_SUCCESS | CE_FAIL | CE_CANCELLED（不得把CE_PENDING当PASS）

  fetchResult(handle: AdapterRunHandle) -> AdapterResult
    # {
    #   rawEvidenceRef: string,        # 原始报告，不可变，写入F-OBS-001
    #   normalizedFindings: NormalizedFinding[],
    #   errorClass: ScannerErrorClass?, # PARSER_ERROR | CONFIG_ERROR | ENGINE_CRASH | DB_UPDATE_ERROR | NETWORK_ERROR
    #   toolVersion: string,
    #   toolCommit_or_digest: string,
    #   isPartial: boolean             # 部分扫描完成时必须显式标注，禁止当0 findings处理
    # }

  cancel(handle: AdapterRunHandle) -> void

# 具体Adapter差异化处理点（各自Adapter内部实现，不影响外部接口契约）：
# - SonarAdapter: submit=触发scanner+等待analysis上传；poll需持续轮询CE task直到terminal状态
# - OpenGrepAdapter: submit=本地/容器内执行CLI，区分core/parser fatal error与finding
# - BetterleaksAdapter + GitleaksAdapter（过渡期并行）: 两者的normalizedFindings按fingerprint合并去重，
#   任一命中即计入blocking集合（并集判定，见第10节）
# - TrivyAdapter: submit需区分fs/image/config/sbom四种target类型，分别映射到不同扫描模式
# - OPAEvaluator: 不走上述submit/poll/fetchResult异步模型，是同步/短时评估：
#   evaluate(input: GatePolicyInput, policyBundleRef: string) -> GateDecision
#   deny=DENY；rego/eval error=POLICY_ERROR；两者都不得fail-open
```

> 出处：专项01 第17节（原文逐字收录，未改写）

## 4.8 Webhook、回调及异步任务规范

- **入站Webhook**（F-DQ-011）：`POST /dq/scm/webhooks/{provider}` 接收 GitHub/GitLab 的 `pull_request`（opened/synchronize）、`push`（merge到受保护分支）事件。签名校验（GitHub: `X-Hub-Signature-256` HMAC）；去重键 = `provider+deliveryId`，重复投递（GitHub重试机制）不得产生第二个有效QualityRun。
- **QualityRun派发**：F-DQ-001创建QualityRun记录后，通过既有Outbox模式（复用F-QUEUE-001/F-TASK-001的Temporal基础设施，不新建第二套队列）派发各Adapter的Scanner Job；Job执行结果通过Temporal Activity回调更新ScannerRun状态，不是裸HTTP callback。
- **异步任务超时/重试**：所有Scanner Job遵循Temporal的Activity重试策略（有界retry+backoff），超过RepairPolicyVersion配置的重试上限后转`BLOCKED_MANUAL`，不得无限重试。
- **F-DQ-009修复任务**：Codex修复Job同样通过Temporal Workflow驱动（复用AI任务运行时 F-TASK-001，不新建第二套Agent Runtime——docx第574行已标注"Shared Agent Runtime"依赖，当前F-TASK-001已建成正式文档，这条依赖已解开，是本次审计核实到的一个可以关闭的历史阻塞项，见下方"当前唯一继续断点"更新）。
- **SCM Status Check回写**：QualityRun状态每次变化（PASS/DENY/RUNNING/BLOCKED_MANUAL）通过SCM Adapter回写为GitHub Commit Status/Check Run，携带跳转到Evidence详情的URL；回写失败（SCM API限流/超时）不得导致QualityRun本身状态丢失，需有本地重试队列。

> 出处：专项01 第18节（原文逐字收录，未改写）

## 4.9 错误码、重试、超时与降级规范

**完全复用** `Matbox_错误码规范_正式开发文档_V1.0-RC.md` 定义的17个跨模块错误码，不新造平行错误码体系。DQ模块的典型映射：

| 场景 | 错误码 | HTTP | 可重试 |
|---|---|---|---|
| 提交QualityRun缺少必需字段/未知WorkPackageID | RESOURCE_NOT_FOUND | 404 | 否 |
| 同idempotencyKey但payload不同 | IDEMPOTENCY_CONFLICT | 409 | 否 |
| QualityRun状态非法转移（如已PASS的Run再次CREATED） | INVALID_STATE_TRANSITION | 409 | 否 |
| Suppression申请人尝试自批准 | AUTH_FORBIDDEN | 403 | 否 |
| 跨租户查询他人WorkPackage的Finding | TENANT_BOUNDARY_VIOLATION | 403 | 否 |
| Scanner Job遭遇引擎/配置/解析错误 | INTERNAL_ERROR（细分errorClass在details字段） | 500 | 是（有界） |
| Scanner/CE/OPA评估超时 | 复用错误码规范中语义相近的PROVIDER_TIMEOUT模式（原码面向Provider Router，DQ场景类比复用，细分至details.scannerErrorClass=TIMEOUT） | 504 | 是 |
| AI Review Provider限流 | RATE_LIMITED | 429 | 是 |
| F-DQ-012成本预算触发 | BUDGET_EXCEEDED | 402 | 否 |
| Gate输出结果未通过（业务DENY，非HTTP层错误） | QUALITY_GATE_FAILED | 422 | 否 |

**唯一需要补充说明的缺口**：现有17码里没有专门覆盖"Scanner部分完成/INCOMPLETE"这一DQ模块高频状态的错误码——这不是要新造一个平行码，而是采用规范第4条明确允许的方式：复用 `QUALITY_GATE_FAILED`（422）作为HTTP层错误码，把 `INCOMPLETE`/`SCANNER_ERROR`/`POLICY_ERROR`/`TIMEOUT`等DQ域内部状态机的精确语义放进 `details` 结构化字段，而不是在跨模块错误码规范里新增4个DQ专属码——这与"新增错误码必须先判断是否已有语义相近码可复用"的原则一致。

**降级规范**：任何Scanner/Policy错误一律fail-closed（不得因为无法判断而放行），与原设计P0规则完全一致，本报告不改变这条。

> 出处：专项01 第19节（原文逐字收录，未改写）

## 4.10 数据库及 Migration 设计

沿用REL-F006已确认的 **Flyway** 迁移工具（与RuoYi的Spring Boot/Java技术栈天然契合），共享表+`tenant_id`字段模式（TENANT-F004）。

```sql
-- V1__dq_core_tables.sql

CREATE TABLE dq_quality_run (
    quality_run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    trigger_type VARCHAR(32) NOT NULL,
    phase VARCHAR(32) NOT NULL,
    feature_id VARCHAR(64) NOT NULL,
    work_package_id VARCHAR(64) NOT NULL,
    baseline_id VARCHAR(64),
    base_commit VARCHAR(64) NOT NULL,
    head_commit VARCHAR(64),
    integration_commit VARCHAR(64),
    release_artifact_ref VARCHAR(64),
    required_check_set_version VARCHAR(32) NOT NULL,
    policy_version VARCHAR(32) NOT NULL,
    parent_quality_run_id UUID REFERENCES dq_quality_run(quality_run_id),
    impact_scope JSONB,
    status VARCHAR(32) NOT NULL DEFAULT 'CREATED',
    idempotency_key VARCHAR(256) NOT NULL,
    triggered_by VARCHAR(128) NOT NULL,
    evidence_bundle_ref VARCHAR(128),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    UNIQUE (tenant_id, work_package_id, baseline_id, trigger_type, phase, idempotency_key)
);
CREATE INDEX idx_dq_quality_run_tenant ON dq_quality_run(tenant_id);
CREATE INDEX idx_dq_quality_run_wp ON dq_quality_run(tenant_id, work_package_id);

CREATE TABLE dq_scanner_run (
    scanner_run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    quality_run_id UUID NOT NULL REFERENCES dq_quality_run(quality_run_id),
    adapter_type VARCHAR(32) NOT NULL, -- SONARQUBE|OPENGREP|BETTERLEAKS|GITLEAKS|TRIVY|ARCH_GUARD|OPA|AI_REVIEW
    tool_version VARCHAR(64) NOT NULL,
    tool_commit_or_digest VARCHAR(128) NOT NULL,
    config_digest VARCHAR(128) NOT NULL,
    target_scope JSONB,
    status VARCHAR(32) NOT NULL,
    exit_code INT,
    error_class VARCHAR(64),
    is_partial BOOLEAN NOT NULL DEFAULT false,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    raw_evidence_ref VARCHAR(128),
    normalized_finding_count INT NOT NULL DEFAULT 0
);
CREATE INDEX idx_dq_scanner_run_qr ON dq_scanner_run(quality_run_id);

CREATE TABLE dq_normalized_finding (
    finding_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    quality_run_id UUID NOT NULL REFERENCES dq_quality_run(quality_run_id),
    source_scanner VARCHAR(32) NOT NULL,
    rule_id VARCHAR(256) NOT NULL,
    category VARCHAR(64) NOT NULL,
    severity VARCHAR(16) NOT NULL,
    confidence VARCHAR(16),
    file_path TEXT,
    location JSONB,
    fingerprint VARCHAR(128) NOT NULL,
    introduced_by_ref VARCHAR(128),
    is_new BOOLEAN NOT NULL DEFAULT true,
    remediation_class VARCHAR(32),
    suppression_ref UUID,
    evidence_ref VARCHAR(128) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_dq_finding_qr ON dq_normalized_finding(quality_run_id);
CREATE INDEX idx_dq_finding_fingerprint ON dq_normalized_finding(tenant_id, fingerprint);

CREATE TABLE dq_gate_decision (
    gate_decision_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    quality_run_id UUID NOT NULL REFERENCES dq_quality_run(quality_run_id),
    policy_version VARCHAR(32) NOT NULL,
    decision_state VARCHAR(32) NOT NULL, -- PASS|DENY|POLICY_ERROR|INCOMPLETE
    blocking_finding_refs UUID[],
    incomplete_check_refs TEXT[],
    reason_codes TEXT[],
    evaluator_version VARCHAR(32) NOT NULL,
    evidence_bundle_ref VARCHAR(128) NOT NULL,
    decided_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_dq_gate_decision_qr ON dq_gate_decision(quality_run_id);

CREATE TABLE dq_repair_attempt (
    repair_attempt_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    parent_quality_run_id UUID NOT NULL REFERENCES dq_quality_run(quality_run_id),
    work_package_id VARCHAR(64) NOT NULL,
    attempt_no INT NOT NULL,
    strategy VARCHAR(32) NOT NULL, -- deterministic|codex|manual
    source_finding_refs UUID[],
    patch_commit VARCHAR(64),
    diff_ref VARCHAR(128),
    impacted_scope_ref JSONB,
    result_quality_run_id UUID REFERENCES dq_quality_run(quality_run_id),
    evidence_ref VARCHAR(128),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (parent_quality_run_id, attempt_no)
);

CREATE TABLE dq_suppression (
    suppression_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    type VARCHAR(32) NOT NULL, -- false_positive|accepted_risk
    fingerprint VARCHAR(128) NOT NULL,
    rule_id VARCHAR(256),
    scope JSONB,
    reason TEXT NOT NULL,
    requested_by VARCHAR(128) NOT NULL,
    owner VARCHAR(128) NOT NULL,
    independent_reviewer VARCHAR(128),
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING', -- PENDING|APPROVED|REVOKED|EXPIRED
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    approved_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    evidence_ref VARCHAR(128),
    CONSTRAINT chk_no_self_approval CHECK (independent_reviewer IS NULL OR independent_reviewer <> requested_by),
    CONSTRAINT chk_p0_no_accepted_risk CHECK (NOT (type = 'accepted_risk' AND scope->>'p0' = 'true'))
);
CREATE INDEX idx_dq_suppression_fingerprint ON dq_suppression(tenant_id, fingerprint);

CREATE TABLE dq_tool_health_check (
    check_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    adapter_type VARCHAR(32) NOT NULL,
    tool_version VARCHAR(64) NOT NULL,
    check_type VARCHAR(32) NOT NULL, -- AVAILABILITY|UPSTREAM_VELOCITY|CHALLENGE_REGRESSION
    result JSONB NOT NULL,
    checked_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE dq_challenge_run (
    challenge_run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    challenge_set_version VARCHAR(32) NOT NULL,
    candidate_tool_version VARCHAR(64) NOT NULL,
    baseline_tool_version VARCHAR(64) NOT NULL,
    result_summary JSONB NOT NULL,
    passed BOOLEAN NOT NULL,
    executed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

（`quality_result`/`audit_event` 相关证据字段不在本模块建表，全部写入 F-OBS-001 的 EvidenceBundle，按第2节Contract约束执行。）

> 出处：专项01 第20节（原文逐字收录，未改写）

## 4.11 前后端开发任务拆分

**后端（Java/Spring Boot，RuoYi-Vue-Pro基座）**：
- BE-01 QualityRunService + CheckPlanResolver + GateTriggerService（F-DQ-001）
- BE-02 EvidenceNormalizer框架 + 各Adapter Parser（SARIF/JUnit/自定义JSON）（F-DQ-002）
- BE-03 SonarAdapter（含CE异步轮询）（F-DQ-003）
- BE-04 OpenGrepAdapter + RulePack仓库管理（F-DQ-004）
- BE-05 BetterleaksAdapter + GitleaksAdapter（过渡期并行）+ 并集判定逻辑（F-DQ-005）
- BE-06 TrivyAdapter（fs/image/config/sbom四模式）（F-DQ-006）
- BE-07 ArchitectureGuard（Registry diff + Protected Scope校验器）（F-DQ-007）
- BE-08 OPAEvaluator封装 + Rego Policy Bundle管理（F-DQ-008）
- BE-09 RepairController（Temporal Workflow集成）（F-DQ-009）
- BE-10 SuppressionService（含双人审批状态机）（F-DQ-010）
- BE-11 SCM Adapter（GitHub/GitLab Webhook+Status Check）（F-DQ-011）
- BE-12 AIReviewAdapter（可选启用）（F-DQ-012）
- BE-13 ToolHealth聚合服务 + ChallengeRunner（F-DQ-013）

**前端（Ops控制台，复用既有Ops FE框架）**：
- FE-01 QualityRun时间线/状态/重试链路视图（F-DQ-001）
- FE-02 Finding列表/详情（含跳转Evidence抽屉）（F-DQ-002，供VIZ模块消费同一投影API）
- FE-03 RepairAttempt diff预览/审批界面（F-DQ-009）
- FE-04 Suppression申请/审批/到期管理界面（F-DQ-010）
- FE-05 PR Status Check展示组件（嵌入SCM PR页面链接，非独立页面）（F-DQ-011）
- FE-06 Tool Health仪表盘（复用F-OBS-001 SigNoz底层，DQ只做业务视图）（F-DQ-013）

> 出处：专项01 第21节（原文逐字收录，未改写）

## 4.12 测试集、Golden Set 与验收脚本

沿用原设计文档第13节 Acceptance Test Matrix（DQ-T001~DQ-T024，docx第822-849行）作为P0验收基线，本报告不重复列出全部24项，只补充本次审计新增的测试要求：

**新增测试（F-DQ-005过渡期专属）**：
- DQ-T025：同一已知泄露样本分别喂给Betterleaks和Gitleaks，验证并集判定确实触发DENY（即便只有一个工具命中）。
- DQ-T026：构造Betterleaks误报但Gitleaks未命中的样本，验证Suppression走正常独立Reviewer审批流程，而非因为"另一工具没报"就自动放行。
- DQ-T027：真实Matbox仓库过渡期结束时的交叉验证脚本——用同一批Golden Set（已知历史泄露样本+对抗样本）分别统计Betterleaks单独recall/precision与并集recall/precision，产出书面证据供决定是否退役并行工具。

**Golden/Challenge Set 4类结构**：复用 F-OBS-001（OBS-F006）已确认的评测集4类结构标准（真实生产流量抽样/对抗性测试库/人为构造边界情况/历史故障重放），F-DQ-013的Challenge Set同样必须覆盖这4类，不能只有人工编的题目，与OBS-F006共用同一套方法论但内容专属DQ域（已知CVE样本、已知泄露凭证样本、已知架构违规样本等）。

**验收脚本执行环境**：Stage 10前置——必须绑定真实Matbox Repo + Base Commit（docx第852-862行G-DQ-ST10系列Gate），本报告不改变这个前置条件，过渡期并行验证（DQ-T025~027）同样要求在真实Repo环境执行，不接受synthetic POC冒充结论（Stage 8已冻结原则）。

> 出处：专项01 第23节（原文逐字收录，未改写）

## 4.13 成本、性能、并发与安全要求

**成本**：5个核心工具（SonarQube/OpenGrep/Betterleaks/Trivy/OPA）+ 过渡期新增Gitleaks均为自托管开源，无许可证费用；主要成本是自托管基础设施（计算资源）与团队维护时间，非订阅费——这是相对SaaS方案（第5节列出的$25-1050/月不等）的核心成本优势，也是本次审计维持原路线的重要依据之一。F-DQ-012 AI Review若启用需计入Provider Router的Token成本，走F-COST-001预算控制，默认关闭。

**性能**：Fast Gate（PR级changed-scope扫描）与Full Gate（Release级全量扫描）必须分离预算，具体P50/P95/P99毫秒阈值不在Stage 9/本报告虚构，按原设计第17节要求留到Stage 10真实Repo跑出baseline后由Quality/Release Owner冻结（本报告不改变这条，虚构阈值本身就是需要避免的伪证据）。

**并发**：QualityRun派发的各ScannerRun可并行执行（不同Adapter互不阻塞），但Gate之间（CODE_QUALITY→SECURITY→AUTOMATED_TEST）业务判定顺序不可跳过（原设计第71行硬规则维持）。

**安全**：
- 扫描器进程最小权限运行，报告/规则/Git内容一律按不可信输入处理（限制文件大小/CPU/内存/超时/网络，第16节原则维持）。
- **新增强制要求（本次审计基于Trivy 2026供应链事件提出）**：所有5+1个工具的容器镜像/二进制必须固定到精确digest（禁止`latest`或浮动tag），发布前校验Cosign签名，升级前必须过Challenge Set canary，Previous Stable保持可秒级回滚——这条把原设计"原则性要求"（第15节"禁止latest进入production gate"）与本次调研到的真实事故证据挂钩，列为Stage 10强制验收项，不是可选建议。
- Betterleaks live secret validation默认关闭（原设计已定），过渡期新增的Gitleaks同样默认不开启任何向外部发起验证请求的功能。

> 出处：专项01 第24节（原文逐字收录，未改写）

## 4.14 开发阶段、优先级与预计工作量

沿用原设计第18节WP-DQ-01~10的WorkPackage逻辑拆分（docx第894-906行），本报告在此基础上标注优先级与量级估算（人天为团队自估量级，非精确工时，Stage 10绑定真实Repo后应重新校准）：

| WP | Feature | 优先级 | 量级估算（人天，粗量级） | 备注 |
|---|---|---|---|---|
| WP-DQ-01 | F001+F002 | P0，最先 | 8-12 | Contract先行，是后续所有Adapter的地基 |
| WP-DQ-02 | F003 | P0 | 5-8 | 含CE异步轮询，第一周预留误报规则调优缓冲 |
| WP-DQ-03 | F004+F007 | P0 | 8-12 | RulePack编写是核心工作量所在，非Adapter接入本身 |
| WP-DQ-04 | F005 | P0，**本次审计要求扩大范围** | 原估6-8 → **调整为10-14**（新增Gitleaks并行适配器+并集判定+过渡期交叉验证脚本DQ-T025~027） | 过渡期方案是本报告新增工作量的主要来源 |
| WP-DQ-05 | F006 | P0 | 5-8 | 含digest固定+签名校验强化要求 |
| WP-DQ-06 | F008 | P0 | 4-6 | OPA本体成熟，主要工作量在Rego策略编写 |
| WP-DQ-07 | F009+F010 | P0 | 8-12 | 双人审批状态机+隔离worktree修复是复杂点 |
| WP-DQ-08 | F011 | P1 | 5-8 | 依赖SCM平台最终选型（尚未确定GitHub/GitLab） |
| WP-DQ-09 | F012 | P2，可选 | 3-5 | Optional，不阻塞P0链路 |
| WP-DQ-10 | F013 | P1 | 5-8 | 含"OPA上游社区节奏监控"等本次审计新增观察指标 |

**总量级变化**：相对原设计，本报告使总工作量估算净增约4-6人天（集中在F-DQ-005过渡期方案），属于可控范围内的必要投入，用于把"7个月历史的年轻工具独占P0安全判定权"这个真实风险降到可接受水平。

> 出处：专项01 第25节（原文逐字收录，未改写）

## 4.15 风险、阻塞项与备用方案

| 风险/阻塞项 | 等级 | 说明 | 备用方案 |
|---|---|---|---|
| Betterleaks成熟度不足即被赋予P0独占判定权 | **高**（本次审计新增） | 详见第6/7/10节 | 过渡期双工具并集判定；若过渡期真实数据显示Betterleaks召回率不足，永久保留Gitleaks/TruffleHog作为长期并行或替换主方案 |
| SonarQube打包分析器SSALv1条款 | 中 | 非纯开源，内部自用场景下合规 | 若未来考虑对外产品化DQ能力，重新评估或切换到纯LGPL/Apache替代分析器组合 |
| Trivy/相关GitHub Action供应链投毒 | 中（已发生过真实事件） | 2026年3月真实事件 | 强制digest固定+签名校验+canary升级（第24节已列为强制项） |
| OPA主要商业支持方Styra停运 | 低-中（新发现，长期观察） | 项目本身治理未变，但社区节奏可能变化 | F-DQ-013持续监控OPA上游issue/PR处理速度；若明显恶化，评估迁移到Cerbos/OpenFGA等OPA替代品的成本（当前无需行动） |
| SCM平台尚未最终选定（GitHub vs GitLab vs 自建） | 高（既有阻塞，非本次新增） | 影响F-DQ-011具体实现 | ScmAdapter接口已做provider抽象，替换成本可控，不阻塞P0链路优先施工 |
| Stage 10真实Repo未绑定 | 高（既有阻塞，原设计已冻结此结论） | 本报告不改变这条 | 无——按原设计等待真实Repo/Base Commit绑定，禁止伪造 |
| OpenGrep社区规则库覆盖面小于付费Semgrep | 低-中（长期观察） | 详见第3.2/6.2节 | Matbox自建RulePack已覆盖P0规则；若通用CVE类规则缺口影响明显，评估补充付费Semgrep AppSec Platform作为规则库补充（非替换OpenGrep引擎本身） |

> 出处：专项01 第26节（原文逐字收录，未改写）

## 4.16 最终验收标准

本模块（Stage 10绑定真实Repo后）的验收标准 = 原设计文档第13节 DQ-T001~T024（24项，docx第822-849行，本报告不重复列出）+ 第14节 G-STAGE10-REPO-001 / G-STAGE10-CONFLICT-001 / G-DQ-ST10-CI-002~G-DQ-ST11-MERGE-006（**7项**Stage10/11 Gate；2026-09-08更正：原写「6项」且首条编号误作 G-DQ-ST10-REPO-001，已统一为全文通用的 G-STAGE10-REPO-001，并补入此前漏列的 G-STAGE10-CONFLICT-001；行号因补写已变动，此处改用节号引用）+ 本报告新增的 DQ-T025~DQ-T027（第23节，F-DQ-005过渡期交叉验证）。

三者全部通过，且：
1. 过渡期并集判定机制真实运行且有真实Matbox仓库产出的对比数据（不接受synthetic样本冒充）；
2. Trivy/OpenGrep/Betterleaks/Gitleaks/SonarQube/OPA全部固定版本+digest+签名校验通过；
3. Suppression双人审批状态机通过DQ-T016（P0高风险代码由Implementer自己Review必须BLOCKED）与本报告新增的自批准数据库约束（`chk_no_self_approval`）双重验证。

未通过任一项，Feature不得进入RC5 ACCEPTED流程，与原设计"Dev Quality PASS≠Feature ACCEPTED"原则一致。

> 出处：专项01 第27节（原文逐字收录，未改写）

## 4.17 交给未来 AI 开发人员的完整执行说明

如果你是接手这个模块施工的未来AI开发者（Codex或其他），请按以下顺序阅读和执行，不需要重新做调研或重新选型：

1. **先读原设计文档**（Stage 9正式依据，仍然有效）：`docs/Matbox_代码持续质检与安全自检_正式开发文档_V1.1-RC_CURRENT_Stage9内容级重验版_2026-08-19.docx`——这份文档定义了13个Feature的完整Implementation Surface（91个施工面）、状态机、P0冻结规则、Acceptance Test Matrix，是主体施工依据。
2. **再读本报告**（本文件）——本报告不推翻原设计的技术路线，只做三处修正：
   - F-DQ-005 Betterleaks 必须先实现"Gitleaks并行+并集判定"过渡期方案（第10/17/20/23节已给出具体接口/表结构/测试用例），不要直接把Betterleaks单独设为P0唯一DENY判定源。
   - Trivy/OpenGrep/Betterleaks/SonarQube/OPA的容器镜像/二进制必须固定digest+签名校验，禁止`latest`（第24节）。
   - F-DQ-013的工具健康监控清单里加入"OPA上游社区节奏"这一观察指标（第6.5/26节）。
3. **依赖检查**：施工前确认以下专项的正式开发文档均已存在且状态为DRAFT_RESEARCH_COMPLETE或更高——`Matbox_证据审计与监控_正式开发文档_V1.0-RC.md`（F-OBS-001）、`Matbox_发布与基线系统_正式开发文档_V1.0-RC.md`（F-RELEASE-001）、`Matbox_密钥管理_正式开发文档_V1.0-RC.md`（F-CRED-001）、`Matbox_租户与权限体系_正式开发文档_V1.0-RC.md`（F-TENANT-001）、`Matbox_错误码规范_正式开发文档_V1.0-RC.md`、`Matbox_AI任务运行时_正式开发文档_V1.0-RC.md`（F-TASK-001，F-DQ-009依赖的Agent Runtime载体，docx原文标注"Shared Agent Runtime"为未解阻塞，现已建成，可以解锁）。以上均已确认存在，不需要重新调研这些底层模块。
4. **Stage 10前置条件不可跳过**：必须先有真实Matbox Repo + Base Commit + WorkPackageID + Worktree/PR，才能开始任何一条WorkPackage施工（WP-DQ-01~10，第25节），这是原设计Stage 9/10边界，本报告不改变。
5. **施工顺序**：按第25节WP-DQ-01→10顺序，WP-DQ-01（Contract地基）必须最先完成，其余P0项（02/03/04/05/06/07）可并行但都依赖01。WP-DQ-04（Betterleaks+Gitleaks并行）比原设计估算多约4-6人天，请提前告知项目负责人这个量级变化的原因（过渡期风险控制，非返工）。
6. **不要重新做的事**：不要重新调研SonarQube/OpenGrep/Trivy/OPA的选型（Stage 6源码级审查+本报告独立复核均已通过）；不要重新设计错误码（复用错误码规范）；不要重新设计鉴权模式（复用F-TENANT-001/F-CRED-001）；不要重新讨论"是否应该用一体化SaaS平台整体替代"（第3.2节已系统性核查并排除，除非出现足以改变结论的全新证据）。
7. **如果发现本报告或原设计与真实Repo情况冲突**：按原设计不可变原则处理——不允许因为图省事就静默绕过P0规则；发现真实冲突应记录并升级给Quality/Security Owner决策，不要自行降级。

---

## 附录｜来源汇总

- SonarQube: [SSALv1条款](https://www.sonarsource.com/license/ssal/)、[License overview](https://www.sonarsource.com/license/)
- OpenGrep: [The New Stack](https://thenewstack.io/opengrep-launches-as-free-fork-after-semgrep-license-shift/)、[Socket](https://socket.dev/blog/opengrep-forks-semgrep)、[Aikido: Launching Opengrep](https://www.aikido.dev/blog/launching-opengrep-why-we-forked-semgrep)、[InfoQ](https://www.infoq.com/news/2025/02/semgrep-forked-opengrep)、[Opengrep官网](https://www.opengrep.dev/)
- Betterleaks: [appsecsanta评测](https://appsecsanta.com/betterleaks)、[BleepingComputer](https://www.bleepingcomputer.com/news/security/betterleaks-a-new-open-source-secrets-scanner-to-replace-gitleaks/)、[GitHub](https://github.com/betterleaks/betterleaks)、[appsecsanta Gitleaks vs TruffleHog对比](https://appsecsanta.com/secret-scanning-tools/gitleaks-vs-trufflehog)、[Aikido Gitleaks Alternatives](https://www.aikido.dev/blog/gitleaks-alternatives)
- Trivy: [StepSecurity事件报告](https://www.stepsecurity.io/blog/trivy-compromised-a-second-time---malicious-v0-69-4-release)、[GitHub Discussion #10425](https://github.com/aquasecurity/trivy/discussions/10425)、[GitHub Discussion #10462](https://github.com/aquasecurity/trivy/discussions/10462)、[TheHackerNews](https://thehackernews.com/2026/03/trivy-security-scanner-github-actions.html)、[appsecsanta Trivy](https://appsecsanta.com/trivy)
- OPA: [2025 OPA Community Survey](https://www.openpolicyagent.org/survey/2025)、[Styra停运报道](https://medium.com/@mathew_30470/opa-got-acquired-sort-of-whats-next-ea54f392d748)、[Mondoo](https://mondoo.com/blog/styra-opa-alternative-for-infrastructure-security-and-compliance-policies)、[Cerbos](https://www.cerbos.dev/blog/opa-alternative)
- 一体化平台调研: [Aikido定价](https://www.trustradius.com/products/aikido-security/pricing)、[Aikido评测](https://thectoclub.com/tools/aikido-security-review/)、[Semgrep定价](https://dev.to/rahulxsingh/semgrep-pricing-in-2026-open-source-vs-team-vs-enterprise-costs-3dic)、[GHAS vs Snyk](https://safeguard.sh/resources/blog/snyk-vs-github-advanced-security-comparison)、[Qodana/DeepSource/Codacy对比](https://dev.to/rahulxsingh/deepsource-vs-qodana-code-quality-platforms-compared-2026-152a)
- 中国大陆可达性: [Censorship of GitHub - Wikipedia](https://en.wikipedia.org/wiki/Censorship_of_GitHub)、[GitHub Community Discussion #156515](https://github.com/orgs/community/discussions/156515)
- 行业build-vs-buy实践: [Augment Code: Multi-Agent Orchestration Build vs Buy 2026](https://www.augmentcode.com/tools/multi-agent-orchestration-platforms-build-vs-buy)
- **V1.1修订新增来源（F-DQ-006 Trivy替代候选）**：[Trivy vs Grype (appsecsanta)](https://appsecsanta.com/sca-tools/trivy-vs-grype)、[Trivy vs Grype (lucaberton)](https://lucaberton.com/blog/trivy-vs-grype-2026/)、[Dependency-Track官方文档](https://docs.dependencytrack.org/datasources/trivy/)、[DependencyTrack GitHub Issue #4164](https://github.com/DependencyTrack/dependency-track/issues/4164)、[DependencyTrack GitHub Issue #5675](https://github.com/DependencyTrack/dependency-track/issues/5675)、[Clair vs Trivy (pistack.xyz)](https://www.pistack.xyz/posts/2026-04-24-self-hosted-container-image-scanning-trivy-grype-clair-anchore-guide-2026/)、[Snyk vs Trivy (dev.to)](https://dev.to/rahulxsingh/snyk-vs-trivy-commercial-security-platform-vs-open-source-scanner-2026-5e4b)
- **V1.1修订新增来源（F-DQ-008 OPA替代候选，含OpenFGA/Permit.io核实）**：[OPA vs Cedar vs Zanzibar (osohq)](https://www.osohq.com/learn/opa-vs-cedar-vs-zanzibar)、[Policy as Code: OPA's Rego vs. Cedar (permit.io)](https://www.permit.io/blog/opa-vs-cedar)、[Kyverno vs OPA Gatekeeper (nirmata)](https://nirmata.com/2026/01/28/whats-the-difference-between-kyverno-and-opa-gatekeeper/)、[Casbin vs OPA (stackshare)](https://stackshare.io/stackups/casbin-vs-oso)、[Top Open-Source Authorization Tools 2026 (permit.io)](https://www.permit.io/blog/top-open-source-authorization-tools-for-enterprises-in-2026)、[Policy Engine Showdown OPA vs OpenFGA vs Cedar (permit.io)](https://www.permit.io/blog/policy-engine-showdown-opa-vs-openfga-vs-cedar)、[OPA vs OpenFGA技术对比 (madappgang)](https://madappgang.com/blog/opa-vs-openfga-a-comprehensive-technical-compariso/)
- **V1.1修订新增来源（F-DQ-003第三候选）**：[Codacy vs SonarQube (DEV Community)](https://dev.to/rahulxsingh/codacy-vs-sonarqube-code-quality-platforms-compared-2026-35d2)、[Code Climate vs SonarQube (aicodereview)](https://aicodereview.cc/blog/sonarqube-vs-codeclimate/)
- **V1.1修订新增来源（F-DQ-004第三候选）**：[8 AI SAST Tools 2026 (Augment Code)](https://www.augmentcode.com/tools/best-ai-sast-tools)、[Semgrep Cloud vs CodeQL (safeguard.sh)](https://safeguard.sh/resources/blog/semgrep-cloud-vs-codeql-comparison-2026)
- **V1.1修订新增来源（F-DQ-002/010 DefectDojo）**：[DefectDojo官方博客](https://defectdojo.com/blog/top-11-open-source-vulnerability-management-tools-for-2026)、[DefectDojo Review (appsecsanta)](https://appsecsanta.com/defectdojo)、[OWASP DefectDojo项目页](https://owasp.org/www-project-defectdojo/)
- **V1.1修订新增来源（F-DQ-007 ArchUnit）**：[ArchUnit架构测试实践 (loiane.com)](https://loiane.com/2026/07/architecture-testing-java-archunit/)、[ArchUnit in Practice (codecentric)](https://www.codecentric.de/en/knowledge-hub/blog/archunit-in-practice-keep-your-architecture-clean)
- **V1.1修订新增来源（F-DQ-009自动修复候选）**：[Best Automated Remediation Tools 2026 (pixee.ai)](https://www.pixee.ai/blog/best-automated-remediation-tools-2026)、[Mobb vs GitHub Copilot Autofix (mobb.ai)](https://www.mobb.ai/blog/mobb-vs-github-copilot-autofix)、[Copilot Agentic Autofix (byteiota)](https://byteiota.com/github-copilot-agentic-autofix-verified-fixes-auto-pr/)
- **V1.1修订新增来源（F-DQ-011 Mergify）**：[Mergify vs GitHub Merge Queue官方对比](https://mergify.com/compare/github-merge-queue)、[GitHub Auto-Merge何时够用 (Mergify)](https://mergify.com/blog/github-auto-merge-when-native-is-enough)
- Matbox内部依据文档: `Matbox_Feature_Register.md`、`Matbox_证据审计与监控_正式开发文档_V1.0-RC.md`、`Matbox_发布与基线系统_正式开发文档_V1.0-RC.md`、`Matbox_密钥管理_正式开发文档_V1.0-RC.md`、`Matbox_租户与权限体系_正式开发文档_V1.0-RC.md`、`Matbox_错误码规范_正式开发文档_V1.0-RC.md`、`Matbox_架构设计原则.md`

> 出处：专项01 第28节（原文逐字收录，未改写）

## 4.18 本地开发环境：从零到能跑（2026-09-08 新补）

> **这一节此前是空白**，而且是本文档 ⑧ 自己承认的空白：「11 块资料回答的都是『要做什么、边界在哪』，没有一块回答『接到任务后敲几个命令、多久能有个能跑的开发环境』」。查证的真实数据：好团队从接到任务到提交第一行代码 3–5 天，差的 2–3 周；靠「一条命令跑起整个环境」能把这个时间从 80 天压到 4 天。**这一维度不需要等真代码库，所以先补上。**

### 4.18.1 技术栈（本文档首次把它明确写死）

| 项 | 定为 | 依据 |
|---|---|---|
| 语言 / 框架 | **Java + Spring Boot**，RuoYi-Vue-Pro 基座 | 专项01 §21；架构原则第31条 |
| 数据库 | **PostgreSQL** | 专项01 §20 的 DDL 用 `UUID` / `JSONB` / `gen_random_uuid()`——这是 PostgreSQL 语法；架构原则第467条讨论 Matbox 扩展路径时按 Postgres 规划；第398条提到「用现有 Postgres 就行」 |
| 迁移工具 | **Flyway** | 专项01 §20；REL-F006 已确认 |
| 多租户 | 共享表 + `tenant_id` 字段（TENANT-F004） | 专项01 §20 |

> ⚠️ **数据库这一条是本文档第一次明确记录。** 此前全仓库没有任何一条「Matbox 用 PostgreSQL」的显式决定——它只是在讲别的事情时被顺带提到。而基座 RuoYi-Vue-Pro 默认面向 MySQL，两者是否冲突从没有人核过。**2026-09-08 已核实：RuoYi-Vue-Pro 官方支持 PostgreSQL**（仓库有 `sql/postgresql/ruoyi-vue-pro.sql`，官方文档列出 MySQL/Oracle/PostgreSQL/SQL Server/达梦/TiDB 等多库支持），**不冲突**。

### 4.18.2 ✅ 已补齐：5 个工具全部锁到完整 40 位哈希（2026-09-08 当天解决）

文档第15节第6条要求：工具版本**必须精确到完整 40 位提交哈希**，不能只锁版本标签——这条是 2026-03 Trivy 供应链攻击后加的。但附录 A 记录的 5 个工具里：

| 工具 | 已记录的 commit | 位数 | 是否满足第15节第6条 |
|---|---|---|---|
| SonarQube | `b33183b846cd47c7a811e280f5755f13d8fa8cc7` | 40 | ✅ |
| OpenGrep | `e7202581ac004654035f5bd08f590ef67bd9c95d` | 40 | ✅ |
| Betterleaks | `5eab48332cc48565864514e3bc6de89df091a7c4` | 40 | ✅ 09-08 补齐 |
| Trivy | `e1fd17a0ea4a8cf24bc4b4dd7e2cfbf4bb31b994` | 40 | ✅ 09-08 补齐 |
| OPA | `85f6d990d19094da38e829561813e7da7fbae272` | 40 | ✅ 09-08 补齐 |

**为什么这不是小事**：Trivy 正是 2026-03 真被供应链攻击的那一个，而它自己的哈希此前只锁了 10 位——短哈希理论上可碰撞，也无法唯一确定一次提交，而第15节第6条恰恰是那次攻击之后才加的。2026-09-08 用 GitHub API 逐个展开、写回 `.docx` 表2 与附录A。三个提交的日期分别是 Betterleaks 2026-08-18、Trivy 2026-08-14、OPA 2026-05-12——**Trivy 这个提交在 2026-03 事件之后，不受那次投毒影响**。

### 4.18.3 从零到能跑：目标 4 步、一条命令

> ⚠️ **下面是规格，不是已跑通的脚本**——Matbox 真代码库还没有第一行代码，无法现在实测。Stage 10 拿到真仓库后的**第一件事**就是把这一节跑通，并把真实耗时回填到 4.18.4。**在跑通之前，本节任何时间数字都不许当作事实引用。**

**第 1 步 · 起依赖**（PostgreSQL + SonarQube Server + 三个 CLI 工具容器）

```bash
# 期望：一条命令，不需要手工装任何东西
docker compose -f docker/dev-quality.compose.yml up -d
```

compose 文件必须满足（对应第15节第6条 + 专项01 §24 安全要求）：

- 每个镜像**固定到精确 digest**（`image: aquasecurity/trivy@sha256:…`），禁止 `latest`、禁止只写版本标签
- 扫描器容器**最小权限**运行：限制 CPU/内存/超时，默认 `network: none`（Trivy 更新漏洞库时才单独放行）
- Betterleaks 的 live secret validation **默认关闭**（文档 16.3）

**第 2 步 · 建库**

```bash
./mvnw flyway:migrate -Dflyway.configFiles=flyway.dev.conf
```

迁移脚本从 `V1__dq_core_tables.sql` 开始（专项01 §20 已给出完整 DDL）。

**第 3 步 · 起服务**

```bash
./mvnw spring-boot:run -pl yudao-server -Dspring-boot.run.profiles=local
```

**第 4 步 · 冒烟验证：环境到底好没好**

不靠「服务起来了」这种感觉判断，跑三条真实调用（端点来自 §4.3）：

```bash
# ① 建一个 QualityRun —— 验证 DB + 幂等键 + 租户上下文
curl -X POST localhost:48080/dq/quality-runs -H 'Content-Type: application/json' \
  -d '{"workPackageId":"WP-SMOKE-001","baselineId":"BL-SMOKE","phase":"CODE_QUALITY","baseCommit":"0000000000000000000000000000000000000000"}'

# ② 同样的请求再发一次 —— 幂等键必须生效，不能产生第二个有效 run
#    这一条专门验 F-DQ-001 施工面里写的「trigger 幂等；同 event 重放不重复创建有效 run」

# ③ 查工具健康 —— 验证 5 个 Adapter 都能被探活
curl localhost:48080/dq/tool-health
```

**通过标准**：① 返回 `qualityRunId` 且状态为 `CREATED`；② 返回同一个 `qualityRunId`（不是新的）；③ 5 个 Adapter 全部可达。**任何一条不过，环境就不算好，不许开始写业务代码。**

### 4.18.4 真实耗时（待 Stage 10 回填）

| 指标 | 目标 | 实测 |
|---|---|---|
| 从 clone 到冒烟三条全过 | ≤ 30 分钟 | **待实测** |
| 需要人工手动做的步骤数 | 0（除填 `.env` 凭据外） | **待实测** |
| 需要的外网访问 | 仅拉镜像与漏洞库 | **待实测** |

> 出处：技术栈来自专项01 §20/§21 + 架构原则第31/398/467条；哈希位数问题为 2026-09-08 本次核对发现；RuoYi PostgreSQL 支持为 2026-09-08 查证；四步流程与冒烟标准为**推导**（依据专项01 §13 端点、§20 DDL、§24 安全要求、`.docx` 第15/16节），标注为规格而非实测。

---

# 附录 · 出处对照与遗留

## A. A 类工具源码基线

| 组件 | Repo | 固定 commit | License | 关键文件 | Matbox 借法 |
|---|---|---|---|---|---|
| SonarQube Community Build | SonarSource/sonarqube | b33183b846cd47c7a811e280f5755f13d8fa8cc7 | LGPL-3.0 core | server/sonar-ce-task-projectanalysis/.../ReportComputationSteps.java; .../QualityGateMeasuresStep.java | 代码质量/复杂度/覆盖/重复/Quality Gate；Matbox 必须等待 CE 完成，不只看 scanner exit。 |
| OpenGrep | opengrep/opengrep | e7202581ac004654035f5bd08f590ef67bd9c95d | LGPL-2.1 | cli/src/semgrep/run_scan.py; cli/src/semgrep/core_runner.py; src/osemgrep/core_runner/Core_runner.ml; src/osemgrep/cli_scan/Scan_subcommand.ml | SAST + Matbox 自定义架构规则；findings、parser/core error、strict/error exit 分离。 |
| Betterleaks | betterleaks/betterleaks | 5eab48332cc48565864514e3bc6de89df091a7c4 | MIT | cmd/root.go; cmd/git.go; detect/*; report/json.go; report/junit.go | Secret 扫描；Git diff/staged/full history；支持 baseline/report；扫描可部分失败，必须标 Incomplete。 |
| Trivy | aquasecurity/trivy | e1fd17a0ea4a8cf24bc4b4dd7e2cfbf4bb31b994 | Apache-2.0 | pkg/commands/run.go; pkg/flag/report_flags.go; pkg/commands/operation/operation.go; pkg/commands/artifact/* | 依赖/Container/IaC/SBOM；security finding exit 与 timeout/cache/db error 分离。 |
| OPA | open-policy-agent/opa | 85f6d990d19094da38e829561813e7da7fbae272 | Apache-2.0 | cmd/eval.go; cmd/check.go; rego/* | 最终 Policy Gate；policy deny 与 Rego/eval engine error 使用不同退出语义，必须 fail-closed。 |

> 出处：`.docx` 第3节 A 类源码与版本基线（表2）

## B. 本文档没有收录什么，以及为什么

2026-09-08 对 20 次「只改了样板、没改 `.docx`」的提交逐条判定，结论：

| 类别 | 条数 | 处置 |
|---|---|---|
| 纯排版 / 交互 / 视觉 | 10 | 不进文档（节点重叠、响应式、弹窗方式、下载按钮…）|
| 已进别的模块文档 | 6 | 本文档只引用不复制（REL-F007、F-TASK/F-QUEUE、OBS-F004、架构原则58~60条）|
| 该回流本文档 | 4 | **已全部收录**（12 块结构、运行中阶段、成熟度定位、为什么要盯运行中）|

**「灰度发布」「自动回滚」在本文档里查不到具体设计，这是故意的**——它们归 `F-RELEASE-001` 管，DQ 只引用。不是漏。

## C. 当前唯一继续断点

- 下一步唯一从：Stage 10 / RC5 Implementer Ready 开始。不是等待 Matbox 整个平台开发完；而是在第一个要接入这套质检链的真实 Feature/WorkPackage 上，绑定真实 repo + Base Commit + Worktree/PR，并实际运行 DQ Gate。
- 禁止从 Stage 1 重做调研；除非出现足以改变技术路线/架构的新证据。
- 附录 A｜源码复查路径
- 附录 B｜最终大白话定义

> 出处：`.docx` 第20节
