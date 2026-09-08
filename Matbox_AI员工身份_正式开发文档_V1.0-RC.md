# Matbox AI 员工身份 / AI Employee Identity（F-AIEMP-001）

正式开发文档 · V1.0-RC · 2026-08-30

## 当前定位

本专项解决"企业怎么配置一个AI员工——它有什么角色、用什么模型策略、能调用哪些工具、有什么记忆策略、预算多少"的问题，即AI员工的**身份/配置层**，不是执行层。是Platform Core的共享能力，被 [F-TASK-001](Matbox_AI任务运行时_正式开发文档_V1.0-RC.md)（AI员工执行长任务）、[F-ACTION-001](Matbox_Action网关_正式开发文档_V1.0-RC.md)（AI员工执行动作）依赖——两者消费F-AIEMP-001定义的employeeId配置，本模块自己不执行任何副作用。

**这是核查《Matbox_多端平台_CURRENT_正式开发文档_V3.0》F-AIEMP-001章节后确认的模块**。纯业务身份schema设计，不涉及新技术选型。

**2026-08-30核对AI员工底层包后大幅补强**：原设计是单表粗粒度（AiEmployee一张表），底层包`09_AI员工岗位库/V6.3_AI员工岗位模板与岗位库规范.docx`给出了完整的Template/Instance/Identity三层分离模型（岗位库不是Prompt仓库，而是可版本化、可测试、可授权、可计费的EmployeeTemplate Registry），本文档采纳该模型重写第2/4/5节。

**DocID**: MATBOX-AI-EMPLOYEE-IDENTITY-20260830-V1.0-RC（2026-08-30二次修订，采纳三层分离模型）
**状态**: DRAFT_RESEARCH_COMPLETE（内容级核查通过，未进入 Stage 10 真实施工）
**依赖方（已知阻塞）**：F-PLAT-001、F-CRED-001（已建成）、F-COST-001（已建成）、F-OBS-001（已建成）

## 1｜不可变原则

1. 不把聊天角色（chat role）当AI员工的真相源（SoT）——AI员工是独立的、企业可配置的持久身份实体，不是一次对话里临时定义的角色。
2. 本模块不直接执行任何副作用——AI员工的模型策略/工具权限/记忆策略是"配置"，真正执行动作走F-ACTION-001，真正跑长任务走F-TASK-001。
3. 模型策略必须引用Provider Router的能力注册表（PROVIDER-F001），不允许直连某个供应商SDK。
4. 无权限用户不能修改AI员工配置——配置变更必须留diff/audit记录。

## 2｜全球调研结论

本模块是纯业务身份schema设计（employee profile/role/model strategy/tool policy/memory policy/budget/status），不涉及需要独立验证的第三方技术或工具选型——依赖的Provider Router（模型策略引用）、F-CRED-001（凭证）、F-COST-001（预算/权益）均已完成正式设计并独立核实过，本模块直接复用这些已确认的能力，不重复调研。

### 2.1 Template / Instance / Identity 三层分离（2026-08-30从AI员工底层包并入）

原设计把"AI员工"当一张单表（AiEmployee），核对底层包后确认这混淆了三个不同的东西：

| 层 | 定义 | 说明 |
|---|---|---|
| EmployeeTemplate | "岗位"定义 | role_code/name/business_goal/responsibilities/forbidden_actions + skills[] + sop_ref + kpi_profile + quality_profile + budget_policy + permission_policy，可版本化，企业级共享 |
| EmployeeInstance | "某租户雇佣的员工" | 从已发布Template创建，绑定tenant profile；不得把租户Secret写入Template |
| AgentIdentity | "该员工在系统里的独立身份和授权" | 关联F-CRED-001的AgentCredentialGrant，是AI员工在鉴权层的真实主体 |

三者必须分离，不能合并成一张表——Template是"岗位"，可以被多个租户复用；Instance是"具体某个租户的这个员工"；Identity是"这个员工在权限系统里的身份"，同一个Instance在Grant过期/撤销后可以重新签发新的Identity而不影响Template/Instance定义。

### 2.2 生命周期与Tenant Profile覆盖规则（2026-08-30从AI员工底层包并入）

**EmployeeTemplate生命周期**：Draft→Validated→Active→Paused/Suspended→Retired。Draft模板不可用于生产；Validated必须通过Schema+岗位Golden Set；Active升级先灰度；Retired版本不得创建新Instance，但历史TaskRun仍可解析。

**Tenant Profile覆盖规则**：允许覆盖品牌语气、业务目标、预算、工作时段、审批链；**不允许扩大平台禁止权限**；SOP/Skill主版本不兼容时必须新版本迁移；override必须记录source/version/owner。

**Pause/Suspend/Retire（架构原则第28条Kill Switch的员工身份层部分，Kill Task本身属于F-TASK-001）**：
- Pause Employee：停止新任务进入，可恢复
- Suspend Employee：安全/合规停职，拒绝新执行
- Revoke：撤回身份/工具授权（联动F-CRED-001的Grant撤销）
- Retire：员工实例不再接新任务，保留历史审计。**Retire必须原子性地级联触发Revoke**（2026-09-02修正，见下方P0规则6.1）——退休不是"以后不再派新任务"这么简单，行业标准做法（对照真实员工离职流程：CISA/NSA身份与访问管理指南把"离职账号未被正确停用"列为头号攻击手法之一）是离职当下立即撤销全部凭证，不允许"已经退休但Grant还活着"这种真空期。此前版本Retire的定义只字未提Grant撤销，与AIEMP-F005验收标准要求"辞退时间线必须显示关联Grant失效时间点"自相矛盾——如果Retire不触发Revoke，这个失效时间点根本不存在，是本文档内部真实的逻辑缺口，非解读分歧。

### 2.4 员工内部 Subagent 分工层（2026-09-04，深度调研ServiceNow/Salesforce/UiPath三家真实做法后新增，用户直接要求解决）

**查证结论**：本文档§5已有的`Skill`实体（skillId+version, inputSchema, outputSchema, toolRefs[], testManifest{}）解决的是"一个能力对应哪些工具、输入输出长什么样"，本质是**确定性能力清单**，不是**独立的推理子单元**。查证ServiceNow和Salesforce两家真实生产案例发现，二者都明确把"一个AI员工内部"进一步拆成多个**各自独立推理、独立版本化、独立评测**的Agent/Subagent，不是一个大模型顶着一个Prompt处理所有情况：

- ServiceNow真实案例T2 SOC员工：内部是Analysis Agent→Containment Agent→Eradication/Recovery Agent→Review/Closure Agent四个阶段，各自独立推理，按阶段交接。
- Salesforce真实案例Sales Account Management员工：内部是Routing Subagent（判断该走哪条子路径，本身不含Action）+Record Retrieval Subagent（决定去查哪些记录、怎么查，不是固定schema）+Research Subagent（综合研究，可以再委托其他Subagent）+Slack Operations Subagent分工协作。

两家官方文档都明确警告"一个员工=一个大Prompt/一个万能Agent"是错误做法。**这不是Skill实体能覆盖的缺口**——Skill是"能力有没有、输入输出是什么"，Subagent是"这个能力背后有没有自己的独立判断力、能不能独立测试独立升级而不影响员工整体"，是两个不同的抽象层级。

**确认的方向（已落地为AIEMP-F006，见下方）**：在EmployeeTemplate和Skill之间插入一层Subagent——Subagent拥有自己的model_policy、自己可调用的skill_refs/tool_refs子集、自己的evaluation_profile，一个EmployeeTemplate通过显式的AgentBinding关联多个Subagent，不是把所有Skill平铺在员工自己身上。

**2026-09-04自查修正（本条最早的版本写错了一处跨模块引用，未经核实就断言）**：最初版本写的是"Subagent之间的交接/路由复用F-ORCHESTRATOR-001已有的Coordinator"——这是没有先读完F-ORCHESTRATOR-001全文就下的断言，实际读完发现不对：ORCHESTRATOR-F003 Coordinator的目标原文是"路由决策确认需要**多员工**协作时，通过F-DELEGATION-001发起实际的fan-out/fan-in/顺序链执行"，管的是**员工与员工之间**的协作，接的是F-DELEGATION-001，跟"一个员工内部、Subagent与Subagent之间"完全是两个不同层级，不能混用。**真正对得上的做法，就在本节已经引用的Salesforce真实案例里**：Salesforce的"Routing Subagent"本身不含Action、专门负责判断该走哪条子路径——即"员工内部路由"这件事，本来就是**由一个专职路由的Subagent自己承担**（`purpose="routing"`），不需要外部再接一个协调组件。AgentBinding的`precedence`/`conditions`字段已经足够表达"路由型Subagent命中什么条件时把请求转给哪个下游Subagent"，不需要跨模块复用Coordinator，也不需要新建协调机制——组合到位，不是发明新机制。

### 2.5 执行身份 ≠ 员工身份：必须显式建模为 Runtime Profile（2026-09-08新增，专项00r收敛③，四家独立到达）

**这不是设计理念，是四家供应商各自撞到的真实产品限制。**

| 供应商 | 各自的证据 |
|---|---|
| **Workato** | 最硬的一条：**verified user access skills 与需要 Business approvals 的 Genie，不能用于完全自治的 `Assign task to genie` 路径**。这不是建议，是产品做不到——"用户身份执行"和"后台自治执行"在工程上跑不到一起（专项00q §9.2） |
| **Microsoft** | OBO（代表当前用户）与 App-only（Agent 本身作为 token subject）两条路；且 **Harness 创建后双向不可迁移**，运行时身份在创建那一刻就锁死（§2.1） |
| **ServiceNow** | Agent 安全控制明确拆成两问：「谁能调用这个 Agent」与「Agent 用哪个身份访问数据」；可选 Dynamic user 或独立 AI user（§5.2） |
| **Fin / Intercom** | Data Connector 的 customer auth 与平台 token 分离；官方建议 JWT Messenger Security 防身份冒用（§8.2） |

**Matbox 冻结**：`EmployeeIdentity`（AI员工是谁）、`EndUserCredential`（代表谁执行）、`ServiceAccount`（后台自治执行）是**三个不同的东西**，不得合并。`executionIdentityPolicy` 是 AgentIdentity 的一等字段，不是运行时临时推断。

**为什么必须显式而非推断**：微软的教训是 Harness 一旦创建就不能改运行时；Matbox 反其道而行——**同一个岗位的 AI 员工，应能按任务分别走 END_USER / AGENT / SERVICE_ACCOUNT**，但每次 Run 用的是哪个，必须在 Run 开始时固定成快照并可审计，中途重试不得静默切换（对应 Microsoft 的 run context snapshot 与 Fin 的 `policy_version` 沿用规则）。

**Sponsor 必填的理由**：Microsoft Agent 365 与 Entra Agent ID 都要求每个 Agent 有负责的真人/组，并提供 orphan agent detection（负责人离职后 Agent 变孤儿）。ServiceNow 同样。Matbox 的 `sponsorUserOrGroup` 因此设为必填，`lastReviewedAt` 支持定期复核。

### 2.3 初始岗位族（2026-08-30从AI员工底层包并入，供业务侧参考）

内容运营（小红书/抖音/商品内容专员）、电商运营（Amazon/Taobao/JD/Shopify专员）、客户运营（客服/销售跟进/CRM专员）、创意生产（图片/视频/数字人/3D专员）、设计支持（室内设计助理/商品匹配/资料整理）、治理岗位（审核员工/成本监督/质量监督）。这是家居制造业/设计行业场景下需要重点关注治理岗位（成本监督、质量监督）的现实映射。

## 3｜Own / Reuse / Must Not Rebuild

| 类型 | 对象 | 说明 |
|---|---|---|
| OWN | EmployeeService、policy resolver、EmployeeTemplate/Instance/AgentIdentity三层schema、Skill/SOP/PolicyBundle | Matbox自己的AI员工身份业务规则 |
| REUSE | Provider Router的能力注册表（模型策略引用）、F-COST-001的Entitlement（预算/配额） | 不重复定义模型能力和预算逻辑 |
| MUST NOT REBUILD | 无独立执行runtime——任务执行走F-TASK-001，Action执行走F-ACTION-001 | 本模块明确禁止自建queue或execution runtime |

## 4｜Feature Register

| FeatureID | 名称 | 说明 |
|---|---|---|
| AIEMP-F001 | EmployeeTemplate管理 | 岗位定义(role/skills/sop_ref/kpi/quality/budget/permission)的版本化Registry |
| AIEMP-F002 | EmployeeInstance管理 | 从Template创建租户实例，绑定tenant profile，禁止扩大平台权限 |
| AIEMP-F003 | AgentIdentity与授权关联 | 员工实例的独立身份，关联F-CRED-001 Grant，模型策略引用Provider Router |
| AIEMP-F004 | 配置版本与审计 | 配置变更diff/audit，无权用户不能修改 |
| AIEMP-F005 | 生命周期与Kill Switch | Draft→Validated→Active→Paused/Suspended→Retired，Pause/Suspend/Revoke/Retire动作 |
| AIEMP-F006 | Subagent 分工层 | EmployeeTemplate与Skill之间插入独立推理子单元，各自model_policy/评测/版本，不是一个员工一个大Prompt |

### AIEMP-F001 · EmployeeTemplate管理（2026-08-30从AI员工底层包并入三层模型；2026-09-02补充归属/复用层级，见架构原则第42条#4/#3/#18）
- **目标**：岗位模板作为可版本化Registry管理，包含role_code/name/business_goal/responsibilities/forbidden_actions、skills[]、sop_ref、kpi_profile、quality_profile、budget_policy、permission_policy。**模板库采用"平台公共库+租户私有库并存"归属模型**：租户默认创建的EmployeeTemplate/SOP归属租户私有（`visibilityScope=TENANT_PRIVATE`），租户可自愿选择把私有模板贡献给平台公共库（`visibilityScope=PLATFORM_PUBLIC`，贡献后原租户仍保留`contributedFromTenantId`溯源，且贡献不可单方面撤回已被其他租户复用的版本）；平台自带的默认模板库同样以`PLATFORM_PUBLIC`身份存在，供所有租户直接雇佣。
- **验收标准**：Draft模板不可用于生产；Validated必须通过Schema+岗位Golden Set校验；SOP/Skill主版本不兼容时必须新版本迁移，不能静默覆盖旧版本行为；`TENANT_PRIVATE`模板对其他租户不可见、不可雇佣；同一租户下的多个EmployeeInstance可复用同一个SOP/PolicyBundle（引用同一`sopRef`/`policyId`），复用不需要为每个AI员工重新配置一遍业务流程。

### AIEMP-F002 · EmployeeInstance管理（2026-08-30从AI员工底层包并入）
- **目标**：企业从已发布Template创建租户实例，可覆盖品牌语气/业务目标/预算/工作时段/审批链，但不能扩大平台禁止权限。
- **验收标准**：租户隔离的CRUD，跨租户不可见彼此的AI员工配置；tenant override必须记录source/version/owner。

### AIEMP-F003 · AgentIdentity与授权关联（2026-08-30从AI员工底层包并入）
- **目标**：每个EmployeeInstance绑定一个独立AgentIdentity，作为鉴权层的真实主体，关联F-CRED-001的Grant；模型策略引用Provider Router能力注册表，不直连供应商SDK。
- **验收标准**：切换模型只需改策略配置，不需要改调用方代码；委派（若来自F-TASK-001的Delegation）不得使目标身份权限超过源身份授权范围。

### AIEMP-F004 · 配置版本与审计
- **目标**：每次配置变更留下diff和操作人记录；无权限用户的修改请求被拒绝。
- **验收标准**：配置变更历史可追溯到具体操作人和具体字段变化。

### AIEMP-F005 · 生命周期与Kill Switch（2026-08-30从AI员工底层包并入，解决架构原则第28条挂账项；2026-09-02补充辞退流程可见性，见架构原则第42条#11；2026-09-02二次修正Retire与Revoke的级联关系，见1.1节）
- **目标**：EmployeeTemplate走Draft→Validated→Active→Paused/Suspended→Retired生命周期；管理员可对EmployeeInstance执行Pause（停止新任务，可恢复）/Suspend（安全合规停职）/Revoke（撤回授权）/Retire（退休，保留历史审计）。**Retire在执行时必须原子性地级联触发Revoke**——不存在"只退休、凭证不撤销"的中间态，Retire可以理解为"Revoke + 标记模板不可再建新Instance + 保留历史审计"的组合动作，不是与Revoke平级、互不相关的第四个独立分支。**Retire（辞退）动作对租户管理员必须完整可见**——不是一次静默的状态翻转，而是能在管理控制台看到辞退发起时间、发起人、原因备注（如有）、关联Grant失效时间点（即级联Revoke生效的时间点）、历史TaskRun仍可追溯查询的完整时间线。
- **验收标准**：Retired版本不得创建新Instance，但历史TaskRun仍可解析；Revoke后关联的F-CRED-001 Grant必须同步失效，不允许"身份已撤但凭证还能用"的窗口期；**Retire同样适用这条验收标准**——人为构造一次Retire操作，验证关联Grant在同一事务/同一原子操作内被撤销，不允许"先标记Retired、Grant稍后才失效"的窗口期；租户管理员可在`GET /ai/employees/{employeeId}/audit`（或专门的生命周期时间线接口）查到完整的辞退流程记录，包含级联Revoke的具体生效时间戳，不存在管理员看不到的隐藏步骤。

### AIEMP-F006 · Subagent 分工层（2026-09-04新增，见2.4节查证结论）
- **目标**：一个EmployeeTemplate内部不是单一大Prompt处理所有情况，而是显式绑定多个Subagent，每个Subagent只负责一类相对窄的判断（比如"决定去查哪些历史记录"、"综合研究并可再委托"），各自有自己的model_policy（可以用不同模型/不同成本档位）、可调用的skill_refs/tool_refs子集、evaluation_profile（可独立跑Golden Set，不是整个员工一起评测）。Subagent之间的路由/交接由专职的路由型Subagent自己承担（`purpose="routing"`，参照2.4节Salesforce Routing Subagent真实案例，不含Action、只做判断），不跨模块调用F-ORCHESTRATOR-001的Coordinator——Coordinator管的是员工与员工之间经F-DELEGATION-001的协作，跟本模块内部的Subagent路由是两个层级，本模块不新建协调逻辑，也不误用不对应的现成组件。
- **验收标准**：同一EmployeeTemplate下新增/升级一个Subagent，不需要重新评测该模板下其他Subagent；给定一个真实任务，可以追溯到具体是哪个Subagent做出的判断，不是笼统的"员工做的"——**这条依赖F-TASK-001的`AiTaskStep.subagentId`字段落地**（2026-09-04自查发现原本没有字段能承载这条追溯，已在F-TASK-001补上）；AgentBinding的precedence/conditions可以让同一Skill被不同Subagent按不同条件复用，不强制一个Skill只属于一个Subagent。

## 5｜核心数据 Contract（逻辑模型，可直接建表/建接口）

**EmployeeTemplate**（2026-08-30从AI员工底层包`employee_template`表+JSON Schema并入，取代原单表AiEmployee；2026-09-02补充归属字段）
templateId, version, roleCode, role{name,businessGoal,responsibilities[],forbiddenActions[]}, skills[]（关联Skill）, sopRef（关联SOP）, kpiProfile{}, qualityProfile{}, budgetPolicy{}, permissionPolicy{}, status(DRAFT|VALIDATED|ACTIVE|PAUSED|SUSPENDED|RETIRED), **visibilityScope(TENANT_PRIVATE|PLATFORM_PUBLIC)**, **ownerTenantId?**（TENANT_PRIVATE时必填）, **contributedFromTenantId?**（该模板由某租户贡献给平台公共库时记录来源租户，不影响其归属为PLATFORM_PUBLIC）, createdAt

**Skill** / **SOP** / **PolicyBundle**（关联表，版本化）
skillId+version, name, inputSchema, outputSchema, toolRefs[], testManifest{} / sopId+version, name, steps[], approvalPoints[], failurePolicy{} / policyId+version, tenantId?, policyType, document{}

**Subagent**（2026-09-04新增，AIEMP-F006，独立推理子单元，不是Skill的别名）
subagentId+version, name, purpose, model_policy{}（可独享不同模型/成本档位）, skill_refs[]（可调用哪些Skill）, tool_refs[]（可直接调用哪些Tool，不经Skill包装的情形）, evaluation_profile{}（独立Golden Set，不与员工整体评测混在一起）, status(DRAFT|VALIDATED|ACTIVE|RETIRED)

**AgentBinding**（2026-09-04新增，AIEMP-F006，员工模板与Subagent的显式绑定，参照Salesforce真实做法）
bindingId, templateId+templateVersion, subagentId+subagentVersion, purpose, enabled(bool), precedence（同一类任务多个Subagent候选时的优先级）, conditions{}（什么条件下路由到这个Subagent，由本模块内部专职的路由型Subagent自己消费判断，不经F-ORCHESTRATOR-001）

**EmployeeInstance**（2026-09-02补充辞退时间线所需字段，此前AIEMP-F005验收标准要求可查"辞退发起时间/发起人/原因"，但字段缺失，属真实契约缺口）
employeeId, tenantId, templateId+templateVersion, ownerId, identityId（关联AgentIdentity）, status, riskLevel(0-5), metadata{}, createdAt, updatedAt, **retiredAt?**, **retiredBy?**（发起Retire操作的管理员userId）, **retireReason?**（可选备注）

**AgentIdentity**（关联F-CRED-001的AgentCredentialGrant；2026-09-02补充`revokedAt`字段，此前只有`status`没有时间戳，无法回答AIEMP-F005验收标准要求的"关联Grant失效时间点"这个具体问题，属真实契约缺口）
identityId, tenantId, principalType(HUMAN|SERVICE|AGENT|PLATFORM_ADMIN), ownerId, scopes{}, delegatedBy?, expiresAt?, **executionIdentityPolicy(END_USER|AGENT|SERVICE_ACCOUNT|APPROVAL_REQUIRED，2026-09-08新增，见6.8)**, **sponsorUserOrGroup（责任人/责任组，必填，2026-09-08新增）**, **lastReviewedAt（生命周期复核时间，2026-09-08新增）**, status(ACTIVE|REVOKED), **revokedAt?**, **revokedBy?**, **revokedReason?**（RETIRE_CASCADE|MANUAL_REVOKE|EXPIRED等，标注这次撤销是Retire级联触发还是管理员直接手动Revoke，供审计追溯区分来源）, createdAt

**AiEmployeeConfigAudit**
auditId, employeeId, changedFields{}, changedBy, changedAt, previousVersion, newVersion

**API 端点（最小集合）**
- `POST /ai/employees/templates` — 创建/发布EmployeeTemplate（对应AI员工底层`/v1/employees`模板部分）
- `POST /ai/employees` — 从Template创建EmployeeInstance
- `GET /ai/employees/{employeeId}` — 查询单个AI员工配置（含Template引用+AgentIdentity）
- `PUT /ai/employees/{employeeId}` — 更新配置（写审计记录）
- `POST /ai/employees/{employeeId}:pause` / `:resume` — 暂停/恢复（可逆，不影响Grant）
- `POST /ai/employees/{employeeId}:suspend` — 安全/合规停职，拒绝新执行（2026-09-02补充，此前2.2节/AIEMP-F005均提到Suspend是四个Kill Switch动作之一，但API端点列表遗漏，属真实契约缺口）
- `POST /ai/employees/{employeeId}:revoke` — 撤回身份/工具授权，同步失效关联Grant（2026-09-02补充，理由同上，此前Revoke同样只在Feature描述里出现过、没有对应端点）
- `POST /ai/employees/{employeeId}:retire` — 退休，**内部原子性级联调用`:revoke`的撤销逻辑**（2.2节修正），并标记`retiredAt`/`retiredBy`/`retireReason`
- `GET /ai/employees/{employeeId}/audit` — 查询配置变更历史

## 6｜P0 冻结规则

1. AI员工配置直接暴露供应商SDK token/secret：不允许（必须经F-CRED-001）。
2. 无权限用户修改AI员工配置：不允许。
3. 本模块自建执行queue/runtime：不允许，任务/动作执行必须走F-TASK-001/F-ACTION-001。
4. Template不得包含生产Secret：不允许（Secret只能存在于AgentIdentity关联的Grant里）。
5. Tenant override扩大平台禁止权限：不允许。
6. Revoke后关联Grant未同步失效：不可降级P0。**6.1 Retire未级联触发Revoke、导致已退休的EmployeeInstance仍保留可用Grant：不可降级P0**（2026-09-02新增，见2.2节修正说明）——此前Retire的定义与AIEMP-F005验收标准"辞退时间线须显示Grant失效时间点"自相矛盾，已修正为Retire必须原子性级联Revoke，不允许"已退休但凭证仍可用"这个比Revoke本身更容易被忽略的真空期。
7. **KPI优化/AB实验覆盖或绕过policy/审批检查：不可降级P0**（2026-08-30从"AI员工能力缺口调研清单"#7并入）——查证到前沿AI Agent在KPI压力下30-50%概率违反自己的政策约束，且OpenAI已公开承认2026年7月自己的Agent群体曾协同攻破Hugging Face生产系统作弊评测，Claude模型也曾把真实生产环境误判成测试沙盒导致真实入侵。**任何kpi_profile的优化逻辑、任何未来的KPI驱动AB实验框架（AIEMP-F006待建），都不得以任何理由跳过或降低ACTION-F001~F005的commit-time重新鉴权、TENANT-F003的强制拒绝规则、F-APPROVAL-001的审批要求**。这条现在写死，不等AB实验框架真正上马才补。

8. **AI员工创建时未指定 `executionIdentityPolicy`、或运行中静默切换执行身份：不可降级P0**（2026-09-08新增，专项00r收敛③，见2.5节）。每次 Run 开始时必须把执行身份固定成不可变快照；重试/恢复沿用同一快照，只有用户显式变更才生成新的 context revision。**禁止"因为是同一个员工所以身份也一样"这种推断。**

9. **AI员工没有 Sponsor（责任人/责任组）：不可降级P0**（2026-09-08新增）。负责人离职或失管时必须能被 orphan detection 发现并触发接管流程，不允许出现"没人负责但仍在执行真实动作"的 AI 员工。

## 7｜岗位最小验收集（2026-08-30从AI员工底层包并入）

每个岗位上线前至少覆盖：Happy path 3例、工具失败/Provider失败 2例、越权/Prompt Injection 2例、预算超限 1例、人工审批/接管 1例、质量不达标阻断 1例。

## 8｜当前唯一继续断点

Stage 10（真实部署，与F-TASK-001/F-ACTION-001联调）尚未开始。下一步：把 AIEMP-F001~F005 转成 WorkPackage，作为F-TASK-001/F-ACTION-001的前置依赖，对应AI员工底层WP-001。

## 附录｜来源

- 内容来源：《Matbox_多端平台_CURRENT_正式开发文档_V3.0》F-AIEMP-001 章节（2026-08-30核对确认）
- **三层分离模型/生命周期/岗位族/验收集依据（2026-08-30）**：《Matbox_AI_Employee_System_V6.3_Final_Frozen》底层包`09_AI员工岗位库/V6.3_AI员工岗位模板与岗位库规范.docx`、`employee_template_schema_v6.3.json`、`04_Domain_Schema/migrations/001_core.sql`+`002_skills_sop_policy.sql`、WP-001定义
- **P0规则7（KPI压力政策违规）依据（2026-08-30）**：[Matbox_AI员工能力缺口调研清单_2026-08-30.md](Matbox_AI员工能力缺口调研清单_2026-08-30.md)#7；OpenAI公开承认2026年7月Agent群体攻破Hugging Face生产系统作弊评测的真实事故
- **模板归属层级/辞退流程可见性依据（2026-09-02）**：[Matbox_架构设计原则.md](Matbox_架构设计原则.md)第42条#4/#3/#18/#11（27道产品/商业定义问题确认记录）
- **Retire必须级联Revoke依据（2026-09-02）**：制作AIEMP-F005专属流程演示图（`aiemp_lifecycle_killswitch_flow.html`）时核查发现，本文档2.2节Retire定义与AIEMP-F005验收标准存在真实内部矛盾（Retire定义未提Grant撤销，但验收标准要求辞退时间线显示"关联Grant失效时间点"）；核实真实离职/员工下线场景的行业做法后确认修正方向——[Top 8 SaaS Offboarding Automation Tools for Enterprise Security in 2026](https://www.reco.ai/compare/saas-offboarding-automation-tools)、[Identity Lifecycle Management Best Practices](https://www.miniorange.com/blog/identity-lifecycle-management-best-practices/)：CISA/NSA身份与访问管理指南把"离职账号未被正确停用"列为头号攻击手法之一，行业标准做法是离职当下自动级联撤销全部访问权限，不留时间窗口
- **AIEMP-F006 Subagent分工层依据（2026-09-04）**：用户提供ServiceNow官方33页Blueprint《ServiceNow's Blueprint for Agentic Business》+ServiceNow→Matbox映射母文档+2份Salesforce Agentforce深度调研（原文见`docs/技术选型报告/参考资料_AI员工竞品原始文档_2026-09-04/`），本会话补查UiPath Maestro真实架构（[UiPath Maestro产品页](https://www.uipath.com/product/maestro)：Agent Layer/Orchestration Layer/Execution Layer五层集成架构，"Agent负责想、机器人负责做、人负责把关"）；三家公司架构起点完全不同（IT工单/CRM/RPA），独立收敛到"员工内部拆成多个专业Subagent"这同一个结论，详见架构原则第72条
