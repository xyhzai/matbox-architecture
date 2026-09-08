# Matbox 专项16｜Action网关 / Tool-Action Gateway（F-ACTION-001，ACTION-F001~F005）技术选型与开发交接报告

技术选型报告 · V1.0 · 2026-08-30

**DocID**: MATBOX-ACTION-TECHSELECT-20260830-V1.0
**审计对象**: `Matbox_Action网关_正式开发文档_V1.0-RC.md`（DocID: MATBOX-ACTION-GATEWAY-20260830-V1.0-RC，状态 DRAFT_RESEARCH_COMPLETE，未进入 Stage 10）
**上游/相邻关联文档**: `Matbox_AI任务运行时_正式开发文档_V1.0-RC.md`（F-TASK-001）、`Matbox_专项28_AgentRuntime_技术选型与开发交接报告_2026-08-30.md`（F-RUNTIME-001，本模块的调用方，边界见第1节）、`Matbox_AI动作审批_正式开发文档_V1.0-RC.md`+`Matbox_专项17_AI动作审批_技术选型与开发交接报告_2026-08-30.md`（F-APPROVAL-001，10步Pipeline第5步的实现者）、`Matbox_密钥管理_正式开发文档_V1.0-RC.md`+`Matbox_专项10_密钥管理_技术选型与开发交接报告_2026-08-30.md`（F-CRED-001，10步Pipeline第7步）、`Matbox_出站请求安全_正式开发文档_V1.0-RC.md`（F-EGRESS-001）、`Matbox_成本控制_正式开发文档_V1.0-RC.md`（F-COST-001）、`Matbox_Provider_Router_正式开发文档_V1.0-RC.md`（F-PROVIDER-001，已独立收窄，本模块不再包含模型调用分支）、`Matbox_错误码规范_正式开发文档_V1.0-RC.md`、`Matbox_专项06_租户与权限体系_技术选型与开发交接报告_2026-08-30.md`（F-TENANT-001）
**方法论**: 逐条执行用户给定的12点build-vs-buy核查方法论；每条市场/事实性结论均标注可核查来源URL；无法验证的一律明确写"未能验证"，不编造统计数字/引用。延续专项01（DQ）PILOT通过后确立的28节格式与"Top-3+获胜理由"要求。

---

## 0｜给忙碌读者的结论摘要

在深入28节之前，先给出本次审计与原设计（V1.0-RC）相比的**三处实质性差异**，其余大部分内容是"验证原设计正确并补齐工程交付物"：

1. **原设计"基于MCP Gateway生态"这句话把两件不同的事混在一起了，本报告拆开重新核查**。原设计写"2026年MCP Gateway生态已经成熟……2026年已有Linux Foundation治理、97M+下载量、13K+已注册MCP server"——这些数字（经核实：MCP协议2025年12月被Anthropic捐赠给Linux Foundation旗下新成立的Agentic AI Foundation，联合创始方含Block/OpenAI，Google/Microsoft/AWS/Cloudflare/Bloomberg参与；截至2026年活跃公开MCP server约1万至1.98万个区间，Tier 1 SDK月下载量约9700万）**描述的是"MCP协议本身作为一个开放标准"的生态规模，不是"某一个具体的MCP Gateway产品"的成熟度或市场占有率**。这是两个不同层面的问题：协议规模大，不代表围绕它的网关产品都已经成熟到可以直接托管Matbox的权限/风险/预算判定业务逻辑。本报告把这两件事拆开，第3/9节单独对"MCP Gateway产品市场"做Top-3核查，结论是：**这批产品普遍年轻（多数GitHub 500~5000 star区间，2025-2026年才出现1.0版本），没有一个产品同时具备Matbox需要的"多租户隔离+RBAC/ABAC+风险半径分级+审批门禁+预算检查+审计"全部能力**——原设计的方向（REUSE协议层、OWN业务判定层）没有错，但引用的证据支撑的是错误的论点，本报告用真实的产品级证据重新支撑同一个结论。
2. **10步Enforcement Pipeline里，没有任何一步可以整体外包给某个MCP Gateway产品，但协议/传输层可以，且有一个具体、可核查的复用点**：`agentgateway`（Apache-2.0，Linux Foundation托管，Rust实现，2536次commit，785 fork，多租户+CEL策略RBAC+预算/花费控制+内容过滤guardrail，同时支持MCP与A2A协议）不仅在专项10（密钥管理）报告里已经被认定为CRED-F004运行时凭据代理的开源候补，本次审计核查后确认**它同时是本模块ACTION-F002"Tool/MCP注册与Adapter层"协议传输能力的最合适REUSE对象**——这意味着Matbox可以只部署一套agentgateway实例，同时服务两个不同专项的两种不同用途（凭据转发 + MCP协议适配），不新增第二套需要独立运维的开源组件，是一次真实的、可核查的架构一致性收益（与Matbox在OPA/Temporal上反复验证过的"一套基础设施多方复用"模式同构）。但agentgateway本身**不理解**Matbox自己的risk_level/blast-radius/tenant_scope/ProposedAction状态机，这些仍然100% 需要Matbox自研——REUSE的范围严格限定在"怎么发现工具、怎么建立到MCP server的连接、怎么转发一次工具调用"这个协议层，不包括"要不要放行这次调用"这个业务判断层。
3. **"审批"在10步Pipeline里的位置需要更明确的边界说明，原设计文档没有讲清楚 ACTION-F003（Action预览与确认）和F-APPROVAL-001（AI动作审批）是不是同一件事**——本报告核查后确认两者是不同粒度的两层机制，不是重复设计：ACTION-F003是"提出动作的人自己看一眼风险/diff再点确认"（同步、单人、UX层面的摩擦控制，类似Claude Code执行破坏性命令前的二次确认）；F-APPROVAL-001是"另一个/另一批有权限的人对高风险动作做正式会签/或签审批"（异步、多人、走Temporal Workflow的正式治理流程）。两者可以同时触发在同一个ProposedAction上：先过ACTION-F003的即时预览确认，如果risk_level触发了ApprovalChainRequirement，再进入F-APPROVAL-001的正式链条，10步Pipeline第5步"审批要求检查"查询的是F-APPROVAL-001，不是ACTION-F003。第1/11节已把这条边界写清楚，避免未来施工时误判两者可以互相替代。

此外，Sierra（对话式AI Agent客服平台，2026年5月估值158亿美元，服务约40%的Fortune 50）2025年12月发生的一次真实事故——Gap.com的AI客服因guardrail配置错误响应了越权话题——为原设计"P0冻结规则第3条：commit时不重新校验不可降级"这条提供了独立的真实反面案例支撑，本报告将其记入第6/26节。

其余结论——10步Enforcement顺序本身、ProposedAction/ToolRegistration/ActionExecution/ActionAuditRecord的核心Contract字段、"REUSE协议层、OWN判定层"的整体方向——经核查**维持不变**，本报告不重新推翻已确认的架构决策。

---

## 1｜专项目标与功能边界

**内部代号**：Action Gateway / Tool-Action Gateway（F-ACTION-001）。

**管什么**：
- AI员工/业务代码需要调用任何有副作用的工具、MCP server、内部/第三方Action时，必须经本模块统一的10步Enforcement Pipeline判定后才允许执行：①Registry状态检查→②租户边界检查→③Identity/RBAC/ABAC检查→④blast-radius（风险半径）检查→⑤审批要求检查（查询F-APPROVAL-001）→⑥预算检查（查询F-COST-001）→⑦Secret解析（查询F-CRED-001）→⑧限流/熔断检查→⑨执行（F-EGRESS-001出站URL防护在此步生效）→⑩结果规范化+审计+成本+trace（写入F-OBS-001）。
- 工具/MCP server的注册与生命周期管理（未注册工具一律拒绝调用）。
- 高风险动作的即时预览/确认（ACTION-F003，见第0节第3条边界说明）。
- 幂等与可逆性（ACTION-F004）：同一idempotencyKey的重复请求只产生一次真实副作用；记录reversibility/compensation引用供人工或自动回滚。
- commit-time重新鉴权：execute前的判断不能沿用propose时刻的旧判断，必须在真正提交副作用前重新校验permission/entitlement/budget/approval。

**不管什么（明确排除，避免与相邻模块重复设计）**：
- **不是** F-RUNTIME-001（Agent Runtime）——不做"这句话该不该调用工具/调用哪个工具"的推理决策；Agent Runtime把模型的tool_use请求转译成ProposedAction后转发给本模块，本模块只做权限/风险/预算判定，不参与推理循环本身（专项28报告第1/2节已确认这条边界，本报告与其保持一致，不重复设计）。
- **不是** F-APPROVAL-001（AI动作审批）——不拥有审批链的状态机/多人会签或签逻辑/Temporal Workflow实现，这些已在专项17报告冻结为F-APPROVAL-001的职责；本模块10步Pipeline第5步只是**查询**F-APPROVAL-001的判定结果，不重新实现一遍。
- **不是** F-PROVIDER-001（Model Gateway）——不处理AI模型/图片/视频/语音供应商调用，这部分已由F-PROVIDER-001独立处理（详见F-ACTION-001原设计文档"结构性修正"说明）。
- **不是** F-CRED-001——不拥有密钥的存储/加密/签发逻辑，本模块只在第7步调用F-CRED-001取得已签发的短期Grant对应的实际密钥值，不持久化密钥本身。
- **不是** F-EGRESS-001——不重新实现SSRF/私有网段/DNS-rebinding校验，第9步执行时直接调用F-EGRESS-001的EgressClient。
- **不是** F-COST-001——不拥有预算规则/告警阈值的业务逻辑，第6步只查询F-COST-001的预算判定结果。
- **不是** F-TENANT-001——不重新实现RBAC/ABAC策略引擎，第③步调用F-TENANT-001已有的`POST /tenant/authz/check`（AI员工场景其判定内部再转OPA评估，专项06报告第12节已确认此调用链）。

## 2｜Matbox架构归属

F-ACTION-001属于**Platform Core Trust & Safety**域，是AI员工"想做什么"和"真的能不能做"之间唯一的强制关卡，不是可选的中间件。

**依赖方向（入）**——F-ACTION-001依赖：
- F-RUNTIME-001（调用方，只转发ProposedAction不裁决，专项28报告第2/9.1节已确认）
- F-TENANT-001（`/tenant/authz/check`，RBAC/ABAC判定，专项06报告已选定OPA为AI员工ABAC引擎）
- F-APPROVAL-001（第5步审批要求检查，专项17报告已确认走Temporal Workflow+OPA/Rego链条求解，不引入Flowable）
- F-COST-001（第6步预算检查，已建成，采用Langfuse做成本追踪、拒绝了LiteLLM合并路线）
- F-CRED-001（第7步Secret解析，已建成，Infisical自托管+CRED-F004混合方案）
- F-EGRESS-001（第9步执行时的出站URL安全防护，已建成）
- F-OBS-001（第10步审计/trace写入EvidenceBundle，已建成）

**被依赖方向（出）**——依赖F-ACTION-001的：
- F-RUNTIME-001（RUNTIME-F003 ToolCallDispatcher，专项28报告已确认工具调用统一走本模块，不允许Agent框架自带的工具执行循环绕过）
- F-DQ-009（Auto Repair Controller执行Codex修复任务时，专项01报告第6.12节已确认其"生成补丁"环节复用Codex/Temporal既有能力，触发的实际代码提交动作应经本模块统一管控，Stage 10施工时需显式打通这条链路，避免F-DQ-009自建一条平行的执行通道）
- 未来所有需要AI员工执行有副作用动作的业务模块

架构上的关键约束（原设计已冻结，本次审计确认无需修改）：F-ACTION-001**只拥有**自己域内的状态对象（ToolRegistration/ProposedAction/ActionExecution/ActionAuditRecord），10步Pipeline中的每一步判定结果都通过Contract引用相邻模块的事实源，不复制表、不重新实现相邻模块已经冻结的业务逻辑。

## 3｜全球方案调研结果

### 3.1 把"MCP协议生态规模"和"MCP Gateway产品成熟度"拆开看（本报告最重要的方法论修正）

原设计引用的"Linux Foundation治理、97M+下载量、13K+已注册MCP server"经核实数字方向大致准确（MCP于2025年12月9日由Anthropic联合Block、OpenAI捐赠给Linux Foundation旗下新成立的Agentic AI Foundation，Google/Microsoft/AWS/Cloudflare/Bloomberg等参与支持；2025年12月基线为活跃公开MCP server超1万个、Tier 1 SDK月下载量9700万，2026年Glama注册表统计的server数已增长到19,831+），**但这是协议本身的采用规模，不是围绕它建的"网关产品"的成熟度证据**。协议规模大恰恰是这个品类快速涌现大量新项目的原因——正因为MCP协议本身火爆，2025-2026年才冒出一批MCP Gateway产品，但产品本身普遍处于早期（多数1.0版本发布在2025年下半年到2026年上半年之间），这两件事需要分开评估，本报告第3.2/9节单独对网关产品市场做核查。

### 3.2 MCP Gateway产品市场分层现状（2026年）

核查后确认这是一个真实存在、正在快速涌现但普遍年轻的品类，按定位分四层：

1. **开源自托管协议网关**：agentgateway、IBM ContextForge（`IBM/mcp-context-forge`）、Obot、Lunar MCPX（`TheLunarCompany/lunar`）、Docker MCP Gateway、Microsoft MCP Gateway——解决"怎么统一发现/连接/代理转发MCP server调用"这个协议层问题，是本模块ACTION-F002可能的REUSE对象。
2. **API网关厂商的MCP扩展**：Kong（Gateway 3.12新增AI MCP Proxy插件，2025年10月）、Higress（阿里系AI原生网关，2026年3月进入CNCF Sandbox，基于Istio/Envoy）、Cloudflare（Workers平台的MCP Server Portals）——把已有的API网关能力（限流/鉴权/可观测）延伸到MCP协议，但对MCP本身的原生支持深度不一（"Bifrost和Higress原生处理MCP，而Kong/APISIX/Envoy AI Gateway基本把工具流量当普通HTTP处理"）。
3. **AI Gateway厂商的MCP尝试**：Portkey（"2026年MCP支持有限，未把MCP网关能力列为优先级"）、LiteLLM（提供基础的MCP代理转发+虚拟key预算功能，本质是"在wire级别注入上游凭证"）——两者的核心产品定位是模型调用路由，MCP只是附加能力，深度均不足以承接ACTION-F002。
4. **商业闭源"AI Agent治理平台"**：TrueFoundry、Composio、MintMCP、Arcade、Runlayer等——功能面更全（部分含审批工作流/风险评分），但均为SaaS或commercial-core为主，与Matbox自托管优先原则冲突，且多数"审批工作流""风险分级"能力如实标注为"未详述/企业层专属"，不构成P0可用的现成能力。

### 3.3 正面核查："10步Pipeline能不能整体外包给某一个MCP Gateway产品"（方法论第2条，最重要的问题）

这是本报告的核心问题，逐一核查上述候选是否原生具备Matbox需要的六项能力组合（多租户隔离/RBAC-ABAC/blast-radius风险分级/审批门禁/预算检查/审计），结果汇总（详细候选清单见第4/9节）：

| 能力 | agentgateway | IBM ContextForge | Obot | Lunar MCPX | Docker MCP GW | Microsoft MCP GW | Kong MCP | 结论 |
|---|---|---|---|---|---|---|---|---|
| 多租户隔离 | 有（原生支持多租户资源/用户隔离） | 有 | 有 | 未详述 | 无 | 有（依赖Entra ID） | 有 | 半数候选具备，但语义是"平台账户隔离"，不等于Matbox的TenantID业务语义 |
| RBAC/ABAC | 有（CEL策略引擎，细粒度） | 部分（Cedar插件） | 有（多角色RBAC） | 有（企业层/工具级） | 无 | 有（依赖Azure APIM） | 有 | 无一家用OPA/Rego，都是自带策略语言，接入等于学习新DSL |
| 预算/花费控制 | 有（LLM Gateway组件自带budget/spend控制） | 未详述 | 未详述 | 未详述 | 不适用 | 未详述 | 有（语义缓存降本，非预算门禁） | **仅agentgateway/Kong有雏形，且都不是"按WorkPackage/AI员工归因的预算门禁"语义** |
| 审批门禁（高风险动作二次确认/会签） | 未详述 | 未详述 | 未详述 | 未详述（沙盒模式≠审批） | 无 | 未详述 | 未详述 | **没有一家原生支持**，独立第三方分析（nhimg.org，2026）明确指出"MCP工具审批是实现层约定，不是协议标准状态"，行业普遍是各自定制 |
| blast-radius/风险分级 | 未详述（有工具级黑白名单，非风险量化） | 未文档化 | "治理优先"定位但未给出具体分级机制 | 风险评分（企业付费层） | 仅容器隔离 | 未内置 | 无 | 仅Lunar MCPX有风险评分雏形，且锁在付费企业层，与Infisical/SonarQube的"功能存在但锁在企业版"是同一种模式 |
| 审计日志 | 有（OpenTelemetry原生） | 有 | 有（企业层） | 未详述 | 未详述 | 未详述 | 有 | 多数具备基础审计，但不理解Matbox自己的ProposedAction/WorkPackage语义 |

**结论**：**没有一个MCP Gateway产品同时具备这六项能力**，"审批门禁"这一项尤其明确——不是Matbox没找全候选，是这个具体组合（尤其是"风险半径分级+审批门禁+按业务对象归因的预算门禁"三者与协议层耦合）在2026年确实还不是任何网关产品的标准功能，独立分析文章（非厂商自证）明确把"审批"定性为"实现层约定"。这与专项01报告对代码质检五件套"没有平台整体理解Matbox领域模型"、专项28报告对Agent框架"自带工具执行循环与F-ACTION-001冲突"得到的结论是同一种模式：**商品化的协议/传输层可以买/接，专属于Matbox自己业务规则的判定层必须自建**。

### 3.4 agentgateway 与 F-CRED-001 的复用协同（本报告新发现的具体复用点）

专项10报告第6.5/9.2节已经把agentgateway评为CRED-F004（AI员工运行时凭据代理层）的第2名候选（"独立于Infisical的开源代理层，遵循IETF CB4A标准草案"），当时的评估范围是"凭据转发"这一件事。本次审计从"MCP协议适配层"这个不同角度重新核查agentgateway，确认它同时满足：Rust实现、Apache-2.0、Linux Foundation托管（Technical Steering Committee治理）、过去365天250+活跃贡献者/50+活跃组织（专项10报告已用同一数据源核实）、原生MCP+A2A协议支持、多租户RBAC（CEL策略引擎）、来自Solo.io团队基于ztunnel/Envoy多年运维经验的架构设计。**这意味着如果Stage 10按专项10报告的建议部署agentgateway承担CRED-F004的凭据转发角色，ACTION-F002可以复用同一个部署实例做MCP工具发现/连接/协议转发，不需要为本模块单独再引入一个协议网关**——这是一次真实的、可核查的基础设施复用，不是重复评估同一个结论，两次评估的角度（凭据转发 vs 协议适配）不同，结论互相加强。

### 3.5 Kong / Higress / Cloudflare 的MCP网关能力（用户特别要求核实）

- **Kong**：Gateway 3.12（2025年10月）新增AI MCP Proxy插件，"把企业已经用在API流量上的治理模型套用到AI工具交互"，可以把现有REST API翻译成MCP，不需要为每个API重写MCP server。但Kong本身是重量级API网关产品，商业核心功能收费，且这套治理模型是通用API治理（限流/鉴权/重试），不是Matbox需要的AI Action专属风险/预算/审批语义，引入意味着为了一个MCP转译能力背上一整套企业API网关的运维负担，性价比不如轻量的agentgateway。
- **Higress**：阿里系AI原生网关，基于Istio/Envoy，2026年3月进入CNCF Sandbox（治理背书是真实的，但"Sandbox"是CNCF最早期阶段，早于Incubating/Graduated），"原生处理MCP协议"（不同于Kong把MCP当普通HTTP代理）。技术路线上比Kong更贴近MCP原生语义，但同样是完整的Envoy/Istio服务网格生态入口，对Matbox当前规模（2人团队，非K8s多集群场景）是过重的基础设施投入，且中国大陆背景的项目在国际化/长期社区独立性上需要额外观察（不构成否决理由，只是需要记录的背景信息）。
- **Cloudflare MCP Server Portals**：基于Cloudflare Workers的边缘路由方案，"在网络边缘处理加密、DDoS防护、基础访问治理"，本质是把多个MCP server聚合到单一URL入口，属于边缘网络层面的便利性方案，不提供Matbox需要的业务级策略判定能力，且是Cloudflare云端产品，与自托管优先原则冲突。
- **结论**：三者均不适合作为ACTION-F002的REUSE对象——Kong/Higress"能力够但太重"，Cloudflare"够轻但太浅"，均不如agentgateway"轻量+协议原生+已经在用"的组合适配Matbox当前阶段。

### 3.6 Portkey / LiteLLM 的工具调用处理能力（与F-COST-001已有结论保持一致）

- **Portkey**：核实确认"2026年MCP支持有限，未把MCP网关能力列为优先级"，无法构建"AI Agent查询内部数据库并带用户级权限""工具调用OAuth token注入"这类复杂agentic工作流，不构成ACTION-F002候选。
- **LiteLLM**：提供基础MCP代理转发能力（`mcp_tools`配置块定义工具，转发给MCP client），本质是"在wire级别为上游注入凭证"，与虚拟key预算功能是同一条产品线的自然延伸。但F-COST-001正式开发文档第2.1节已经**独立核查并否决**了"用LiteLLM同时做路由+成本控制"的合并路线，原因是"团队级预算强制执行等治理功能在开源版中被阉割（需付费企业版）"+"自建LiteLLM网关需要额外部署Redis+PostgreSQL，是新增两块基础设施的维护负担"。本次审计从工具调用角度重新核查LiteLLM，确认同一种模式在ACTION-F002场景下依然成立——它的MCP代理能力只是模型路由主产品线上的附属能力，不是围绕"工具执行安全"设计的专职产品，且与F-COST-001已经否决的理由完全同构，本报告不重复评估，直接维持不采纳的结论，两处评估互相印证而非矛盾。

### 3.7 真实AI-Agent平台怎么做工具执行安全（用户要求核实Sierra/Salesforce Agentforce）

`Matbox_中央编排层_正式开发文档_V1.0-RC.md`第2.5节已经确认Salesforce Agentforce（Atlas Reasoning Engine的真实产品）在"路由"层面的真实评价（G2）——本报告不重复调研路由能力，只补强**工具执行安全**这一具体维度：

- **Sierra**：核实确认其Agent SDK提供"声明式定义Agent目标与不可逾越的guardrail"，具体机制含"supervisory agents强制执行策略、关键业务逻辑用deterministic guardrails（不是纯靠LLM自我约束）、PII自动脱敏加密、内置话题黑名单过滤"，且专门为"Agent构建工具"提供了名为Agency的沙盒基础设施。这与Matbox 10步Pipeline的设计哲学（deterministic pipeline判定，不依赖模型自我约束；execute前二次校验）方向一致，是独立第三方（非Matbox自证）对同一设计范式的验证。**真实反面案例**：2025年12月，一批伪装的恶意用户对十余个客户的Sierra Agent发起协同越狱攻击，Gap.com的Agent因为一处guardrail配置错误对越权话题作出了响应——这说明"有guardrail机制"不等于"guardrail一定生效"，安全性最终取决于配置是否正确、是否有强制而非可选的兜底机制，直接支撑了Matbox P0冻结规则第3条"commit时不重新校验不可降级"以及第6条"委派权限不得放大"的必要性，本报告要求把这个案例记入第26节风险登记，作为ACTION-T0xx验收测试要覆盖"guardrail被绕过"场景的真实依据。
- **Salesforce Agentforce**：`Matbox_中央编排层_正式开发文档_V1.0-RC.md`已有的调研未展开工具执行安全细节，本报告核查未找到独立于路由评价之外的、专门针对"工具/动作执行安全机制"的可核查第三方评测，如实标注为"未能验证到独立于路由评价之外的工具执行安全专项证据"，不编造。

## 4｜GitHub候选项目清单

| 项目 | Repo | 规模/治理（查证日期2026-08） | License | 状态 |
|---|---|---|---|---|
| agentgateway | https://github.com/agentgateway/agentgateway | Rust实现，4.6k star，785 fork，2536次commit，Linux Foundation托管+Technical Steering Committee治理，过去365天250+活跃贡献者/50+活跃组织（同专项10报告数据源） | Apache-2.0 | 本次审计新增评估角度（协议适配层），评为ACTION-F002 Top-3第1名，与专项10 CRED-F004候选为同一项目 |
| IBM ContextForge (`mcp-context-forge`) | https://github.com/IBM/mcp-context-forge | 4.1k star，161+贡献者，v1.0.0已GA，Apache-2.0，**社区维护、无IBM官方商业支持**（README/项目状态明确标注） | Apache-2.0 | 本次审计新增，评为ACTION-F002 Top-3第2名 |
| Obot | https://github.com/obot-platform/obot | 923 star，MIT，K8s/Docker自托管，多角色RBAC+工具目录，G2平台0条评分记录（截至查证日） | MIT | 本次审计新增，评为ACTION-F002 Top-3第3名 |
| Lunar MCPX | https://github.com/TheLunarCompany/lunar | 468 star，39 fork，TypeScript，MIT（核心），最近一次commit 2026-07-16 | MIT（核心）+ 企业层功能另计 | 本次审计新增，规模最小，风险评分等能力锁在企业层，落选 |
| Docker MCP Gateway | Docker官方 | 官方产品线一部分，无独立RBAC/多租户 | 开源 | 本次审计新增，能力过于基础（仅容器隔离），落选 |
| Microsoft MCP Gateway | 官方AKS参考实现 | 依赖Entra ID/Azure APIM才具备多租户/RBAC | 开源 | 本次审计新增，强绑定Azure生态，与Matbox不绑定单一云厂商原则冲突，落选 |
| Kong (Gateway 3.12 AI MCP Proxy) | konghq.com | 2025年10月发布，企业级API网关+MCP转译插件 | 部分开源+商业核心 | 本次审计新增，能力够但基础设施过重，落选 |
| Higress | https://github.com/alibaba/higress | 阿里系，2026年3月CNCF Sandbox，基于Istio/Envoy | Apache-2.0 | 本次审计新增，MCP原生但服务网格量级过重，落选 |
| Cloudflare MCP Server Portals | Cloudflare Workers产品线 | 云端边缘产品 | 商业闭源SaaS | 本次审计新增，云端为主，与自托管优先原则冲突，落选 |
| （对照组，未采用）Portkey | github.com/Portkey-AI | MCP支持有限，未列为产品优先级 | 部分开源 | 本次审计新增，落选 |
| （对照组，未采用）LiteLLM | https://github.com/BerriAI/litellm | MCP代理为模型路由主产品线的附属能力 | MIT（核心）+ 企业层另计 | 本次审计新增，F-COST-001已用同一模式否决合并路线，本报告维持一致结论 |
| （对照组，REUSE不新增）agentgateway 同项目 | 见上 | — | Apache-2.0 | 与专项10报告CRED-F004候选为同一REUSE对象，本报告不重复引入新依赖 |

## 5｜API、SDK、模型及商业服务清单

| 服务 | 类型 | 认证方式 | 自托管 | 中国大陆可达性 | 结论 |
|---|---|---|---|---|---|
| agentgateway | 开源自托管协议网关 | JWT/API Key/OAuth（CEL策略引擎） | 是 | 不适用（自托管） | **REUSE**，ACTION-F002协议层，与CRED-F004共用同一实例 |
| IBM ContextForge | 开源自托管协议网关 | OAuth 2.0内置 | 是 | 不适用（自托管） | 未采用为主方案，见第9节 |
| Obot | 开源自托管/托管服务 | 内置多角色RBAC | 是（K8s/Docker） | 未查证 | 未采用为主方案，见第9节 |
| Lunar MCPX | 开源自托管 | 内置 | 是（Docker） | 未查证 | 未采用，规模过小+关键能力锁企业层 |
| Kong AI/MCP Gateway | 商业核心+部分开源 | Kong内置鉴权体系 | 是（企业版） | 未查证 | 未采用，基础设施过重 |
| Higress | 开源，CNCF Sandbox | Istio/Envoy生态内置 | 是 | 不适用（自托管） | 未采用，服务网格量级过重 |
| Cloudflare MCP Server Portals | SaaS边缘产品 | Cloudflare Access | 否 | 未查证，云端为主默认视为可达性风险 | 未采用，云端SaaS |
| Portkey | SaaS + 部分开源 | API Key | 部分 | 未查证 | 不采用为主方案，MCP能力非其优先级 |
| LiteLLM | 开源+企业层SaaS | API Key/虚拟Key | 是 | 未查证 | 不采用，F-COST-001已否决同一模式 |

## 6｜真实用户与开发者评价

### 6.1 MCP工具审批的行业共识（本模块核心问题的独立证据）

独立技术分析（非厂商自证，nhimg.org，2026）明确指出"MCP工具审批是一个实现层的约定，不是协议标准状态"（"an implementation-layer control, not a protocol-standard approval state"），组织必须自己在MCP协议之上搭建审批语义。文章列出的真实治理难点——"待批状态的可观测性"（区分等待/拒绝/重试/放行，避免把流程噪音误判为治理信号）、"申请者身份必须成为鉴权变量本身而非只是审计标签"（防止审批权限跨身份/跨会话漂移）、"审批疲劳"（如果人类批准的动作本来policy就能决定，审批门就变成了"只增加延迟的表演"）——这三条与Matbox原设计P0规则"高风险动作必须明确展示风险/可逆性给用户确认，不能隐藏在无感知的自动执行里"以及F-APPROVAL-001已有的ApprovalChainPolicy fail-closed机制方向一致，本报告要求把"申请者身份是鉴权变量而非仅审计标签"这条显式写入ACTION-F001的验收标准（第23/27节），原设计对这一点没有讲清楚。

### 6.2 agentgateway

- 定位准确性核实："AgentGateway同时是双重用途的安全网关"——既做LLM路由的凭据注入层（专项10已评估），也做MCP集成的工具执行安全网关（本报告新评估角度），"支持细粒度RBAC(CEL策略引擎)、限流、TLS、OpenTelemetry"；文档未明确提及原生approval workflow或blast-radius量化分级能力，本报告如实标注这条边界，不夸大它的现成能力。
- 架构背书："开发者把构建ztunnel（Rust轻量级代理）的经验以及多年运维Envoy的经验应用到了agentgateway"——出自Solo.io团队（Istio生态核心贡献商业公司之一），是有真实工程履历支撑的团队，不是概念验证项目。
- **对Matbox的意义**：技术可信度足够高，但审批/风险分级能力的缺失恰好印证了第3.3节的核心结论——即便是这批候选里最成熟、最活跃的一个，也没有原生覆盖Matbox 10步Pipeline的全部judgement逻辑，只能承担协议层这一段。

### 6.3 IBM ContextForge

- 真实的、非营销材料的Issue记录：`IBM/mcp-context-forge#4202`记录了一个真实的协议合规bug——"ContextForge Gateway无条件校验MCP工具响应的outputSchema，包括`isError:true`的错误响应，这违反了MCP规范，导致标准合规的错误处理触发校验失败"。另有集成测试文档记录的多个上游API bug（"Toggle Endpoints Return Stale State"、"Prompts API Accepts Empty Template Field"）。
- **命名与实际治理关系需要澄清的一点**：仓库名带"IBM"前缀容易让人误以为有厂商级商业支持，但项目页面/社区讨论明确该项目"是社区维护的开源项目，没有IBM或其关联公司的官方商业支持"——这是一条容易被误判的信号，本报告要求Stage 10前置任务如果考虑ContextForge，需在合同/依赖登记时明确标注"非IBM官方支持产品"，避免团队产生"大厂背书"的错误安全感。
- **对Matbox的意义**：功能面（Tools/Agent/API Gateway三合一+40多个插件）比agentgateway更全，1.0 GA也是真实的成熟度信号，但真实bug记录+"品牌名与实际支持关系不符"这两条使其排在agentgateway之后。

### 6.4 Obot

- 定位："开源MCP Gateway和AI治理平台"，"内置目录、组合式server支持、开箱即用的多角色RBAC"。
- 真实的成熟度信号（非负面，是中性事实）：G2平台该产品条目截至查证日**0条评分记录**，说明这个产品目前主要靠自身博客/公关材料建立认知，独立第三方使用体验证据几乎为零，这与专项01报告对Betterleaks"7个月历史、独立评测方明确标注太年轻"是同一类型的证据缺口，本报告用同一标准对待。
- **对Matbox的意义**：923 star规模显著小于agentgateway/ContextForge，且"AI治理平台"这个定位本身有一定风险——如果它的RBAC/policy机制设计得足够"重"，反而可能像专项28报告发现的Google ADK Runner/Session那样，与Matbox自己的判定层产生"两个真相源"冲突，因此即便社区规模足够也不适合作为协议层REUSE对象，排第3。

### 6.5 Lunar MCPX

- 独有能力核实："三层粒度的策略控制——全局(所有server)/单服务(一个server)/单工具(具体工具函数)"，被独立评测称为"开源MCP网关里最细粒度的访问控制模型"，且有"风险评分"能力。
- **关键限制**：风险评分/自动化能力被核实为"企业层"专属，MIT许可只覆盖核心，与Infisical Dynamic Secrets、SonarQube打包分析器同款"核心开源、关键能力锁企业版"模式。且规模（468 star，39 fork）是本轮候选里最小的。
- **对Matbox的意义**：细粒度策略模型设计思路有参考价值，但免费自托管版本能拿到的能力比宣传的"风险评分"要少，规模也不足以支撑长期依赖，本报告不采纳，仅记录设计思路供ACTION-F001自研的blast-radius分级逻辑参考。

### 6.6 Sierra（真实事故案例，独立于厂商自证）

见第3.7节。Gap.com案例来源为多篇独立安全/AI行业媒体对2025年12月越狱攻击事件的报道交叉印证，不是Sierra自己的公关材料。

## 7｜源码审查报告

本模块自身的判定业务逻辑（ACTION-F001/F003/F004/F005）不存在"需要复核的现成源码"（自研）。本节聚焦REUSE对象的最低限度可信度核查：

| 组件 | 复核对象 | 结论 |
|---|---|---|
| agentgateway | 主分支（Rust实现，MCP/A2A协议处理、CEL策略引擎） | 未做逐行代码级复核（Stage 10前置任务之一，与专项10报告对该项目的处理方式一致），但治理背书（Linux Foundation TSC治理、250+贡献者/50+组织的独立活动数据、Solo.io团队的Envoy/ztunnel履历）已达到"值得列为正式REUSE对象"的最低可信度门槛，与专项01报告对DefectDojo/ArchUnit、专项10报告对OpenBao采用的治理背书标准一致 |
| IBM ContextForge | 主分支（Python + Rust运行时组件） | 确认为真实、可运行的生产级代码（1.0 GA、161+贡献者），非demo；已知bug（#4202等）记录在案，未发现License或架构层面的阻断性问题 |
| Obot | 主分支 | 确认为真实存在、可自托管部署的代码库，非空壳项目；但独立第三方使用证据几乎为零，源码可信度本身不构成否决理由，否决理由是社区验证不足+定位风险（见第6.4节） |

**本次审计的源码级结论**：所有REUSE候选中，只有agentgateway同时满足"有独立于本次评估之外的第二次核查印证"（专项10报告已用同一数据源核实过它的活跃度）+"团队履历可信"两条，是本模块唯一建议进入Stage 10真实联调的协议层组件；其余候选记录在案供未来触发条件出现时重新评估，不构成当前阻塞。

## 8｜License与商用风险

| 组件 | License | 是否OSI开源 | 商用/自托管是否允许 | 风险等级 | 备注 |
|---|---|---|---|---|---|
| agentgateway | Apache-2.0 | 是 | 完全允许，含专利授权条款 | 低 | 与专项10报告License结论一致，同一REUSE对象不重复评估 |
| IBM ContextForge | Apache-2.0 | 是 | 完全允许 | 低 | 核实文件本身内容为标准Apache-2.0全文，非"IBM"品牌带来的额外条款 |
| Obot | MIT | 是 | 完全允许 | 低 | — |
| Lunar MCPX | MIT（核心） | 是（核心） | 核心功能完全允许，企业层功能需另行商业授权 | 低（核心）/不适用（企业层未采纳） | 与Infisical企业功能同款风险登记模式 |
| Kong | 部分开源（核心）+商业闭源（企业插件，含AI MCP Proxy是否需要企业层，需Stage 10前核实） | 部分 | 商业插件需付费订阅 | 未采纳，风险等级不适用 | — |
| Higress | Apache-2.0 | 是 | 完全允许 | 低 | 未采纳，非License原因 |
| Cloudflare MCP Server Portals | 商业闭源SaaS | 否 | 需商业订阅 | 未采纳，风险等级不适用 | — |
| Portkey | 部分开源 | 部分 | 未采纳 | 不适用 | — |
| LiteLLM | MIT（核心）+ 企业层商业授权 | 是（核心） | 核心功能允许 | 低（核心），未采纳理由非License | 与F-COST-001报告License结论一致 |

**P0结论**：本模块最终技术路线（自研判定层+REUSE agentgateway协议层）不引入任何AGPL/SSPL/BUSL级别的核心依赖；agentgateway的Apache-2.0与Matbox已有的OPA/Temporal同属"真开源、专利条款干净"的许可证类别，风险画像一致。

## 9｜候选方案对比及淘汰原因（含前三名排名+理由）

### 9.1 "整体外包给某个MCP Gateway产品"的模块级核查（方法论第2条，最重要的问题）

| 排名 | 方案 | 排名理由 |
|---|---|---|
| **#1** | **现有路线：10步Pipeline业务判定100%自研 + agentgateway承担协议层** | 唯一同时满足"理解Matbox自己的ProposedAction/WorkPackage/risk_level语义""自托管优先""不新增第二套需要独立运维的协议网关（与CRED-F004共用agentgateway）"三条硬约束的方案；第3.3节的六维能力核查表已证明没有任何现成产品覆盖全部六项能力 |
| 落选（非整体外包，见3.3/9.2） | IBM ContextForge / Obot / Lunar MCPX 整体采纳 | 均只能替代协议层这一小块，且都不具备审批门禁/blast-radius分级/按业务对象归因预算门禁这些Matbox专属语义，整体采纳不会消除自研工作量，只会多背一个需要独立评估的开源依赖 |
| 落选 | Kong / Higress | 能力方向对但基础设施量级与Matbox当前2人团队规模不匹配，见3.5节 |
| 落选 | Cloudflare MCP Server Portals / Portkey | 云端SaaS为主，与自托管优先原则冲突 |
| 落选 | LiteLLM | 与F-COST-001已否决的合并路线同构，见3.6节 |

**#1为什么赢**：这不是"默认自建"，是第3.3节六维能力表逐项核查后的必然结论——市面上最成熟的候选（agentgateway）本身也主动把"要不要放行"这个判断留给了接入方（"部署agentgateway代理的Agent不持有凭据，且无法调用未被显式允许的工具，工具级访问控制可以实时观测到某个工具被拦截"——这句话本身描述的是agentgateway**执行**Matbox配置好的允许/拒绝名单，不是agentgateway自己**决定**risk_level该不该允许），这与专项28报告发现的"主流Agent框架都提供手动接管工具执行模式，说明工具调用这个最核心环节无论如何都要自己接管"是同一类型的独立证据。

### 9.2 ACTION-F002 Tool/MCP协议适配层 Top-3（本报告新增，原设计"基于MCP Gateway生态"是一句未展开的定性描述，本节是展开后的具体选型）

| 排名 | 候选 | 排名理由 |
|---|---|---|
| **#1 agentgateway** | Apache-2.0，Linux Foundation治理，Rust | 规模最大（4.6k star/785 fork/2536 commit）、治理最正式（Technical Steering Committee）、原生MCP+A2A协议、多租户+CEL RBAC+预算控制雏形一应俱全；**决定性因素是与专项10报告CRED-F004的复用协同**——同一部署实例可以同时服务两个专项，边际运维成本趋近于零，这是其余候选都不具备的独特优势 |
| **#2 IBM ContextForge** | Apache-2.0，1.0 GA | 功能面（Tools/Agent/API Gateway三合一）比agentgateway更全，社区规模相当（4.1k star/161+贡献者）；排第2是因为(1)无法与CRED-F004共用同一部署（专项10报告未评估过它作为凭据代理的可行性，引入意味着新增一套独立运维的组件）(2)已发现真实、非阻断但需要跟踪的协议合规bug(3)"IBM"命名容易造成误判的商业支持假象 |
| **#3 Obot** | MIT，K8s/Docker自托管 | "AI治理平台"定位使其RBAC/policy能力理论上覆盖面更广，但独立第三方验证证据（G2评分数）几乎为零，且"治理平台"定位有与Matbox自己判定层产生状态源冲突的潜在风险（类比专项28报告Google ADK Runner/Session问题），社区规模也是三者中最小 |
| 落选 | Lunar MCPX | 规模最小（468 star），关键的风险评分能力锁在企业层，见6.5节 |
| 落选 | Docker MCP Gateway / Microsoft MCP Gateway | 前者无RBAC/多租户，后者强绑定Azure生态，均不满足Matbox"不绑定单一云厂商"原则 |
| 落选 | Kong / Higress | 基础设施量级过重，见3.5节 |

**#1为什么胜过#2/#3**：不是因为agentgateway单项能力最强（ContextForge的功能面确实更全），而是**"一套基础设施、两个专项复用"这个真实、可核查的边际成本优势**——这与Matbox在OPA（F-DQ-008/TENANT-F003/APPROVAL-F005三方复用同一实例）、Temporal（F-QUEUE-001/F-TASK-001/F-APPROVAL-001/F-RUNTIME-001共用同一集群）上反复验证过的模式完全一致，是Matbox自己方法论内部一致性的直接应用，不是新发明的判断标准。

## 10｜最终技术路线与选择依据

| FeatureID | 最终路线 | 依据（含Top-3排名回填） |
|---|---|---|
| ACTION-F001 ActionGateway核心（Policy/Risk/Reauth/Idempotency） | **Matbox自研** | 第9.1节：没有任何候选整体覆盖这层业务判定逻辑，六维能力核查表逐项证明 |
| ACTION-F002 Tool/MCP注册与Adapter层 | **REUSE协议传输层（agentgateway）+ Matbox自研ToolRegistration业务语义** | 第9.2节Top-3第1名：击败IBM ContextForge（#2，功能更全但无CRED-F004协同+已知bug）、Obot（#3，治理平台定位有状态源冲突风险+社区证据不足）；Lunar MCPX/Docker/Microsoft/Kong/Higress均落选 |
| ACTION-F003 Action预览与确认 | **Matbox自研** | 第0/1节：与F-APPROVAL-001是不同粒度的两层机制（同步单人UX确认 vs 异步多人正式审批），非重复设计，无第三方候选理解这层UX/风险展示语义 |
| ACTION-F004 幂等与可逆性 | **Matbox自研（复用F-TASK-001/F-APPROVAL-001已验证的Outbox/幂等模式）** | 与APPROVAL-F002 Transactional Outbox同构，不新建第二套幂等实现 |
| ACTION-F005 10步Enforcement Pipeline | **Matbox自研编排 + REUSE各步骤对应的既有专项判定结果** | 每一步查询相邻已冻结专项（TENANT/APPROVAL/COST/CRED/EGRESS/OBS），本身不是可以整体外包的单一产品能力，是跨6个专项的编排逻辑 |

## 11｜自研、复用、二开和采购的边界

| 类型 | 对象 | 说明 |
|---|---|---|
| OWN | ActionGateway核心Policy/Risk/Reauth/Idempotency判定逻辑、ProposedAction/ToolRegistration/ActionExecution/ActionAuditRecord状态机、blast-radius风险半径分级规则、ACTION-F003预览UX展示逻辑、10步Pipeline编排本身 | Matbox自己的工具/动作执行安全业务规则，是本模块90%以上的真实工作量所在 |
| REUSE | agentgateway承担的MCP协议发现/连接/转发能力（不含策略判定）；F-TENANT-001的RBAC/ABAC判定结果；F-APPROVAL-001的审批链判定结果；F-COST-001的预算判定结果；F-CRED-001的Secret解析结果；F-EGRESS-001的出站URL安全校验；F-OBS-001的审计/trace存储 | 严格限定在"已经在Matbox其他专项冻结过的判定结果/协议传输机制"，本模块只做编排调用，不复制实现 |
| MUST NOT REBUILD | MCP协议本身的握手/消息格式规范（用agentgateway等现成实现，不自己写协议栈）；OPA的Rego引擎（F-TENANT-001已REUSE）；Temporal的Workflow/Signal机制（F-APPROVAL-001已REUSE） | 保留边界声明，避免未来重复造轮子 |
| **本报告新增的边界澄清** | ACTION-F003（即时预览确认）与F-APPROVAL-001（正式审批链）不是同一个东西，不能互相替代 | 见第0/1节详细说明，是本报告发现的原设计文档未讲清楚的一处真实边界模糊点 |

## 12｜系统架构与数据流

```
┌──────────────────────────────────────────────────────────────────────┐
│  F-RUNTIME-001 Agent Runtime（RUNTIME-F003 ToolCallDispatcher）        │
│  模型返回tool_use → 转译为ProposedAction                                │
└───────────────────────────────┬────────────────────────────────────────┘
                                 │ ① POST /action/propose
                                 ▼
        ┌──────────────────────────────────────────────────────────────┐
        │                F-ACTION-001 ActionGateway（本专项）              │
        │  ┌────────────────────────────────────────────────────────┐  │
        │  │ ACTION-F005 10步Enforcement Pipeline                     │  │
        │  │  ①Registry状态检查 ──────────────────────────▶ ToolRegistration（本域） │
        │  │  ②租户边界检查 ─────────────────────────────▶ F-TENANT-001 │
        │  │  ③Identity/RBAC/ABAC检查 ──POST /tenant/authz/check──▶ F-TENANT-001(OPA)│
        │  │  ④blast-radius风险半径检查（本域自研规则）                    │  │
        │  │  ⑤审批要求检查 ──────────────────────────────▶ F-APPROVAL-001│
        │  │  ⑥预算检查 ─────────────────────────────────▶ F-COST-001   │
        │  │  ⑦Secret解析 ───────────────────────────────▶ F-CRED-001   │
        │  │  ⑧限流/熔断检查（本域自研，可选REUSE agentgateway限流能力）      │  │
        │  │  ⑨执行 ──经ACTION-F002协议层(agentgateway转发MCP调用)───▶ Tool/MCP Server │
        │  │      （出站URL安全校验 ──────────────────────▶ F-EGRESS-001） │
        │  │  ⑩结果规范化+审计+成本+trace ─────────────────▶ F-OBS-001    │
        │  └────────────────────────────────────────────────────────┘  │
        │  ACTION-F003 预览/确认（propose返回时同步展示risk/diff，不含secret）│
        │  ACTION-F004 幂等（idempotencyKey去重）+ 可逆性（compensationRef）│
        └──────────────────────────────────────────────────────────────┘
                                 │ ② 200/403/409/402/429... + ActionExecution
                                 ▼
                    F-RUNTIME-001（回填tool_result继续推理循环）
```

**与相邻模块的调用链总结**：F-RUNTIME-001 → F-ACTION-001（propose→10步Pipeline→execute）→ 依次查询F-TENANT-001/F-APPROVAL-001/F-COST-001/F-CRED-001/F-EGRESS-001，通过ACTION-F002的agentgateway协议层实际转发到目标MCP Server/第三方API → 结果回F-RUNTIME-001，全程审计写入F-OBS-001。

## 13｜API接口清单

统一前缀`/action`。鉴权规范见第16节，错误码规范见第19节。

| 方法 | 路径 | 说明 | 对应Feature |
|---|---|---|---|
| POST | `/action/registry/tools` | 注册工具/MCP server（tool_id/tenant_scope/owner/type/version/endpoint_ref/secret_ref/capabilities/allowed_actions/risk_level/data_classes/rate_limit/timeout_ms/healthcheck/status） | ACTION-F002 |
| GET | `/action/registry/tools/{toolId}` | 查询工具注册信息/当前健康状态 | ACTION-F002 |
| POST | `/action/propose` | 提交一个ProposedAction，返回预览（risk/diff/scope，不含secret） | ACTION-F001/F003 |
| POST | `/action/{actionId}/execute` | commit时重新鉴权后按10步Pipeline真正执行 | ACTION-F001/F005 |
| GET | `/action/{actionId}` | 查询动作状态/审计记录 | ACTION-F001 |
| POST | `/action/{actionId}/compensate` | 触发可逆动作的补偿/回滚（仅reversibility=REVERSIBLE适用） | ACTION-F004 |
| GET | `/action/tool-health` | 工具/MCP server健康看板数据（含agentgateway连通性） | ACTION-F002 |

## 14｜Request/Response Schema

```yaml
ToolRegistration:
  type: object
  required: [toolId, version, name, type, endpointRef, riskLevel, status]
  properties:
    toolId: {type: string}
    version: {type: string}
    tenantScope: {type: string, nullable: true, description: "为空表示平台级工具，跨租户共享"}
    name: {type: string}
    type: {type: string, enum: [MCP_SERVER, REST_API, INTERNAL_SERVICE]}
    endpointRef: {type: string, description: "经ACTION-F002 agentgateway转发的目标地址引用，不直接暴露真实内网地址"}
    secretRef: {type: string, nullable: true, description: "关联F-CRED-001 SecretRef"}
    capabilities: {type: array, items: {type: string}}
    allowedActions: {type: array, items: {type: string}}
    riskLevel: {type: integer, minimum: 0, maximum: 5, description: "0=只读无副作用，5=不可逆高风险"}
    dataClasses: {type: array, items: {type: string}}
    rateLimit: {type: object, properties: {rpm: {type: integer}, burst: {type: integer}}}
    timeoutMs: {type: integer}
    healthcheck: {type: string, nullable: true}
    status: {type: string, enum: [ACTIVE, DISABLED]}
    createdAt: {type: string, format: date-time}

ProposedAction:
  type: object
  required: [actionId, tenantId, employeeId, toolId, toolVersion, risk, reversibility, status, idempotencyKey]
  properties:
    actionId: {type: string, format: uuid}
    tenantId: {type: string}
    employeeId: {type: string}
    toolId: {type: string}
    toolVersion: {type: string}
    resourceScope: {type: array, items: {type: string}}
    risk: {type: string, enum: [LOW, MEDIUM, HIGH, CRITICAL]}
    reversibility: {type: string, enum: [REVERSIBLE, IRREVERSIBLE]}
    budgetRef: {type: string, nullable: true}
    approvalRef: {type: string, nullable: true, description: "关联F-APPROVAL-001 AiApproval.approvalId，仅risk触发审批要求时非空"}
    status: {type: string, enum: [PROPOSED, APPROVED, EXECUTING, SUCCEEDED, FAILED, DENIED]}
    idempotencyKey: {type: string}
    previewShownAt: {type: string, format: date-time, nullable: true, description: "ACTION-F003预览确认时间戳"}
    previewConfirmedBy: {type: string, nullable: true}
    createdAt: {type: string, format: date-time}

ActionExecution:
  type: object
  required: [executionId, actionId, resultStatus]
  properties:
    executionId: {type: string, format: uuid}
    actionId: {type: string}
    egressValidationRef: {type: string, nullable: true, description: "关联F-EGRESS-001校验记录，执行步生效"}
    compensationRef: {type: string, nullable: true}
    executedAt: {type: string, format: date-time}
    resultStatus: {type: string, enum: [SUCCEEDED, FAILED, TIMEOUT]}
    costRef: {type: string, nullable: true, description: "关联F-COST-001 UsageLedgerEntry"}
    delegatedBy: {type: string, nullable: true, description: "关联F-CRED-001 AgentIdentity.delegatedBy链条，用于ACTION-F005验收标准'委派权限不得放大'的校验"}

ActionAuditRecord:
  type: object
  required: [recordId, actionId, decision, reauthCheckedAt, actorId]
  properties:
    recordId: {type: string, format: uuid}
    actionId: {type: string}
    decision: {type: string, enum: [ALLOWED, DENIED]}
    denyReason: {type: string, nullable: true, description: "对应10步Pipeline哪一步拒绝，如TOOL_UNREGISTERED/TENANT_BOUNDARY_VIOLATION/AUTH_FORBIDDEN/APPROVAL_REQUIRED/BUDGET_EXCEEDED/RATE_LIMITED"}
    reauthCheckedAt: {type: string, format: date-time, description: "commit-time重新鉴权时间戳，不得为propose时刻的旧值"}
    actorId: {type: string}
    untrustedContentFlags: {type: array, items: {type: string}, description: "标记工具返回内容中被判定为不可信内容的片段引用，呼应架构原则'Web/browser/tool输出必须当作不可信内容处理'"}
```

## 15｜OpenAPI 3.0文档

```yaml
openapi: 3.0.3
info:
  title: Matbox Action Gateway API
  version: "1.0.0"
  description: >
    F-ACTION-001对外暴露的最小API集合。10步Enforcement Pipeline的实现细节见第9-12节，
    鉴权见第16节，错误码统一使用 Matbox_错误码规范_正式开发文档_V1.0-RC.md。
servers:
  - url: https://internal.matbox.local/action
paths:
  /action/propose:
    post:
      operationId: proposeAction
      summary: 提交一个ProposedAction，返回risk/diff预览（不含secret）
      security: [{ bearerAuth: [] }]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [toolId, toolVersion, resourceScope, idempotencyKey]
              properties:
                toolId: { type: string }
                toolVersion: { type: string }
                resourceScope: { type: array, items: { type: string } }
                idempotencyKey: { type: string }
      responses:
        "201":
          description: 已创建，含预览信息（ACTION-F003）
          content:
            application/json:
              schema: { $ref: "#/components/schemas/ProposedAction" }
        "403":
          description: TOOL_UNREGISTERED / AUTH_FORBIDDEN / TENANT_BOUNDARY_VIOLATION
        "409":
          description: IDEMPOTENCY_CONFLICT
  /action/{actionId}/execute:
    post:
      operationId: executeAction
      summary: commit时重新鉴权后按10步Pipeline真正执行
      security: [{ bearerAuth: [] }]
      parameters:
        - { name: actionId, in: path, required: true, schema: { type: string } }
      responses:
        "200":
          description: 执行完成
          content:
            application/json:
              schema: { $ref: "#/components/schemas/ActionExecution" }
        "402": { description: BUDGET_EXCEEDED }
        "409": { description: "APPROVAL_REQUIRED（审批未完成）/ INVALID_STATE_TRANSITION" }
        "429": { description: RATE_LIMITED }
        "504": { description: TOOL_TIMEOUT }
  /action/{actionId}/compensate:
    post:
      operationId: compensateAction
      summary: 触发可逆动作的补偿/回滚
      security: [{ bearerAuth: [] }]
      parameters:
        - { name: actionId, in: path, required: true, schema: { type: string } }
      responses:
        "200": { description: 补偿已触发 }
        "409": { description: "reversibility=IRREVERSIBLE，不可补偿" }
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT（携带tenantId claim，见第16节）
  schemas:
    ProposedAction:
      type: object
      description: 见第14节完整定义
    ActionExecution:
      type: object
      description: 见第14节完整定义
```

## 16｜鉴权、权限与多租户规范

**完全复用**F-TENANT-001（TENANT-F001~F006）已冻结的模式，不新建平行鉴权体系，与专项17（F-APPROVAL-001）报告采用的模式一致：

1. **AI员工发起动作**：调用方持有F-CRED-001签发的CRED-F003短期Token（AgentCredentialGrant），`POST /action/propose`校验该Token对应的scope是否覆盖`resourceScope`，不足则直接拒绝（`AUTH_FORBIDDEN`），不进入后续9步。
2. **10步Pipeline第③步Identity/RBAC/ABAC检查**：调用`POST /tenant/authz/check`（`resource_type=action_tool`, `action=execute`），AI员工主体先查F-CRED-001取scope再转OPA评估，与专项06报告第12节架构图完全同构，不新增第二套判定逻辑。
3. **委派权限不得放大（P0）**：`ActionExecution.delegatedBy`必须与F-CRED-001 AgentIdentity的委派链条一致，`POST /action/{actionId}/execute`时校验委派链上每一环的scope是交集缩小而非扩大，违反则`AUTH_FORBIDDEN`并记入`untrustedContentFlags`同级的委派异常审计。
4. **多租户隔离**：`tool_registration`/`proposed_action`/`action_execution`/`action_audit_record`全部带`tenant_id`字段（`tool_registration.tenant_scope`为空时表示平台级共享工具），遵循TENANT-F004"共享表+租户ID字段"模式。
5. **PlatformAdmin访问**：查看跨租户ActionExecution记录必须走TENANT-F002定义的break-glass流程，不能静默查看，与专项17报告APPROVAL-001同一原则。
6. **禁止自我批准式绕过**：ACTION-F003的即时预览确认者（`previewConfirmedBy`）与最终触发execute的调用方身份必须来自同一AuthContext链条，不能由AI员工自己伪造"用户已确认"，预览确认动作本身要经过与决策相同等级的身份校验。

## 17｜Provider Adapter接口规范

```yaml
# ToolAdapter：ACTION-F002协议层的可插拔接口。
# 默认实现绑定agentgateway承担MCP协议发现/连接/转发，
# Matbox自己的10步Pipeline判定逻辑不感知具体走的是agentgateway还是未来替换的其他协议网关。
ToolAdapter接口（逻辑契约，非语言绑定）:
  discover(registration: ToolRegistration) -> ToolCapabilitySnapshot
    # 默认实现：调用agentgateway的MCP server发现能力，同步capabilities/allowedActions到ToolRegistration

  invoke(action: ProposedAction, resolvedSecret: SecretValue) -> ToolInvocationResult
    # 默认实现：经agentgateway转发实际的MCP tools/call请求；
    # resolvedSecret由10步Pipeline第⑦步从F-CRED-001取得，仅在本次调用的agentgateway代理进程内存中短暂存在，
    # 不落Matbox自己的日志/数据库

  healthcheck(toolId: string) -> ToolHealthStatus
    # 默认实现：查询agentgateway对该MCP server的连接健康状态

  # 未来可选的第二实现：如果agentgateway在真实场景暴露出限制（例如需要IBM ContextForge
  # 更完整的Agent Gateway/A2A能力），新增一个绑定ContextForge的实现，
  # 不改变上层ACTION-F001/F005判定逻辑对ToolAdapter接口的调用方式。
```

## 18｜Webhook、回调及异步任务规范

- **长时间运行的工具调用**：`execute`端点对于预计超过同步HTTP超时的工具调用（如需要人工介入的第三方系统操作），走worker/outbox模式而非阻塞HTTP连接——`ActionExecution`先落PENDING态，Activity执行完成后经Outbox Dispatcher回写状态，与F-APPROVAL-001已确立的"DB commit后才对外发事件"模式同构，不允许在事务commit前就先触发外部副作用。
- **agentgateway连通性事件**：ACTION-F002监听agentgateway的健康检查/连接状态变化，异常时触发`TOOL_UNREGISTERED`类降级（该工具的新ProposedAction一律拒绝，不是让请求超时才发现）。
- **委派链回执**：跨AI员工委派场景下，子Agent的ActionExecution完成后需要把结果通过Signal机制回传给发起委派的父Agent对应的F-RUNTIME-001 Workflow，复用F-TASK-001已有的Outbox+Signal模式，不新建第二套委派结果回传通道。

## 19｜错误码、重试、超时和降级规范

**完全复用**`Matbox_错误码规范_正式开发文档_V1.0-RC.md`定义的17个跨模块错误码——该规范制定时已经预留了F-ACTION-001专属映射（`TOOL_UNREGISTERED`/`TOOL_POLICY_DENIED`/`TOOL_TIMEOUT`三个码的"主要使用模块"列已标注ACTION-F002），本模块直接落地，不新造码：

| 场景（对应10步Pipeline哪一步） | 错误码 | HTTP | 可重试 |
|---|---|---|---|
| ①Registry状态检查：工具未注册/已禁用 | TOOL_UNREGISTERED | 403 | 否 |
| ②租户边界检查：跨租户访问工具/资源 | TENANT_BOUNDARY_VIOLATION | 403 | 否 |
| ③Identity/RBAC/ABAC检查：策略拒绝 | AUTH_FORBIDDEN | 403 | 否 |
| ④blast-radius风险半径检查：策略拒绝该风险等级动作 | TOOL_POLICY_DENIED | 403 | 否 |
| ⑤审批要求检查：需要审批但尚未完成 | APPROVAL_REQUIRED | 409 | 否 |
| ⑥预算检查：预算策略阻断 | BUDGET_EXCEEDED | 402 | 否 |
| ⑦Secret解析失败 | INTERNAL_ERROR（details标注`secretResolveError`） | 500 | 是（有界） |
| ⑧限流/熔断检查：触发限流 | RATE_LIMITED | 429 | 是 |
| ⑨执行：工具调用超时 | TOOL_TIMEOUT | 504 | 是（幂等键保护下） |
| ⑨执行：agentgateway/工具端不可用 | PROVIDER_UNAVAILABLE（沿用同一降级语义，不新造TOOL_UNAVAILABLE） | 503 | 是 |
| 同idempotencyKey但payload不同 | IDEMPOTENCY_CONFLICT | 409 | 否 |
| ProposedAction已是终态，收到非法转移请求 | INVALID_STATE_TRANSITION | 409 | 否 |

**降级规范**：任一步判定错误或不确定（如OPA/agentgateway不可达）一律fail-closed（默认DENY，不放行），与F-APPROVAL-001、TENANT-F003同一原则；`RATE_LIMITED`/`TOOL_TIMEOUT`/`PROVIDER_UNAVAILABLE`的重试必须携带同一`idempotencyKey`，重试前不得重新生成新的ActionExecution记录。

## 20｜数据库及Migration设计

沿用Flyway迁移工具，共享表+`tenant_id`字段模式，与F-APPROVAL-001/F-CRED-001同构。

```sql
-- V1__action_gateway_core_tables.sql

CREATE TABLE tool_registration (
    tool_id VARCHAR(64) NOT NULL,
    version VARCHAR(32) NOT NULL,
    tenant_scope UUID, -- NULL = 平台级共享工具
    name VARCHAR(128) NOT NULL,
    type VARCHAR(32) NOT NULL, -- MCP_SERVER|REST_API|INTERNAL_SERVICE
    endpoint_ref VARCHAR(256) NOT NULL, -- 经agentgateway转发的目标地址引用
    secret_ref VARCHAR(128),
    capabilities JSONB NOT NULL DEFAULT '[]',
    allowed_actions JSONB NOT NULL DEFAULT '[]',
    risk_level SMALLINT NOT NULL CHECK (risk_level BETWEEN 0 AND 5),
    data_classes JSONB NOT NULL DEFAULT '[]',
    rate_limit_rpm INT,
    rate_limit_burst INT,
    timeout_ms INT NOT NULL DEFAULT 30000,
    healthcheck_ref VARCHAR(256),
    status VARCHAR(16) NOT NULL DEFAULT 'ACTIVE', -- ACTIVE|DISABLED
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (tool_id, version)
);
CREATE INDEX idx_tool_registration_tenant ON tool_registration(tenant_scope);
CREATE INDEX idx_tool_registration_status ON tool_registration(status);

CREATE TABLE proposed_action (
    action_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    employee_id VARCHAR(128) NOT NULL,
    tool_id VARCHAR(64) NOT NULL,
    tool_version VARCHAR(32) NOT NULL,
    resource_scope JSONB NOT NULL DEFAULT '[]',
    risk VARCHAR(16) NOT NULL, -- LOW|MEDIUM|HIGH|CRITICAL
    reversibility VARCHAR(16) NOT NULL, -- REVERSIBLE|IRREVERSIBLE
    budget_ref VARCHAR(128),
    approval_ref UUID, -- 关联F-APPROVAL-001 ai_approval.approval_id
    status VARCHAR(16) NOT NULL DEFAULT 'PROPOSED', -- PROPOSED|APPROVED|EXECUTING|SUCCEEDED|FAILED|DENIED
    idempotency_key VARCHAR(256) NOT NULL,
    preview_shown_at TIMESTAMPTZ,
    preview_confirmed_by VARCHAR(128),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    FOREIGN KEY (tool_id, tool_version) REFERENCES tool_registration(tool_id, version),
    UNIQUE (tenant_id, employee_id, idempotency_key)
);
CREATE INDEX idx_proposed_action_tenant ON proposed_action(tenant_id);
CREATE INDEX idx_proposed_action_status ON proposed_action(status);

CREATE TABLE action_execution (
    execution_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    action_id UUID NOT NULL REFERENCES proposed_action(action_id),
    egress_validation_ref VARCHAR(128),
    compensation_ref VARCHAR(128),
    delegated_by VARCHAR(128), -- 关联F-CRED-001 AgentIdentity.delegatedBy链条
    executed_at TIMESTAMPTZ,
    result_status VARCHAR(16) NOT NULL DEFAULT 'PENDING', -- PENDING|SUCCEEDED|FAILED|TIMEOUT
    cost_ref VARCHAR(128),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_action_execution_action ON action_execution(action_id);

CREATE TABLE action_audit_record (
    record_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    action_id UUID NOT NULL REFERENCES proposed_action(action_id),
    decision VARCHAR(16) NOT NULL, -- ALLOWED|DENIED
    deny_reason VARCHAR(64), -- 对应第19节错误码
    reauth_checked_at TIMESTAMPTZ NOT NULL,
    actor_id VARCHAR(128) NOT NULL,
    untrusted_content_flags JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_action_audit_action ON action_audit_record(action_id);
CREATE INDEX idx_action_audit_tenant_decision ON action_audit_record(tenant_id, decision);
```

## 21｜前后端开发任务拆分

**后端（Java/Spring Boot，RuoYi-Vue-Pro基座）**：
- BE-01 ActionGatewayService + ProposedAction状态机（propose/execute状态转移，ACTION-F001）
- BE-02 10步Enforcement Pipeline编排器（依次调用TENANT/APPROVAL/COST/CRED/EGRESS客户端，ACTION-F005）
- BE-03 ToolRegistrationService（注册/查询/健康检查，ACTION-F002）
- BE-04 ToolAdapter接口 + AgentGatewayToolAdapter默认实现（封装agentgateway MCP协议调用，ACTION-F002）
- BE-05 ACTION-F003预览渲染逻辑（risk/diff计算，secret脱敏校验）
- BE-06 幂等/补偿服务（idempotencyKey去重、compensationRef回滚触发，ACTION-F004）
- BE-07 与F-TENANT-001/F-APPROVAL-001/F-COST-001/F-CRED-001/F-EGRESS-001/F-OBS-001的客户端封装（shared-clients）

**前端（Ops控制台，复用既有多端框架）**：
- FE-01 工具/MCP server注册管理页（ACTION-F002）
- FE-02 ProposedAction预览/确认组件（risk/diff展示，明确不渲染secret字段，ACTION-F003）
- FE-03 工具健康看板（含agentgateway连通性状态，第13节`/action/tool-health`）
- FE-04 ActionAuditRecord审计查询页（按tenant/actor/decision过滤）

## 22｜源码目录、模块和依赖关系

```
backend/
  modules/
    action-gateway/
      registry/               # ACTION-F002：ToolRegistrationService
      adapter/                 # ACTION-F002：ToolAdapter接口, AgentGatewayToolAdapter实现
      pipeline/                 # ACTION-F005：10步Enforcement Pipeline编排器
      preview/                   # ACTION-F003：预览/确认逻辑
      idempotency/                # ACTION-F004：幂等/补偿服务
      shared/
        contracts/                 # ToolRegistration/ProposedAction/ActionExecution/ActionAuditRecord DTO
        errors/                      # 复用Matbox_错误码规范统一ErrorResponse
    shared-clients/
      tenant-client/                  # F-TENANT-001
      approval-client/                  # F-APPROVAL-001
      cost-client/                       # F-COST-001
      cred-client/                        # F-CRED-001
      egress-client/                       # F-EGRESS-001
      obs-client/                           # F-OBS-001
      agentgateway-client/                   # ACTION-F002协议层REUSE对象
frontend/
  apps/ops-console/
    features/action-gateway/        # 对应FE-01/FE-02/FE-03/FE-04
```

**依赖方向铁律**：`action-gateway/*`只允许依赖`shared-clients/*`和自己内部子模块；`adapter/`内部的`ToolAdapter`接口实现可插拔（`AgentGatewayToolAdapter`为默认且唯一当前实现），新增第二个协议层实现（如ContextForge）时不得反向修改`pipeline/`或`preview/`模块的对外契约，与专项17报告`ChainEngine`可插拔接口的设计原则一致。

## 23｜测试集、Golden Set和验收脚本

| 测试ID | 场景 | 验收标准 |
|---|---|---|
| ACTION-T001 | 未注册工具调用 | 工具未在`tool_registration`登记，propose请求被拒绝（TOOL_UNREGISTERED），留审计 |
| ACTION-T002 | commit-time重新鉴权 | propose时刻权限有效，execute前该权限被撤销，execute必须重新校验并拒绝，不沿用propose时刻的旧判断 |
| ACTION-T003 | 委派权限放大检测 | 构造子Agent尝试用超过父Agent授权范围的scope执行动作，验证被拒绝（AUTH_FORBIDDEN），对应P0冻结规则第6条 |
| ACTION-T004 | 高风险动作预览不泄露secret | 构造risk=HIGH的ProposedAction，验证`/action/propose`返回体的risk/diff字段不包含任何secret值 |
| ACTION-T005 | 幂等重试不重复产生副作用 | 同一idempotencyKey重复调用execute，验证只产生一次真实外部副作用（如只发一次邮件） |
| ACTION-T006 | 审批未完成时execute被拒绝 | ProposedAction的risk触发了ApprovalChainRequirement但F-APPROVAL-001尚未APPROVED，execute返回APPROVAL_REQUIRED |
| ACTION-T007 | 预算超限拦截 | 构造budgetRef对应的F-COST-001预算已耗尽，execute返回BUDGET_EXCEEDED，不产生任何外部副作用 |
| ACTION-T008 | agentgateway不可达降级 | 人为断开agentgateway连接，验证该工具的execute请求fail-closed返回PROVIDER_UNAVAILABLE，不静默放行 |
| ACTION-T009 | 出站URL安全校验联调 | 构造工具endpoint指向私有网段/云元数据端点，验证F-EGRESS-001在执行步正确拦截 |
| ACTION-T010 | 跨租户越权 | 租户A的AI员工尝试调用租户B专属（`tenant_scope`非空）的工具，验证TENANT_BOUNDARY_VIOLATION |
| ACTION-T011 | 不可信内容标记 | 工具返回内容中嵌入伪装成指令的文本，验证`untrustedContentFlags`正确标记，不被F-RUNTIME-001当作可信指令回填 |
| ACTION-T012 | Sierra式guardrail绕过场景回归 | 参照第3.7/6.6节Gap.com真实案例构造对抗性输入，验证10步Pipeline在配置正确情况下仍能拦截，且任一步判定异常时fail-closed而非fail-open |

**Golden/Challenge Set**：复用F-OBS-001（OBS-F006）已确认的4类结构标准（真实生产流量抽样/对抗性测试库/人为构造边界情况/历史故障重放），Action Gateway域专属内容包括：已知的委派链越权样本、已知的risk_level误分类样本（工具实际影响范围与注册时声明的riskLevel不符）。

**验收脚本执行环境**：Stage 10前置——必须绑定真实Matbox Repo + F-TENANT-001/F-APPROVAL-001/F-COST-001/F-CRED-001/F-EGRESS-001已联调环境，且agentgateway真实部署完成，不接受synthetic样本冒充结论。

## 24｜成本、性能、并发及安全要求

**成本**：agentgateway为已投入的既有基础设施（与CRED-F004共用同一部署实例，REUSE），本模块不新增订阅费用；相对"为ACTION-F002单独再选一个协议网关"的路线，本报告的复用路线额外节省一套独立运维的开源组件成本，这是本次审计带来的真实成本节省。

**性能**：10步Pipeline中查询相邻专项（TENANT/APPROVAL/COST/CRED）的调用应尽量并行化非依赖步骤（如②③可与⑥并行发起，⑤依赖④的risk_level结果），P95延迟目标应在Stage 10真实环境下测得，不在本报告虚构阈值；agentgateway作为Rust实现的高性能代理，本身不构成性能瓶颈的主要来源。

**并发**：同一`idempotency_key`的并发execute请求必须通过数据库唯一约束/乐观锁防止重复执行；`tool_registration`的`(tool_id, version)`复合主键防止重复注册同一工具版本。

**安全**：
- 10步Pipeline任一步判定异常（含agentgateway/OPA/Temporal不可达）一律fail-closed，不允许因为下游服务不可用就默认放行。
- `resolvedSecret`只在ToolAdapter实际发起工具调用的进程内存中短暂存在，不落Matbox自己的日志/数据库/trace（呼应F-CRED-001"AI员工不得看到真实密钥明文"原则的执行层落地）。
- 工具返回内容必须标记为不可信内容（`untrustedContentFlags`），防止Prompt Injection类攻击通过工具输出反向操纵F-RUNTIME-001的推理循环，这条要求与专项28报告第9.1节发现的Google ADK真实安全事故（恶意GitHub Issue文本触发高权限Agent）针对的是同一类风险，本报告独立确认这条防护在Matbox自己的判定层生效，不依赖任何第三方框架自带的防注入机制。

## 25｜开发阶段、优先级和预计工作量

| WP | Feature | 优先级 | 量级估算（人天，粗量级） | 备注 |
|---|---|---|---|---|
| WP-ACT-01 | ACTION-F001+F002地基（ProposedAction状态机+ToolRegistration+AgentGatewayToolAdapter接入） | P0，最先 | 10-14 | agentgateway部署本身可与CRED-F004共用同一套Stage 10前置任务，见专项10报告WP估算 |
| WP-ACT-02 | ACTION-F005 10步Pipeline编排器（依次调用5个相邻专项客户端） | P0 | 8-10 | 每个客户端调用本身简单，复杂点在于错误处理/降级策略的一致性 |
| WP-ACT-03 | ACTION-F003预览/确认（risk/diff计算+secret脱敏校验） | P0 | 4-6 | secret脱敏的自动化测试覆盖是重点 |
| WP-ACT-04 | ACTION-F004幂等与可逆性（idempotency+compensation） | P0 | 5-7 | 复用F-APPROVAL-001已验证的Outbox模式，比从零设计省一部分工作量 |
| WP-ACT-05 | 与F-TENANT-001/F-APPROVAL-001/F-COST-001/F-CRED-001/F-EGRESS-001/F-OBS-001联调 | P0 | 6-8 | 依赖六个上下游模块Stage 10真实环境就绪 |

**相对原设计的工作量变化**：原设计"基于MCP Gateway生态"这句定性描述没有落到具体产品和具体工作量，本报告把ACTION-F002的REUSE对象具体化为agentgateway并确认与CRED-F004共用部署，**净节省了"为ACTION-F002单独引入并运维一个协议网关"这部分原本会隐性发生的工作量**（估算约3-5人天的独立部署/监控/升级成本），但10步Pipeline编排器（WP-ACT-02）本身是原设计文档没有拆解到具体调用顺序/降级策略层面的新增工作量，两者大致抵消，净变化持平偏正面。

## 26｜风险、阻塞项及备用方案

| 风险/阻塞项 | 等级 | 说明 | 备用方案 |
|---|---|---|---|
| agentgateway协议层能力边界不足（如未来需要IBM ContextForge更完整的A2A网关能力） | 中 | agentgateway当前不支持的MCP高级特性可能在真实接入时暴露 | ToolAdapter接口保持可插拔（第17节），触发时可新增ContextForge实现，不推翻上层判定逻辑 |
| ACTION-F003与F-APPROVAL-001边界在真实施工时被误用/混淆 | 中 | 原设计文档未讲清楚两者关系，本报告第0/1/11节已澄清但需要施工团队严格遵守 | Stage 10前置代码评审显式检查：任何"高风险"判断只能触发F-APPROVAL-001，不能用ACTION-F003的即时确认替代正式审批链 |
| 10步Pipeline中某一步相邻专项不可用导致全链路阻塞 | 中 | 本模块依赖6个其他专项，任一未就绪都会阻塞Stage 10联调 | 五个依赖专项（TENANT/APPROVAL/COST/CRED/EGRESS/OBS）均已达到DRAFT_RESEARCH_COMPLETE或已建成状态（见DocID头部依赖列表），当前无实质阻塞，只是联调顺序需要协调 |
| Sierra式guardrail配置错误导致越权响应（第3.7/6.6节真实案例） | 高（已知真实风险类型，非假设） | 即便10步Pipeline设计正确，运维配置错误仍可能导致实际防护失效 | ACTION-T012已纳入验收测试；要求Stage 10上线前对blast-radius分级规则做人工复核，不允许"配置了就默认生效"的假设 |
| agentgateway作为年轻项目（相对OPA/Temporal）未来出现治理/维护力度变化 | 低-中 | 250+贡献者/50+组织的活跃度是当前快照，不保证长期维持 | 与专项01报告对OPA"把上游issue/PR处理速度纳入长期工具健康监控指标"同一处理方式，纳入OBS-F006工具健康监控清单 |
| Stage 10真实环境未绑定（与多个依赖专项共同阻塞） | 高（既有阻塞） | 需协调与F-TENANT-001/F-APPROVAL-001/F-COST-001/F-CRED-001/F-EGRESS-001的联调顺序 | 无——等待真实Repo/Base Commit绑定，禁止伪造 |

### 26.1 外部真实案例佐证（P0规则必要性的独立验证证据，2026-09-02回填）

以下均为真实、当前可查证的外部安全问题，不是假设场景，用于说明第1节"不可变原则"不是过度设计：

| 外部案例 | 对应P0规则 | 说明 |
|---|---|---|
| Paperclip（paperclipai/paperclip）CVE-2026-41679（3个链式漏洞，含CVSS 10.0未鉴权RCE，公开Metasploit模块） | 不可变原则第1条"模型不得裸调生产API" | 详见`Matbox_专项00d_Paperclip专项评估_2026-09-02.md`——协议/权限层校验缺失导致的真实、已被武器化的RCE案例 |
| OpenWorker（andrewyng/openworker）issue #520（审批回复解析器fail open——否定句"no, don't approve"被误判为同意，且`InboxStore.resolve`一次性生效无法挽回，截至核查时仍open未修复） | 不可变原则第2条"commit-time重新鉴权是P0" | 若Matbox按已定义的commit时二次校验实现，这类"审批当时被误判"的场景会在真正提交副作用前被重新拦下，不会像OpenWorker现在这样一次性生效即执行 |
| OpenWorker issue #443（崩溃后durable resume可能把已成功的外部调用当作未完成重放，故障注入测试确定性复现邮件重复发送两次，截至核查时仍open未修复） | 不可变原则第4条"幂等是强制要求" | 印证ACTION-F004将幂等/可逆性当作独立Feature设计（而非依赖执行循环自身状态推断）是必要的，不是过度设计 |

详见`Matbox_专项00i_OpenWorker专项评估_2026-09-02.md`第2.1/3.2节（issue原文核查）。

## 27｜最终验收标准

ACTION-T001~T012（第23节）全部通过，且：
1. 人为构造agentgateway/OPA/Temporal任一下游不可达场景，确认全部fail-closed，无一处默认放行（对应第24节安全要求最高优先级验收项）。
2. commit-time重新鉴权在execute端点真实生效，propose时刻的旧判断不能作为execute放行依据（对应P0冻结规则第3条）。
3. 委派权限放大检测（ACTION-T003）与Sierra式guardrail绕过回归（ACTION-T012）两类对抗性测试全部通过。
4. ACTION-F003预览界面的secret脱敏校验在真实工具返回含敏感字段的场景下验证通过。
5. ToolAdapter接口的AgentGatewayToolAdapter默认实现完整覆盖discover/invoke/healthcheck三个方法，且与F-RUNTIME-001的RUNTIME-F003联调打通。

未通过任一项，Feature不得进入RC5 ACCEPTED流程。

## 28｜交给未来AI开发人员的完整执行说明

如果你是接手这个模块施工的未来AI开发者（Codex或其他），请按以下顺序阅读和执行：

1. **先读原设计文档**：`docs/Matbox_Action网关_正式开发文档_V1.0-RC.md`——不可变原则1-4、10步Enforcement顺序、P0冻结规则1-6仍然有效，本报告不修改这些核心业务约束。
2. **再读本报告**——本报告对原设计的三处实质性修正（详见第0节）：
   - 原设计"基于MCP Gateway生态"这句定性描述被具体化为**REUSE agentgateway承担ACTION-F002协议层**（第17节`ToolAdapter`接口+`AgentGatewayToolAdapter`默认实现），不是笼统的"生态成熟"，10步Pipeline的判定逻辑（Registry/租户/RBAC/blast-radius/审批/预算等9步业务判断）100%自研，只有第⑨步的实际协议转发REUSE。
   - 明确了ACTION-F003（即时预览确认）与F-APPROVAL-001（正式审批链）是两层不同粒度的机制，不能互相替代（第0/1/11节）。
   - agentgateway应与专项10报告CRED-F004共用同一部署实例，Stage 10施工时先确认CRED-F004的agentgateway部署状态，不要重复部署第二套。
3. **依赖检查**：施工前确认F-TENANT-001、F-APPROVAL-001、F-COST-001、F-CRED-001、F-EGRESS-001、F-OBS-001均已达到DRAFT_RESEARCH_COMPLETE或更高状态——均已确认存在（见DocID头部依赖列表）。**特别注意**：F-RUNTIME-001（Agent Runtime）作为本模块的唯一调用方，其RUNTIME-F003 ToolCallDispatcher的契约已在专项28报告中定义，Stage 10施工顺序上F-ACTION-001应先于或至少同步于F-RUNTIME-001完成核心Pipeline，避免F-RUNTIME-001被迫先实现一套临时的直连工具调用逻辑再回头改造。
4. **不要重新做的事**：不要重新调研MCP协议生态本身（第3.1节已澄清协议规模与网关产品成熟度的区别）；不要重新讨论"是否应该整体采用某个MCP Gateway产品替代自研Pipeline"——第3.3/9.1节的六维能力核查表已经系统性证明没有任何候选覆盖全部六项能力，除非未来出现某个新产品同时原生支持"tenant隔离+RBAC/ABAC+blast-radius+审批门禁+预算门禁+审计"六项且经过独立第三方验证，否则不需要重新做这个核查；不要重新调研OPA/Temporal（专项01/06/17报告已完成）。
5. **施工顺序**：WP-ACT-01（地基）必须最先完成且需与CRED-F004的agentgateway部署协调时间点，WP-ACT-02（Pipeline编排器）依赖WP-ACT-01，WP-ACT-03（预览）与WP-ACT-04（幂等）可与WP-ACT-02并行，WP-ACT-05（联调）最后。
6. **如果发现本报告与真实Repo情况冲突**：不允许因为图省事就静默降级安全要求（尤其是"fail-closed"和"commit-time重新鉴权"这两条）；发现真实冲突应记录并升级给Quality/Security Owner决策，不要自行降级。特别是如果Stage 10真实测试发现agentgateway无法满足某个具体协议场景，正确做法是评估第9.2节#2候选（IBM ContextForge）而不是绕开ToolAdapter接口直连工具。

---

## 附录｜来源汇总

- MCP协议治理与生态规模：[MCP joins the Agentic AI Foundation](https://blog.modelcontextprotocol.io/posts/2025-12-09-mcp-joins-agentic-ai-foundation/)、[Linux Foundation Announces the Formation of the Agentic AI Foundation](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation)、[OpenAI, Anthropic, and Block join new Linux Foundation effort - TechCrunch](https://techcrunch.com/2025/12/09/openai-anthropic-and-block-join-new-linux-foundation-effort-to-standardize-the-ai-agent-era/)、[MCP Hits 97M Downloads](https://www.digitalapplied.com/blog/mcp-97-million-downloads-model-context-protocol-mainstream)、[MCP Adoption Statistics 2026](https://www.digitalapplied.com/blog/mcp-adoption-statistics-2026-model-context-protocol)
- MCP Gateway产品市场综述：[10 Best MCP Gateways In 2026 - TrueFoundry](https://www.truefoundry.com/blog/best-mcp-gateways)、[Best MCP Gateways in 2026 - Manveer](https://manveerc.substack.com/p/best-mcp-gateways)、[MCP Gateway Comparison 2026 - Requesty](https://www.requesty.ai/blog/mcp-gateway-comparison-2026-enterprise-scalability-security)、[10 Best MCP Gateways - Composio](https://composio.dev/content/best-mcp-gateway-for-developers)、[The 13 Best MCP Gateways for Enterprise Teams - Obot](https://obot.ai/blog/the-13-best-mcp-gateways-for-enterprise-teams/)、[Best MCP Gateways for Rate Limiting and Access Control - MintMCP](https://www.mintmcp.com/blog/mcp-gateways-rate-limiting-access-control)、[Best Open Source MCP Gateways 2026 - Lunar](https://www.lunar.dev/post/the-best-open-source-mcp-gateways-in-2026)、[MCP Gateways Compared - Particula](https://particula.tech/blog/mcp-gateway-comparison-govern-agent-tool-access)
- agentgateway: [agentgateway/agentgateway GitHub](https://github.com/agentgateway/agentgateway)、[Designing agentgateway - agentgateway.dev](https://agentgateway.dev/blog/2026-06-04-designing-agentgateway-unified-gateway/)、[Solo.io: A new Gateway for AI Agents](https://www.solo.io/blog/why-do-we-need-a-new-gateway-for-ai-agents)、[agentgateway on Kubernetes - Kubesimplify](https://blog.kubesimplify.com/controlling-mcp-tools-with-agentgateway-on-kubernetes)、[agentgateway FAQs](https://agentgateway.dev/docs/standalone/latest/faqs/)
- IBM ContextForge: [IBM/mcp-context-forge GitHub](https://github.com/IBM/mcp-context-forge)、[Issue #4202](https://github.com/ibm/mcp-context-forge/issues/4202)、[mcp-context-forge LICENSE](https://github.com/IBM/mcp-context-forge/blob/main/LICENSE)
- Obot: [obot-platform/obot GitHub](https://github.com/obot-platform/obot)、[Introducing the Obot MCP Gateway](https://obot.ai/introducing-the-obot-mcp-gateway/)
- Lunar MCPX: [TheLunarCompany/lunar GitHub](https://github.com/TheLunarCompany/lunar)、[MCPX: From Local Experimentation to Production-Grade Infrastructure](https://www.lunar.dev/post/mcpx-from-local-experimentation-to-production-grade-infrastructure)
- Kong/Higress/Cloudflare: [Kong AI/MCP Gateway Technical Breakdown](https://konghq.com/blog/engineering/ai-gateway-mcp-gateway-mcp-server-breakdown)、[Securing MCP Servers with Kong AI Gateway](https://konghq.com/blog/product-releases/securing-observing-governing-mcp-servers-with-ai-gateway)、[Higress CNCF Sandbox](https://higress.ai/en/)、[The AI Agent Control Plane in 2026 - Preloop](https://preloop.ai/resources/ai-agent-control-plane-2026)
- Portkey/LiteLLM: [5 Portkey MCP Gateway Alternatives - MintMCP](https://www.mintmcp.com/blog/portkey-with-mcp)、[LiteLLM MCP Support PR #9426](https://github.com/BerriAI/litellm/pull/9426)、[AI Gateway Setup 2026 - Spheron](https://www.spheron.network/blog/ai-gateway-litellm-portkey-kong-gpu-cloud/)
- MCP工具审批治理分析: [MCP tool approvals at the gateway boundary - nhimg.org](https://nhimg.org/articles/mcp-tool-approvals-at-the-gateway-boundary-what-changes/)、[Top 5 MCP Gateways for Governance and Cost Controls - Maxim](https://www.getmaxim.ai/articles/top-5-mcp-gateways-for-governance-and-cost-controls/)
- Sierra真实事故案例: [Sierra AI Platform Architecture - Atlan](https://atlan.com/know/ai-agent/ai-agent-applications/what-is-sierra-ai/)、[Sierra AI review - Cybernews](https://cybernews.com/ai-tools/sierra-ai-review/)、[AI Agent Risks & Guardrails 2026 - Atlan](https://atlan.com/know/ai-agent-risks-guardrails/)
- Matbox内部依据文档: `Matbox_Action网关_正式开发文档_V1.0-RC.md`、`Matbox_AI任务运行时_正式开发文档_V1.0-RC.md`、`Matbox_AI动作审批_正式开发文档_V1.0-RC.md`、`Matbox_密钥管理_正式开发文档_V1.0-RC.md`、`Matbox_出站请求安全_正式开发文档_V1.0-RC.md`、`Matbox_成本控制_正式开发文档_V1.0-RC.md`、`Matbox_Provider_Router_正式开发文档_V1.0-RC.md`、`Matbox_错误码规范_正式开发文档_V1.0-RC.md`、`Matbox_中央编排层_正式开发文档_V1.0-RC.md`、`Matbox_专项01_代码持续质检与安全自检_技术选型与开发交接报告_2026-08-30.md`（12点方法论与Top-3格式模板）、`Matbox_专项06_租户与权限体系_技术选型与开发交接报告_2026-08-30.md`、`Matbox_专项10_密钥管理_技术选型与开发交接报告_2026-08-30.md`（agentgateway首次评估来源）、`Matbox_专项17_AI动作审批_技术选型与开发交接报告_2026-08-30.md`、`Matbox_专项28_AgentRuntime_技术选型与开发交接报告_2026-08-30.md`（F-RUNTIME-001边界依据）
