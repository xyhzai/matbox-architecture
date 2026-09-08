# Matbox 专项00m｜Conductor OSS（conductor-oss/conductor）专项评估

技术选型报告 · V1.0 · 2026-09-02

**DocID**: MATBOX-CONDUCTOROSS-TECHSELECT-20260902-V1.0
**审计对象**: [github.com/conductor-oss/conductor](https://github.com/conductor-oss/conductor)（2026-09-02 API直查：**32,161 stars / 1,002 forks / 260 open issues**，Apache-2.0，2026-09-01仍有push，前身为Netflix于2016年开源的Netflix Conductor）
**报告性质**：聚焦影响评估报告，不是新模块技术选型——核查该候选对Matbox**已完成**的专项28（Agent Runtime，2026-08-30，已冻结Temporal作为执行运行时）的具体影响，不产生新FeatureID，不推翻任何已冻结架构决策。
**触发背景**：用户排查清单中的"conducting"一项，经排查"Conductor"这个名字目前对应至少5个不同真实项目（Netflix系Conductor OSS、Microsoft Conductor CLI、Code Conductor、conductor.build桌面应用、Conductor AgentStack SEO产品），本报告判断用户最可能指向**conductor-oss/conductor**——理由是它是唯一一个"为AI Agent提供durable/可恢复执行能力的工作流引擎"，与Matbox专项28已选定的Temporal属于同一技术赛道的真实竞品，其余4个"Conductor"要么是编程类Agent并行工具、要么与AI Agent技术无关。核查过程中未发现任何证据推翻这个判断——conductor-oss/conductor的定位、代码结构、近期issue讨论全部围绕"durable workflow/agent execution engine"这个主题，与Matbox的场景高度相关，因此本报告按这个身份判断继续执行，不需要用户额外确认。
**方法论**：沿用专项00d/00i已确立的标准——不是有star数就行，要看真实源码、真实issue、真实第三方讨论；每条结论标注可核查来源URL。**本次核查的目的不是"要不要换成Conductor"（Temporal已在Stage阶段冻结，不建议无理由推翻），而是验证性核查：Temporal这条已选路线相对Conductor OSS是不是真的更适合Matbox场景，以及是否存在此前专项28调研遗漏的重要事实。**

---

## 0｜给忙碌读者的结论摘要

1. **这是一次真实、有意义的补漏，不是重复劳动**：专项28（AgentRuntime技术选型报告）认真核查了8个真实候选（Claude Agent SDK、OpenAI Agents SDK、LangGraph、CrewAI、Microsoft Agent Framework、Google ADK、Vercel AI SDK、Temporal原生Agent模式），**但确认没有一个是conductor-oss/conductor**——这是本次核查的第一个真实发现：专项28的候选清单里存在一个当时未评估的真实竞品，而且是本报告核查后认为8个候选之外**最值得补上的一个**，因为它和Temporal是同一类"durable execution引擎"，不是Python-only的通用Agent框架。
2. **核心结论：Temporal的既定选择被验证是对的，但不是没有代价——Conductor OSS用JSON任务图换来了Matbox目前必须自己造的"开箱即用AI集成层"，这是一条值得记录、不代表推翻选型的真实观察。** Conductor OSS原生自带LLM Chat/Embeddings/图像生成、MCP工具发现与调用、向量库读写这些"系统级Task"（`LLM_CHAT_COMPLETE`/`CALL_MCP_TOOL`/`LLM_SEARCH_EMBEDDINGS`等），零胶水代码即可用；而Matbox选择Temporal后，这些能力全部要靠F-PROVIDER-001/F-ACTION-001自己实现——这不是"Matbox漏做了"，是专项28/专项16已经主动选择"自己拥有这层集成、换取单一Enforcement Pipeline/单一Provider Adapter"的架构一致性，本报告确认这个取舍依然成立，但如实记录"Conductor OSS这条路线本可以省下多少胶水代码"这个真实的机会成本，供未来复盘。
3. **技术机制上，Conductor OSS和Temporal解决的是同一类问题（durable execution/故障恢复），但架构路线本质不同**：Temporal是"Workflow即确定性代码，靠事件溯源(event-sourcing)replay重建状态"；Conductor OSS是"Workflow即JSON任务图，服务端把每个Task的状态机(SCHEDULED→IN_PROGRESS→COMPLETED)直接落库(Redis/PostgreSQL/MySQL/Cassandra)、Worker靠HTTP长轮询`/tasks/poll`领任务"——**Conductor的Java SDK虽然支持"code native"方式构建工作流（`java-sdk`仓库示例里有"typed Plan with dependencies"），但最终仍是编译成同一份JSON任务图，不是Temporal那种"代码本身就是可重放的执行历史"的模型**。这个差异直接决定了：Matbox专项28需要的"复杂条件分支+循环+TASK-F008自我纠错这类动态终止条件的推理主循环"，用Java写成Temporal Workflow代码比拆成Switch/DoWhile/Fork/Join的JSON任务图更自然，这是本报告认为Temporal依然是正确选择的关键技术理由，不是重复专项28的结论，是本次针对Conductor OSS的具体路线核实后独立确认的。
4. **真实的License/治理历史值得记录，符合"核心开源+关键能力锁企业版"的排查标准，但方向和结果比预想的更复杂**：核查发现Orkes（Conductor OSS的商业化母公司）2024年的官方博客明确把"LLM tasks（text complete/embeddings/chat）"列为Orkes商业版独有、不在OSS任务清单里的能力；但本报告直接核查2026-09当前的`conductor-oss/conductor`仓库源码，确认`ai/`模块（含全部LLM Task类型、MCP工具调用、向量库任务）**已经是Apache-2.0许可下的OSS代码，不再是商业独占**——这条能力经历了"曾经锁在商业版→现在开源"的真实演变，方向对Matbox有利，但也说明这类商业化边界会随时间移动，不能假设当前免费的能力永远免费；Orkes官方对比页仍列出可视化拖拽编辑器、SSO/RBAC/SOC2认证、99.99% SLA、托管基础设施等作为商业版独有（该对比页面本身发布于2024年5月，部分条目如"OSS无可视化编辑"已被2026年的UI更新部分推翻，具体边界建议真正落地前重新核实）。
5. **治理风险是这次核查里比"要不要用"更重要的一条独立发现**：Netflix已于2023年12月正式停止维护公开版Conductor（`Netflix/conductor`已归档），转而运营一个**与社区版分道扬镳的内部fork**——Netflix 2026年8月官方技术博客原文明确写"Netflix's internal roadmap for Conductor is primarily aligned with its company-level objectives, which is distinct from the community's innovation roadmap"。这意味着**"Netflix每月跑4.2亿次workflow"这个常被引用的生产规模数字，指向的是Netflix内部fork，不是今天`conductor-oss/conductor`这个公开仓库本身**——两者同源但已分叉，公开仓库现在的唯一主要维护方是单一商业公司Orkes，这是一个需要如实标注的、与"生产验证过的成熟度"直觉不完全对应的细节。
6. **推荐：PASS/USE/REFERENCE三选一判断——REFERENCE-ONLY，不采纳依赖、不照搬架构，仅作为F-PROVIDER-001/F-ACTION-001未来实现时的任务分类词表和"AI集成层该长什么样"的一个真实可运行参照。** 不构成推翻Temporal选型的理由，具体怎么参考见第6节。

---

## 1｜技术本质核查：是不是真的"为AI Agent设计的durable执行引擎"

### 1.1 项目定位与代码规模：真实工程，非包装demo

`api.github.com/repos/conductor-oss/conductor`直查确认：**32,161 stars、1,002 forks、260 open issues，主语言Java，仓库体积58,253 KB，2026-09-01 23:46仍有push**（[GitHub API](https://api.github.com/repos/conductor-oss/conductor)）。仓库描述原文："Conductor is an event driven agentic workflow engine providing durable and highly resilient execution engine for applications and AI Agents"——定位从项目描述本身就直接对应Matbox专项28的场景（AI员工的durable执行运行时）。

顶层目录结构核查确认这是一个真实的多模块生产级工程，非demo：`core`（执行引擎核心）、`ai`（LLM/向量库/MCP集成模块）、`agentspan`（Agent级追踪/编排模块）、`redis-persistence`/`postgres-persistence`/`mysql-persistence`/`cassandra`（4种可选持久化后端）、`es6/7/8-persistence`（Elasticsearch索引层，3个版本并存说明有真实的长期兼容性维护负担）、`grpc`/`rest`（双协议对外接口）、`conductor-clients`（多语言SDK）、`ui`/`ui-next`（两代可视化界面并存，说明UI正在迁移期）（[repo tree](https://github.com/conductor-oss/conductor)）。

### 1.2 AI/Agent能力的真实性：`ai`模块源码直读确认

直接核查`ai/README.md`确认这不是营销话术，是真实可运行的系统级Task实现：支持**13家LLM/图像/语音供应商**（OpenAI、Anthropic Claude、Google Gemini、Azure OpenAI、AWS Bedrock、Mistral、Cohere、Grok、Perplexity、HuggingFace、Ollama、LiteLLM代理100+模型、Stability AI），**3种向量库**（pgvector、Pinecone、MongoDB Atlas），以及**14种AI Task类型**：`LLM_CHAT_COMPLETE`（多轮对话+工具调用）、`LLM_TEXT_COMPLETE`、`LLM_GENERATE_EMBEDDINGS`、`GENERATE_IMAGE`/`GENERATE_AUDIO`/`GENERATE_VIDEO`、`LLM_INDEX_TEXT`/`LLM_STORE_EMBEDDINGS`/`LLM_SEARCH_INDEX`/`LLM_SEARCH_EMBEDDINGS`/`LLM_GET_EMBEDDINGS`（向量库读写全套）、`LIST_MCP_TOOLS`/`CALL_MCP_TOOL`（MCP工具发现与调用）、`GENERATE_PDF`（[`ai/README.md`原文](https://raw.githubusercontent.com/conductor-oss/conductor/main/ai/README.md)）。`LLM_CHAT_COMPLETE`的入参甚至细到`thinkingTokenLimit`（Claude/Gemini扩展思考预算）、`reasoningEffort`（OpenAI推理强度）、`webSearch`/`codeInterpreter`（供应商原生工具开关）——这是对2026年各家模型API能力做过真实跟踪的实现，不是套壳。

### 1.3 Durable Agent模式的真实机制：JSON任务图 + 服务端状态机，不是代码事件溯源

直接核查仓库内`docs/architecture/durable-execution.md`（维护者自己撰写的架构文档，非营销页面）确认核心机制：

- **持久化的是数据，不是代码执行历史**：每次workflow执行时，Conductor把"workflow定义快照、workflow状态（status/input/output/变量）、每个task的执行记录（状态/输入输出/时间戳/重试次数/workerID）、task队列状态"直接写入配置好的持久化存储（Redis/PostgreSQL/MySQL/Cassandra），**所有状态在进入下一步之前先落库**（[`durable-execution.md`原文](https://raw.githubusercontent.com/conductor-oss/conductor/main/docs/architecture/durable-execution.md)）。
- **Worker是HTTP长轮询模型**：Task进队列后由Worker主动`poll`领取、状态流转为`IN_PROGRESS`，完成后上报`COMPLETED`；Worker崩溃或未响应则触发`responseTimeout`把Task重新放回队列被其他Worker领走——这是"at-least-once投递"语义，要求Worker自己保证幂等（文档原文明确写"Workers should be idempotent"）。
- **失败矩阵覆盖相当完整**：文档给出一张具体的场景对照表（Worker poll后未开始工作就崩溃/Worker做完副作用但还没上报完成就崩溃/服务端重启/长时间等待跨越多次部署/网络分区），每种场景都有明确的可预测行为，这份文档质量本身是一条正面证据——说明维护者对"到底怎么保证不丢状态"这件事有过认真设计，不是空谈durable。
- **Replay/恢复操作细分为三种**（Restart从头重跑/Rerun从某个task起复用之前的输出/Retry只重试最后失败的task），且"workflow定义更新不影响正在跑的execution"（用快照隔离）——这套语义与Matbox已在F-TASK-001冻结的Checkpoint/Resume概念类似，但**实现方式是"服务端Task状态机+数据库行"，不是Temporal那种"Workflow代码通过event history replay重建内存状态"的模型**。

### 1.4 与Temporal的核心架构差异（本报告认为最重要的技术判断）

| 维度 | Temporal（Matbox已选） | Conductor OSS |
|---|---|---|
| Workflow如何定义 | **确定性代码**（Java/Go/等真实编程语言），受"不能有非确定性操作"约束，非确定性工作必须包在Activity里 | **JSON任务图**（Switch/DoWhile/Fork/Join/Dynamic Task等operator拼出控制流），Java SDK提供"code native"构建器，但最终产出同一份JSON定义，不是Temporal意义上"代码即历史" |
| 状态如何持久化/恢复 | Event Sourcing：持久化的是事件流，重启后通过**replay代码**重建内存状态 | 状态机数据直接落库（Redis/PostgreSQL/MySQL/Cassandra），重启后从**持久化的状态行**恢复，不需要replay代码 |
| Worker执行模型 | Worker通过gRPC长连接接收Activity任务，`Activity.getExecutionContext().heartbeat()`原生心跳+`Cancellation`随心跳投递 | Worker主动HTTP轮询`/tasks/poll`；心跳/存活检测依赖`responseTimeoutSeconds`+`pollTimeoutSeconds`超时机制，不是"循环内部主动发出的心跳"这种原生原语 |
| 复杂条件分支/动态终止条件的表达力 | 原生（任意Java代码：递归、复杂条件、动态计算的循环终止条件） | 受限于Switch/DoWhile/Dynamic Task这组有限operator；官方也承认Dynamic Task"lets the graph be resolved at runtime"，是对纯JSON表达力不足的补丁而非本质解决 |
| 开箱即用AI集成 | **无**——Matbox靠F-PROVIDER-001/F-ACTION-001自己实现 | **有**——`ai`模块原生14类AI Task，零胶水代码 |

**对Matbox架构原则第28条（心跳必须从工作循环内部发出、连续漏2次才报警）的具体影响**：Temporal的`Activity.heartbeat()`是从工作代码内部主动调用的原语，与该条原则的字面要求直接对应（专项28第7节已核实源码级机制）；Conductor OSS的存活检测建立在轮询超时配置上，理论上Worker代码内部同样可以在长任务中主动上报进度（Conductor的Task Update API支持中途更新状态），但**不是引擎原生提供的"心跳"概念**，需要Matbox自己在Worker代码里补一层等价语义——这是一条真实的、此前专项28没有机会对比出来的架构细节差异，进一步支持"Temporal的心跳原语与Matbox已定的原则28字面契合度更高"这个判断。

---

## 2｜真实用户与开发者证据

### 2.1 项目历史：Netflix开源→归档→Orkes接棒，且Netflix内部已分叉

- Netflix于2016年开源Conductor，用于自身微服务编排；2022年，包括原Conductor创建者Jeu George、Viren Baraiya、Boney Sekh在内的团队创立Orkes，做Conductor的商业化托管服务（[TechCrunch](https://techcrunch.com/2023/12/13/orkes-forks-conductor-as-netflix-abandons-the-open-source-project/)）。
- **Netflix于2023年12月13日正式归档`Netflix/conductor`公开仓库**，官方声明转向维护自己的内部fork；Orkes随即以"Conductor OSS"名义接棒维护社区版，即今天的`conductor-oss/conductor`（[The New Stack](https://thenewstack.io/orkes-to-maintain-conductor-project-as-netflix-steps-back/)、[Orkes公告](https://orkes.io/blog/evolving-conductor-open-source-and-the-conductor-community/)）。
- **关键细节（本报告核查后需要澄清的一点）**：Netflix 2026年8月的官方技术博客《Netflix Conductor: The Next Chapter》原文明确写"Netflix's internal roadmap for Conductor is primarily aligned with its company-level objectives, which is distinct from the community's innovation roadmap"——即Netflix内部现在跑的是一个**与公开OSS仓库路线图不同的独立fork**，文中提到的"每月约4.2亿次workflow执行、每天500万-2000万次、约20万个workflow定义、约150个应用方"这些惊人的生产规模数字，指向的是这个**内部fork**，不能直接等同于"今天`conductor-oss/conductor`这份代码在Netflix生产环境里跑出来的成绩单"（[Netflix Tech Blog via Medium](https://netflixtechblog.medium.com/netflix-conductor-the-next-chapter-41ad21067649)，因反爬直接fetch返回403，内容通过WebSearch摘要交叉确认）。

### 2.2 当前公开仓库的维护活跃度：真实、持续，但主要由单一商业公司驱动

- 合并PR数**672**、当前开放PR数**96**、已关闭issue数**278**（对比260个仍开放，issue关闭率约52%，说明有真实的、未完全消化的积压）（GitHub Search API直查，2026-09-02）。
- Contributors API返回至少100个不同贡献者（受单页上限，真实数字≥100）（[contributors API](https://api.github.com/repos/conductor-oss/conductor/contributors)）。
- `OSSMETADATA`文件（Netflix系项目标准治理文件格式）标注`osslifecycle=active`（[OSSMETADATA](https://raw.githubusercontent.com/conductor-oss/conductor/main/OSSMETADATA)）。
- **治理结构判断**：主要维护方是Orkes单一商业公司（"Orkes is the primary maintainer of the Conductor OSS repository"），这与Matbox此前评估Lunar MCPX/Infisical类项目时用过的"核心开源、由单一商业公司主导路线图"风险模式相同——Apache-2.0协议本身能防止"锁死无法自托管"这种最坏情况（可以永久fork自用），但功能优先级、哪些能力进OSS哪些进商业版，长期看仍由Orkes一家公司决定，不是社区共治。

### 2.3 真实GitHub issue抽样：AI/Agent模块活跃但明显不成熟，核心引擎有真实未解决的可靠性问题

**AI/Agent相关issue（新功能区，抽样近20条按创建时间排序）**：
- `#1532`（已关闭）："agents with MCP tools loop to the iteration cap — tool results never reach the LLM"——MCP工具调用结果没能正确回填给模型，导致Agent循环空转到上限，这正是Matbox RUNTIME-F002推理主循环最核心的一步（工具结果回填），说明Conductor自己的Agent循环实现踩过这个坑。
- `#1499`（已关闭）：Agent的`DO_WHILE`循环内`JOIN`任务在所有并行工具任务都`COMPLETED`的情况下仍返回空输出。
- `#1416`（已关闭）：自托管模型（`base_url`参数）抛NPE，环境变量`OPENAI_BASE_URL`被静默忽略。
- `#1583`（仍open）：`SUB_WORKFLOW`被系统误判为"handoff"，导致被当作工具调用的子Agent永远不被识别为一次真正的tool call。
- `#1437`（已关闭）：供应商API Key未做trim校验，末尾换行符导致"Unexpected char 0x0a in Authorization value"这种不友好的报错。
- **交叉信号**：AI Cookbook相关issue（`#1513`/`#1509`）反映的示例代码路径均为`.py`文件（`90_guardrail_e2e_tests.py`/`Example 39c_serverless_code_execution.py`），说明AI/Agent这层能力的官方示例和早期打磨**以Python为主**，Java侧的`conductor-client-ai-spring`模块相对更新、被验证的深度可能不如Python路径（本报告未能找到直接证据证明Java AI集成模块存在同等数量级的真实生产使用，这是一条如实标注的"未能完全验证"）。

**核心引擎（非AI）真实未解决问题**：
- `#712`（open，2026-01-13创建，仅1条评论）：升级到v3.21.23后，子workflow执行完成但父workflow不再继续，需要手动调用`POST /api/workflow/decide/{parent}`才能恢复——这是一个真实的、影响核心Fork/Join/SubWorkflow机制的可靠性问题，报告后长期未获实质性回应。
- `conductor-oss/getting-started#7`（open，16条评论）：Docker Hub上的`conductoross/conductor-standalone`镜像已经**两年多未更新**（3.15.0 vs 当前3.22.3）却比最新镜像下载量更高，新用户很容易在不知情的情况下跑一个严重过时的本地镜像——真实的、持续了半年多仍未解决的发行/文档卫生问题（[issue原文](https://github.com/conductor-oss/getting-started/issues/7)）。

### 2.4 第三方独立视角

一篇独立对比博客（非Orkes自己发布）原话评价："Temporal.io is winning mindshare because it's modern, well-documented, and solves a real pain point for microservices teams, while Orkes Conductor is the dark horse — less famous but remarkably capable and efficient"——这与本报告的技术判断方向一致：Conductor OSS技术能力是真实的，但社区认知度/文档打磨程度不如Temporal（[Medium对比文章](https://medium.com/@easwaranvijayakumar/workflow-orchestration-showdown-temporal-io-vs-orkes-conductor-vs-camunda-e59fd79c2b65)，本报告如实标注这是单一博主观点，非权威评测）。

### 2.5 真实生产使用案例

`USERS.md`（仓库内志愿PR登记文件，**非独立验证，本报告如实标注这是自报名单**）列出Netflix、Florida Blue、UWM、Deutsche Telekom Digital Labs、VMware、JPMorgan Chase、Atlassian、GE Healthcare、ReliaQuest、Clari、Supercharge等公司（[`USERS.md`原文](https://raw.githubusercontent.com/conductor-oss/conductor/main/USERS.md)）。**本报告的判断**：这份名单能证明"确实有知名企业尝试或使用过"，但因为是自愿PR登记、无更新时间戳、无法核实当前是否仍在生产使用，不能等同于专项28对LangGraph"约400家企业含Klarna/Uber/JPMorgan"那种有独立第三方案例文章佐证的证据强度——本条证据强度评级为"中"，弱于LangGraph，强于大多数一般开源项目的空白名单。

---

## 3｜License与商业化边界

### 3.1 License核查

`LICENSE`文件原文核实为标准Apache License 2.0全文（[LICENSE](https://raw.githubusercontent.com/conductor-oss/conductor/main/LICENSE)），GitHub API的`license.spdx_id`同样确认为`apache-2.0`。**这是OSI标准开源许可证，允许自托管商用、允许修改分发、附带专利授权条款，对Matbox不构成任何License层面的商用障碍**。

### 3.2 "核心开源+关键能力锁企业版"模式的真实核查结果——一条方向有利但需要谨慎解读的历史证据

Orkes官方博客《6 Differences between Conductor OSS and Orkes Conductor》（**核实发布/最后更新时间为2024年5月28日**，[原文](https://orkes.io/blog/differences-between-conductor-oss-vs-orkes-conductor)）明确把以下能力列为Orkes商业版独有、OSS不含：

- **LLM Task（text complete/embeddings/chat）、OpenAI/Cohere/Anthropic/Google Vertex AI/Pinecone/Weaviate等"开箱即用集成"**
- 可视化工作流编辑器（该文原话："the visual diagram is simply a static representation... built in code"，OSS只能看不能编辑）
- 性能/可用性：OSS约100 task/秒，Orkes 1,000+ task/秒；OSS无HA保证，Orkes承诺99.99%可用性
- 企业安全：SSO、RBAC、SOC 2 Type II认证基础设施
- 托管基础设施（Redis/Elasticsearch由Orkes代管 vs OSS自己运维）

**本报告核查后需要指出的关键更正**：直接核查2026-09当前的`conductor-oss/conductor`仓库源码，确认顶层`ai/`目录（含全部LLM Task类型、MCP工具集成、向量库任务）**是Apache-2.0许可下、与主仓库同一份代码，不再是Orkes商业独占能力**——即"LLM tasks是商业版专属"这条2024年的说法，到2026年已经不成立，这个能力经历了从锁到开的真实迁移。**本报告判断这条变化对Matbox的实际参考价值有限（因为Matbox本来就不打算整体采纳Conductor OSS的AI集成层），但它是一条重要的方法论提醒：任何"某能力当前是否商业独占"的判断都必须用当前日期重新核实源码，不能引用一份两年前的博客当作现状——这条经验本身值得记录进方法论**。

**尚未能确认当前状态、建议真正需要时再核实的条目**：可视化编辑器是否已经支持在OSS里"编辑"而非"只读展示"（2026年3月的`ui-next`更新博客只提到"更清晰的可视化"，未明确提到编辑能力）、吞吐量数字（100 vs 1000+ task/秒）、HA/SSO/RBAC是否仍是商业独占——这些条目均来自同一份2024年的博客，鉴于LLM Task条目已被证明过时，**这些条目也应视为"未经2026年重新验证、可能已经过时"，本报告不采信其当前有效性，仅标注为历史参考**。

### 3.3 治理集中度风险

Netflix归档公开仓库、转向自己不对外的内部fork后，`conductor-oss/conductor`的路线图和"哪些能力开源、哪些进商业版"的边界完全由Orkes一家公司决定。这不构成License层面的风险（Apache-2.0保证即使Orkes未来收紧策略，现有OSS代码仍可永久自托管/fork），但构成一条**长期功能可预期性**上的风险——与Matbox此前评估同类"单一商业公司主导的核心开源项目"（如Lunar MCPX/Infisical）时使用的判断标准一致：核心执行引擎能用，但不应假设它会一直保持当前的开放程度。**由于Matbox本次结论是REFERENCE-ONLY、不产生代码依赖，这条风险不构成实际暴露，仅作为记录。**

---

## 4｜Java SDK可达性核查（Matbox架构原则第33条硬性要求）

- `conductor-oss/java-sdk`独立仓库确认存在，Apache-2.0协议，2026-08-31仍有push，通过Maven Central分发，要求**Java 21+**（[java-sdk README](https://raw.githubusercontent.com/conductor-oss/java-sdk/main/README.md)）。
- 提供专门的Spring集成模块：`conductor-client-spring`（核心自动配置）、`conductor-client-spring-boot4`（专为Spring Boot 4适配）、`conductor-client-ai-spring`（AI Agent自动配置）——这组模块划分方式与专项28第6.7节对Spring AI"2.0需要Spring Boot 4"版本耦合问题的关注点一致，Matbox若真要用，同样需要先确认RuoYi的Spring Boot具体版本。
- 支持Java代码构建workflow（README示例"Example108PlanExecuteRefs builds a typed `Plan` with dependencies and cross-step output references"），但如第1.4节所述，这是JSON定义之上的类型安全构建器，不是Temporal意义上的"代码即执行历史"。
- **可见度警示信号**：`java-sdk`仓库本身只有**12 stars**，远低于主仓库的32,161 stars，也低于`python-sdk`（102 stars）——这不直接等于"Java SDK不成熟"（很多用户直接用主仓库自带的Java客户端代码而非这个独立仓库），但结合2.3节"AI Cookbook示例以`.py`为主"的观察，**本报告判断Conductor OSS的AI/Agent这层新能力，目前的社区验证深度以Python生态为主，Java路径存在但相对更新、被更少人真实跑过**，这是一条如实标注、专项28对Google ADK/LangGraph等候选同样适用的"Java支持存在但生态权重更轻"类型判断。

**结论**：Java可达性这一项**通过**（有官方维护、Apache-2.0、Maven Central分发、专门Spring Boot模块），但**Java侧AI/Agent能力的社区验证深度弱于Python侧**，这是一条比"有没有Java SDK"更细致、专项28框架下可以直接复用的判断维度。

---

## 5｜候选定位：PASS / USE / REFERENCE

| 判断维度 | 结论 |
|---|---|
| **整体采纳为Agent Runtime执行引擎** | **REJECT**（不是"能力不够"，是与专项28已确认的架构一致性理由完全相同——Conductor OSS同样是"自带循环控制+自带状态持久化"的完整引擎，整体采纳会在"谁的Checkpoint/谁的task状态为真相源"上与F-TASK-001已冻结的Temporal模型产生结构性冲突，这与专项28否决Google ADK/LangGraph的理由是同一条原则的再次验证） |
| **代码/依赖直接引用** | **REJECT**（不同执行模型，无法与Temporal混用；`ai`模块的Provider/MCP集成代码是Java写的、理论上可读，但引入即意味着同时维护两套持久化引擎，专项28第3.3节已经论证过这类"两个真相源"风险） |
| **架构模式照搬** | **PARTIAL REFERENCE**——`docs/architecture/durable-execution.md`里的失败矩阵（网络分区/服务端重启/长时间等待跨部署/definition更新时运行中execution的隔离）是一份高质量的"durable execution需要覆盖哪些场景"清单，值得作为专项28/F-TASK-001文档的**自查checklist**，核对Matbox基于Temporal的实现是否也覆盖了同样完整的场景，而不是照搬其JSON任务图机制本身 |
| **任务分类/AI集成设计参考** | **REFERENCE，价值最高的一条**——`ai`模块把"LLM对话/Embedding/图像生成/向量库读写/MCP工具发现与调用"拆分成14个具体、边界清晰的Task类型这件事本身是一份有价值的分类词表，F-PROVIDER-001定义Provider Adapter的能力边界、F-ACTION-001设计MCP Gateway的工具发现协议时，可以把这14个Task类型当作一份"别人已经在生产场景里趟过一遍的能力清单"来对照检查有没有遗漏（例如Matbox目前的设计里是否明确考虑了"向量库读写"要不要走F-ACTION-001的统一工具调用通道，还是单独设一条路径） |
| **治理/风险案例** | **REFERENCE**——"LLM Task从商业独占迁移为OSS开源"和"Netflix内部fork与公开仓库分道扬镳"这两条历史事实，值得作为Matbox评估其他"核心开源+商业公司主导"类候选时的标准案例补充 |

**最终判断：REFERENCE-ONLY**。不建议改变专项28已冻结的"Matbox自研（Java，Temporal Workflow/Activity）"路线，不产生新FeatureID，不建议引入`conductor-oss`任何代码依赖。

---

## 6｜具体怎么"参考"

1. **`Matbox_专项28_AgentRuntime_技术选型与开发交接报告`第4节"GitHub候选项目清单"补充一行**：把`conductor-oss/conductor`列为"事后核查，验证性候选，非否决"，注明与Temporal同属durable execution引擎赛道，本报告（专项00m）是完整核查记录，避免未来有人重复调研这同一个项目。
2. **F-PROVIDER-001正式设计Provider Adapter能力边界时**，参照`ai/README.md`列出的14个AI Task类型（`LLM_CHAT_COMPLETE`的入参字段细到`thinkingTokenLimit`/`reasoningEffort`/`webSearch`/`codeInterpreter`），核对Matbox自己的Provider Adapter接口是否遗漏了某个供应商能力开关。
3. **F-ACTION-001设计MCP Gateway的工具发现/调用协议时**，`LIST_MCP_TOOLS`/`CALL_MCP_TOOL`两个Task的实现（`ai/src`目录内，Java代码，Apache-2.0可读）可作为"别人怎么处理MCP工具发现结果缓存/调用参数校验"的实现细节参考，非采纳其代码本身。
4. **`docs/架构选型方法论`或类似文档**，可以把"LLM Task 2024年商业独占→2026年开源"这个案例，补充为"核查商业化边界必须用当前日期重新验证源码，不能信任历史博客"的一条方法论证据，与本项目已经在专项00i（OpenWorker）、专项00c/00d确立的"不能只看营销材料"标准并列。
5. **不建议**做的事：不建议把`docs/architecture/durable-execution.md`的失败矩阵直接翻译成Matbox文档的一部分（机制不同、直接照搬容易造成误导),而应该只用它做"我们是否想到了同样多的失败场景"这层校验,校验完之后其表述方式不需要保留。

---

## 7｜信息来源清单

- Conductor OSS GitHub仓库：[github.com/conductor-oss/conductor](https://github.com/conductor-oss/conductor)、[API直查](https://api.github.com/repos/conductor-oss/conductor)（2026-09-02：stars 32,161/forks 1,002/open_issues 260/language Java/license apache-2.0/pushed_at 2026-09-01）、[顶层目录树](https://api.github.com/repos/conductor-oss/conductor/contents/)、[PR/issue统计](https://api.github.com/search/issues)（merged PR 672/open PR 96/closed issue 278）、[contributors API](https://api.github.com/repos/conductor-oss/conductor/contributors)、[LICENSE原文](https://raw.githubusercontent.com/conductor-oss/conductor/main/LICENSE)、[OSSMETADATA](https://raw.githubusercontent.com/conductor-oss/conductor/main/OSSMETADATA)、[USERS.md](https://raw.githubusercontent.com/conductor-oss/conductor/main/USERS.md)
- 核心源码/架构文档直读：[`ai/README.md`](https://raw.githubusercontent.com/conductor-oss/conductor/main/ai/README.md)（AI Task类型全表）、[`docs/architecture/durable-execution.md`](https://raw.githubusercontent.com/conductor-oss/conductor/main/docs/architecture/durable-execution.md)（durable execution语义、失败矩阵）
- 官方站点/文档：[conductor-oss.org](https://conductor-oss.org/)、[docs.conductor-oss.org](https://docs.conductor-oss.org/)、[FAQ](https://conductor-oss.github.io/conductor/devguide/faq.html)、[Why Conductor](https://conductor-oss.github.io/conductor/devguide/concepts/conductor.html)
- Java SDK：[conductor-oss/java-sdk](https://github.com/conductor-oss/java-sdk)（[README](https://raw.githubusercontent.com/conductor-oss/java-sdk/main/README.md)，12 stars，Java 21+，Maven Central，Spring Boot 3/4模块）
- 项目历史与治理：[TechCrunch: Orkes forks Conductor as Netflix abandons the open source project](https://techcrunch.com/2023/12/13/orkes-forks-conductor-as-netflix-abandons-the-open-source-project/)、[The New Stack: Orkes to Maintain Conductor Project as Netflix Steps Back](https://thenewstack.io/orkes-to-maintain-conductor-project-as-netflix-steps-back/)、[Orkes: Evolving the Conductor Open Source and the Conductor Community](https://orkes.io/blog/evolving-conductor-open-source-and-the-conductor-community/)、[Netflix Tech Blog: Netflix Conductor - The Next Chapter（2026-08，经WebSearch摘要交叉确认，直接WebFetch返回403）](https://netflixtechblog.medium.com/netflix-conductor-the-next-chapter-41ad21067649)
- 商业化边界：[Orkes Blog: 6 Differences between Conductor OSS and Orkes Conductor（发布于2024-05-28，部分条目已过时，详见第3.2节）](https://orkes.io/blog/differences-between-conductor-oss-vs-orkes-conductor)、[Orkes: Conductor OSS vs. Orkes Conductor对比页](https://orkes.io/platform/conductor-oss-vs-orkes)
- 真实issue（均通过`api.github.com`直接抓取原文核实state/评论数）：[#712（子workflow执行后挂起，open）](https://github.com/conductor-oss/conductor/issues/712)、[getting-started#7（Docker镜像过期误导新用户，open，16评论）](https://github.com/conductor-oss/getting-started/issues/7)、[#1532（MCP工具结果未回填导致循环空转，已关闭）](https://github.com/conductor-oss/conductor/issues/1532)、[#1499（DO_WHILE内JOIN返回空输出，已关闭）](https://github.com/conductor-oss/conductor/issues/1499)、[#1416（自托管模型NPE，已关闭）](https://github.com/conductor-oss/conductor/issues/1416)、[#1583（SUB_WORKFLOW误判为handoff，open）](https://github.com/conductor-oss/conductor/issues/1583)、[#1437（API Key未trim导致鉴权报错，已关闭）](https://github.com/conductor-oss/conductor/issues/1437)
- 第三方独立视角：[Medium: Workflow Orchestration Showdown - Temporal.io vs Orkes Conductor vs Camunda](https://medium.com/@easwaranvijayakumar/workflow-orchestration-showdown-temporal-io-vs-orkes-conductor-vs-camunda-e59fd79c2b65)
- UI更新记录：[Orkes Blog: Conductor OSS Updates - Polished Look for Workflow Visualizer and More](https://orkes.io/blog/new-conductor-oss-workflow-visualizer/)
- 前置Matbox文档：[`Matbox_专项28_AgentRuntime_技术选型与开发交接报告_2026-08-30.md`](Matbox_专项28_AgentRuntime_技术选型与开发交接报告_2026-08-30.md)、[`Matbox_专项00i_OpenWorker专项评估_2026-09-02.md`](Matbox_专项00i_OpenWorker专项评估_2026-09-02.md)（方法论与格式参照）
