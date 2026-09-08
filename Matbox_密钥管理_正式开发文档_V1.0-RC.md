# Matbox 密钥与凭据管理（F-CRED-001）

正式开发文档 · V1.0-RC · 2026-08-29

## 当前定位

本专项解决 Matbox 所有"密码/密钥/Token"（GitHub 凭据、AI 模型 API Key、数据库密码、云服务凭据等）的统一存取问题。是 Platform Core 的共享能力，被 F-DQ-003（SonarQube）、F-DQ-005（Betterleaks）、F-DQ-012（AI Review）等已有模块直接依赖，也是未来 Provider Router、Agent Runtime 的前提。

**DocID**: MATBOX-CRED-GATE-20260829-V1.0-RC
**状态**: DRAFT_RESEARCH_COMPLETE（已完成全球选型调研，未进入 Stage 10 真实施工）
**依赖方（已知阻塞）**: F-DQ-003、F-DQ-005、F-DQ-012
**2026-08-30 补充**：新增 CRED-F007（企业第三方集成凭证），来自《Matbox_多端平台_CURRENT_正式开发文档_V3.0》F-CRED-001 章节——该文档最初也用了 F-CRED-001 这个编号，但管的是完全不同的一件事（企业连第三方服务的OAuth凭证，不是AI员工的临时Token）。核对后确认：这是一件真实存在、原来的CRED-F001~F006没覆盖到的新能力，不是重复定义，所以并入本文档当新Feature，不单独占用F-CRED-001编号（详见架构原则第31条）。

## 1｜不可变原则

1. 任何密钥不得出现在代码、Prompt、日志、聊天记录、Word/Excel 文档、Artifact 中——这是不可降级 P0，一旦发生按安全事故处理。
2. AI 员工（Codex/Claude 等）不得被直接告知真实密钥明文；能不给就不给，能只给"临时通行证"就不给"永久钥匙"。
3. 人类用户和 AI 员工都必须有各自独立的身份，不能共用一个账号/密钥登录任何系统。
4. 密钥的"存放工具"（Infisical）可以换，但"谁能访问什么、访问记录"这套规则是 Matbox 自己的，不依赖工具本身的实现。

## 2｜全球调研结论（2026-08-29）

### 2.1 存放工具选型

| 候选 | License | 结论 |
|---|---|---|
| HashiCorp Vault | BSL 1.1（2023年从MPL 2.0改为半开源） | **淘汰**——与"不绑定单一供应商/协议"原则冲突 |
| OpenBao | MPL-2.0（Linux基金会治理，Vault开源分支） | 备选，动态凭据机制成熟，但对当前团队规模偏重 |
| **Infisical** | **MIT（真开源）** | **采用**——小团队友好，不需要专职运维 |

**已知短板**（选型时接受的代价，不是忽略）：
- 不支持数据库密码自动轮换，需要额外自建轮换逻辑
- 权限粒度只到"项目"级别，不能精确到单个密钥——因此 Matbox 侧必须用"一个敏感用途一个项目"的方式弥补，而不是把所有密钥堆进一个项目
- 自建部署 = 自己维护更新和备份，没有厂商兜底支持（除非付费）

### 2.2 AI 员工凭据管理标准（2026年）

1. **短期化**：AI 员工用的凭据必须是临时的，任务做完就失效，不能是永久有效的密钥。
2. **最小权限化**：只给这次任务需要的那一小块权限，不给"万能钥匙"。
3. **代理注入优于直接下发**：更安全的做法是 AI 员工全程不知道真实密钥是什么，由中间层代它去调用外部系统，AI 员工只知道"调用结果"，密钥本身对它不可见。
4. **每个 AI 员工独立身份**：不同的 AI 员工/不同任务要用不同的身份标识，方便事后审计"是哪个 AI 干的"。
5. **OAuth 2.1 + OIDC**：这是行业推荐的认证标准，Anthropic 官方的 MCP 协议也推荐这套，与 Matbox 用 Claude 做 AI 员工的现状直接吻合。

## 3｜Own / Reuse / Must Not Rebuild

| 类型 | 对象 | 说明 |
|---|---|---|
| OWN | CredentialRef、AccessPolicy、AgentIdentity、AccessLog | Matbox 自己的凭据引用和策略规则 |
| REUSE | 实际密钥存储、加密、基础访问接口 | 直接用 Infisical，不重新造存储引擎 |
| MUST NOT REBUILD | 加密算法本身 | 不自己写加密逻辑，用 Infisical/OpenBao 已验证的实现 |

## 4｜Feature Register

| FeatureID | 名称 | 说明 |
|---|---|---|
| CRED-F001 | Infisical 集成适配器 | 连接自建 Infisical 实例，项目/环境结构设计 |
| CRED-F002 | 人类用户访问控制 | 团队成员（本人+1位同事）的权限分配 |
| CRED-F003 | AI 员工身份签发 | 每个 AI Agent 的独立身份 + 短期限权 Token 签发 |
| CRED-F004 | 运行时代理注入 | AI 员工调用外部系统时，密钥不经过 AI 员工本身，由中间层代理注入 |
| CRED-F005 | Token 生命周期与轮换 | 过期、轮换、撤销规则 |
| CRED-F006 | 访问审计日志 | 谁/什么在什么时候访问了什么密钥，接入 F-OBS-001 |
| CRED-F007 | 企业第三方集成凭证（Integration Credential Vault） | 企业连第三方服务（非AI员工/非人类账号）的OAuth凭证，2026-08-30从多端平台文档并入 |
| CRED-F008 | AgentIdentity 持久身份层 | AI员工的持久身份（跟着EmployeeInstance走），跟CRED-F003的任务级临时Grant是两层不同的东西，2026-08-30从AI员工底层包核对后补充 |
| CRED-F009 | 匿名访客会话身份（Anonymous Visitor Session） | 独立站未登录消费者的会话级临时身份，可升级关联到正式Contact身份，2026-08-30从调研清单#9并入 |

### CRED-F001 · Infisical 集成适配器
- **目标**：Matbox 后端统一通过这一层读写密钥，不直接裸调用 Infisical API。
- **依赖**：无前置阻塞（Infisical 自身部署不依赖 Matbox 其他模块）。
- **验收标准**：任何模块要读密钥，必须经过这一层；直接硬编码或裸调用视为违规，对应 F-DQ-007 架构守卫的检查项之一。

### CRED-F002 · 人类用户访问控制
- **目标**：本人和技术同事分别用独立账号登录，权限按"项目"划分（GitHub凭据一个项目、AI模型Key一个项目、数据库密码一个项目……），弥补 Infisical 权限粒度不到单个密钥的短板。
- **验收标准**：两人账号互相独立，可单独查日志区分谁做的操作。

### CRED-F003 · AI 员工身份签发
- **目标**：每个 AI Agent（Codex 施工、Claude 审核等）任务开始时领取一个短期 Token，任务结束或超时自动失效，权限只覆盖这次任务范围。
- **验收标准**：Token 默认有效期不超过单次任务预期时长；同一 AI 员工不同任务的 Token 互不复用。
- **与CRED-F008的关系（2026-08-30核对AI员工底层包后明确）**：AgentCredentialGrant（本Feature）是**任务级、短期**的临时授权，每次任务开始新签发；AgentIdentity（CRED-F008）是**员工级、持久**的身份，跟着F-AIEMP-001的EmployeeInstance走，不随单次任务变化。关系是：一个AgentIdentity在其生命周期内会申请很多个AgentCredentialGrant（每次任务一个），AgentIdentity被Revoke时，其名下所有未过期的Grant必须同步失效——这是两层不同粒度的东西，不能合并成一张表，也不能把AgentIdentity误当作另一种"更长期的Token"来用（长期Token本身违反不可变原则第4条）。

### CRED-F004 · 运行时代理注入
- **目标**：AI 员工的 Prompt、日志、生成的代码里，任何情况下都不出现真实密钥字符串；调用外部系统时由 Matbox 后端代为注入密钥，AI 员工只拿到调用结果。
- **验收标准**：对 AI 员工的输出做扫描（复用 F-DQ-005 Betterleaks），0 泄露。这是不可降级 P0。

### CRED-F005 · Token 生命周期与轮换
- **目标**：定义各类密钥的轮换周期（人类账号密码、AI Token、第三方API Key各自的策略）；Infisical 不支持的自动轮换（如数据库密码）需要额外脚本实现。
- **验收标准**：轮换记录可追溯，轮换失败有告警，不能"改了但不知道"。

### CRED-F006 · 访问审计日志
- **目标**：所有密钥访问都留痕，接入 F-OBS-001（尚未建成前先本地记录，F-OBS-001 建成后迁移）。
- **验收标准**：任意一次密钥访问，能查到"谁/什么身份/什么时间/访问了什么/做了什么操作"。

### CRED-F007 · 企业第三方集成凭证（Integration Credential Vault，2026-08-30新增）
- **目标**：企业连接第三方服务（非AI员工用、非人类账号密码）的OAuth凭证，永不进入模型/日志/普通业务表。跟CRED-F001~F006管的"AI员工临时Token/人类账号"是两类不同的密钥使用场景，但都用Infisical存，不新增第二套存储。
- **In Scope**：tenant+integration credential ref；KMS加密；OAuth refresh/rotation/revoke；last-used记录；redaction。
- **Out of Scope**：不保存明文token；不把secret放进Tool的输入/prompt里。
- **上游输入**：企业方发起的集成设置/OAuth回调。
- **下游输出**：credentialRef + 运行时注入句柄。
- **页面/入口**：`/settings/integrations`
- **依赖**：无前置阻塞（跟CRED-F001~F006共用同一套Infisical实例，逻辑上独立）。
- **验收标准（按七层施工面，原样保留自多端平台文档，未做删减）**：
  - Frontend/UI：连接/断开/权限scope/健康状态可见，不回显secret；UI永不获得真实token，revoke即时生效。
  - Backend/API/Service：CredentialVaultService/OAuth回调/运行时注入；模型/业务service不得直接读secret；secret redaction + 过期/撤销token拒绝。
  - Data/DB/Migration：只存集成元数据+加密ref/版本，不存明文secret；DB dump无可用明文credential。
  - Async/Runtime：refresh/rotation过期提醒；AI任务不得自己刷新token；重复refresh幂等、race受控。
  - Provider：OAuth/KMS/Secret Manager适配器；业务代码不绑定provider token格式；provider可替换测试。
  - Infra/Config：KMS密钥/轮换/IAM；Git/env里不留长期明文secret；最小权限+轮换演练。
  - Tests/Observability：secret泄露扫描/撤销/轮换/审计测试；日志/错误/证据0 secret泄露。

### CRED-F008 · AgentIdentity 持久身份层（2026-08-30从AI员工底层包并入）
- **目标**：每个F-AIEMP-001的EmployeeInstance绑定一个持久AgentIdentity，作为该AI员工在鉴权体系里的真实主体，与F-TENANT-001的RBAC/ABAC判定共用同一个身份概念（principal_type统一区分HumanUser/ServiceAccount/AgentIdentity/PlatformAdmin）。
- **验收标准**：AgentIdentity被Revoke/Retire时，名下所有未过期的AgentCredentialGrant必须在同一事务或紧随的补偿动作里同步失效；delegated_by字段记录委派链条，委派产生的Identity权限不得超过源Identity授权范围（对应F-ACTION-001 ACTION-F005的委派权限检查）。

### CRED-F009 · 匿名访客会话身份（2026-08-30从调研清单#9并入）
- **目标**：独立站未登录消费者访问时签发一个会话级、租户绑定的匿名身份，只带极窄的默认权限（对应F-TENANT-001 TENANT-F006的allowlist判定）；访客后续留资/下单时，把该会话身份"升级"关联到正式Contact身份，会话期间产生的上下文（如AI对话历史）随之转移，不丢失。
- **依据**：查证Auth0 2026年"Anonymous Sessions"（Beta，付费计划）模式——无状态匿名会话支持访客浏览/加购/预登录个性化，登录后通过账号关联把匿名数据合并到已认证身份，这是行业当前标准做法。
- **Out of Scope**：不涉及独立站具体页面/路由设计（依赖用户尚未提供的"独立站"业务包，属F-CHANNEL-001/F-PAGE-001范围）；不允许匿名会话被授予Risk 3级以上的有副作用权限。
- **验收标准**：匿名会话默认权限只覆盖只读allowlist（如浏览public产品目录、跟该租户公开AI员工对话）；身份升级后原会话上下文正确关联到新Contact身份且不可被其他访客冒领；会话过期或长时间不活跃后自动失效。

## 5｜核心数据 Contract（逻辑模型，可直接建表/建接口）

**SecretRef**
secretRefId, tenantId, infisicalProjectId, infisicalPath, secretType(scm_token|model_api_key|db_password|other), owningModule, createdAt, lastRotatedAt, rotationPolicyId, status(ACTIVE|ROTATING|REVOKED)

**AgentCredentialGrant**（AI员工临时授权，核心表，任务级/短期）
grantId, agentId, workPackageId, tenantId, scope[]（资源+action粒度）, issuedAt, expiresAt, revokedAt?, status(ACTIVE|EXPIRED|REVOKED), issuedByPolicyId, identityRef（关联AgentIdentity，2026-08-30新增字段）, evidenceBundleRef（写入F-OBS-001，字段名统一沿用质检文档已有的evidenceBundleRef）

**AgentIdentity**（员工级/持久，完整定义见[Matbox_AI员工身份_正式开发文档](Matbox_AI员工身份_正式开发文档_V1.0-RC.md)第5节，此处只列跟本模块相关的字段）
identityId, tenantId, principalType(HUMAN|SERVICE|AGENT|PLATFORM_ADMIN), ownerId, scopes{}, delegatedBy?, expiresAt?, status(ACTIVE|REVOKED)

**HumanAccessGrant**
grantId, userId, tenantId, role(admin|member), grantedProjects[]（对应2.2节按用途分项目）, grantedAt, grantedBy

**RotationPolicy**
policyId, secretType, rotationIntervalDays, autoRotate(bool)（Infisical原生不支持DB密码自动轮换，此字段为false时走Feature CRED-F005的外部轮换脚本）, lastRunAt, nextRunAt

**CredentialAccessEvent**（审计事件，写入F-OBS-001，不在本模块自己存储）
eventId, actorType(human|agent), actorId, secretRefId, action(read|rotate|revoke), tenantId, result(ALLOW|DENY), timestamp, reasonCode?

**IntegrationCredentialRef**（CRED-F007，企业第三方集成OAuth凭证，2026-08-30新增，原样保留自多端平台文档的字段定义）
credentialRefId, tenantId, integrationType, kmsKeyRef（加密存储引用）, oauthRefreshTokenRef, scope[], status(ACTIVE|EXPIRED|REVOKED), lastUsedAt, issuedAt, expiresAt?, rotatedAt?

**AnonymousVisitorSession**（CRED-F009，独立站匿名访客会话身份，2026-08-30新增）
visitorSessionId, tenantId, channel（如INDEPENDENT_SITE，具体渠道枚举随"独立站"业务包到达后细化）, scopeAllowlist[]（只读，如catalog_view/public_ai_chat）, linkedContactId?（升级后关联的正式Contact，未升级为null）, createdAt, lastActiveAt, expiresAt, status(ACTIVE|EXPIRED|LINKED)

**API 端点（最小集合）**
- `POST /cred/agent-grants` — 为AgentID+WorkPackageID申请临时授权，返回grantId+短期token
- `GET /cred/agent-grants/{grantId}` — 查询某Grant的scope/状态（供F-TENANT-001的OPA鉴权判断调用，AI员工授权以此为唯一事实源，不在TENANT模块另存一份）
- `DELETE /cred/agent-grants/{grantId}` — 提前撤销
- `GET /cred/secrets/{secretRefId}` — 按SecretRef取值（内部服务调用，经TENANT-F003策略校验，返回值不落日志）
- `POST /cred/rotate/{secretRefId}` — 触发轮换
- `POST /cred/integrations` — 发起第三方集成OAuth连接（CRED-F007）
- `DELETE /cred/integrations/{credentialRefId}` — 断开集成，撤销凭证
- `GET /cred/integrations/{credentialRefId}/status` — 查询集成健康状态（不返回secret本身）
- `POST /cred/visitor-sessions` — 为独立站未登录访客签发匿名会话身份（CRED-F009），返回visitorSessionId+默认allowlist
- `POST /cred/visitor-sessions/{visitorSessionId}/link` — 访客留资/下单时，把匿名会话升级关联到正式Contact身份，会话上下文随之转移

## 6｜P0 冻结规则

1. 密钥明文出现在代码/Prompt/日志/文档/Artifact中：不可降级 P0，立即按安全事故处理。
2. AI 员工被直接告知真实密钥明文：不可降级 P0。
3. 人类账号和 AI 身份共用同一凭据：不允许。
4. Token 无过期时间（永久有效）用于 AI 员工：不允许，除非产品/业务明确决定并留痕（届时需要用户本人拍板，不是技术问题）。
5. 匿名访客会话（CRED-F009）被授予allowlist之外的权限，或永不过期：不允许。

## 7｜当前唯一继续断点

Stage 10（绑定真实 Infisical 实例与真实 Matbox Repo）尚未开始。下一步：实际部署 Infisical、定义具体项目/环境结构、把 CRED-F001~F007 转成 WorkPackage 交给施工。

## 附录｜来源

- [Top 16 Secrets Management Tools and Platforms for 2026](https://blog.gitguardian.com/top-secrets-management-tools/)
- **CRED-F008 AgentIdentity依据（2026-08-30）**：《Matbox_AI_Employee_System_V6.3_Final_Frozen》底层包`08_质量安全成本/security/auth_rbac_abac.md`、`04_Domain_Schema/migrations/001_core.sql`（agent_identity表）、WP-002定义
- [OpenBao vs HashiCorp Vault](https://lalatenduswain.medium.com/openbao-vs-hashicorp-vault-the-secrets-management-showdown-every-devops-team-needs-to-read-in-2026-458ae0d9a408)
- [Open Source Secrets Management for DevOps in 2026 (Infisical)](https://infisical.com/blog/open-source-secrets-management-devops)
- [Infisical Review 2026](https://cybersecurityo.com/secrets-management/infisical-review/)
- [AI Agent Secrets Management: Best Practices for 2026](https://fast.io/resources/ai-agent-secrets-management/)
- [Credential Injection Patterns for AI Agents](https://agentgateway.dev/blog/2026-07-27-credential-injection-ai-agent-egress-cb4a/)
- [How to manage API keys, tokens, and secrets for AI agents — WorkOS](https://workos.com/blog/ai-agent-secrets-management)
- CRED-F007 内容来源：《Matbox_多端平台_CURRENT_正式开发文档_V3.0》F-CRED-001 章节（2026-08-30 核对合并，详见架构原则第31条）
- CRED-F007 设计独立核实（2026-08-30，按12条完整核对表执行，非单次搜索）：KMS加密+OAuth refresh/rotation这套设计经查证与2026年标准做法一致；查到真实攻击案例佐证"token加密存储+运行时代理注入"设计的必要性——被盗的第三方集成token能绕过SSO/MFA横向渗透（SaaS-to-SaaS攻击）。**待办已解决（2026-09-02）**：原待办"认证/凭证管理可以全球统一路由，只有业务数据才需要按地区强制隔离"这条判断已被架构原则第40条正式确认——服务器地区大方向定为中国区(阿里云/腾讯云)+欧盟区(欧盟本地云)混合架构，认证/凭证这类控制层可以全球共用一套，密钥/凭证服务本身不需要按地区拆分部署，本模块现有设计不需要改动——[Refresh Token Security: Best Practices for OAuth Token Protection](https://www.obsidiansecurity.com/blog/refresh-token-security-best-practices)、[Why authentication doesn't need to stay local — WorkOS](https://workos.com/blog/data-residency-for-enterprise-saas)、[Matbox_架构设计原则.md](Matbox_架构设计原则.md)第40条
- **CRED-F009匿名访客会话依据（2026-08-30）**：[Matbox_AI员工能力缺口调研清单_2026-08-30.md](Matbox_AI员工能力缺口调研清单_2026-08-30.md)#9；Auth0 Changelog（2026年Anonymous Sessions Beta）；[Auth0 Community — Anonymous Users](https://community.auth0.com/t/anonymous-users/65009)
