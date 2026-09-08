# Matbox 发布产物与基线系统（F-RELEASE-001）

正式开发文档 · V1.0-RC · 2026-08-29

## 当前定位

本专项解决"怎么证明现在跑在生产上的东西，就是当初审核通过的那份代码"——即 ReleaseArtifact（发布产物）和 Baseline（版本基线）的管理。是 Platform Core 的共享能力，被 F-DQ-001/006/011 直接依赖。

**DocID**: MATBOX-RELEASE-GATE-20260829-V1.0-RC
**状态**: DRAFT_RESEARCH_COMPLETE（已完成全球选型调研，未进入 Stage 10 真实施工）
**2026-08-30 补充**：新增 REL-F006（数据库迁移追溯），来自《Matbox_多端平台_CURRENT_正式开发文档_V3.0》F-RELEASE-001 章节——该文档也用了 F-RELEASE-001 编号，多出"数据库迁移(Flyway)可追溯/可回滚"这块，是REL-F001~F005没覆盖到的真实缺口，并入本文档当新Feature，不单独占用编号（详见架构原则第31条）。

## 1｜不可变原则

1. ReleaseArtifact 一旦生成不可修改；同一个 Commit 因依赖/构建参数/配置不同产生不同产物时，必须是不同的 ReleaseArtifactID。
2. Baseline 创建后不得修改；关键组成变化必须创建新 BaselineID，旧 Baseline 的历史通过记录永久保留，不得删除或篡改。
3. 追溯链条必须完整：Merge Commit → 依赖快照 → 构建记录 → 产物摘要 → ReleaseArtifactID → 部署记录，任何一环缺失都不能声称"已验证发布"。
4. 不重复造轮子——SBOM 已经由 F-DQ-006（Trivy）生成，本模块直接复用，不新增第二套 SBOM 工具。

## 2｜全球调研结论（2026-08-29）

### 2.1 制品仓库选型

| 候选 | 说明 | 结论 |
|---|---|---|
| **Harbor** | 开源自建，内置漏洞扫描、复制、权限管理，CNCF毕业项目 | **采用**——自建，够小团队用，社区成熟 |
| Docker Hub / 云厂商仓库 | 托管服务 | 不用——与"不绑定单一供应商"原则冲突，且涉及自建优先原则 |

### 2.2 SBOM：不新增工具，直接复用

F-DQ-006（Trivy Adapter）已经具备 SBOM 生成能力，本模块直接消费其产出，不再引入 Syft 等第二套 SBOM 工具——避免同一件事被两个工具重复做，产生两份可能不一致的结果。

### 2.3 构建溯源签名（SLSA Provenance）

延续架构原则第11条已确认的要求：目标 SLSA Level 2。多数主流 CI 系统能原生生成 SLSA Provenance（构建产物的源仓库、commit、依赖、构建环境的密码学签名），具体接入方式待确定 CI 平台后细化，本文档先定规则，不绑定具体 CI 工具。

### 2.4 版本编号策略

内部产物用 **Git Commit SHA** 做溯源（每次提交天然唯一，直接关联源码），对外正式发布再叠加语义化版本号（Semantic Versioning）。这与 RC5 已定义的 ReleaseArtifactID/BaselineID 编号体系兼容，不冲突。

## 3｜Own / Reuse / Must Not Rebuild

| 类型 | 对象 | 说明 |
|---|---|---|
| OWN | BaselineID、ReleaseArtifactID 编号规则、追溯链条业务逻辑 | Matbox 自己的发布事实源 |
| REUSE | Harbor 镜像存储、F-DQ-006 的 SBOM 产出、CI 原生 SLSA 签名能力 | 直接用现成实现，不重复造 |
| MUST NOT REBUILD | 容器镜像格式（OCI标准）、SBOM生成算法 | 用现成标准和工具 |

## 4｜Feature Register

| FeatureID | 名称 | 说明 |
|---|---|---|
| REL-F001 | Harbor 自建制品仓库 | 存放构建产物/镜像，带摘要（digest）和漏洞扫描 |
| REL-F002 | SBOM 复用接入 | 消费 F-DQ-006 产出，不重复生成 |
| REL-F003 | SLSA 构建溯源签名 | 目标 Level 2，CI原生能力接入 |
| REL-F004 | BaselineID/ReleaseArtifactID 追溯链条 | Merge Commit→依赖快照→构建→产物→部署 全链条可查 |
| REL-F005 | Baseline 冻结与历史保留 | 新Baseline不改旧Baseline，历史PASS永久保留 |
| REL-F006 | 数据库迁移追溯（Migration Digest） | Flyway迁移可追溯/可回滚，2026-08-30从多端平台文档并入 |
| REL-F007 | 灰度发布 + 自动回滚（2026-09-04补，纠正此前遗漏） | 新ReleaseArtifact先按比例放量而非全量切换，实时指标越过阈值自动回滚，不等人工发现；此前只有`rollbackOf`这个事后人工回滚指针，没有灰度放量和自动触发机制，是真实缺口 |

### REL-F001 · Harbor 自建制品仓库
- **目标**：所有构建产物统一存放，带不可变摘要（digest），支持按 Base Commit 追溯。
- **验收标准**：任一 ReleaseArtifact 可通过摘要精确定位到具体产物，不可被覆盖替换。

### REL-F002 · SBOM 复用接入
- **目标**：直接读取 F-DQ-006 的 Trivy SBOM 产出，关联到对应 ReleaseArtifactID，不新建生成逻辑。
- **验收标准**：每个 ReleaseArtifact 都能查到对应 SBOM，且明确是复用而非重复生成。

### REL-F003 · SLSA 构建溯源签名
- **目标**：达到 SLSA Level 2——构建产物有可验证的来源证明（源仓库、commit、构建环境）。
- **验收标准**：任一 ReleaseArtifact 可验证其 Provenance 签名有效。

### REL-F004 · BaselineID/ReleaseArtifactID 追溯链条
- **目标**：实现 RC5 定义的完整链条：Merge Commit → DependencySnapshot/Lockfile Digest → BuildRunID → Artifact/Image Digest → ReleaseArtifactID → Deploy/ReleaseID。
- **验收标准**：给定任一环节的ID，能反查出链条上的其余所有环节。

### REL-F005 · Baseline 冻结与历史保留
- **目标**：Baseline创建后不可修改；关键组成（Doc/依赖/配置/策略）变化时创建新Baseline，旧Baseline历史PASS不被覆盖或删除。
- **验收标准**：人为制造一次基线变化，验证旧Baseline记录原样保留，新Baseline独立生成。

### REL-F006 · 数据库迁移追溯（Migration Digest，2026-08-30新增）
- **目标**：让代码、DB、Workflow、配置、构建产物可追溯、可回滚、可重验——这次新增的是"数据库迁移"这一环，之前REL-F001~F005只覆盖了镜像/SBOM/签名/追溯链条/Baseline，没覆盖DB schema变更本身怎么追溯。
- **In Scope**：Flyway迁移；依赖版本锁定；SBOM/CVE/secret扫描；产物摘要/签名；配置/迁移快照；回滚兼容性；接入RC5 Registry。
- **工具选型对比（2026-08-30深度核实补充）**：

| 候选 | 真实案例/数据 | 结论 |
|---|---|---|
| **Flyway** | Verizon Connect全球统一数据库交付改用Flyway后，运维工单降90%，变更类故障降30-40% | **采用**——SQL优先、跟RuoYi的Spring Boot/Java技术栈天然契合，Matbox当前"共享表+租户ID字段"架构不需要Atlas的"每租户一库"能力 |
| Liquibase | 某风控企业250+数据库用Liquibase，部署频率提升8倍，DBA人力释放70%+ | 备选——数据库种类更多（50+ vs Flyway的20+）时更合适，Matbox当前只用PostgreSQL，用不上这个优势 |
| Atlas | 原生支持"每租户一个数据库/schema"架构，可跨多库批量变更；某航司分析公司用它做到无需人工审核的多次日更新 | **不采用**——它的核心优势针对"database-per-tenant"架构，Matbox已经确定用"共享表+租户ID字段"模式（架构原则已定），这个优势用不上 |
- **Out of Scope**：不在Stage9阶段伪造真实ReleaseArtifactID/BaselineID；不靠全量SQL覆盖升级（必须是增量迁移+可回滚）。
- **上游输入**：repo/CI/迁移脚本/配置。
- **下游输出**：签名+摘要的ReleaseArtifact证据链（含迁移摘要）。
- **页面/入口**：CI/CD / release console
- **依赖**：与REL-F001~F005共用同一套Harbor+Trivy+SLSA基础设施，逻辑上独立环节。
- **验收标准（按七层施工面，原样保留自多端平台文档，未做删减）**：
  - Frontend/UI：仅授权release owner可操作，管理端可看迁移状态/回滚证据。
  - Backend/API/Service：release元数据/baseline/验收钩子；Merge commit→build→artifact→迁移→deploy→验收全程可追溯。
  - Data/DB/Migration：Flyway+迁移摘要；不得靠重新导入最新SQL文件代替增量迁移；空库创建/上一版升级/回滚兼容性三种场景都要测试。
  - Async/Runtime：build/deploy/验收作业；验收失败不得标记ACCEPTED。
  - Provider：SBOM/CVE/签名registry；provider可替换。
  - Infra/Config：锁定运行时/依赖/配置快照，不用浮动的latest标签；CVE/secret扫描失败即阻断发布。
  - Tests/Observability：集成/回归/恢复演练；合并后新Baseline重新验收。

### REL-F007 · 灰度发布 + 自动回滚（2026-09-04补，纠正此前遗漏）
- **背景**：查证2026年真实数据发现——72%的团队报告过AI生成代码导致的生产事故，74%的AI生成代码里至少四分之一上线后需要返工，很多问题上线30天后才冒出来。这说明"①②③Gate全PASS+POST_MERGE_REVALIDATION通过"只能证明这次改动没有已知问题，证明不了它在真实流量下长期没事。REL-F004/F005已有的追溯链条和Baseline冻结，管的是"能不能查清楚现在跑的是哪个版本"，不管"新版本上线这个动作本身该怎么降低风险"，是两件不同的事。
- **目标**：新ReleaseArtifact部署时，先只切一小部分真实流量到新版本（不是全量直接切），实时监控关键指标（错误率、延迟、②&③Gate涉及的关键业务指标），指标越过预设阈值时自动把流量切回上一个稳定Baseline，不依赖人工发现后手动执行`DeployRecord.rollbackOf`。
- **In Scope**：灰度流量比例控制、`RolloutThreshold`阈值配置、自动切回逻辑、灰度过程留痕。**不含**指标的实时采集与阈值评估本身（见下方2026-09-04补充）。
- **Out of Scope**：不新建独立的灰度网关/服务网格组件——具体技术选型（如复用CI/CD平台原生的灰度能力，还是接入服务网格）留到Stage10按已选定的CI平台能力确定，本条现在只定机制和数据Contract，不绑定具体工具。
- **2026-09-04场景模拟发现的断点**：推演"灰度期间指标异常，触发自动回滚"这个场景时发现——原设计完全没写**谁在实时盯着这些指标、判断有没有超阈值**。"自动回滚"这四个字，"自动"部分的执行者是空的。查证后确认这件事不该由本模块自己另建一套监控——[Matbox_证据审计与监控_正式开发文档](Matbox_证据审计与监控_正式开发文档_V1.0-RC.md)已经有OBS-F004（高信号告警规则）和OBS-F007（生产环境持续质量漂移监测），这两个模块本来就是干"实时看指标、判断要不要报警"这件事的，本模块不重复造。**修正**：`RolloutThreshold`的评估由OBS-F004/F007负责（复用已有的OpenTelemetry+SigNoz管线），突破阈值时OBS-F004按"可行动告警"原则，直接调用本模块的`POST /release/deploys/{deployId}:rollback`（`rollbackTrigger=AUTO_THRESHOLD`），不是本模块自己再起一套监控进程去盯指标。**另发现一处联动缺口**：灰度触发的自动回滚，本质上是比"合并后逃逸"更严重的一种"逃逸"（已经影响了真实生产流量），但"运行中"R3已经定的规则（每条合并后逃逸必须回填成永久回归测试用例）没有明确提到覆盖这种情况——**修正**：`AUTO_THRESHOLD`触发的回滚必须同样回填为一条新的DQ回归测试用例，不能因为"这不是merge阶段发现的"就不算数。
- **验收标准**：①人为构造一次新版本关键指标异常的部署，验证OBS-F004/F007能正确评估出阈值被突破并调用本模块的rollback接口，本模块不需要自己实现指标采集/评估逻辑；②验证一次AUTO_THRESHOLD触发的回滚，最终在DQ的回归测试用例库里能查到对应新增的用例，不是回滚完就当没发生过；③（2026-09-04新增）人为构造一次硬指标（错误率/延迟）全部正常、但QUALITY类指标（行为/输出质量分数）异常的场景，验证系统同样能触发回滚，不是只认HARD类指标——这条直接对应真实发生过的"指标全绿但行为劣化"事故，不能只测硬指标场景就算完。

## 5｜核心数据 Contract（逻辑模型，可直接建表/建接口）

**ReleaseArtifact**
releaseArtifactId, mergeCommitSha, dependencySnapshotRef（字段名沿用质检文档F-DQ-006已定义的DependencySnapshotRef，不新造名字）, buildRunId, artifactDigest（Harbor镜像摘要）, sbomRef（对应质检文档F-DQ-006已定义的SBOMRef，指向F-DQ-006的Trivy产出，不重复存储）, provenanceRef（SLSA签名引用）, harborRepoPath, createdAt

**Baseline**
baselineId, docVersion, requirementVersion, releaseArtifactId, adapterVersions(jsonb), externalVersions(jsonb), goldenTestSetVersion, environment(sandbox|staging|production), configHash, frozenAt, immutable(true恒定)

**DeployRecord**
deployId, releaseArtifactId, baselineId, environment, deployedAt, deployedBy, rollbackOf?（指向被回滚的deployId）, **trafficPercent**（REL-F007，0-100，灰度当前放量比例）, **rollbackTrigger**（REL-F007，MANUAL|AUTO_THRESHOLD，区分是人工回滚还是自动阈值触发）, **rolledBackAt**?（REL-F007）

**RolloutThreshold**（REL-F007新增——灰度自动回滚的判定阈值配置；2026-09-04场景模拟+全球真实案例核查后扩展指标范围）
thresholdId, releaseArtifactId, metricName（如error_rate/p95_latency，**2026-09-04明确不止硬指标，也包含行为/输出质量类指标**——metricCategory区分HARD（error_rate/p95_latency等）｜QUALITY（复用OBS-F007已有的质量漂移分数，不新建第二套评分体系）), maxValue, evaluationWindow（如"5分钟滚动窗口"）, breachedAt?

**2026-09-04补充依据**：查证2025年真实事故——OpenAI一次GPT-4o更新，错误率/延迟等硬指标全部正常，但3天内模型行为明显劣化（过度谄媚），4天后被迫全量回滚；OpenAI官方复盘后明确把"模型行为问题"和安全漏洞一样列为"发布拦截项"。这条真实教训说明`RolloutThreshold`如果只配置HARD类指标，会漏掉这一整类真实发生过的问题，必须同时支持QUALITY类指标才算完整。

**MigrationRecord**（REL-F006，数据库迁移追溯，2026-08-30新增，原样保留自多端平台文档的字段定义）
migrationId, releaseArtifactId, migrationDigest, sequenceVersion, rollbackCompatible(bool), appliedAt, appliedEnvironment

**API 端点（最小集合）**
- `POST /release/artifacts` — 注册新ReleaseArtifact（CI流水线在Merge后调用）
- `GET /release/artifacts/{id}/trace` — 反查完整链条（Commit→依赖快照→构建→产物→部署）
- `POST /release/baselines` — 冻结新Baseline（不可修改，仅追加）
- `GET /release/baselines/{id}` — 查询Baseline详情，历史Baseline永久可查
- `POST /release/migrations` — 注册一次数据库迁移记录（REL-F006，CI执行Flyway后调用）
- `GET /release/migrations/{releaseArtifactId}` — 查询某ReleaseArtifact关联的迁移历史
- `PUT /release/deploys/{deployId}/traffic` — （2026-09-04新增，REL-F007）调整灰度放量比例
- `POST /release/deploys/{deployId}/thresholds` — （2026-09-04新增，REL-F007）设置该次部署的自动回滚阈值
- `POST /release/deploys/{deployId}:rollback` — （2026-09-04新增，REL-F007）执行回滚，rollbackTrigger记录是MANUAL还是AUTO_THRESHOLD触发

## 6｜P0 冻结规则

1. ReleaseArtifact 被覆盖或事后修改：不可降级 P0。
2. Baseline 历史 PASS 记录被删除或篡改：不可降级 P0。
3. 声称"已发布验证"但追溯链条任一环节缺失：不允许，必须标注为未完成验证。
4. （2026-09-04新增，REL-F007）新版本部署未经灰度直接100%切量，且未配置任何RolloutThreshold：不允许，除非Release Owner显式标注该次发布豁免（如紧急安全补丁），豁免必须留痕。

## 7｜当前唯一继续断点

Stage 10（真实部署 Harbor，接通 CI 生成真实 SLSA 签名）尚未开始，且依赖 CI 平台选型（尚未确定）。下一步：确定 CI 工具、实际部署 Harbor、把 REL-F001~F007 转成 WorkPackage；REL-F007的具体灰度技术方案（复用CI平台原生能力还是接入服务网格）需等CI平台选型确定后才能定，现在只定了机制和数据Contract。

## 附录｜来源

- [Best SBOM Tools 2026: Syft Leads OSS](https://appsecsanta.com/sca-tools/sbom-tools-comparison)
- [From Source Code to Trusted Release: Building Immutable Artifacts](https://medium.com/@sharathkumarlokesh/from-source-code-to-trusted-release-building-immutable-artifacts-with-versioning-packaging-and-daa5e8476951)
- [The 2026 Guide to Software Supply Chain Security](https://cloudsmith.com/blog/the-2026-guide-to-software-supply-chain-security-from-static-sboms-to-agentic-governance)
- [Choosing a Container Registry in 2026: Docker Hub vs ECR vs Harbor](https://shipyard.build/blog/container-registries/)
- [Container Registry Comparison 2026: 12 Options Ranked](https://distr.sh/blog/container-image-registry-comparison/)
- REL-F006 内容来源：《Matbox_多端平台_CURRENT_正式开发文档_V3.0》F-RELEASE-001 章节（2026-08-30 核对合并，详见架构原则第31条）
- REL-F006 设计独立核实（2026-08-30，按12条完整核对表执行，非单次搜索）：Flyway截至2026年仍在活跃维护（v13，Redgate），且对Spring Boot+PostgreSQL/MySQL技术栈（RuoYi正是此栈）是明确推荐选择；已补充Liquibase/Atlas的候选/结论对比表（含真实生产案例数据），确认Atlas的多租户优势面向"每租户一库"架构，跟Matbox已定的"共享表+租户ID"模式不匹配，Flyway仍是合适选择——[Flyway vs. Liquibase: The Definitive Comparison in 2026](https://www.bytebase.com/blog/flyway-vs-liquibase/)、[Atlas vs Liquibase: Why Modern Teams Choose Atlas](https://atlasgo.io/guides/atlas-vs-liquibase)
- REL-F007 并入依据（2026-09-04，用户核对"运行中"设计时发现的真实缺口）：[How to Monitor AI Generated Code Quality in Production](https://blog.exceeds.ai/monitor-ai-code-quality-production/)、[Canary Deployment for AI Models: A 2026 Guide — MLflow](https://mlflow.org/articles/what-is-canary-deployment-ai)、[Agent Rollout Strategies in 2026: The Four-Stage Gate](https://futureagi.com/blog/agent-rollout-strategies-2026/)
- RolloutThreshold扩展至QUALITY类指标依据（2026-09-04，用户要求多轮深查现在的数据、看成熟公司真实做法）：[OpenAI: Expanding on what we missed with sycophancy](https://openai.com/index/expanding-on-sycophancy/)、[OpenAI rolls back ChatGPT's sycophancy — VentureBeat](https://venturebeat.com/ai/openai-rolls-back-chatgpts-sycophancy-and-explains-what-went-wrong)
