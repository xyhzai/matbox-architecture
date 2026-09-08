# Matbox 租户与权限体系（F-TENANT-001）

正式开发文档 · V1.0-RC · 2026-08-29

## 当前定位

本专项解决"谁能看到什么数据、谁能做什么操作"的问题，覆盖人类用户和 AI 员工两类身份。是 Platform Core 的共享能力，架构原则第2、4条明确要求的"企业级多租户""数据隔离"由本模块落地。

**这是本次自我复查（非用户提出）新发现的缺口**——之前只有原则性要求，从未设计具体方案。RC5 文档明确把"跨Tenant数据访问或隔离失效"列为不可降级 P0 风险，优先级高于成本控制。

**DocID**: MATBOX-TENANT-GATE-20260829-V1.0-RC
**状态**: DRAFT_RESEARCH_COMPLETE
**2026-08-30 与 F-PLAT-001 分工确认**：《Matbox_多端平台_CURRENT_正式开发文档_V3.0》里的F-PLAT-001（Tenant/Identity/RBAC/Session Hardening）跟本模块管的都是"权限/租户"，容易混——查证2026年AuthN/AuthZ分离最佳实践（身份提供方管登录会话，策略决策点如OPA管操作判断；AI Agent更要求授权跟人类身份分开管理）后确认：**本模块（F-TENANT-001）只管AI员工鉴权(OPA)+数据隔离；F-PLAT-001管人类登录/会话安全(MFA/SSO/密码找回/设备管理)**，两个都保留，不合并，互相通过AuthContext契约调用（详见架构原则第31条）。

## 1｜不可变原则

1. 任一租户（未来的客户/商家/品牌方）不得看到另一租户的数据，这是最高优先级安全红线，不允许任何"临时绕过"。
2. 人类用户和 AI 员工的权限判定用同一套底层规则，不搞两套平行系统。
3. AI 员工默认零权限，每次任务临时获得"只够做这件事"的授权，任务结束权限自动收回——与 F-CRED-001 的短期凭据机制配合。
4. 权限判断逻辑要能被审计追溯（依赖 F-OBS-001）：谁在什么时候被允许/拒绝做了什么，必须可查。

## 2｜全球调研结论（2026-08-29）

### 2.1 关键决策：复用已有的 OPA，不引入新工具

F-DQ-008（质检系统的策略引擎）已经采用 OPA 做 GatePolicy 判定。查证后确认：**OPA 正是 2026 年"细粒度策略判断"领域的主流选择**，尤其适合 AI 员工场景——传统角色权限（RBAC）给 AI 员工分配角色容易"角色爆炸"（每个AI、每个仓库都要建一个角色，管理员看不过来），OPA 的策略式判断能更好应对这个问题。

**结论：Matbox 的权限判断统一复用 OPA，不新增第二套策略引擎。**

### 2.2 人类用户：简单角色权限（RBAC）已经够用

查证确认：团队规模小（2人）、角色种类少、不需要精确到每个资源单独设置权限时，简单 RBAC 就够，上复杂的细粒度授权系统（FGA）反而是负担。**人类用户用简单角色（管理员/成员，以及 RC5 已定义的 Feature Owner/Implementer/Reviewer/Acceptance Owner 等项目角色）。**

### 2.3 租户隔离核心模式

业界标准做法：租户身份（TenantID）写入登录令牌（JWT），每次请求都校验"当前操作的数据"和"当前登录者所属租户"是否一致；数据库层面用"共享表+租户ID字段"的模式起步（够用、简单），不需要一开始就上"每个租户独立数据库"这种重量级方案。

### 2.4 AI 员工授权模式

延续 F-CRED-001 已确认的原则：AI 员工任务开始时零权限，按任务临时授予窄范围权限，任务结束自动收回，可随时秒级撤销。

### 2.5 匿名访客身份（2026-08-30从"AI员工能力缺口调研清单"#9并入，仅身份/权限层，不含独立站页面设计）

查证确认：Auth0 在2026年正式把"Anonymous Sessions"（匿名会话）做成付费计划的Beta能力，支持访客先用无状态的匿名会话做浏览/加购物车/预登录个性化，登录后再把匿名会话数据"链接"到已认证用户身份——这是2026年行业标准做法，不是Matbox自己发明的模式。**结论**：独立站的终端消费者（未登录）需要一个新的principalType——`AnonymousVisitor`：会话级、租户绑定（属于访问的那个厂商租户）、默认零信任，只允许显式加入allowlist的只读公开数据访问（如浏览该租户标记为public的产品目录、跟该租户的公开AI员工对话），不允许任何写操作或跨租户数据访问；访客后续填写联系方式/下单时，触发"身份升级"，把匿名会话关联到一个正式Contact/Lead身份，会话期间的上下文不丢失。**范围说明**：本条只解决"匿名访客要不要有身份、这个身份能做什么"，不涉及独立站具体页面/路由/内容分发设计——那部分需要用户尚未发送的"独立站"业务包，属于F-CHANNEL-001/F-MULTIEND-001/F-PAGE-001范围，明确不在本次执行内。

## 3｜Own / Reuse / Must Not Rebuild

| 类型 | 对象 | 说明 |
|---|---|---|
| OWN | TenantID模型、角色定义、权限判断业务规则 | Matbox 自己的租户/权限业务逻辑 |
| REUSE | OPA 策略引擎（已在F-DQ-008采用） | 不新增第二套策略引擎 |
| MUST NOT REBUILD | JWT/会话令牌标准 | 用现成成熟方案，不自造认证协议 |

## 4｜Feature Register

| FeatureID | 名称 | 说明 |
|---|---|---|
| TENANT-F001 | 租户身份与会话模型 | TenantID嵌入登录令牌，每次请求校验 |
| TENANT-F002 | 人类用户角色权限 | 简单RBAC，管理员/成员 + RC5项目角色 |
| TENANT-F003 | AI员工策略授权 | 复用OPA，零权限起步+按任务临时授权 |
| TENANT-F004 | 数据隔离实现 | 共享表+租户ID字段模式，防跨租户查询 |
| TENANT-F005 | 权限决策审计接入 | 接入F-OBS-001，权限判断可追溯 |
| TENANT-F006 | 匿名访客身份与权限（Anonymous Visitor） | 独立站未登录终端消费者的会话级身份，默认零信任+只读allowlist，可升级为正式Contact身份 |

### TENANT-F001 · 租户身份与会话模型
- **目标**：每个登录会话明确知道"属于哪个租户"，所有后续操作都带这个上下文。
- **验收标准**：跨租户请求（用A租户身份查B租户数据）必须被拒绝。

### TENANT-F002 · 人类用户角色权限（2026-08-30从AI员工底层包补强角色定义）
- **目标**：本人+同事等人类用户按角色分配权限，不需要逐个资源单独配置。角色定义采纳AI员工底层`auth_rbac_abac.md`已核实过的分层：**TenantOwner**(租户级配置+计费，不能读平台secret)、**TenantAdmin**(员工生命周期/策略/工具/审批)、**EmployeeOwner**(管理自己名下的AI员工，查看其运行/成本)、**Operator**(可启动/取消/接管允许的任务)、**Reviewer**(可对配置的审批类型做决定)、**Viewer**(只读)、**PlatformAdmin**(平台运维，访问租户数据须走break-glass留痕)。
- **验收标准**：角色变更后权限立即生效，可追溯变更记录；PlatformAdmin访问租户数据必须走时限+理由+不可篡改审计的break-glass流程，不能用平台管理员身份静默查看租户数据。

### TENANT-F003 · AI员工策略授权（2026-08-30补强ABAC属性与强制拒绝规则）
- **目标**：每个AI员工任务开始时零权限，通过OPA策略临时授予任务所需的最小权限集合，任务结束/超时自动收回。ABAC决策所需属性采纳AI员工底层已定义的集合：`tenant_id/resource_type/resource_owner/employee_id/risk_level/data_classification/action/environment/time_window/delegated_scope`。
- **依赖**：F-CRED-001（AI员工身份+短期凭据，含CRED-F008 AgentIdentity持久身份层）。
- **强制拒绝规则（2026-08-30从AI员工底层包并入，不可降级）**：跨租户访问默认DENY；委派权限放大（delegated scope超过源身份授权范围）默认DENY；Risk 4/5的有副作用动作没有Approval默认DENY；过期的身份/会话/凭证默认DENY。
- **验收标准**：AI员工任务结束后，尝试用旧权限访问必须被拒绝；上述4条强制拒绝规则各自有可执行的对抗测试用例。

### TENANT-F004 · 数据隔离实现
- **目标**：数据库层面按租户隔离，同一张表里不同租户的数据互不可见。
- **验收标准**：人为构造跨租户查询尝试，必须被数据层拦截，不能只依赖应用层代码"记得加过滤条件"。

### TENANT-F005 · 权限决策审计接入
- **目标**：每次权限允许/拒绝的判断都留痕，接入F-OBS-001。
- **验收标准**：任意一次拒绝访问的事件，能查到是谁/什么身份/试图做什么/为什么被拒绝。

### TENANT-F006 · 匿名访客身份与权限（2026-08-30从调研清单#9并入，仅身份/权限层）
- **目标**：独立站未登录终端消费者拿到一个会话级的`AnonymousVisitor`身份，绑定发起访问的那个租户，默认零权限，仅允许显式加入allowlist的只读公开数据访问；填写联系方式/下单等动作触发身份升级，关联到正式Contact身份，会话上下文不丢失。
- **依赖**：F-CRED-001（CRED-F009，匿名访客会话的签发/升级实现）。
- **验收标准**：匿名访客尝试访问allowlist之外的资源或其他租户数据必须被拒绝；身份升级后原会话的上下文（如AI对话历史）能正确关联到新的Contact身份，不丢失也不误关联到别人。

## 5｜核心数据 Contract（逻辑模型，可直接建表/建接口）

**Tenant**
tenantId, name, createdAt, status(ACTIVE|SUSPENDED)

**Session**（人类用户）
sessionId, userId, tenantId, role(admin|member), issuedAt, expiresAt, jwtClaims(jsonb)

**PolicyDecision**（OPA评估结果，每次判断都记录，2026-08-30新增visitor主体类型）
decisionId, subjectType(human|agent|visitor), subjectId, tenantId, action, resourceType, resourceId, result(ALLOW|DENY), policyVersion, reasonCode, timestamp, evidenceBundleRef（写入F-OBS-001，字段名统一沿用质检文档已有的evidenceBundleRef）

**（不新建匿名访客身份表）** `AnonymousVisitor`的会话/身份数据以 F-CRED-001 的 `AnonymousVisitorSession`（CRED-F009）为唯一事实源，本模块只做OPA鉴权判断，不复制一份数据。

**（不新建AI员工授权表）** AI员工的授权范围以 F-CRED-001 的 `AgentCredentialGrant`（grantId/scope[]）为唯一事实源——本模块不复制一份。OPA做鉴权判断时，通过 grantId 向 F-CRED-001 查询该Grant的 scope，再evaluate是否允许当前action/resource，避免同一份数据在两个模块各存一份。

**API 端点（最小集合）**
- `POST /tenant/sessions` — 人类用户登录，创建会话并签发带TenantID的JWT（对应TENANT-F001）；密码校验走F-CRED-001，本接口只负责登录成功后的会话/令牌签发，不重复实现密码验证
- `POST /tenant/authz/check` — 核心鉴权接口，输入{subjectId, tenantId, action, resource, grantId?}，输出ALLOW/DENY+原因；若subjectType=agent，内部先调用 `GET /cred/agent-grants/{grantId}`（F-CRED-001提供）取scope，再转发OPA评估
- `GET /tenant/{tenantId}/roles` — 查询租户内人类用户角色配置
- `PUT /tenant/{tenantId}/users/{userId}/role` — 分配/修改人类用户角色（对应TENANT-F002），变更写入PolicyDecision同源的审计记录，可追溯

## 6｜P0 冻结规则（不可降级）

1. 跨租户数据访问或隔离失效：不可降级 P0，最高优先级。
2. 权限绕过（人类或AI员工获得超出其应有范围的访问）：不可降级 P0。
3. AI 员工权限任务结束后未被收回，造成"僵尸权限"残留：不可降级 P0。
4. 匿名访客（AnonymousVisitor）被授予allowlist之外的访问权限，或访问到其他租户/其他访客的数据：不可降级 P0。

## 7｜当前唯一继续断点

Stage 10（真实实现租户隔离+OPA策略、接入真实数据库）尚未开始，依赖 F-CRED-001（AI员工身份）已完成、F-OBS-001（审计）已完成。下一步：把 TENANT-F001~F005 转成 WorkPackage。

## 附录｜来源

- [How to design an RBAC model for multi-tenant SaaS — WorkOS](https://workos.com/blog/how-to-design-multi-tenant-rbac-saas)
- [Architecting Secure Multi-Tenant Data Isolation](https://medium.com/@justhamade/architecting-secure-multi-tenant-data-isolation-d8f36cb0d25e)
- [The best authorization platforms for managing AI agent permissions in 2026 — WorkOS](https://workos.com/blog/best-authorization-platforms-ai-agent-permissions-2026)
- [Top Open-Source Authorization Tools for Enterprises in 2026](https://www.permit.io/blog/top-open-source-authorization-tools-for-enterprises-in-2026)
- [RBAC vs ABAC vs ReBAC: Choosing an Authorization Model](https://guptadeepak.com/ciam-compass/guides/rbac-vs-abac-vs-rebac/)
- [Authorization for Agents | OpenFGA](https://openfga.dev/docs/modeling/agents)
- **角色定义/ABAC属性/强制拒绝规则依据（2026-08-30）**：《Matbox_AI_Employee_System_V6.3_Final_Frozen》底层包`08_质量安全成本/security/auth_rbac_abac.md`、WP-002定义
- **TENANT-F006匿名访客身份依据（2026-08-30）**：[Matbox_AI员工能力缺口调研清单_2026-08-30.md](Matbox_AI员工能力缺口调研清单_2026-08-30.md)#9；Auth0 Changelog（2026年Anonymous Sessions Beta，付费计划）；[Auth0 Community — Anonymous Users](https://community.auth0.com/t/anonymous-users/65009)
