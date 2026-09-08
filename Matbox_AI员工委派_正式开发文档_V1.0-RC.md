# Matbox AI 员工委派 / Delegation Service（F-DELEGATION-001）

正式开发文档 · V1.0-RC · 2026-08-30

## 当前定位

本专项解决"一个AI员工怎么把任务的一部分委派给另一个AI员工"的问题——比如"内容运营专员"生成文案后，委派"设计支持专员"生成配图，委派方和被委派方各自有独立身份，权限和预算不能无限传递放大。这是一个全新模块，之前《多端平台V3.0》和已建成的任何模块都没有对应设计。

**这是核对AI员工底层包`05_Control_Plane_Runtime/V6.3_Control_Plane_Runtime_Spec.docx`第7节 + 架构图册"02 AI员工团队协作与委派图"后确认的模块**，直接采纳该包的Delegation设计，是本轮"AI员工底层"核对中确认的C类新增模块之一（详见架构原则第33条）。

**DocID**: MATBOX-DELEGATION-20260830-V1.0-RC
**状态**: DRAFT_RESEARCH_COMPLETE（内容级核查通过，未进入 Stage 10 真实施工）
**依赖方（已知阻塞）**：F-AIEMP-001（已建成，AgentIdentity）、F-CRED-001（已建成，CRED-F008 AgentIdentity持久身份层）、F-TASK-001（已建成，长任务运行时）

## 1｜不可变原则

1. 目标Agent的权限="自身权限 ∩ 委派权限"——被委派方的实际权限永远不能超过（源Agent本次授权范围 ∩ 委派时显式给的权限），严禁权限放大。
2. 委派必须携带最小上下文，不是把源Agent的全部上下文/记忆都传给目标Agent。
3. 委派必须有明确的budget_envelope和deadline，不允许无限期、无预算上限的委派链。
4. 跨租户委派100%拒绝——委派只能发生在同一租户内的AI员工之间。
5. 委派链条必须可追溯（trace_id贯通），不能出现"任务最终是谁做的"查不清楚的情况。
6. **委派链深度必须有硬上限，循环检测必须是数学上可判定的，不能靠"问Agent是不是卡住了"**（2026-08-30从"AI员工能力缺口调研清单"#2并入）。
7. **下游Agent不得把上游Agent的输出自动当作真相直接使用**——必须携带可信度标记，下游在关键决策/高风险动作前需要独立校验，不能无条件信任上游产出（防止幻觉级联）。

## 2｜全球调研结论（2026-08-30）

### 2.0 失败模式防护——真实生产事故驱动，不是理论担忧（2026-08-30补充）

查证到三类多Agent协作真实生产失败模式，是本文档新增第6/7条不可变原则的直接依据：
1. **重试风暴**：一个环节失败触发级联重试，负载在秒级放大到10倍以上。真实案例：2025年7月一家财富500强保险公司的AI Agent系统陷入死循环，对同一个老旧承保系统发起了**84.7万次API调用，产生6.3万美元云账单，触发生产事故**。
2. **循环委派**：A委派给B、B委派给C、C又委派回A，没有人真正拥有任务，每次转手都丢失上下文。CrewAI真实从业者反馈中，"角色定义太松散导致角色幻觉"和"循环委派卡死工作流"是**反复出现**的抱怨，不是个案。
3. **幻觉级联**：一个Agent产出幻觉内容，下游Agent把它当真相继续加工放大，不去核实——被认为是多Agent系统里"最危险的失败模式之一"。

**行业共识**：不能靠"问Agent是不是在循环里"，必须**数学上可判定**（深度计数器、访问过的节点集合去重、超过阈值强制终止），这是2026年多Agent编排设计的硬性要求，40%的多Agent试点6个月内在生产失败，这三类是主要根因之一。

### 2.1 内部Delegation Contract为真相，适配A2A而不直接绑定

查证2026年AI Agent互操作协议现状：**A2A（Agent2Agent）协议已在2026年发布v1.0，由Linux Foundation治理，Google/Microsoft/Salesforce/ServiceNow等支持，是企业级多Agent委派场景事实上的标准协议**。但A2A本身只标准化"信封"格式（Agent Card发现、JSON-RPC任务提交、生命周期状态机），"委派的语义"本身（权限怎么收窄、预算怎么传递、失败怎么处理）留给上层业务自己定义——这跟AI员工底层技术选型文档的判断一致："内部Delegation Contract为真相；可适配A2A"。

**结论**：Matbox自建Delegation Contract（权限收窄/预算传递/失败处理这些业务语义是自己的），不直接绑定A2A协议本身；预留A2A适配接口，为将来"Matbox的AI员工需要跟外部第三方Agent协作"这类真实需求出现时留一条路，但现在不做这件事本身（没有真实需求，符合第27条）。

### 2.2 为什么现在补这个模块——真实缺口而非过度设计

第27条原则要求"没有真实需求不要提前建复杂"，但本模块不属于"提前建复杂"：《多端平台V3.0》定义的岗位族（内容运营/电商运营/客户运营/创意生产/设计支持/治理岗位，见F-AIEMP-001文档2.3节）天然存在协作场景——一个岗位的产出是另一个岗位的输入，这是当前已确认的业务需求本身决定的，不是凭空设想的未来需求。

## 3｜Own / Reuse / Must Not Rebuild

| 类型 | 对象 | 说明 |
|---|---|---|
| OWN | DelegationService、permission_envelope收窄逻辑、budget_envelope传递规则 | Matbox自己的委派业务规则 |
| REUSE | F-AIEMP-001的AgentIdentity（委派双方都是已有身份）、F-TASK-001的Temporal Workflow（委派任务本身走Task Runtime） | 不重新造身份系统和任务运行时 |
| MUST NOT REBUILD | A2A协议本身（若将来需要对外协作） | 预留适配接口，不现在自己实现一套Agent互操作协议 |

## 4｜Feature Register

| FeatureID | 名称 | 说明 |
|---|---|---|
| DELEGATION-F001 | 委派发起与权限收窄 | 源Agent发起委派，目标Agent权限=自身权限∩委派权限 |
| DELEGATION-F002 | 委派上下文与预算传递 | 最小上下文+budget_envelope+deadline+expected_output_schema |
| DELEGATION-F003 | 委派链路追溯 | trace_id贯通，委派链条可查询 |
| DELEGATION-F004 | 跨租户委派拦截 | 100%拒绝跨租户委派，P0安全红线 |
| DELEGATION-F005 | 失败模式防护 | 委派深度硬上限+数学可判定循环检测+上游输出可信度标记，防重试风暴/循环委派/幻觉级联 |

### DELEGATION-F001 · 委派发起与权限收窄
- **目标**：源AI员工可以把任务的一部分委派给目标AI员工，目标Agent的实际权限严格不超过"源Agent本次授权范围 ∩ 本次委派显式授予的权限"。
- **验收标准**：人为构造委派方尝试给被委派方超出自身权限的授权，必须被拒绝（对应AI员工底层测试项"permission amplification denial"）。

### DELEGATION-F002 · 委派上下文与预算传递
- **目标**：委派携带最小必要上下文（不是全量上下文/记忆），显式的budget_envelope（预算上限）、deadline（截止时间）、expected_output_schema（期望产出格式）。
- **验收标准**：委派任务的实际花费不能超过传递的budget_envelope；超过deadline未完成的委派任务按预设策略处理（超时不是无限等待）。

### DELEGATION-F003 · 委派链路追溯
- **目标**：一条完整的委派链（如A委派给B，B又委派给C）必须可以用trace_id完整查到，不能中途断链。
- **验收标准**：人为构造3个Agent的委派链，验证端到端trace完整可查（对应AI员工底层Gate"3-agent trace complete and secure"）。

### DELEGATION-F004 · 跨租户委派拦截
- **目标**：委派只能发生在同一租户内的AI员工之间，跨租户委派请求100%拒绝。
- **验收标准**：人为构造跨租户委派尝试，必须被拒绝且留审计记录，不可降级P0。

### DELEGATION-F005 · 失败模式防护（2026-08-30从"AI员工能力缺口调研清单"#2并入）
- **目标**：委派链深度有硬上限（超过即强制终止并留痕）；循环检测用已访问节点集合去重判定，不依赖询问Agent自身状态；下游Agent接收上游产出时标记可信度，关键决策/高风险动作前必须独立校验，不能直接当真相使用。
- **验收标准**：人为构造超过深度上限的委派链，验证在达到上限时被强制终止而非无限传递；人为构造A→B→C→A的循环委派，验证被数学判定拦截而非无限转手；人为在上游注入错误产出，验证下游在高风险动作前有独立校验环节而非直接采信。

## 5｜核心数据 Contract（逻辑模型，可直接建表/建接口）

**Delegation**（2026-08-30从AI员工底层包`delegation`表并入，新增depth/visitedNodes/upstreamTrustLevel字段落地DELEGATION-F005）
delegationId, tenantId, sourceEmployeeId（关联F-AIEMP-001 EmployeeInstance）, targetEmployeeId, goal(jsonb), contextRef?（指向最小上下文，不是全量）, permissionEnvelope(jsonb), budgetEnvelope(jsonb), deadline?, expectedOutputSchema?, depth（委派链当前深度，超过硬上限拒绝创建）, visitedEmployeeIds[]（已访问节点集合，用于循环检测）, upstreamTrustLevel(VERIFIED|UNVERIFIED)（本次委派若消费了上游产出，标记是否已独立校验）, state(PROPOSED|ACCEPTED|RUNNING|SUCCEEDED|FAILED|REJECTED|EXPIRED|TERMINATED_LOOP_DETECTED|TERMINATED_DEPTH_EXCEEDED), traceId, createdAt

**API 端点（最小集合）**
- `POST /v1/delegations` — 发起一次委派（对应AI员工底层API路径），内部先做深度/循环检测再创建
- `GET /v1/delegations/{delegation_id}` — 查询委派状态/结果
- `GET /delegations/trace/{traceId}` — 查询完整委派链路（跨多层委派）

## 6｜P0 冻结规则

1. 委派权限放大（目标Agent权限超过源Agent授权范围∩本次委派授权）：不可降级P0。
2. 跨租户委派：不可降级P0，100%拒绝。
3. 委派链路trace中断（查不清任务最终由谁完成）：不允许。
4. 委派无预算上限/无截止时间（无限期无上限委派链）：不允许。
5. 委派链深度无硬上限、循环委派未被数学判定拦截：不可降级P0。
6. 下游Agent在高风险动作前未独立校验上游产出、直接当真相使用（幻觉级联风险）：不允许。

## 7｜当前唯一继续断点

Stage 10（真实部署，与F-AIEMP-001/F-TASK-001联调）尚未开始。下一步：把 DELEGATION-F001~F004 转成 WorkPackage，对应AI员工底层WP-005，依赖WP-001/002/003/004（本项目对应F-AIEMP-001/F-CRED-001/F-TENANT-001/F-TASK-001）已就绪。

## 附录｜来源

- 内容来源：《Matbox_AI_Employee_System_V6.3_Final_Frozen》底层包`05_Control_Plane_Runtime/V6.3_Control_Plane_Runtime_Spec.docx`第7节、`04_Domain_Schema/migrations/003_runtime.sql`（delegation表）、WP-005定义、架构图册"02 AI员工团队协作与委派图"
- A2A协议现状依据（2026-08-30）：[A2A Protocol: The Definitive Agent-to-Agent Guide](https://tyk.io/learning-center/a2a-protocol-architecture-and-technical-specification/)、[What is the Agent2Agent (A2A) protocol?](https://mastra.ai/blog/what-is-agent-to-agent-protocol)
- **DELEGATION-F005失败模式防护依据（2026-08-30）**：[Matbox_AI员工能力缺口调研清单_2026-08-30.md](Matbox_AI员工能力缺口调研清单_2026-08-30.md)#2；40%多Agent试点6个月生产失败统计；2025年7月财富500强保险公司真实事故（84.7万次API调用死循环，6.3万美元账单）
