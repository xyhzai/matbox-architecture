# Matbox 专项28｜Agent Runtime（AI员工执行运行时，F-RUNTIME-001）技术选型与开发交接报告

技术选型报告 · V1.0 · 2026-08-30

**DocID**: MATBOX-RUNTIME-TECHSELECT-20260830-V1.0
**审计对象**: 无——本模块在 `Matbox_Feature_Register.md` 中状态为 **⚪ NOT_STARTED**，此前没有任何正式开发文档、没有既定选型，是本系列报告中第一个真正意义上的**从零选型**（GREENFIELD）专项。
**报告性质**: 正式技术选型报告，遵循专项01（DQ）PILOT通过后确立的12点build-vs-buy方法论与"前三名+获胜理由"格式标准。
**方法论**: 本报告逐条执行用户给定的12点build-vs-buy核查方法论；每条市场/事实性结论均标注可核查来源URL；无法验证的一律明确写"未能验证"，不编造。**因为是GREENFIELD决策，本报告对"整体执行引擎"这个模块级问题给出完整Top-3排名+获胜理由，不是走过场。**

---

## 0｜给忙碌读者的结论摘要

在深入28节之前，先给出本次审计的核心结论：

1. **模块级最终结论：Matbox自研（Java，跑在已冻结的Temporal基础设施上），不整体采纳任何现成Agent框架。** 这不是"图省事默认自研"——本报告认真核查了 Claude Agent SDK、OpenAI Agents SDK、LangGraph、CrewAI、Microsoft Agent Framework（AutoGen+Semantic Kernel合并后的继任者）、Google ADK、Vercel AI SDK、Temporal原生Agent模式共8个真实候选，前三名是 **#1 Matbox自研（Java on Temporal）> #2 Google ADK for Java > #3 LangGraph（需跨语言桥接）**，详见第9/10节。
2. **决定性证据是架构一致性，不是能力强弱**：Matbox的 F-ACTION-001（工具网关）要求所有工具调用必须经过其10步enforcement pipeline，F-TASK-001（任务运行时）已经把Checkpoint/Resume/Kill Switch这套持久化语义冻结在Temporal之上——这两条已经拍板的硬约束，让"整体采纳一个现成Agent框架（该框架自带工具执行循环和自己的持久化/checkpoint模型）"在架构上天然产生**两个竞争的执行/持久化真相源**，不是能力不够，是引入即冲突。
3. **跨语言桥接成本是本报告认真核算过的真实数字，不是含糊带过**：LangGraph生产证据最强（Klarna 8500万用户、Uber、LinkedIn、Replit、JPMorgan等约400家企业部署），但它是Python生态，Matbox后端是Java/Spring Boot（RuoYi），且团队在架构原则第33条已经明确拍板"AI员工底层保持Java单语言栈"（"团队只维护一种语言"）——引入LangGraph意味着为每一次LLM调用和每一次工具调用新增一次跨进程RPC，且需要团队新增一门语言的运维/调试能力，这个成本在本报告第9.1/10节有具体展开，不是回避这个问题。
4. **真实的技术意外发现**：Temporal官方文档里就有"Basic agentic loop with Claude and tool calling"官方Cookbook示例、以及"Spring AI integration"官方Java集成文档——这意味着"Java原生Agent Runtime"不是Matbox闭门造车，是Temporal官方认可并文档化的推荐模式，且Temporal Activity的原生心跳机制（`Activity.getExecutionContext().heartbeat()`）与架构原则第28条"心跳必须从工作循环内部发出、连续漏2次才报警"的要求高度吻合，这是本报告认为"自研"是正确路线的关键新证据，详见第3.4/9.1节。

---

## 1｜专项目标与功能边界

**Agent Runtime（内部代号 AI员工执行运行时）解决的问题**：AI员工被F-ORCHESTRATOR-001路由到、F-TASK-001创建了`ai_task`/`ai_task_step`之后，**谁、用什么机制真正执行"调用模型→模型决定要不要用工具→派发工具→把工具结果喂回模型→再判断要不要继续"这个多轮推理循环本身**——这是此前所有已建成文档都还没有写清楚的一层。

- **管什么**：
  1. 单次`ai_task_step`执行时的Prompt/上下文组装（把EmployeeTemplate的角色定义、任务目标、工具清单、历史轮次组装成一次LLM调用的message列表）；
  2. 推理主循环本身（调用模型→解析响应→按需派发工具→回填结果→判断终止条件→继续或结束）；
  3. 把LLM返回的工具调用请求（tool_use）转译成对F-ACTION-001的调用，并把工具执行结果转译回模型能理解的tool_result；
  4. 单次task step内的多轮上下文窗口管理（裁剪/摘要/缓存，区别于F-MEM-001未来要做的跨会话长期记忆）；
  5. LLM调用这一层级的错误/重试（区别于Temporal Activity级别的粗粒度重试）；
  6. 从循环内部主动发出的心跳（架构原则第28条）与对Kill信号的响应（TASK-F005）；
  7. 流式输出/中间进度通过Task API事件序列转发给前端（不直接写client response，遵守TASK-F001 P0规则1）。
- **不管什么（明确排除，避免与相邻模块重复设计）**：
  - **不是** F-TASK-001——不拥有`ai_task`/`ai_task_step`的生命周期状态机、不拥有Checkpoint/Resume/Kill Task的持久化语义，这些已经在F-TASK-001冻结；Agent Runtime只是"被F-TASK-001的Workflow在RUNNING状态下调用来执行一个具体step"的执行体。
  - **不是** F-ORCHESTRATOR-001——不做"这句话该找哪个AI员工"的路由决策，Agent Runtime拿到的输入已经是"哪个employeeId执行哪个goal"的确定结果。
  - **不是** F-ACTION-001——不做工具的权限/风险/预算/审批判定，Agent Runtime只负责把模型的工具调用请求正确地转发给F-ACTION-001的10步pipeline，自己不裁决"能不能执行"。
  - **不是** F-PROVIDER-001——不直连任何AI供应商SDK，一次模型调用永远经过F-PROVIDER-001的`invoke()`统一接口。
  - **不是** F-DELEGATION-001——跨AI员工的委派链路防护（深度上限/循环检测/幻觉级联防护）已经在DELEGATION-F005冻结，Agent Runtime内部的"单步骤自我纠错重试"复用同一条"硬上限防重试风暴"原则，但不是同一个组件。
  - **不是** F-MEM-001（记忆系统，🟡部分设计中）——跨会话/跨任务的长期记忆检索是F-MEM-001的职责，Agent Runtime只做"当前这一次task step执行期间"的短期上下文窗口管理，两者边界在第2/12节详细画出。

## 2｜Matbox架构归属

Agent Runtime属于 **Platform Core Execution** 域，是"AI员工一旦被分配了一个goal，具体怎么把这个goal执行成结果"这条主链路的心脏，被F-TASK-001在每个需要模型推理/工具调用的step上调用。

**依赖方向（入）**——Agent Runtime依赖：
- F-TASK-001（`ai_task`/`ai_task_step`生命周期，Agent Runtime是被其Workflow调用的执行体，不是反向依赖；TASK-F008自我纠错闭环包裹在Agent Runtime的输出之上）
- F-ACTION-001（所有工具/动作调用的唯一入口，Agent Runtime只转发不裁决）
- F-PROVIDER-001（所有模型调用的唯一入口，含限流/成本/区域策略，Agent Runtime只调用`invoke()`不直连SDK）
- F-AIEMP-001（EmployeeTemplate的角色定义/职责/禁止动作/技能清单，Prompt组装的输入源，只读查询不复制存储）
- F-OBS-001（心跳事件/AgentTraceEvent/OpenTelemetry写入目标，OBS-F004消费心跳做"连续漏2次报警"判定）
- F-CRED-001（AI员工执行工具调用所需的短期Grant，经F-ACTION-001间接使用，Agent Runtime自己不直接持有凭证）
- F-错误码规范（统一错误响应格式）
- Temporal（与F-TASK-001/F-QUEUE-001共用同一套集群，Agent Runtime的推理循环控制流以Temporal Workflow/Activity代码形式存在）

**被依赖方向（出）**——依赖Agent Runtime的：
- F-TASK-001（TASK-F008自我纠错、TASK-F006中途漂移检测，都需要Agent Runtime产出结构化的"本次执行结果"供其对照goal评估）
- 代码持续质检系统 F-DQ-009（Auto Repair Controller执行Codex修复任务时依赖的"Shared Agent Runtime"，这正是`Matbox_Feature_Register.md`第38行记录的挂账项——本报告落地后即解锁F-DQ-009不再是"预留占位"）
- 未来任何需要AI员工做多步骤推理+工具调用的业务模块，都通过F-TASK-001间接调用Agent Runtime，不直接依赖本模块

**与F-MEM-001的边界（明确画线，避免未来重复设计）**：
Agent Runtime管理的是"这一次task step执行期间、这一条对话/工具调用历史"要不要裁剪/摘要/利用prompt缓存——生命周期等于这一次执行；F-MEM-001（目前只完成了ACL/权限控制层，向量库/Embedding/RAG检索链路仍是⚪未开始）管的是"跨会话、跨任务、能持久检索"的长期记忆。**Agent Runtime现在不等F-MEM-001，先用自己的短期上下文管理机制跑起来；等F-MEM-001的检索链路建成后，Agent Runtime的Prompt组装步骤（RUNTIME-F001）留一个显式的"记忆检索结果注入点"，不需要现在提前设计检索算法本身。**

## 3｜全球方案调研结果

### 3.1 2026年Agent执行引擎市场分层现状

这是2026年最活跃的技术品类之一，但真实调研后发现一个此前没人系统梳理过的关键事实：**几乎所有"通用Agent框架"目前都只支持Python和/或TypeScript，专门针对Java后端的选项非常少，而Matbox恰好是Java/Spring Boot（RuoYi）技术栈**。市场按语言/定位分四层：

1. **模型厂商自带的Agent SDK**（Claude Agent SDK、OpenAI Agents SDK）——各自厂商把自己产品（Claude Code、ChatGPT/Codex）背后的Agent Loop抽出来开源/半开源给开发者，天然对自家模型优化最深，但都只有Python/TypeScript实现。
2. **独立开源编排框架**（LangGraph、CrewAI、AutoGen/Microsoft Agent Framework）——不绑定单一模型厂商，生产证据/生态成熟度差异巨大，同样以Python为主。
3. **云厂商Agent开发套件**（Google ADK）——罕见地同时提供Python **和 Java** 两套官方SDK，是本次调研里唯一"厂商官方支持、非社区移植"的Java选项。
4. **持久化工作流引擎的Agent化用法**（Temporal官方"agent as durable workflow"模式）——不是一个独立Agent框架，是"把Agent循环写成Workflow/Activity代码、复用引擎本身的durable execution能力"这条路线，Matbox已经因F-TASK-001/F-QUEUE-001把Temporal定为持久化工作流引擎，这条路线的边际引入成本趋近于零。

### 3.2 8个真实候选逐一核查

| 候选 | 语言 | License | Java支持 | 生产证据 |
|---|---|---|---|---|
| Claude Agent SDK | Python/TypeScript | **Commercial ToS（非OSI开源）** | 无 | Claude Code自身（非第三方独立案例） |
| OpenAI Agents SDK | Python/TypeScript | MIT | 无 | 生产可用但**发布15个月后仍未到1.0**（2025年3月发布，2026年6月仍是v0.17.5） |
| LangGraph | Python（+JS移植版） | MIT | 无 | **最强**：约400家企业含Klarna(8500万用户)/Uber/LinkedIn/Replit/JPMorgan/BlackRock/Cisco |
| CrewAI | Python | MIT | 无 | 54k+ stars，活跃，但生产可靠性有真实、反复出现的抱怨 |
| Microsoft Agent Framework（AutoGen+Semantic Kernel继任者） | Python/.NET | MIT | 无 | 2026-04-03刚GA到1.0，AutoGen/Semantic Kernel已被官方降级为"维护模式" |
| Google ADK | **Python和Java（官方双语言）** | Apache-2.0 | **有，官方一等公民支持** | 企业级定位，2026-08曾有一次真实安全事故（见6.6节） |
| Vercel AI SDK | TypeScript/JS | Apache-2.0 | 无（语言完全不对） | 前端/边缘函数场景为主，不适合Java后端 |
| Temporal原生Agent模式（非独立框架） | 任意语言，Matbox用Java | BSL 1.1（Temporal Server）/MIT（SDK） | **有，官方Java SDK+官方Spring AI集成** | OpenAI Codex生产环境运行在Temporal上，处理每分钟数百万级请求 |

**核查方法**：不是只看GitHub star数排知名度，而是逐一核对"能否用Java调用/桥接""是否与Matbox已冻结的F-ACTION-001强制工具网关兼容""是否与F-TASK-001已冻结的Temporal Checkpoint/Resume模型冲突"这三条Matbox特有的硬约束，详细排名理由见第9.1节。

### 3.3 关键架构冲突点（本报告发现的最重要的一条新证据，不是原则性描述）

几乎所有独立Agent框架（LangGraph/CrewAI/Microsoft Agent Framework/Claude Agent SDK）的默认设计都是**框架自己决定何时执行工具、自己把工具结果喂回循环**——这与Matbox已经冻结的ACTION-F005"10步Enforcement Pipeline"（Registry→租户边界→RBAC/ABAC→风险半径→审批→预算→取凭证→限流→执行→审计）**直接冲突**：如果照搬框架默认行为，工具调用会绕开F-ACTION-001的强制审批/预算/幂等检查，这正是ACTION-F001不可变原则第1条明令禁止的"domain自建权限绕过统一校验"。

好消息是：主流框架基本都提供"用户控制工具执行"的手动模式（LangGraph的`interrupt()`/human-in-the-loop middleware、Spring AI的`tool-calling.enabled=false`手动循环模式），意味着**即便真的采用某个框架，也必须先关掉它的自动工具执行、自己接管这一段逻辑**——这个事实直接削弱了"整体采纳一个框架能省下多少工作量"的论据，因为工具调用这个最核心的环节无论如何都要自己接管，详见第9.1节。

### 3.4 Temporal官方对"AI Agent循环"的态度——不是Matbox一厢情愿

查证确认Temporal官方文档里有一篇正式Cookbook《Basic agentic loop with Claude and tool calling》，明确给出了"Workflow代码承载推理循环控制流、每次LLM调用和每次工具调用各自是一个独立Activity"的官方推荐架构；另有一篇官方集成文档《Spring AI integration - Java SDK》，给出`ActivityChatModel`让Spring AI的模型调用自动经Temporal Activity执行、纳入Workflow History实现可恢复。这两份文档合起来说明：**"用Java在Temporal之上原生写Agent Runtime"不是Matbox自己发明的小众做法，是Temporal官方认证、有官方Cookbook和官方Java集成的推荐路线**，且OpenAI自己的Codex生产环境就跑在Temporal上（"处理每分钟数百万级请求"，2026年3月OpenAI Agents SDK正式GA集成Temporal）——这条证据链是本报告认为"自研"应当是#1而不是"图省事默认"的关键支撑。

## 4｜GitHub候选项目清单

| 项目 | Repo | Star/规模（查证日期2026-08） | License | 状态 |
|---|---|---|---|---|
| claude-agent-sdk-python | https://github.com/anthropics/claude-agent-sdk-python | 官方维护，活跃 | **Commercial ToS治理，非独立OSI许可证**（详见第8节） | 候选，本次否决整体采纳 |
| openai-agents-python | https://github.com/openai/openai-agents-python | 27,000+ stars（另有JS/TS移植版3,100+ stars） | MIT | 候选，本次否决整体采纳 |
| langgraph | https://github.com/langchain-ai/langgraph | 约30,925 stars，5,282 forks | MIT | 候选，本次评为Top-3第3名 |
| crewAI | https://github.com/crewAIInc/crewAI | 54,242 stars（2026-06数据） | MIT | 候选，本次否决 |
| microsoft/autogen | https://github.com/microsoft/autogen | 历史项目，官方已宣布"维护模式" | MIT/CC-BY-4.0（文档） | 候选，本次否决（继任者见下） |
| microsoft/agent-framework | 官方新仓库（AutoGen+Semantic Kernel合并后） | 2026-04-03刚GA 1.0 | MIT | 候选，本次否决 |
| google/adk-python | https://github.com/google/adk-python | 官方维护，活跃release节奏 | Apache-2.0 | 候选，本次评为Top-3第2名 |
| google/adk-java | https://github.com/google/adk-java | 官方维护，2026年发布1.0.0 | Apache-2.0 | 候选，本次评为Top-3第2名（Java实现） |
| vercel/ai | https://github.com/vercel/ai | 活跃，Vercel官方 | Apache-2.0 | 候选，本次否决（语言不匹配） |
| temporalio/samples-java | https://github.com/temporalio/samples-java | 官方Sample仓库 | MIT（SDK部分） | 参考实现，非独立候选，是#1自研方案的基础设施来源 |
| （对照组）AG2（AutoGen社区分支） | https://github.com/ag2ai/ag2 | 社区维护，非Microsoft官方 | Apache-2.0 | 未采用，"lifeboat not cruise ship"，无企业背书 |
| （对照组）spring-projects/spring-ai | https://github.com/spring-projects/spring-ai | 官方Spring项目，1.0 GA 2025-05，1.1 GA 2025-11 | Apache-2.0 | 未整体采纳为Agent框架，作为#1自研方案内部的模型调用辅助库候选之一（见6.7节） |
| （对照组）langchain4j/langchain4j | https://github.com/langchain4j/langchain4j | 1.0 GA 2025-05 | Apache-2.0 | 同上，作为辅助库候选之一 |
| （事后核查，验证性候选）conductor-oss/conductor | https://github.com/conductor-oss/conductor | 32,161 stars（2026-09-02数据） | Apache-2.0 | 本报告完成后新增核查，与Temporal同属durable execution引擎赛道；结论**非否决、非采纳，仅作验证性参考**——Conductor OSS用JSON任务图+服务端解释执行，Temporal用真实代码表达workflow逻辑，后者对TASK-F008自我纠错这类复杂条件分支场景更合适，不构成推翻本报告#1自研+Temporal方案的理由。完整核查记录见[`Matbox_专项00m_ConductorOSS专项评估_2026-09-02.md`](Matbox_专项00m_ConductorOSS专项评估_2026-09-02.md)，避免后续重复调研 |

## 5｜API、SDK、模型及商业服务清单

| 服务 | 类型 | 认证方式 | 自托管 | Java可达性 | 结论 |
|---|---|---|---|---|---|
| Claude Agent SDK | Python/TS库 | API Key（Commercial ToS，OAuth订阅额度被明确禁止用于程序化调用） | 是（进程内运行） | 无，需跨语言桥接 | 不整体采纳（第9节） |
| OpenAI Agents SDK | Python/TS库 | API Key | 是 | 无，需跨语言桥接 | 不整体采纳 |
| LangGraph Platform | 托管/自托管均可 | API Key（自托管免此项） | 是（开源版可自托管） | 无，需跨语言桥接 | 不整体采纳，列为长期能力监控项 |
| Microsoft Agent Framework | Python/.NET库 | API Key/Azure身份 | 是 | 无（.NET非Java），需跨语言/跨运行时桥接 | 不采纳 |
| Google ADK | Python/**Java**库 | API Key/Vertex身份 | 是 | **原生Java** | 认真评估，Top-3第2名，未整体采纳（见9.1节理由） |
| Vercel AI SDK | TS/JS库 | API Key | 是 | 无（语言完全不对） | 不采纳 |
| Anthropic Context Editing API + Memory Tool | Claude Developer Platform Beta能力 | 走F-PROVIDER-001已有的Claude adapter凭证 | N/A（API能力） | 可用（HTTP API，任意语言可调用） | **采纳为RUNTIME-F004上下文管理的Claude专属优化层**（见6.8/9.2节） |
| Spring AI | Java库 | 走F-PROVIDER-001的凭证代理 | 是 | 原生Java | 评估为#1自研方案内部辅助库候选（非整体框架） |
| LangChain4j | Java库 | 走F-PROVIDER-001的凭证代理 | 是 | 原生Java | 评估为#1自研方案内部辅助库候选（非整体框架） |
| Temporal（Server+Java SDK） | 已冻结基础设施 | 复用F-TASK-001/F-QUEUE-001已有部署 | 是 | 原生Java | **REUSE，Agent Runtime的执行载体**（见3.4/9.1节） |

## 6｜真实用户与开发者评价

### 6.1 Claude Agent SDK
- 定位准确："The Claude Agent SDK is Anthropic's library that exposes the same agent loop, built-in tools, permission system and subagents that power Claude Code"——是把Claude Code本身的Harness抽出来给开发者用，**不是一个中立、多厂商适配的通用框架**，天然对Claude模型本身优化最深。
- 真实的License风险信号（非厂商自己说的话）："Use of the Claude Agent SDK is governed by Anthropic's Commercial Terms of Service"，且**2026年这条ToS本身处于反复调整状态**："Anthropic pauses Claude Agent SDK subscription change on day it was due to take effect"（2026-06-15）——说明这不是一份稳定多年不变的开源许可证，是一份仍在被厂商单方面调整的商业条款，长期依赖它做核心执行引擎存在条款变化风险。
- 真实用户痛点（GitHub Issue，非营销材料）：`anthropics/claude-agent-sdk-python#507` 明确指出SDK目前只给累计token用量，没有按类别细分的上下文用量可见性，用户反馈"这妨碍了识别上下文消耗问题、做出智能的上下文管理决策"——这恰好是Agent Runtime RUNTIME-F004要解决的核心问题，说明连Anthropic自己的Harness在这块的可观测性也不完善，不能假设"用了官方SDK这个问题就自动解决"。
- 真实成本失控案例："with 10 parallel subagents on a 200K context, the worst case is 2M tokens billed per turn"——多子代理并行时上下文会成倍复制，这与F-COST-001"预算控制"的P0要求直接相关，进一步说明**不能把成本治理完全托付给框架默认行为，必须由Matbox自己的成本/上下文治理层兜底**。
- **对Matbox的意义**：技术能力强、对Claude优化最深，但(1)Python/TS-only需要跨语言桥接，(2)自带工具执行循环与F-ACTION-001冲突，(3)Commercial ToS不是真正开源、条款仍在变化，(4)即便是Anthropic自己也没解决好的上下文可见性问题，Matbox一样要自己解决。三条硬伤+一条"即便采纳也解决不了"的证据，第9.1节据此判定不进入Top-3。

### 6.2 OpenAI Agents SDK
- 成熟度真实信号（非负面评价，是中性的时间线事实）："shipping roughly weekly releases (v0.17.5 on June 11, 2026) yet still pre-1.0 fifteen months after its March 2025 launch"——15个月未到1.0，对比LangGraph（2025年10月正式到1.0并承诺2.0前不做破坏性变更），OpenAI Agents SDK的API稳定性承诺明显更弱。
- 核心抽象是"handoffs"（Agent间显式转交控制权），设计目标与Matbox的F-DELEGATION-001（委派）概念部分重叠但语义不同——若整体采纳，等于同时维护OpenAI自己的handoffs语义和Matbox自己的Delegation Contract两套委派模型，增加而非减少复杂度。
- **对Matbox的意义**：同样是Python/TS-only，且未到1.0意味着近期API面还可能继续变化，不适合作为Matbox要长期依赖的核心执行引擎，本次不进入Top-3。

### 6.3 LangGraph（Top-3候选，最强生产证据）
- 生产证据是本次调研里最扎实的一个：**约400家企业**部署LangGraph Platform，含**Klarna**（AI客服助手服务8500万活跃用户，客户问题解决时间降低80%）、**Replit**（Agent产品用LangGraph多智能体架构，执行轨迹复杂到"数百个步骤"，LangChain团队为此专门改进了LangSmith的摄取/渲染能力）、Uber、LinkedIn、Elastic、BlackRock、Cisco、JPMorgan。
- 历史"破坏性变更多"的名声有真实依据但2026年已改善："LangGraph hit v1.0 in October 2025 — with a formal stability commitment and no breaking changes until 2.0"，但**即便如此，2026年初仍发生过真实的破坏性变更事故**：GitHub Issue `langchain-ai/langgraph#6363` 记录了 `langgraph-prebuilt==1.0.2` 在没有正确版本约束的情况下引入破坏性变更；`langgraph.prebuilt`模块本身在1.0时就已被标记deprecated、功能迁移到`langchain.agents`，破坏了旧的导入路径。**这条证据支撑了任务书里提出的"验证LangGraph确实存在快速迭代破坏性变更历史"的要求**——1.0承诺缓解了但没有完全消除这个风险，长期维护成本仍然是真实存在的。
- **对Matbox的意义**：生产证据最强、技术能力最全面（durable state/checkpointing/interrupts/human-in-the-loop都是官方一等公民支持），**但Python-only是硬约束**——Matbox架构原则第33条已经明确拍板"AI员工底层保持Java单语言栈"（"团队只维护一种语言"），引入LangGraph意味着：①新增一个独立部署的Python微服务；②每次LLM调用和每次工具调用都要多一次跨进程/跨语言RPC（Java Workflow ⟷ Python LangGraph服务⟷ 再回调Java的F-ACTION-001/F-PROVIDER-001，序列化/网络开销叠加在每一轮推理循环上）；③团队从"维护一种语言"变成"维护两种语言的生产服务"，与已冻结的架构原则直接冲突；④LangGraph自带的Checkpointer持久化模型与F-TASK-001已冻结的Temporal Checkpoint/Resume语义是两套不同的"任务在哪个执行点"记录方式，会产生"两个真相源"的真实架构风险，不是"多一层"这么简单。评为Top-3第3名，理由和局限详见9.1节。

### 6.4 CrewAI
- License友好（MIT），社区规模大（54k+ stars），但**真实生产可靠性抱怨是反复出现的模式，不是个案**："The non-deterministic and sometimes slow nature of LLM chains makes it a terrible choice for applications requiring real-time responses or 99.999% reliability"；"CrewAI's verbosity is too noisy and you'll need to build your own structured logging on top of it"。
- **Matbox自己的DELEGATION-001正式文档里已经独立记录过CrewAI的真实从业者抱怨**（非本报告新查）："CrewAI真实从业者反馈中，'角色定义太松散导致角色幻觉'和'循环委派卡死工作流'是反复出现的抱怨，不是个案"（`Matbox_AI员工委派_正式开发文档_V1.0-RC.md`第31行）——这是一条已经在Matbox内部文档里留痕、且与本次外部调研互相印证的证据，两个独立来源指向同一个结论。
- **对Matbox的意义**：CrewAI的角色分工模式（Crew/Agent/Task）设计目标接近F-ORCHESTRATOR-001+F-DELEGATION-001已经做的事，但可靠性证据薄弱、且是Python-only，第9.1节不进入Top-3。

### 6.5 Microsoft Agent Framework（AutoGen+Semantic Kernel继任者）
- 真实的产品线变动："Microsoft Agent Framework was released in public preview on October 1, 2025...On April 3, 2026, Microsoft shipped Microsoft Agent Framework 1.0"；"AutoGen and Semantic Kernel were placed into maintenance mode—continuing bug fixes and security patches but no new features"——这意味着**如果Matbox在2026年之前调研时选择了AutoGen，现在就正处于被强制迁移的窗口期**，这正是任务书要求核实的"是否已经有更好选择"的一个真实反面案例。
- AG2（社区分叉，试图延续AutoGen 0.2 API）的定位很诚实地被行业评价为"a lifeboat, not a cruise ship"——没有企业背书、没有Azure集成路线图、没有企业销售支持，只是给"来不及迁移的老用户"一个过渡。
- **对Matbox的意义**：产品线本身两年内经历了"AutoGen独立→AutoGen+Semantic Kernel合并→AutoGen维护模式"的完整变迁，且只支持Python/.NET，本次不进入Top-3，同时这条证据本身值得写入第26节风险清单——**任何"厂商Agent框架"都存在被合并/重命名/降级维护的真实风险，这正是Matbox坚持自研核心执行引擎、只把易替换的模型调用层REUSE给F-PROVIDER-001的关键理由之一**。

### 6.6 Google ADK（Top-3候选，唯一原生Java选项）
- 唯一"厂商官方、非社区移植"提供Java实现的候选："Announcing ADK for Java 1.0.0: Building the Future of AI Agents in Java"（Google Developers Blog），Apache-2.0协议，与Python版本共享同一套设计理念。
- 模型无关性经查证属实，且**明确支持Claude**："You can use Anthropic's Claude models with ADK in both Python and Java...using the ADK's Claude wrapper class"；同时支持LiteLLM桥接100+模型——这意味着ADK不是"Gemini专属"，理论上可以对接Matbox已有的F-PROVIDER-001模型路由。
- **真实的负面证据（安全事故，非假设）**："Google Deletes 3 ADK AI Workflows After Malicious GitHub Issue Could Trigger Privileged Agent"（The Hacker News，2026-08）——Pillar Security披露一个公开GitHub Issue的文本内容能够操纵ADK的triage agent触发一个高权限的code-fixing agent，最终在CI runner上实现代码执行并窃取bot的PAT。Google已于2026-07-21确认修复，但**这是一次真实发生、被独立安全研究机构披露的prompt injection→权限提升事故，且事故场景（"不可信的外部文本触发高权限Agent执行"）与Matbox的ACTION-F005验收标准"Web/browser/tool输出必须当作不可信内容处理"针对的正是同一类风险**，说明即便采用成熟框架也不能免除Matbox自己在ACTION-F005/架构原则第10条上做的防注入设计。
- 真实的破坏性变更记录：LlmAgent默认模型从gemini-2.5-flash改为preview版gemini-3-flash-preview、GCP Skill Registry endpoint变更、artifacts命名空间变更——release节奏快、变更也快，属于"仍在快速演进期"的框架，非"稳态"。
- **对Matbox的意义**：是本次调研里唯一"官方Java优先支持"的通用Agent框架，值得认真评估（因此本报告没有像其余候选一样一句话否决，给了完整的Top-3第2名分析），但它有自己的Runner/Session状态管理模型，若整体采纳，需要把这套状态模型硬塞进Matbox已经冻结的Temporal Checkpoint/Resume之下做双写或做取舍，属于"削足适履"式集成，详见9.1节。

### 6.7 Spring AI vs LangChain4j（作为#1自研方案的内部辅助库，非独立框架候选）
- 两者都已GA且生产可用："Both frameworks hit 1.0 GA in May 2025 and are production-ready...LangChain4j 1.0 GA (May 2025), Spring AI 1.0 GA (May 2025), Spring AI 1.1 GA (November 2025)"，都原生支持Java Tool Calling、MCP协议、Anthropic官方SDK底层封装（"Spring AI uses the official anthropic-java SDK under the hood"）。
- **真实的版本耦合风险（Spring AI）**："Spring AI 2.0 requires Spring Boot 4.0 or 4.1, Spring Framework 7, and Jackson 3. If your app is still on Spring Boot 3.x, you cannot adopt Spring AI 2.0 without a framework upgrade first"——Matbox后端基座是RuoYi-Vue-Pro，其Spring Boot具体版本需要Stage 10施工前核实，若仍在Boot 3.x，Spring AI 2.0直接不可用，需锁定Spring AI 1.x或等Boot升级。
- **真实的破坏性API变更（Spring AI，与本次"手动控制工具执行"直接相关）**："Code that sets .internalToolExecutionEnabled(false) to opt into user-controlled tool execution will no longer compile in Spring AI 2.0 and later. internalToolExecutionEnabled was removed, and you should delete the old option and choose either advisor-managed execution or a manually controlled loop"——这正是Agent Runtime必须依赖的"手动接管工具执行、经F-ACTION-001裁决"这条关键能力，Spring AI在2.0做了破坏性重命名/重构，说明即便只是把它当"辅助库"使用，也要显式锁定版本、写清楚适配层，不能假设API长期不变。
- LangChain4j的优势是**不绑定Spring Boot具体大版本**："LangChain4j sidesteps this entirely: it ships both a Boot 3.5+ starter and a separate Boot 4 starter, so it runs on either generation"，且"the most flexible AI toolbox in Java — 30+ vector stores and framework-agnostic design"，对不确定RuoYi具体Boot版本的当前阶段更安全。
- **对Matbox的意义**：两者都不是"整体Agent框架"意义上的候选（不参与第9.1节Top-3排名），而是**Agent Runtime自研实现内部可选的辅助库**——用于生成工具的JSON Schema、封装Anthropic Java SDK的样板代码、处理prompt caching标记等零散工作，具体选哪个（或者都不用、直接用`anthropic-sdk-java`+F-PROVIDER-001已有的Adapter抽象自己写）留到Stage 10按当时RuoYi真实Spring Boot版本决定，不在本报告拍死。

### 6.8 Anthropic Context Editing API + Memory Tool（RUNTIME-F004上下文管理子能力的关键REUSE来源）
- 官方性能数据（**厂商自证，不是独立测试，本报告如实标注**）："Anthropic reports 29% performance improvement with context editing alone, and 39% with context editing + memory tool over baseline"；"Combined with context editing, Anthropic's internal benchmarks on a 100-turn web search task showed 84% token savings"。
- 技术机制真实且可核查："Context Editing API (beta: anthropic-beta: context-management-2025-06-27) that automatically manages context by clearing old tool use/result pairs and thinking blocks at the API level, before token counting and after prompt cache lookup"——是服务端能力，在token计费前生效，理论上能同时省成本和省上下文空间。
- **关键限制（本报告主动核查出的边界，厂商宣传材料不会强调）**：这是**Claude专属能力**，Matbox是多供应商架构（F-PROVIDER-001要支持故障转移到其他供应商），Context Editing API不能作为唯一的上下文管理方案，非Claude供应商必须有Matbox自己的截断/摘要兜底逻辑，两者是互补关系不是替代关系。

## 7｜源码审查报告

| 组件 | 复核对象 | 结论 |
|---|---|---|
| Temporal Java SDK | `temporalio/sdk-java`（已在F-TASK-001/F-QUEUE-001复核过的同一套依赖，本次复核聚焦Activity Heartbeat/Cancellation机制部分） | 官方文档确认`Activity.getExecutionContext().heartbeat()`是Worker向Cluster发送的心跳ping，`ActivityOptions.newBuilder().setHeartbeatTimeout(...)`配置超时；**Cancellation信号的投递机制是"随心跳一起下发"**（"Activity Cancellations are delivered to Activities from the Temporal Service when they Heartbeat. Activities that don't Heartbeat can't receive a Cancellation"）——这条源码级机制细节直接决定了RUNTIME-F007 Kill Switch响应必须依赖RUNTIME-F006心跳的正确落地，两者是同一条链路的两端，不是两个独立功能，详见12节数据流 |
| temporalio/samples-java（Spring AI集成样例） | 官方Cookbook代码（`ActivityChatModel`包装Spring AI的`ChatModel`接口） | 确认为真实可运行的官方参考实现，非概念验证性质的demo，可作为RUNTIME-F002主循环Activity封装层的起点参考 |
| google/adk-java | 官方1.0.0发布，Apache-2.0 | 确认为真实生产级代码（非demo），但其`Runner`/`Session`抽象与Temporal的Workflow/Activity模型是两套独立的执行/状态管理框架，整体嵌入需要做一层"以Temporal为主、ADK Runner降级为纯推理库"的改造，改造成本本身接近于自己写，第9.1节展开 |
| anthropic-sdk-java | `com.anthropic:anthropic-java`（v0.121.0，2026-08数据） | 官方持续发布，是F-PROVIDER-001已经规划要REUSE的Provider Adapter实现基础之一（Claude Adapter），Agent Runtime本身不直接依赖它——只经F-PROVIDER-001的`invoke()`间接使用，符合"不绑定单一供应商SDK"的P0原则 |

**本次审计的源码级结论**：Agent Runtime自身不存在"需要复核的现成源码"（因为是自研），本节的源码审查聚焦在**Agent Runtime要REUSE的两块基础设施（Temporal Activity Heartbeat/Cancellation机制、官方Spring AI集成样例）确实是真实、成熟、文档化的能力，不是Matbox凭空假设的可行性**。

## 8｜License与商用风险

| 组件 | License | 是否OSI开源 | 商用/自托管是否允许 | 风险等级 | 备注 |
|---|---|---|---|---|---|
| Temporal Server | BSL 1.1（Business Source License） | 否 | 允许自托管商用，BSL对"作为竞品服务转售"有限制，Matbox内部使用不触发 | 低（Matbox已在F-TASK-001/F-QUEUE-001承担并接受这条风险，本报告不重复评估，仅复用结论） | Matbox可选Temporal Cloud（$100/月起）规避自托管BSL细节 |
| Temporal Java SDK | MIT | 是 | 完全允许 | 低 | — |
| Claude Agent SDK | **Commercial Terms of Service（非OSI许可证）** | 否 | 允许商用但受Anthropic单方面条款约束，2026年已发生过至少一次条款变更又暂停的真实事件 | 中（未采纳，风险仅供记录） | 未整体采纳，见9.1节 |
| OpenAI Agents SDK | MIT | 是 | 完全允许 | 低（未采纳，风险不适用） | — |
| LangGraph | MIT | 是 | 完全允许 | 低（未采纳，风险不适用） | License本身无风险，未采纳原因是语言/架构冲突，非License |
| CrewAI | MIT | 是 | 完全允许 | 低（未采纳，风险不适用） | — |
| Microsoft Agent Framework | MIT | 是 | 完全允许 | 低（未采纳，风险不适用） | — |
| Google ADK（Python+Java） | Apache-2.0 | 是 | 完全允许，含专利授权条款 | 低（未整体采纳，风险不适用） | License是本次所有候选里最干净的之一，未整体采纳是架构集成成本问题不是License问题 |
| Vercel AI SDK | Apache-2.0 | 是 | 完全允许（未采纳，语言不匹配） | 低，不适用 | — |
| Spring AI | Apache-2.0 | 是 | 完全允许 | 低 | 版本升级需注意Spring Boot 4.x耦合（第6.7节） |
| LangChain4j | Apache-2.0 | 是 | 完全允许 | 低 | — |
| anthropic-sdk-java | MIT | 是 | 完全允许 | 低 | — |
| Anthropic Context Editing API/Memory Tool | 属于Claude Developer Platform服务条款（非独立开源许可证） | 不适用（API能力非代码库） | 允许商用，走已有Commercial API协议 | 低 | 与Claude Agent SDK的Commercial ToS是两回事，这是Messages API的Beta功能，风险profile更接近"API功能开关"而非"框架依赖" |

**P0结论**：Agent Runtime本身不引入任何AGPL/SSPL/BUSL级别的核心代码依赖；唯一需要长期关注的条款风险是**如果未来真的整体采纳Claude Agent SDK或依赖其Commercial ToS下的某些功能，需要跟踪Anthropic 2026年仍在调整的计费/使用条款**——但本报告的结论是不整体采纳它，这条风险因此不构成P0阻塞项。

## 9｜候选方案对比及淘汰原因（含前三名排名+理由）

### 9.1 模块级"整体执行引擎"Top-3排名（最核心的决策，用户明确要求的格式）

| 排名 | 候选 | 语言/部署 | 排名理由 |
|---|---|---|---|
| **#1 Matbox自研（Java，Temporal Workflow/Activity承载推理循环）** | Java，复用F-TASK-001/F-QUEUE-001已有Temporal集群 | 唯一同时满足"与F-ACTION-001强制工具网关零冲突""与F-TASK-001已冻结Checkpoint/Resume模型零冲突""不新增语言栈（架构原则第33条）""Temporal官方Cookbook+Spring AI集成文档提供了现成参考架构，不是从零发明"四条的方案；核心模型调用/工具执行安全判定全部REUSE给F-PROVIDER-001/F-ACTION-001，自研范围收窄为"推理循环控制流+Prompt组装+上下文裁剪+心跳/Kill响应"这几块Matbox专属胶水逻辑，不是重新发明一个通用Agent框架 |
| **#2 Google ADK for Java** | Java，官方SDK | 本次调研里唯一"厂商官方Java一等公民支持"的通用Agent框架，Apache-2.0协议干净，模型无关（支持Claude wrapper），技术能力成熟；**排第2的原因是架构集成成本，不是能力不足**——ADK自带的Runner/Session状态管理与Temporal的Workflow/Activity/Checkpoint是两套独立的持久化/恢复模型，整体采纳意味着要么"关闭ADK的状态管理、只当纯推理库用"（等于自己重写大半，收益趋近于0），要么"让ADK的Session和Temporal的Checkpoint并存"（产生第3节已指出的"两个真相源"风险，与F-TASK-001 TASK-F001不可变原则第2条"不把XX当业务真相源"精神冲突）；同时2026-08曾有真实的prompt injection→权限提升安全事故（第6.6节），说明即便框架成熟也不能替代Matbox自己在ACTION-F005上做的防注入设计，进一步降低"整体采纳换安全性"这条论据的说服力 |
| **#3 LangGraph（需跨语言桥接）** | Python，需为Matbox新增一个独立Python微服务并跨进程调用 | 生产证据全场景最强（Klarna/Uber/LinkedIn/Replit/JPMorgan等约400家企业），技术能力最全面（durable state/interrupts/checkpointing均为一等公民），**但Python-only与架构原则第33条"AI员工底层保持Java单语言栈"直接冲突**——引入意味着每一次LLM调用和每一次工具调用都新增一次跨语言RPC开销，团队从维护一种语言变成两种，且LangGraph自己的Checkpointer与Temporal的Checkpoint同样构成第2节已指出的"双持久化真相源"风险；2026年即便v1.0承诺"2.0前不做破坏性变更"，仍发生过真实的`prebuilt`模块版本不匹配破坏性事故（GitHub Issue #6363），长期维护成本的担忧并非过时的旧印象 |
| 落选 | Claude Agent SDK | Python/TypeScript-only，Commercial ToS非真正开源、2026年条款仍在被单方面调整（第6.1/8节），自带工具执行循环与F-ACTION-001冲突，且连Anthropic自己的Harness都还没解决好上下文用量可见性问题（GitHub Issue #507）——四条独立理由，任何一条单独都够否决，四条叠加更明确 |
| 落选 | OpenAI Agents SDK | Python/TS-only，发布15个月仍未到1.0（对比LangGraph已到1.0并承诺稳定），核心"handoffs"抽象与Matbox已有的F-DELEGATION-001委派模型概念重叠但语义不同，整体采纳等于维护两套委派语义 |
| 落选 | CrewAI | Python-only，生产可靠性抱怨反复出现（噪音日志/角色幻觉/循环委派卡死），且这条抱怨在Matbox自己的DELEGATION-001正式文档里已有独立记录，两个独立来源互相印证 |
| 落选 | Microsoft Agent Framework（AutoGen继任者） | Python/.NET-only（无Java），且其前身AutoGen/Semantic Kernel在两年内经历"独立→合并→维护模式"的完整产品线变迁，是"厂商Agent框架被合并/降级维护"真实风险的活教材 |
| 落选 | Vercel AI SDK | TypeScript/JS-only，与Matbox Java后端语言完全不匹配，第一轮即淘汰；其`stopWhen`循环终止条件的设计理念（`stepCountIs`/`hasToolCall`）值得作为#1自研方案RUNTIME-F002终止条件设计的参考灵感，但不构成候选本身 |

**#1为什么胜过#2/#3（正式回答）**：这不是"找不到候选所以默认自研"——本报告认真评估了8个真实候选，其中2个（ADK-Java、LangGraph）技术能力和生态成熟度都值得认真对待。#1胜出的核心不是"Matbox自己写的代码质量更高"，而是**架构一致性**：Matbox已经在F-TASK-001（Temporal Checkpoint/Resume/Kill）和F-ACTION-001（10步Enforcement Pipeline）两份正式文档里冻结了具体的持久化模型和工具执行安全模型，这两条不是本报告可以推翻的既定事实——任何"整体采纳一个自带循环控制+自带工具执行+自带状态持久化"的现成框架，都会与这两条冻结决策产生**结构性冲突**（不是"多花点时间集成"的量级问题，是"到底以谁的Checkpoint/谁的工具执行判定为准"的真相源冲突）。#2（ADK-Java）和#3（LangGraph）都在"值得认真评估"这一档，且分别代表了"Java优先"和"生产证据优先"两种不同的取舍方向，留作长期能力监控项——如果未来Matbox的推理循环需求变得极其复杂（例如需要ADK/LangGraph才有的高级图编排能力），可以把它们降级为"仅用于生成Prompt/Schema的工具库"复用，但不会整体把执行主权交给它们。

### 9.2 RUNTIME-F004 上下文窗口管理子能力 Top-3

| 排名 | 候选 | 排名理由 |
|---|---|---|
| **#1 混合方案：Anthropic Context Editing API（Claude专属优化）+ Matbox自研通用裁剪/摘要兜底** | 唯一同时覆盖"Claude场景下的服务端高效裁剪（官方数据29-84%token节省，需独立验证）"与"非Claude供应商仍有基础保障"两端的方案，且不依赖第三方长期记忆服务，符合"上下文管理"和"F-MEM-001长期记忆"边界分离原则 |
| **#2 LangMem（LangChain生态的上下文压缩库）** | "LangMem is a context compressor more than a memory store, summarizing older turns and re-injecting only relevant summaries"——定位与RUNTIME-F004接近，但深度绑定LangGraph生态（"native to LangGraph with few extra moving parts"），Matbox不采纳LangGraph主循环的前提下单独引入它意义不大，且仍是Python库 |
| **#3 Mem0（开源+云服务双轨的记忆层）** | 50,000+开发者使用，支持"最多80%的prompt token压缩"，但定位更接近**跨会话长期记忆**（"knowledge graph that links entities and relationships across conversations"），与F-MEM-001的职责边界重叠而非RUNTIME-F004的短期上下文管理，评估结论是：**如果F-MEM-001未来选型长期记忆方案，Mem0值得作为该模块的候选之一重新评估，但不是Agent Runtime本节要解决的问题** |

**#1为什么赢**：RUNTIME-F004要解决的是"这一次task step执行期间的多轮上下文别撑爆窗口/别浪费token"，不是"跨会话记住用户偏好"这类长期记忆问题——#2/#3本质上都更贴近后者，混入会让Agent Runtime的职责边界模糊，与F-MEM-001产生功能重复。

### 9.3 未做Top-3排名的子能力及原因

| 子能力 | 是否需要Top-3 | 说明 |
|---|---|---|
| RUNTIME-F002 推理主循环控制流 | 否，已在9.1节模块级排名回答 | 主循环控制流的载体选型就是模块级决策本身，不单独二次排名 |
| RUNTIME-F003 工具调用派发 | 否 | 协议层已经由F-ACTION-001（MCP Gateway生态REUSE）和F-PROVIDER-001（Provider Adapter标准接口）分别定义，Agent Runtime只是按既有契约转发，不存在"选哪个工具调用协议"的独立市场选型问题 |
| RUNTIME-F005 LLM调用级重试 | 否 | 是对F-错误码规范已有17个码的场景化应用（哪些码可重试/怎么退避），不是独立的工具/框架选型问题 |
| RUNTIME-F006/F007 心跳与Kill响应 | 否，但有明确REUSE来源 | 已在3.4/7节论证：直接REUSE Temporal Activity的原生Heartbeat/Cancellation机制，这是Temporal SDK自带能力，不存在独立的第三方"心跳SDK"市场可比较 |
| RUNTIME-F008 流式进度桥接 | 否 | 复用F-TASK-001已有的Task API+事件序列模式（TASK-F001 P0规则1），不是独立选型问题 |

## 10｜最终技术路线与选择依据

| FeatureID | 最终路线 | 依据（含Top-3排名回填） |
|---|---|---|
| RUNTIME-F001 PromptAssembler | **Matbox自研** | 纯Matbox专属逻辑（读EmployeeTemplate/AiTaskStep/ToolRegistration组装message），未发现任何外部产品理解这套跨模块组合语义，非"多候选选一"场景 |
| RUNTIME-F002 ReasoningLoopController | **Matbox自研（Java，Temporal Workflow/Activity）** | 第9.1节Top-3第1名：击败Google ADK for Java（#2，能力强但与Temporal Checkpoint模型冲突）、LangGraph（#3，生产证据最强但Python-only与架构原则第33条冲突）；Claude Agent SDK/OpenAI Agents SDK/CrewAI/Microsoft Agent Framework/Vercel AI SDK均落选，理由见9.1节表格 |
| RUNTIME-F003 ToolCallDispatcher | **Matbox自研（协议层REUSE已有ACTION-F005/PROVIDER-F006契约）** | 不是独立选型问题，是把模型返回的tool_use转成已经存在的F-ACTION-001 ProposedAction schema，双方契约已在各自正式文档中定义 |
| RUNTIME-F004 ContextWindowManager | **混合方案** | 第9.2节Top-3第1名：Anthropic Context Editing API（Claude专属，REUSE）+ Matbox自研通用裁剪/摘要兜底；击败LangMem（#2，深度绑定LangGraph生态）、Mem0（#3，定位是长期记忆非本子能力职责范围） |
| RUNTIME-F005 CallLevelRetryHandler | **Matbox自研（复用已有错误码规范）** | 场景化应用F-错误码规范已定义的17个码，不新增独立市场选型 |
| RUNTIME-F006 HeartbeatEmitter | **直接引用（REUSE Temporal Activity原生心跳机制）+ Matbox自研业务语义层** | 3.4/7节：Temporal Activity Heartbeat是原生能力，Matbox自研的是"心跳事件写入F-OBS-001、2-3分钟频率、连续漏2次报警"这层业务规则（架构原则第28条） |
| RUNTIME-F007 KillSwitchResponder | **直接引用（REUSE Temporal Activity Cancellation机制）+ Matbox自研安全终止点判断** | 同上，源码级证据（第7节）确认Cancellation随Heartbeat一起投递，RUNTIME-F006/F007是同一条链路的两端 |
| RUNTIME-F008 StreamingProgressBridge | **API/SDK接入（复用F-TASK-001已有Task API+事件序列）** | 不新建平行的进度推送机制，遵守TASK-F001 P0规则1 |

## 11｜自研、复用、二开和采购的边界

- **OWN（Matbox自己拥有的业务逻辑）**：ReasoningLoopController的循环控制流与终止条件判断、PromptAssembler的组装规则、ToolCallDispatcher与F-ACTION-001的桥接映射逻辑、CallLevelRetryHandler的重试/退避策略、HeartbeatEmitter/KillSwitchResponder的Matbox业务语义（频率/报警阈值/安全终止点选择）、非Claude供应商的上下文裁剪/摘要兜底策略。
- **REUSE（引用其他专项/外部成熟能力的事实源，不复制）**：
  - Temporal Workflow/Activity引擎本身（含原生Heartbeat/Cancellation机制），与F-TASK-001/F-QUEUE-001共用同一套集群，不新建第二套持久化工作流系统；
  - F-PROVIDER-001的`invoke()`统一模型调用接口，不直连任何供应商SDK；
  - F-ACTION-001的10步Enforcement Pipeline，不重复实现工具执行的权限/风险/预算判定；
  - F-AIEMP-001的EmployeeTemplate只读查询，不复制存储角色定义；
  - Anthropic Context Editing API + Memory Tool（Claude场景的上下文管理优化）；
  - （可选，Stage 10按RuoYi真实Spring Boot版本决定）Spring AI或LangChain4j的零散工具类库，仅用于Anthropic SDK封装样板代码/JSON Schema生成等辅助环节，不采纳其Agent Loop本身。
- **MUST NOT REBUILD（禁止重写的外部成熟能力）**：模型推理能力本身（已由F-PROVIDER-001封装的供应商SDK提供）、Temporal自身的crash恢复/replay/幂等去重机制、MCP Gateway生态的工具调用安全治理层（F-ACTION-001已REUSE）、跨AI员工的委派链路防护算法（F-DELEGATION-001已冻结）。
- **本次审计特别澄清的边界（避免未来重复设计）**：Agent Runtime的"上下文窗口管理"（RUNTIME-F004）与F-MEM-001的"长期记忆检索"是两个不同生命周期的功能——前者随单次task step执行结束而结束，后者跨会话持久化；Mem0/LangMem类工具属于后者的候选范围，不应被误用来解决Agent Runtime本节的问题（详见2/9.2节）。

## 12｜系统架构与数据流

```
┌──────────────────────────────────────────────────────────────────────┐
│  F-ORCHESTRATOR-001（路由决策：这句话该找哪个AI员工）                    │
└───────────────────────────────┬────────────────────────────────────────┘
                                 │ ① 单员工可处理 → 创建AiTask
                                 ▼
                  ┌───────────────────────────────┐
                  │  F-TASK-001（AiTask Workflow）   │──reads──▶ F-AIEMP-001
                  │  CREATED→VALIDATED→QUEUED→RUNNING│         EmployeeTemplate
                  └────────────────┬────────────────┘
                                   │ ② 每个AiTaskStep需要AI执行时调用
                                   ▼
        ┌──────────────────────────────────────────────────────────────┐
        │        Agent Runtime（本专项，F-RUNTIME-001）                   │
        │  ┌────────────────────────────────────────────────────────┐  │
        │  │ RUNTIME-F001 PromptAssembler                             │  │
        │  │  组装 employeeTemplate.role/goal/skills                   │  │
        │  │  + AiTaskStep.description + 工具清单 + 历史轮次              │  │
        │  └────────────────────────┬───────────────────────────────┘  │
        │                           ▼                                    │
        │  ┌────────────────────────────────────────────────────────┐  │
        │  │ RUNTIME-F002 ReasoningLoopController                     │  │
        │  │  (Temporal Workflow代码：确定性循环控制流)                    │  │
        │  │  loop:                                                    │  │
        │  │   ① 调F-PROVIDER-001.invoke()（Activity，含心跳/Kill响应）──▶ F-PROVIDER-001
        │  │   ② 响应含tool_use? ──否──▶ 判断终止条件 ──▶ 结束            │  │
        │  │   ③ 是 → RUNTIME-F003 ToolCallDispatcher                  │  │
        │  │        转ProposedAction → F-ACTION-001 propose→execute ───▶ F-ACTION-001
        │  │        （10步Enforcement Pipeline在此生效）                  │  │
        │  │   ④ 工具结果标记为不可信内容，回填tool_result → 回到①         │  │
        │  │  RUNTIME-F004 上下文窗口管理：每轮循环检查是否需裁剪/摘要        │  │
        │  │  RUNTIME-F005 调用级重试：①失败时区分可重试/不可重试错误码        │  │
        │  │  RUNTIME-F006/F007 心跳/Kill：Activity心跳附带业务语义        ─▶ F-OBS-001(OBS-F004告警)
        │  │                                          Kill信号随心跳投递  ◀─ F-TASK-001(TASK-F005 Kill Task)
        │  └────────────────────────────────────────────────────────┘  │
        │  RUNTIME-F008 StreamingProgressBridge：中间进度经Task API事件序列 ─▶ 前端(经F-TASK-001)
        └──────────────────────────────────────────────────────────────┘
                                   │ ③ 循环结束，产出AiTaskStep结果
                                   ▼
                  TASK-F008 自我纠错（生成→自我批判→修正，硬上限内可能再次调用Agent Runtime）
                                   │
                                   ▼
                        AiTaskStep.status = SUCCEEDED/FAILED
                                   │
                                   ▼
                        AiTask继续下一步或SUCCEEDED/FAILED
```

**与相邻模块的调用链总结（避免未来实现时凭感觉现编依赖关系）**：
F-ORCHESTRATOR-001 → F-TASK-001（创建AiTask）→ **Agent Runtime**（执行单个AiTaskStep的推理循环）→ 循环内部调 F-PROVIDER-001（每次模型调用）+ F-ACTION-001（每次工具调用，含F-CRED-001取凭证、F-EGRESS-001出站校验、F-COST-001成本记账，均在F-ACTION-001内部完成，Agent Runtime不直接触达）→ 结果回F-TASK-001（TASK-F008自我纠错评估）→ 心跳/Kill信号经Temporal Activity机制双向流转于Agent Runtime与F-TASK-001/F-OBS-001之间。

## 13｜API接口清单

Agent Runtime**主要以Temporal Workflow/Activity代码形式存在，不是一个独立对外暴露HTTP API的服务**——它被F-TASK-001的Workflow代码直接调用（同进程/同Worker内的Activity调度，非HTTP）。仅为运维/调试目的暴露以下只读端点，统一前缀`/runtime`：

| 方法 | 路径 | 说明 | 对应Feature |
|---|---|---|---|
| GET | `/runtime/reasoning-turns/{taskId}/{stepId}` | 查询某个AiTaskStep内部的推理轮次明细（每轮的模型调用ref、工具调用ref、停止原因） | RUNTIME-F002 |
| GET | `/runtime/heartbeats/{taskId}` | 查询某AiTask最近的心跳事件序列（供人工排查"是否卡住"用，正式告警走F-OBS-001 OBS-F004） | RUNTIME-F006 |
| POST | `/runtime/kill-ack` | Kill Task信号被Agent Runtime在安全点确认收到并即将终止时的内部回执（供F-TASK-001 TASK-F005验证Kill真正生效，非人工直接调用） | RUNTIME-F007 |
| GET | `/runtime/context-stats/{taskId}/{stepId}` | 查询某step当前上下文窗口占用/裁剪历史（RUNTIME-F004可观测性，直接回应第6.1节Claude Agent SDK Issue #507指出的可见性缺口，Matbox自己解决这个问题） | RUNTIME-F004 |

## 14｜Request/Response Schema

```yaml
ReasoningTurn:
  type: object
  required: [turnId, taskId, stepId, turnIndex, role]
  properties:
    turnId: {type: string, format: uuid}
    taskId: {type: string}
    stepId: {type: string}
    turnIndex: {type: integer}
    role: {type: string, enum: [MODEL_CALL, TOOL_CALL]}
    modelInvocationRef: {type: string, nullable: true, description: "关联F-PROVIDER-001.ModelInvocation.invocationId"}
    actionExecutionRefs: {type: array, items: {type: string}, description: "关联F-ACTION-001.ActionExecution.executionId，一轮可能有多个并行工具调用"}
    stopReason: {type: string, enum: [CONTINUE, END_TURN, MAX_TURNS_REACHED, SELF_CORRECTION_TRIGGERED, KILLED, ERROR], nullable: true}
    untrustedContentFlags: {type: array, items: {type: string}, description: "标记本轮工具/网页输出中被判定为不可信内容的片段引用，供审计"}
    createdAt: {type: string, format: date-time}

HeartbeatEvent:
  type: object
  required: [heartbeatId, taskId, emittedAt, sequenceNo]
  properties:
    heartbeatId: {type: string, format: uuid}
    taskId: {type: string}
    stepId: {type: string, nullable: true}
    temporalActivityId: {type: string, nullable: true}
    sequenceNo: {type: integer}
    emittedAt: {type: string, format: date-time}
    source: {type: string, enum: [LOOP_INTERNAL], description: "架构原则第28条要求：必须标注心跳来自循环内部，不是进程存活检查"}

KillAcknowledgement:
  type: object
  required: [taskId, acknowledgedAt, safePointReached]
  properties:
    taskId: {type: string}
    stepId: {type: string, nullable: true}
    acknowledgedAt: {type: string, format: date-time}
    safePointReached: {type: boolean, description: "是否在当前工具调用完成后的安全点终止，而非mid-flight强行杀死"}
    compensationTriggeredRef: {type: string, nullable: true, description: "关联TASK-F005补偿动作引用"}

ContextStats:
  type: object
  required: [taskId, stepId, currentTokens, maxWindowTokens]
  properties:
    taskId: {type: string}
    stepId: {type: string}
    currentTokens: {type: integer}
    maxWindowTokens: {type: integer}
    trimEventsCount: {type: integer}
    claudeContextEditingApplied: {type: boolean, description: "本次是否使用了Anthropic Context Editing API（仅Claude供应商场景为true）"}
```

## 15｜OpenAPI 3.0文档

```yaml
openapi: 3.0.3
info:
  title: Matbox Agent Runtime Ops API
  version: "1.0.0"
  description: >
    Agent Runtime（F-RUNTIME-001）对外暴露的最小只读运维API集合。
    本模块主体不是HTTP服务，是被F-TASK-001 Workflow调用的Temporal Activity集合，
    以下端点仅用于排查/审计目的。鉴权见第16节，错误码见第19节。
servers:
  - url: https://internal.matbox.local/runtime
paths:
  /reasoning-turns/{taskId}/{stepId}:
    get:
      operationId: listReasoningTurns
      security: [{ bearerAuth: [] }]
      parameters:
        - { name: taskId, in: path, required: true, schema: { type: string } }
        - { name: stepId, in: path, required: true, schema: { type: string } }
      responses:
        "200":
          description: OK
          content:
            application/json:
              schema:
                type: array
                items: { $ref: "#/components/schemas/ReasoningTurn" }
        "404":
          description: RESOURCE_NOT_FOUND
  /heartbeats/{taskId}:
    get:
      operationId: listHeartbeats
      security: [{ bearerAuth: [] }]
      parameters:
        - { name: taskId, in: path, required: true, schema: { type: string } }
      responses:
        "200":
          description: OK
          content:
            application/json:
              schema:
                type: array
                items: { $ref: "#/components/schemas/HeartbeatEvent" }
  /kill-ack:
    post:
      operationId: acknowledgeKill
      security: [{ bearerAuth: [] }]
      requestBody:
        required: true
        content:
          application/json:
            schema: { $ref: "#/components/schemas/KillAcknowledgement" }
      responses:
        "200": { description: 已记录 }
        "409": { description: INVALID_STATE_TRANSITION（任务已处于终态，无法再确认Kill） }
  /context-stats/{taskId}/{stepId}:
    get:
      operationId: getContextStats
      security: [{ bearerAuth: [] }]
      parameters:
        - { name: taskId, in: path, required: true, schema: { type: string } }
        - { name: stepId, in: path, required: true, schema: { type: string } }
      responses:
        "200":
          description: OK
          content:
            application/json:
              schema: { $ref: "#/components/schemas/ContextStats" }
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT（携带tenantId claim，见第16节）
  schemas:
    ReasoningTurn:
      type: object
      description: 见第14节完整定义
    HeartbeatEvent:
      type: object
      description: 见第14节完整定义
    KillAcknowledgement:
      type: object
      description: 见第14节完整定义
    ContextStats:
      type: object
      description: 见第14节完整定义
```

## 16｜鉴权、权限与多租户规范

**不新建平行鉴权体系**——完全复用F-TENANT-001/F-CRED-001已冻结的模式：

1. **Agent Runtime本身不是终端用户直接访问的服务**——它由F-TASK-001的Workflow代码内部调用，Workflow/Activity本身运行在Matbox后端进程内，天然继承发起该AiTask的AgentIdentity（F-CRED-001）上下文，不需要为Agent Runtime单独发一套凭证。
2. **第13节列出的只读运维端点**：走与其余`/dq/*`、`/task/*`等端点同一套JWT校验，角色要求`Operator`及以上（排查/审计场景），不需要新增专属角色。
3. **多租户隔离**：`ReasoningTurn`/`HeartbeatEvent`表继承其所属`AiTask.tenantId`（复用TENANT-F004"共享表+租户ID字段"模式），查询层禁止绕过租户过滤。
4. **AI员工执行权限边界**：Agent Runtime的循环体在派发工具调用时，**不携带、不判断权限本身**——权限判断完全交给F-ACTION-001的Identity/RBAC/ABAC检查（ACTION-F005第③步），Agent Runtime只是把已经附带AgentIdentity上下文的ProposedAction转发过去，这是本模块"不重复实现权限判定"的具体落地方式。
5. **委派放大红线的复用**：ACTION-F005验收标准已明确"委派权限不得放大（delegated agent权限不能超过源Agent本次授权范围）"——Agent Runtime在组装ProposedAction时必须原样携带发起本次AiTask的AgentIdentity，不允许在推理循环内部临时提升权限范围。

## 17｜Provider Adapter接口规范

Agent Runtime**不定义新的Provider Adapter接口**——完全REUSE F-PROVIDER-001已经定义的`PROVIDER-F006 Provider Adapter标准接口`（`healthcheck()`/`list_models()`/`invoke(request)`/`estimate_cost(request)`/`cancel(provider_request_id)`/`normalize_error(provider_error)`）。

Agent Runtime在RUNTIME-F002主循环里对`invoke(request)`的调用方式：

```yaml
# RUNTIME-F002每一轮循环对F-PROVIDER-001的调用（伪代码/逻辑契约）
invoke_one_turn(conversationHistory, toolDefinitions, employeeTemplate):
  request = {
    tenant_id, run_id: taskId, trace_id, capability: "llm",
    model_route: employeeTemplate.model_policy_ref,
    input: conversationHistory + toolDefinitions,  # 工具定义作为input的一部分传给F-PROVIDER-001
    parameters: { max_tokens, temperature, ... },
    data_classification: employeeTemplate.data_class,
    timeout_ms, budget_envelope: task.budgetRef
  }
  response = F-PROVIDER-001.invoke(request)
  # 本报告在9.1/9.2节核查中发现的真实缺口（非本报告修复，记录供F-PROVIDER-001 Owner协调）：
  # PROVIDER-F006当前定义的响应字段(output/usage/cost/latency_ms/finish_reason/safety_metadata/raw_metadata_ref)
  # 尚未显式定义"跨供应商统一的tool_use结构化字段"——Claude的tool_use、OpenAI的function_call、
  # Gemini的function_call三者字段名/结构不同。Agent Runtime现阶段的应对方案：
  # 在output.raw_metadata_ref基础上，自己解析各Provider Adapter已知的原始响应格式提取工具调用，
  # 同时向F-PROVIDER-001 Owner登记这条协调需求，建议Stage 10前在PROVIDER-F006补一个
  # 跨供应商归一化的 normalized_tool_calls[] 字段，避免Agent Runtime里散落供应商专属解析逻辑。
  return response

dispatch_tool_calls(response.normalized_tool_calls, agentIdentity):
  for each toolCall in response.normalized_tool_calls:
    proposedAction = F-ACTION-001.propose({
      toolId: toolCall.name, params: toolCall.arguments,
      employeeId: agentIdentity.employeeId, resourceScope: employeeTemplate.allowed_scope
    })
    result = F-ACTION-001.execute(proposedAction.actionId)  # commit时重新鉴权，10步pipeline生效
    mark_as_untrusted(result.output)  # ACTION-F005验收标准要求：Web/browser/tool输出当作不可信内容处理
    append_tool_result_to_history(toolCall.id, result.output)
```

## 18｜Webhook、回调及异步任务规范

- Agent Runtime**不接收外部Webhook**——它是被内部Workflow调用的执行体，没有对外的异步回调入口。
- **异步任务模型**：完全复用Temporal Activity模型（与F-TASK-001/F-QUEUE-001一致，不新建第二套队列/回调机制）——每次模型调用（经F-PROVIDER-001）和每次工具调用（经F-ACTION-001）在Agent Runtime的Workflow代码里各自封装为独立Activity，Activity失败按Temporal Retry Policy处理（有界retry+backoff），超过重试上限的Activity失败会被Workflow代码捕获，转译为该AiTaskStep的`FAILED`状态并附带`reasonCode`（见19节）。
- **心跳/Kill信号的传递机制（第7节源码级证据）**：Activity在循环体内部每隔一段时间（架构原则第28条：2-3分钟一次）调用`Activity.getExecutionContext().heartbeat(payload)`，payload携带`HeartbeatEvent`结构（第14节）；Temporal Server在下发Cancellation（对应F-TASK-001的Kill Task信号，TASK-F005）时，**投递时机绑定在下一次心跳到达时**（非立即中断）——这意味着**心跳间隔本身就是Kill信号的最大响应延迟上限**，架构原则第28条定的"2-3分钟一次心跳"同时决定了Kill Switch的响应及时性，两者是同一个参数的两个效果，Stage 10调参时必须一并考虑，不能只从"报警灵敏度"单一维度决定心跳间隔。
- **流式进度**：RUNTIME-F008不直接给前端推流，模型的流式片段/中间工具调用结果经Task API的事件序列（`AiTaskEvent`，F-TASK-001已定义）异步落库，前端走已有的断线重连补齐机制（TASK-F004）读取，不新增WebSocket/SSE通道。

## 19｜错误码、重试、超时和降级规范

**完全复用** `Matbox_错误码规范_正式开发文档_V1.0-RC.md` 定义的17个跨模块错误码，Agent Runtime的典型映射：

| 场景 | 错误码 | HTTP | 可重试 |
|---|---|---|---|
| 模型调用超时（F-PROVIDER-001透传） | PROVIDER_TIMEOUT | 504 | 是 |
| 模型/供应商不可用（F-PROVIDER-001透传，触发fallback） | PROVIDER_UNAVAILABLE | 503 | 是（Provider Router内部fallback，Agent Runtime感知到fallback发生但不重复处理） |
| 供应商拒绝合法请求（如内容策略拒绝） | PROVIDER_REJECTED | 422 | 否 |
| 触发限流（F-PROVIDER-001 PROVIDER-F004透传） | RATE_LIMITED | 429 | 是（Agent Runtime在Workflow层做指数退避后重试该轮LLM调用，不是重跑整个task） |
| 工具未注册 | TOOL_UNREGISTERED | 403 | 否 |
| 工具调用被策略拒绝（F-ACTION-001透传） | TOOL_POLICY_DENIED | 403 | 否，转人工审批或该step判定FAILED |
| 工具调用超时 | TOOL_TIMEOUT | 504 | 是（有界） |
| 循环状态非法转移（如已终态的step又收到新一轮调用请求） | INVALID_STATE_TRANSITION | 409 | 否 |
| 预算超限（循环中途触发F-COST-001阻断） | BUDGET_EXCEEDED | 402 | 否，转人工审批 |
| 自我纠错（TASK-F008）达到硬上限仍未通过 | 复用INTERNAL_ERROR，`details.reasonCode=SELF_CORRECTION_LIMIT_REACHED` | 500 | 否，转人工审批（对应TASK-F008验收标准） |
| 未预期的内部错误 | INTERNAL_ERROR | 500 | 是（有界） |

**唯一需要补充说明的缺口**（与专项01第19节同一处理原则）：现有17码里没有专门覆盖"自我纠错达到硬上限"这一Agent Runtime高频状态的独立错误码——本报告不新造平行码，采用规范第4条允许的方式，复用`INTERNAL_ERROR`（500）作为HTTP层错误码，把精确语义放进`details.reasonCode`结构化字段。

**降级规范**：任何模型调用/工具调用错误一律不允许静默吞掉继续假装成功（fail-closed精神与F-ACTION-001/DQ系列一致）；Provider fallback到更贵供应商的场景已经由F-PROVIDER-001（PROVIDER-F003）负责留痕，Agent Runtime不重复记录，只在`ReasoningTurn.modelInvocationRef`里带出这条关联即可查询到。

## 20｜数据库及Migration设计

沿用REL-F006已确认的**Flyway**迁移工具，共享表+`tenant_id`字段模式（TENANT-F004）。Agent Runtime的OWN数据表刻意保持最小（大部分状态已经在F-TASK-001/F-PROVIDER-001/F-ACTION-001落库，Agent Runtime只补"推理轮次"这一层缺失的关联记录）：

```sql
-- V1__runtime_core_tables.sql

CREATE TABLE runtime_reasoning_turn (
    turn_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    task_id UUID NOT NULL,          -- 关联 F-TASK-001 ai_task.task_id
    step_id UUID NOT NULL,          -- 关联 F-TASK-001 ai_task_step.step_id
    turn_index INT NOT NULL,
    role VARCHAR(16) NOT NULL,      -- MODEL_CALL | TOOL_CALL
    model_invocation_ref VARCHAR(128),   -- 关联 F-PROVIDER-001 model_invocation.invocation_id
    action_execution_refs UUID[],        -- 关联 F-ACTION-001 action_execution.execution_id（可多个）
    stop_reason VARCHAR(32),        -- CONTINUE|END_TURN|MAX_TURNS_REACHED|SELF_CORRECTION_TRIGGERED|KILLED|ERROR
    untrusted_content_flags JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (task_id, step_id, turn_index)
);
CREATE INDEX idx_runtime_turn_task ON runtime_reasoning_turn(tenant_id, task_id);
CREATE INDEX idx_runtime_turn_step ON runtime_reasoning_turn(step_id);

CREATE TABLE runtime_heartbeat_event (
    heartbeat_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    task_id UUID NOT NULL,
    step_id UUID,
    temporal_activity_id VARCHAR(128),
    sequence_no INT NOT NULL,
    source VARCHAR(16) NOT NULL DEFAULT 'LOOP_INTERNAL',
    emitted_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_runtime_heartbeat_task ON runtime_heartbeat_event(tenant_id, task_id, emitted_at DESC);

CREATE TABLE runtime_kill_acknowledgement (
    ack_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    task_id UUID NOT NULL,
    step_id UUID,
    safe_point_reached BOOLEAN NOT NULL,
    compensation_triggered_ref VARCHAR(128),
    acknowledged_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE runtime_context_snapshot (
    snapshot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    task_id UUID NOT NULL,
    step_id UUID NOT NULL,
    current_tokens INT NOT NULL,
    max_window_tokens INT NOT NULL,
    trim_events_count INT NOT NULL DEFAULT 0,
    claude_context_editing_applied BOOLEAN NOT NULL DEFAULT false,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_runtime_context_step ON runtime_context_snapshot(step_id, recorded_at DESC);
```

（`ai_task`/`ai_task_step`本身的表结构不在本模块重复定义，属于F-TASK-001；`model_invocation`属于F-PROVIDER-001；`action_execution`属于F-ACTION-001；本模块只存"轮次级"的关联/心跳/上下文快照记录。）

## 21｜前后端开发任务拆分

**后端（Java/Spring Boot，RuoYi-Vue-Pro基座，Temporal Java SDK）**：
- BE-01 ReasoningLoopController Workflow/Activity骨架（RUNTIME-F002），含终止条件判断
- BE-02 PromptAssembler（RUNTIME-F001），对接F-AIEMP-001/F-TASK-001只读查询
- BE-03 ToolCallDispatcher（RUNTIME-F003），对接F-ACTION-001 propose/execute契约+不可信内容标记
- BE-04 ContextWindowManager（RUNTIME-F004），含Claude Context Editing API适配层+通用裁剪/摘要兜底
- BE-05 CallLevelRetryHandler（RUNTIME-F005），错误码场景化映射+退避策略
- BE-06 HeartbeatEmitter + KillSwitchResponder（RUNTIME-F006/F007），Temporal Activity心跳封装+F-OBS-001事件写入
- BE-07 StreamingProgressBridge（RUNTIME-F008），对接F-TASK-001 Task API事件序列
- BE-08 与F-PROVIDER-001协调补齐`normalized_tool_calls[]`跨供应商归一化字段（第17节记录的协调项，非本模块单方面可完成）

**前端（Ops控制台，复用既有Ops FE框架，仅运维排查用途，非面向租户业务界面）**：
- FE-01 ReasoningTurn时间线视图（第13节只读端点消费）
- FE-02 心跳/Kill Ack状态面板（排查"AI员工是否卡住"用）
- FE-03 ContextStats可视化（上下文占用趋势，回应6.1节指出的可见性缺口）

## 22｜源码目录、模块和依赖关系

```
backend/
  modules/
    agent-runtime/
      loop/                    # RUNTIME-F002：ReasoningLoopController（Temporal Workflow定义）
      activities/               # RUNTIME-F002子模块：ModelCallActivity/ToolCallActivity（Temporal Activity实现）
      prompt/                   # RUNTIME-F001：PromptAssembler
      dispatch/                 # RUNTIME-F003：ToolCallDispatcher（依赖 shared-clients/action-client）
      context/                  # RUNTIME-F004：ContextWindowManager（claude/子目录：Context Editing API适配；generic/子目录：通用裁剪兜底）
      retry/                    # RUNTIME-F005：CallLevelRetryHandler
      liveness/                 # RUNTIME-F006/F007：HeartbeatEmitter + KillSwitchResponder
      progress/                 # RUNTIME-F008：StreamingProgressBridge（依赖 shared-clients/task-client）
      shared/
        contracts/               # ReasoningTurn/HeartbeatEvent/KillAcknowledgement/ContextStats DTO
        errors/                  # 复用 Matbox_错误码规范 的统一ErrorResponse
    shared-clients/              # 跨模块共享的Contract客户端（不属于agent-runtime私有）
      task-client/                # F-TASK-001
      action-client/               # F-ACTION-001
      provider-client/              # F-PROVIDER-001
      aiemp-client/                  # F-AIEMP-001
      obs-client/                     # F-OBS-001
frontend/
  apps/ops-console/
    features/agent-runtime/       # 对应FE-01~FE-03
```

**依赖方向铁律**：`agent-runtime/*`只允许依赖`shared-clients/*`和自己内部子模块，不允许被`task-client`等基础设施客户端反向依赖；`agent-runtime/loop`（Workflow定义）必须保持Temporal确定性约束（不直接调用非确定性API，所有外部调用经`activities/*`封装），这是Temporal编程模型的硬性要求，不是Matbox自定的规则，违反会导致Workflow replay时行为不一致。

## 23｜测试集、Golden Set和验收脚本

由于Agent Runtime是GREENFIELD模块，测试集从零设计，复用F-OBS-001（OBS-F006）已确认的评测集4类结构标准（真实生产流量抽样/对抗性测试库/人为构造边界情况/历史故障重放）：

- **RT-T001**：构造一个多轮工具调用任务，验证ReasoningLoopController能正确在"模型返回tool_use→派发→回填→再调用"之间循环，且循环内每一步都经过F-ACTION-001（不是绕过网关直接执行）。
- **RT-T002**：人为让F-ACTION-001对某次工具调用返回`TOOL_POLICY_DENIED`，验证Agent Runtime正确把拒绝原因回填进上下文（而不是当作工具执行失败重试），并让模型据此调整下一步决策。
- **RT-T003**：构造超长多轮对话（模拟接近上下文窗口上限），验证ContextWindowManager在Claude场景触发Context Editing、在非Claude场景触发通用裁剪，且裁剪后任务仍能产出正确结果（不是裁掉关键信息导致任务失败）。
- **RT-T004**：人为让某次模型调用返回`RATE_LIMITED`，验证CallLevelRetryHandler做指数退避重试而不是让Temporal Activity整体重跑（重跑会丢失已经进行到一半的多轮上下文）。
- **RT-T005**：人为在Kill Task信号下发后立即检查响应延迟，验证Agent Runtime在下一次心跳（≤架构原则第28条设定的心跳间隔）内确认收到Kill并在当前工具调用完成后的安全点终止，不是mid-flight强行杀死导致工具执行状态不一致。
- **RT-T006**：连续2次不发送心跳（模拟循环卡死在某个非心跳感知的阻塞调用里），验证F-OBS-001（OBS-F004）在约定时间窗口内触发告警，而不是无声无息挂起。
- **RT-T007**：构造一个真实的prompt injection场景（工具返回的网页内容里嵌入"忽略之前的指令"类文本），验证Agent Runtime按ACTION-F005验收标准把工具输出标记为不可信内容、不被模型误当作新指令执行高风险动作（对应架构原则第10条+第6.6节Google ADK真实安全事故的教训）。
- **RT-T008**：构造TASK-F008自我纠错达到`selfCorrectionMaxAttempts`硬上限的场景，验证Agent Runtime正确转`INTERNAL_ERROR/SELF_CORRECTION_LIMIT_REACHED`并转人工审批，而不是无限重试（对应DELEGATION-F005"硬上限防重试风暴"同一原则，2025年7月保险公司84.7万次API调用死循环真实事故是这条要求的依据）。

**验收脚本执行环境**：与其余已建成模块一致，Stage 10前置——必须绑定真实Matbox Repo + Base Commit + 真实Temporal集群部署才能执行，本报告不接受synthetic样本冒充结论。

## 24｜成本、性能、并发及安全要求

**成本**：Agent Runtime自身不引入新的经常性订阅费用（核心执行引擎自研，REUSE的Temporal/Anthropic Context Editing API走已有的F-TASK-001基础设施成本和F-PROVIDER-001已有的Claude API调用成本，不重复计费）；编排器自己的LLM调用开销已由F-ORCHESTRATOR-001不可变原则第1条要求独立计入F-COST-001，Agent Runtime的每一次模型调用同样必须携带`taskId`/`stepId`标签走F-PROVIDER-001已有的成本归因机制，不允许出现"测试时几毛钱、规模化后账单失控查不出原因"（与ORCHESTRATOR-001同一条教训）。

**性能**：单轮LLM调用+工具调用的P50/P95/P99延迟目标不在本报告虚构，留到Stage 10真实Repo+真实Temporal集群跑出baseline后冻结（与专项01第24节同一原则）；已知的架构约束是——心跳间隔（2-3分钟）同时是Kill信号响应延迟上限（第18节已论证），Stage 10调参时需要在"报警灵敏度"和"Kill响应及时性"之间找真实平衡点，不能只优化一侧。

**并发**：单个AiTask内的多个AiTaskStep按F-TASK-001既有顺序执行（不在本模块引入新的并发模型）；单个task step内如果模型一次返回多个并行tool_use（Claude/主流模型均支持"parallel tool calls with multiple tool_use blocks per response"，第6.1节已确认），Agent Runtime应并行派发给F-ACTION-001（每个工具调用仍各自独立经过10步Enforcement Pipeline，互不阻塞），全部返回后再统一回填进下一轮上下文——这与F-ORCHESTRATOR-001的fan-out/fan-in模式是同一个设计原则在更细粒度上的复用。

**安全**：
- 工具/网页输出必须当作不可信内容处理（ACTION-F005验收标准+架构原则第10条），Agent Runtime在RUNTIME-F003回填工具结果时必须显式标记来源不可信，不能让模型把工具输出误判为系统指令——第6.6节Google ADK的真实安全事故是这条要求的具体反面教材。
- 委派权限不得放大（第16节已展开）。
- 心跳payload不得携带敏感数据（Prompt原文/工具调用参数可能含租户业务机密），只携带最小必要的进度标识字段。

## 25｜开发阶段、优先级和预计工作量

| WP | Feature | 优先级 | 量级估算（人天，粗量级） | 备注 |
|---|---|---|---|---|
| WP-RUNTIME-01 | RUNTIME-F002主循环骨架+RUNTIME-F001 Prompt组装 | P0，最先 | 10-15 | 是后续一切的地基，含Temporal Workflow确定性约束的正确落地 |
| WP-RUNTIME-02 | RUNTIME-F003工具调用派发+不可信内容标记 | P0 | 6-10 | 依赖F-ACTION-001已冻结的10步Pipeline契约，本身逻辑不复杂但联调工作量在于跨模块契约对齐 |
| WP-RUNTIME-03 | RUNTIME-F004上下文窗口管理（含Claude Context Editing适配） | P0 | 8-12 | 需要真实长对话数据才能验证裁剪/摘要不丢关键信息，Stage 10需预留调优缓冲 |
| WP-RUNTIME-04 | RUNTIME-F005调用级重试 | P1 | 3-5 | 场景化应用已有错误码规范，逻辑相对简单 |
| WP-RUNTIME-05 | RUNTIME-F006/F007心跳与Kill响应 | P0 | 6-8 | 需要与F-OBS-001（OBS-F004告警规则）和F-TASK-001（TASK-F005 Kill Task）两端联调，逻辑本身简单但涉及三个模块协调 |
| WP-RUNTIME-06 | RUNTIME-F008流式进度桥接 | P1 | 3-5 | 复用F-TASK-001已有Task API，工作量主要在事件序列的正确落库 |
| WP-RUNTIME-07 | 与F-PROVIDER-001协调补齐跨供应商`normalized_tool_calls[]`字段 | P0，阻塞项 | 2-4（Agent Runtime侧）+ 需F-PROVIDER-001 Owner配合 | 第17节记录的真实协调缺口，不是Agent Runtime能单方面关闭的WorkPackage |

**总量级估算**：约38-59人天（不含Stage 10真实调参/联调缓冲），与已建成的F-TASK-001/F-ACTION-001同量级，符合"核心执行引擎"应有的工作量占比。

## 26｜风险、阻塞项及备用方案

| 风险/阻塞项 | 等级 | 说明 | 备用方案 |
|---|---|---|---|
| F-PROVIDER-001尚未定义跨供应商统一的tool_use归一化字段 | 高（本次审计新发现，真实阻塞） | 第17/21节已记录，需与F-PROVIDER-001 Owner协调补齐 | Agent Runtime短期先自行解析各Provider Adapter的原始响应格式，同时登记协调需求，不阻塞P0链路开工 |
| RuoYi后端真实Spring Boot版本未核实，影响Spring AI 1.x/2.x选型 | 中 | 第6.7节已指出Spring AI 2.0要求Boot 4.0/4.1 | Stage 10前置核实；若仍在Boot 3.x，锁定Spring AI 1.x或改用LangChain4j（两代Boot都支持）或直接用`anthropic-sdk-java`手写适配层，三条路都可行，不构成真正阻塞 |
| 心跳间隔同时决定Kill响应延迟，两个需求可能存在真实张力 | 中（本次审计新发现） | 第18/24节已展开 | Stage 10用真实数据决定具体间隔秒数，允许心跳与Kill检查采用不同频率（例如心跳2-3分钟一次用于报警，但在每次工具调用返回后额外主动检查一次Kill标志位，不完全依赖心跳间隔） |
| Temporal Workflow确定性约束对开发团队是新增的编程模型学习成本 | 中 | 团队此前只在F-TASK-001/F-QUEUE-001层面接触过Temporal，Agent Runtime是第一个把复杂业务循环逻辑写成Workflow代码的模块 | 第7节已提供官方Cookbook+Spring AI集成样例作为起点参考，降低从零摸索的成本 |
| Google ADK / LangGraph生态演进过快，未来可能出现更成熟的Java方案 | 低-中（长期观察） | 第6.6/6.3节已记录两者当前的破坏性变更/安全事故证据 | 不是"现在错过了"，是"现在的架构冲突是真实的，不是能力不够"，留作WP-RUNTIME-08之外的长期能力监控项，若未来ADK-Java真的原生支持Temporal风格的durable execution，可重新评估 |
| Stage 10真实Temporal集群/真实Repo未绑定 | 高（既有阻塞，与其余模块一致） | 与F-TASK-001/F-QUEUE-001共享同一阻塞 | 无——按既定Stage 9/10边界等待，不伪造 |

## 27｜最终验收标准

本模块（Stage 10绑定真实Repo+真实Temporal集群后）的验收标准 = 第23节RT-T001~RT-T008（8项，本报告新建，Agent Runtime此前无任何既有验收基线）+ Own/Reuse边界核查（第11节）+ 第24节安全要求。

三者全部通过，且：
1. 推理循环的每一次工具调用均可在审计记录里追溯到对应的F-ACTION-001 ActionExecution（不存在绕过网关的工具调用）；
2. 心跳事件确认从循环内部（`source=LOOP_INTERNAL`）发出，而非仅依赖进程存活检查（对应架构原则第28条的字面要求，不是抽象满足）；
3. TASK-F008自我纠错硬上限、DELEGATION-F005式重试风暴防护在Agent Runtime层面同样生效（RT-T008）。

未通过任一项，Feature不得进入RC5 ACCEPTED流程。

## 28｜交给未来AI开发人员的完整执行说明

如果你是接手这个模块施工的未来AI开发者（Codex或其他），请按以下顺序阅读和执行：

1. **先读三份边界文档，弄清楚Agent Runtime不做什么**：`Matbox_中央编排层_正式开发文档_V1.0-RC.md`（F-ORCHESTRATOR-001，路由不归本模块）、`Matbox_AI任务运行时_正式开发文档_V1.0-RC.md`（F-TASK-001，任务生命周期/Checkpoint/Kill Switch不归本模块，本模块是被它调用的执行体）、`Matbox_Action网关_正式开发文档_V1.0-RC.md`（F-ACTION-001，工具权限判定不归本模块，本模块只转发）。**这三份文档定义的边界是本报告第2/12节的直接依据，施工前必须先内化，避免重复实现已经存在的功能。**
2. **再读本报告**（本文件）——本报告的核心结论是：Agent Runtime整体自研（Java，Temporal Workflow/Activity承载推理循环），不整体采纳Claude Agent SDK/OpenAI Agents SDK/LangGraph/CrewAI/Microsoft Agent Framework/Google ADK/Vercel AI SDK中任何一个现成框架，理由是架构一致性冲突（第9.1节），不是能力不够。
3. **依赖检查**：施工前确认F-TASK-001/F-ACTION-001/F-PROVIDER-001/F-AIEMP-001/F-OBS-001均已存在正式文档且状态为DRAFT_RESEARCH_COMPLETE或更高——本次核查确认全部已具备。**唯一的真实协调缺口**：F-PROVIDER-001的Provider Adapter响应schema尚未定义跨供应商统一的`normalized_tool_calls[]`字段（第17/21/26节），施工WP-RUNTIME-02前需要与负责F-PROVIDER-001的开发者/AI协调，不能自己在Agent Runtime里悄悄加一份平行的归一化逻辑然后当作既成事实，应该推动补进F-PROVIDER-001正式文档。
4. **Stage 10前置条件不可跳过**：必须先有真实Matbox Repo + Base Commit + 真实部署的Temporal集群（与F-TASK-001/F-QUEUE-001共用），才能开始任何一条WorkPackage施工。
5. **施工顺序**：按第25节WP-RUNTIME-01→07顺序，01（主循环骨架+Prompt组装）必须最先完成，02/03/05可在01完成后并行，04/06可随时并行，07（与F-PROVIDER-001协调）应尽早发起（协调周期通常比开发周期长，不要等到02开工才发现被阻塞）。
6. **不要重新做的事**：不要重新调研"要不要整体采用一个现成Agent框架"（第9.1节已经系统性核查8个候选并给出理由，除非未来出现能同时满足"原生Java+与Temporal Checkpoint模型零冲突+与F-ACTION-001强制网关零冲突"三条硬约束的全新候选，否则不需要重新打开这个问题）；不要重新设计错误码（复用错误码规范）；不要重新设计鉴权模式（复用F-TENANT-001/F-CRED-001）；不要重新实现工具执行的权限判定（严格MUST NOT REBUILD，属于F-ACTION-001）。
7. **Temporal Workflow确定性约束是真实的技术红线，不是建议**：`agent-runtime/loop`目录下的Workflow代码必须保持确定性（所有真正的外部调用、随机性、系统时间读取都必须封装进`activities/*`），违反会导致Workflow replay时产生不一致行为，这不是Matbox自定的规范，是Temporal编程模型本身的硬性要求，第7/22节已给出官方参考实现路径。
8. **如果发现本报告与真实Repo/真实Temporal集群行为冲突**：按既定不可变原则处理——记录并升级给对应Owner决策，不要自行静默绕过第2/9/11节已经画定的模块边界。

---

## 附录｜来源汇总

- Claude Agent SDK：[Claude Agent SDK: Agent Loops, Tool Calls, and Multi-Step Workflows](https://www.augmentcode.com/guides/claude-agent-sdk-agent-loops-tool-calls)、[Anthropic Agent SDK: What It Ships vs. What You Build](https://www.augmentcode.com/guides/anthropic-agent-sdk-what-ships-vs-what-you-build)、[Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview)、[Use the Claude Agent SDK with your Claude plan](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan)、[Anthropic pauses Claude Agent SDK subscription change](https://thenewstack.io/anthropic-pauses-claude-agent-sdk-subscription-change/)、[GitHub Issue #507](https://github.com/anthropics/claude-agent-sdk-python/issues/507)
- OpenAI Agents SDK：[What is the OpenAI Agents SDK? Loops and Handoffs in 2026](https://futureagi.com/blog/what-is-openai-agents-sdk-2026/)、[The next evolution of the Agents SDK](https://openai.com/index/the-next-evolution-of-the-agents-sdk/)
- LangGraph：[LangGraph vs Semantic Kernel](https://dev.to/theprodsde/langgraph-vs-semantic-kernel-python-ai-agents-in-2026-1p4g)、[GitHub Issue #6363](https://github.com/langchain-ai/langgraph/issues/6363)、[LangGraph is MIT-Licensed](http://rvernica.github.io/2026/03/langchain-license)、[What Is LangGraph? Production Use Cases 2026](https://atlan.com/know/ai-agent/ai-agent-memory/what-is-langgraph/)
- CrewAI：[CrewAI Wikipedia](https://en.wikipedia.org/wiki/CrewAI)、[CrewAI Review 2026](https://blog.reviewaitool.com/2026/04/12/crewai-review-2026/)、Matbox内部文档`Matbox_AI员工委派_正式开发文档_V1.0-RC.md`第31行独立记录的从业者反馈
- Microsoft Agent Framework/AutoGen：[Two Lineages, One Framework](https://alexbevi.com/blog/2026/06/18/two-lineages-one-framework-how-autogen-and-semantic-kernel-became-the-microsoft-agent-framework/)、[Microsoft Retires AutoGen](https://agentmarketcap.ai/blog/2026/04/13/microsoft-autogen-maintenance-mode-agent-framework-sunset-2026)、[Discussion #7210](https://github.com/microsoft/autogen/discussions/7210)
- Google ADK：[Announcing ADK for Java 1.0.0](https://developers.googleblog.com/announcing-adk-for-java-100-building-the-future-of-ai-agents-in-java/)、[google/adk-java](https://github.com/google/adk-java)、[Claude models for ADK agents](https://raw.githubusercontent.com/google/adk-docs/main/docs/agents/models/anthropic.md)、[Google Deletes 3 ADK AI Workflows After Malicious GitHub Issue](https://thehackernews.com/2026/08/google-deletes-3-adk-ai-workflows-after.html)、[Release v2.5.0](https://github.com/google/adk-python/releases/tag/v2.5.0)
- Vercel AI SDK：[Agents: Loop Control](https://ai-sdk.dev/docs/agents/loop-control)
- Temporal官方Agent模式：[Of course you can build dynamic AI agents with Temporal](https://temporal.io/blog/of-course-you-can-build-dynamic-ai-agents-with-temporal)、[Basic agentic loop with Claude and tool calling](https://docs.temporal.io/ai/cookbook/agentic-loop-tool-call-claude-python)、[Spring AI integration - Java SDK](https://docs.temporal.io/develop/java/integrations/spring-ai)、[Activity Timeouts - Java SDK](https://docs.temporal.io/develop/java/activities/timeouts)、[Detecting Activity failures](https://docs.temporal.io/encyclopedia/detecting-activity-failures)
- Spring AI/LangChain4j：[Spring AI vs LangChain4j 2026](https://medium.com/@muruganantham52524/spring-ai-vs-langchain4j-which-java-ai-framework-to-choose-in-2026-fd93bb7aa653)、[Spring AI Issue #3366](https://github.com/spring-projects/spring-ai/issues/3366)、[Tool Calling :: Spring AI Reference](https://docs.spring.io/spring-ai/reference/api/tools.html)、[Anthropic Chat :: Spring AI Reference](https://docs.spring.io/spring-ai/reference/api/chat/anthropic-chat.html)
- Anthropic Context Editing/Memory Tool：[Managing context on the Claude Developer Platform](https://claude.com/blog/context-management)、[Context engineering: memory, compaction, and tool clearing](https://platform.claude.com/cookbook/tool-use-context-engineering-context-engineering-tools)
- Agent Memory市场（F-MEM-001边界参考，非本模块直接采纳）：[State of AI Agent Memory 2026](https://mem0.ai/blog/state-of-ai-agent-memory-2026)、[Agent Memory at Scale 2026: Letta, Zep, Mem0, and LangMem Compared](https://agentmarketcap.ai/blog/2026/04/10/agent-memory-vendor-landscape-2026-letta-zep-mem0-langmem)
- Matbox内部依据文档：`Matbox_Feature_Register.md`、`Matbox_架构设计原则.md`（第10/28/33条）、`Matbox_中央编排层_正式开发文档_V1.0-RC.md`、`Matbox_AI任务运行时_正式开发文档_V1.0-RC.md`、`Matbox_Action网关_正式开发文档_V1.0-RC.md`、`Matbox_Provider_Router_正式开发文档_V1.0-RC.md`、`Matbox_AI员工身份_正式开发文档_V1.0-RC.md`、`Matbox_AI员工委派_正式开发文档_V1.0-RC.md`、`Matbox_错误码规范_正式开发文档_V1.0-RC.md`、`Matbox_证据审计与监控_正式开发文档_V1.0-RC.md`
