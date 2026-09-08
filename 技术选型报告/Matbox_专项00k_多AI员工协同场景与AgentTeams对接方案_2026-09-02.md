# Matbox 专项00k｜多AI员工协同场景与AgentTeams对接方案

技术选型报告 · V1.0 · 2026-09-02

**DocID**: MATBOX-MULTIAGENT-COLLAB-AGENTTEAMS-TECHSELECT-20260902-V1.0
**触发背景**：用户在`专项00j`（Distilly与AgentTeams专项评估）基础上进一步判断——"好几个AI员工一起干活、人还能实时看着"这个场景**是Matbox真实要面对的需求**，而不是00j第7节原本归类的"记录但不紧急"档位。本报告的任务是深挖这个判断是否有真实业务场景支撑，如果支撑成立，具体怎么把AgentTeams验证过的"Matrix共享房间"模式对接到Matbox已有架构上。
**方法论延续**：`专项00c/00d/00e/00j`的做法——不因为用户直觉方向明确就单向论证，正反证据都记录；关键技术判断（Java Matrix SDK是否成熟、AgentTeams当前真实维护状态）用WebFetch/GitHub API/WebSearch重新核实，不复用旧报告的印象；不臆造家具行业业务流程，用可查证的行业资料反推。
**状态**: DRAFT_RESEARCH_COMPLETE（设计级提案，未进入Stage 10真实施工）

---

## 0｜给忙碌读者的结论摘要

1. **用户的判断部分成立，但成立的范围比"好几个AI员工一起干活"这个原始表述要窄**——本报告用真实家具定制行业资料核查后确认：一个客户定制订单从"设计→报价→生产排产→物流"的完整链条，在真实行业里天然是**顺序、分阶段、checkpoint式**的（业内用APS/MES/WMS三套系统分别管这三段，一段的产出是下一段的输入门槛），这条链条本身**不需要**"多方实时同处一室、互相看见"这种更强的共享可见性——`F-DELEGATION-001`已有的委派语义（A做完交给B，权限收窄+预算传递+trace留痕）就是这条链条的正确技术形态，AgentTeams的价值在这里不大。
2. **但确实存在一个更窄、更真实的场景，AgentTeams的"共享房间"模式在这里有直接价值**：当一个人类项目负责人需要**同时**监督**多个正在并发运行**的AI员工在同一个客户项目/订单上工作（不是排队等前一个做完，是真的同时在跑——比如客户运营AI正在跟客户实时对话的同时，设计支持AI在迭代出图、治理岗位AI在核算预算），人类需要一屏看到所有相关AI员工的当前状态，并能针对某一个单独插话纠正而不打断其他人——这才是AgentTeams真正解决的问题（"多个Agent+人类同处一室、互相可见、可单独插话"），且与`专项00f`已确认的"看板模式优于纯聊天"结论不冲突（详见第1.4节的边界划分）。
3. **技术对接方案：不采用AgentTeams的实现（Matrix协议本身、K8s架构、Go/Python代码），只借鉴其"共享可见性+可单独插话不打断"这条设计模式**，落地为Matbox自己的新Feature（建议命名`F-COLLAB-001`），本质是**在已有的`AiTask`（F-TASK-001）之上做一层只读聚合投影**，把同一个项目/订单下的多个`AiTask`（可能来自`F-ORCHESTRATOR-001`的fan-out，也可能是人类手动分别发起）聚合到一个"协作会话"视图里，人类的每一次插话仍然走F-TASK-001**已经存在**的`POST /task/{taskId}/instructions`（轻量追加，2026-09-02已补齐）或`/takeover`（重量级接管），`F-COLLAB-001`本身不新增任何执行/委派/权限语义，只做可见性聚合——这条设计原则与Matbox已有的`F-VIZ-006`（代码问题定位与人工修复台的Realtime模块，"事件订阅复用F-QUEUE-001，不新建第二套队列"）是**同一套已验证的架构套路**，不是新发明。
4. **Matrix协议本身不建议采用，理由是真实技术证据，不是"Java单语言栈原则"一句话带过**：本报告用GitHub API直接核查确认——matrix.org官方**没有**Java SDK；曾经的`matrix-android-sdk`（Java）已于2022年归档弃用；第三方候选`Cosium/matrix-communication-client`（Java，47★）和`Trixnity`（Kotlin Multiplatform含JVM目标，49★，Apache-2.0，活跃维护）都是**规模很小、未被验证过大型生产系统采用**的项目，没有一个够格作为Matbox核心平台层的技术依赖。且Matrix协议本身假设"持久化的sync长连接是房间状态的真相来源"，这与Matbox`F-TASK-001`已经写入的不可变原则第1条"不让HTTP长连接承载业务任务，状态必须能在断线重连后从服务端真实状态补齐"存在方向性冲突——不是简单的"没有SDK所以不用"，是协议本身的状态模型和Matbox已确认的架构哲学不一致。真正需要的"实时推送"能力，Matbox自己已经有现成先例（`F-VIZ-006`的SSE/WebSocket事件网关，转发`F-QUEUE-001`事件、按`EventID`/`OccurredAt`重放防止断线丢事件），`F-COLLAB-001`应该复用同一套模式，不引入Matrix。
5. **License/技术栈/维护健康度交叉核实（2026-09-02，与`专项00j`同日复核，结论一致，未发现漂移）**：AgentTeams当前GitHub API直查——5,537★/678 fork/Apache-2.0/主语言Go（2,647,019字节）+Python（2,070,468字节）+Shell，issue总数455、PR总数744（编号已连续排到#1197+），最近一次commit `2026-08-22`，贡献者结构健康（`johnlanni`442次、`shiyiyue1102`93次、`Jing-ze`43次、`max-wc`34次、`googs1025`33次，非单人项目），`homepage`字段指向阿里云官方产品页——`专项00j`的评估结论今日复核**完全站得住**，不是过时判断。但Go+Python技术栈与Matbox Java单语言栈原则（架构原则第33条已反复验证的红线，`专项28`否决LangGraph等候选同一理由）直接冲突，代码本身不能引入。
6. **最终判断（PASS/USE/REFERENCE三选一）**：AgentTeams的**代码/依赖/Matrix协议本身 = PASS**（不采纳，技术栈冲突+协议模型与Matbox已确认架构哲学冲突+无成熟Java生态支撑）；**"共享房间式多方实时协作可见性+可单独插话不打断"这条设计模式 = REFERENCE**（值得作为Matbox新增`F-COLLAB-001`的设计参照，但落地是用Matbox自己的Java技术栈、复用`F-QUEUE-001`/`F-TASK-001`已有能力重新实现，不是移植代码）；**没有USE档位的判断**——AgentTeams没有任何组件能被直接复用而不经过重新实现，不构成"部分代码可用"的情形。

---

## 1｜真实业务场景核查：家具定制订单是否需要多AI员工实时共享可见性

### 1.1 家具定制行业真实工作流——用外部行业资料核查，不臆造

查证真实的家具定制制造行业资料（家具行业APS/MES/WMS系统集成研究、家具定制商业流程指南，见附录来源）后确认，一个客户定制订单的真实链条是：

1. **需求澄清**：产品类型、目标尺寸、数量、使用场景、设计参考、预算区间、交付要求、期望完成时间——这是订单的起点。
2. **报价（Quotation）**：制造方基于需求澄清阶段收到的brief，评估材料/工艺要求/产能/时间线，给出明确报价——**这一步的输入是上一步的输出**，报价不能在需求没澄清前给出。
3. **生产与物流（Production & Logistics）**：真实资料明确指出，成熟的家具制造企业用**三套独立系统**分别管这一段——APS（Advanced Planning and Scheduling，负责把订单拆解成生产任务、分配产线、排每日计划）、MES（Manufacturing Execution System，负责控制生产顺序/车间流转/生产节奏保证质量效率）、WMS（Warehouse Management System，负责原料及时分发+物流交付计划）。这三套系统之间也是**接力关系**——APS先排产，MES按排产结果执行，WMS在生产接近完成时介入物流规划，不是三者同时对同一个订单做决策。

**这条链条的结构性质**：查证资料明确用"从报价到交付的checkpoint"来描述这套流程，且强调"把项目拆成分阶段的里程碑，而不是当成一个笼统的时间数字"——这是一个**天然带阶段门（stage-gate）的顺序流程**，不是"多方同时决策、互相实时看见对方在干什么"的协同模式。行业自己选择用APS/MES/WMS三套独立系统而不是一个统一的"多方实时协作房间"来管这条链，本身就是一条真实的、行业已经用脚投票的证据——即便在真实制造业里，"设计→报价→排产→物流"这条链的正确技术形态也是**接力式的系统对接**，不是"共享房间"。

### 1.2 Matbox当前岗位族与这条链条的映射差距——一个需要如实指出的边界

`F-AIEMP-001`已确认的初始岗位族是：**内容运营**（小红书/抖音/商品内容专员）、**电商运营**（Amazon/Taobao/JD/Shopify专员）、**客户运营**（客服/销售跟进/CRM专员）、**创意生产**（图片/视频/数字人/3D专员）、**设计支持**（室内设计助理/商品匹配/资料整理）、**治理岗位**（审核员工/成本监督/质量监督）。

**如实指出**：这个岗位族清单里，只有"设计支持"部分对应第1.1节链条的第一段（设计），"治理岗位"里的成本监督可以对应报价/预算核算的一部分，**但"生产排产"和"物流跟踪"这两个岗位角色目前完全不在Matbox已确认的岗位族范围内**——Matbox当前的AI员工定位更偏"品牌的市场/内容/客户/设计支持"这一侧，不是深入到工厂ERP层面的生产排产/仓储物流。用户在任务简报里举的"设计AI员工出图→报价AI员工核算成本→生产排产AI员工订材料/排产→物流AI员工跟踪交付"这个四段链条，**目前只有前两段（设计、报价/成本核算的部分能力）能映射到Matbox已定义的岗位族上，后两段（生产排产、物流）是假设性的、尚未被Matbox立项的能力**，不能当作"Matbox现在已经有这些AI员工"来论证，这是本报告核查后必须如实标注的一处边界，不构成对用户判断方向的否定，但影响"现在具体设计到多细"的范围判断（见第6节）。

### 1.3 顺序委派够不够用？——分场景回答，不给单一答案

把"多AI员工协作"拆成两类真实会发生的子场景，分别判断：

**子场景A：跨阶段接力（设计做完交给报价，报价做完交给生产）**——第1.1节已用真实行业资料确认，这条链条本身是**接力式、有明确产出门槛**的，A阶段的产出必须存在，B阶段才能开始，不存在"A和B同时在做同一件事、需要互相实时看见"的真实需求。**`F-DELEGATION-001`已有的委派语义完全够用**：源AI员工做完后把结果（权限收窄+最小上下文+budget_envelope+deadline）委派给下一个AI员工，`upstreamTrustLevel`标记确保下游不会盲目信任上游产出，`trace_id`保证链路可查——这正是"接力"场景需要的能力，不需要AgentTeams的共享房间。

**子场景B：同一项目内并发协作，人类需要同时监督多条并行线**——这是真实存在、但比子场景A窄得多的场景。典型情况不是"设计→报价→生产"这条主链本身，而是**同一个项目/订单在某个阶段需要多个AI员工同时介入、且人类项目负责人需要实时掌握全局**，例如：
- 一个较大金额的B2B定制项目，客户运营AI员工正在与客户做实时的需求澄清对话，同时设计支持AI员工需要基于客户刚说的话即时调整效果图，治理岗位（成本监督）AI员工需要实时校验新方案是否超预算——三者理论上可以顺序接力，但实际业务场景里客户是"边聊边看效果图边问预算"，三个AI员工的工作在时间上是**重叠**的，不是干净的先后关系。
- 一个人类项目负责人手上同时挂着好几个客户项目，每个项目各自有1-2个AI员工在跑（比如同时有3个装修项目分别有设计支持AI员工在出图），负责人需要一个统一视图看到"这几个项目现在都到哪一步了、谁需要我立刻处理"，而不是逐个打开每个AiTask分别看。

**这类场景的关键需求不是"AI员工之间需要互相看见对方"（AI员工本身不需要知道彼此的存在，各自完成自己的`AiTask`即可），而是"人类需要一个统一的、实时的、跨多个`AiTask`的监督视图，并能在其中任何一个上单独插话"**——这与AgentTeams"人类在房间里可以@某个Worker插话、不打断其他Worker"这条能力的实际需求形状高度吻合，但注意：**不需要Agent之间也互相可见彼此的消息**（AgentTeams的设计是Agent和人类共处一室、Agent之间也能看见彼此），Matbox这里真正需要的是"人类可见多个Agent，Agent之间不需要互相可见"——这是一个比AgentTeams原始设计**更窄**的需求，落地时不需要照搬AgentTeams的"所有参与者对等可见"这条完整语义。

### 1.4 判断：与`专项00f`的关系，不是替代，是新增一层不同粒度的可见性

`专项00f`已确认"看板模式（目标→任务→子任务）优于纯聊天记录"，解决的是"**一个人类怎么看清一个AI员工的单次任务进展**"。本报告第1.3节子场景B要解决的是"**一个人类怎么同时看清多个AI员工/多个任务的全局状态，并能对其中任何一个单独干预**"——这是任务粒度之上的**项目/会话粒度**，两者不冲突，是可见性层级的两个不同缩放级别（zoom level），如同"看单个任务详情页"和"看项目仪表盘"是同一套数据的两种视图，不是互斥的设计选择。

**结论**：用户"好几个AI员工一起干活、人还能实时看着"这个判断，**在"顺序委派链条本身"这个层面证据不支持**（行业真实做法是接力式system-to-system对接，不是共享房间），**但在"人类同时监督多个并发运行的AI员工/项目"这个层面证据支持**——这是一个真实、此前确实没有被`F-DELEGATION-001`/`专项00f`/`F-CONSOLE-001`覆盖的缺口（`F-DELEGATION-001`管委派链条的安全语义，不管"人怎么看全局"；`专项00f`管单任务的指令/进度；`F-CONSOLE-001`的Control Tower是管理员治理视角的汇总仪表盘，是历史/统计聚合，不是"正在发生的多个任务实时并发监督"）。第2节梳理这个空白具体卡在哪。

---

## 2｜与Matbox现有架构的关系梳理——空白具体在哪

逐一核对本报告任务要求核查的4份文档，确认第1.4节识别的空白确实不被任何已有模块覆盖：

| 已有模块 | 管的是什么 | 是否覆盖"人类同时监督多个并发AiTask" |
|---|---|---|
| `F-DELEGATION-001`（委派） | AI员工之间点对点委派的**安全语义**（权限收窄、预算传递、深度熔断、循环检测） | 否——这是委派*应不应该发生*、发生后*会不会失控*的问题，不涉及人类怎么"看"这条链条正在发生什么 |
| `F-ORCHESTRATOR-001`（编排） | 一句话进来该路由给谁、要不要拆解/协作（Coordinator做fan-out/fan-in） | 否——Coordinator决定"要不要"多员工协作并发起，但发起之后人类怎么实时看这几个并发分支各自的状态，本文档没有设计 |
| `专项00f`（指令交互流程） | 单个人类指挥单个AI员工做**一个任务**的指令捕获+看板式进度可见 | 否——文档第1.2节明确排除"多个AI员工互相协作、人类同时监督"场景，本报告任务简报本身也是这么定性的 |
| `F-CONSOLE-001`（管理台，含Control Tower/CONSOLE-F005） | 企业管理员的**治理**视角——雇佣、训练、质检、成本、五支柱汇总，数据来源是F-AIEMP-001/F-COST-001/F-OBS-001等**历史/统计**数据的投影 | 否——Control Tower是"最近发生了什么、整体健康度如何"的仪表盘，不是"现在正在跑的这几个AiTask，每一步实时发生了什么，我要不要现在插一句话"这种**正在进行时**的监督需求 |
| `F-SUPERVISOR-001`（输出监督层） | AI员工**单条输出内容本身**发出前的policy/scope检查（fail-closed） | 否——这是内容安全层，跟"人类看多个任务的全局进度并插话"是完全不同的问题（本报告任务简报要求核查的"人类监督机制"实际上是这一层+`F-CONSOLE-001`的CONSOLE-F003质检中心，两者都不是本报告要解决的问题） |

**确认结论**：第1.4节识别的空白（人类同时监督多个并发AiTask、能对单个AiTask插话不打断其他AiTask）是一个真实的、此前所有已有模块都没有覆盖的缺口，不是重复设计。

---

## 3｜技术对接方案

### 3.1 新Feature设计：`F-COLLAB-001`（协作会话/多任务并发监督视图）

**定位**：一个**只读聚合投影层**，不新增执行/委派/权限语义，本质上是"把同一个项目/订单下的多个`AiTask`聚合到一个视图，供人类同时监督+单独插话"。这条设计原则参照`F-CONSOLE-001`第1条不可变原则（"不重新存一份AI员工的业务数据，全部通过已有模块API聚合展示，禁止两份真相"）和`F-VIZ-006`已验证的"事件订阅复用已有队列，不新建第二套队列"套路——`F-COLLAB-001`是同一类模块（聚合投影+复用已有实时通道），不是新发明一种架构模式。

**是不是`AiTask`之上的一层可见性聚合，还是独立新实体**：是前者。`CollaborationSession`本身**不是**执行实体，不驱动任何AI员工的实际执行，纯粹是"把哪些`AiTask`归到同一个人类监督视图里"这个分组关系+对应的聚合事件流。

### 3.2 核心数据Contract（逻辑模型，供后续正式开发文档细化）

```
CollaborationSession
  sessionId, tenantId, projectRef?（可选关联客户订单/项目编号，业务侧自定义）,
  memberTaskIds[]（关联的AiTask.taskId列表，可以是F-ORCHESTRATOR-001 Coordinator
                   fan-out时自动创建，也可以是人类手动把多个已有AiTask加入同一个session）,
  humanParticipantIds[]（有权限查看/插话的人类用户），
  state(ACTIVE|CLOSED), createdAt, closedAt?

CollaborationEvent（聚合事件，只读投影，不持久化第二份AiTaskEvent，
                     实时转发已有的AiTaskEvent流，按sessionId聚合）
  eventId（复用源AiTaskEvent.eventId）, sessionId, sourceTaskId, sourceEventType,
  actorId, payload, occurredAt
```

**API端点（最小集合，草案）**
- `POST /collab/sessions` — 创建一个协作会话，传入初始`memberTaskIds[]`
- `POST /collab/sessions/{sessionId}/members` — 追加一个已有`AiTask`到会话（如中途发现需要拉另一个AI员工进来）
- `GET /collab/sessions/{sessionId}` — 查询会话当前状态+成员任务列表
- `GET /collab/sessions/{sessionId}/events/stream` — 实时事件流（SSE/WebSocket，聚合转发成员任务的`AiTaskEvent`，参照`F-VIZ-006`的`GET /viz/events/stream`同款设计，按`EventID`/`occurredAt`重放防止断线丢事件）
- 人类对某个成员任务插话/接管：**不新增API**，直接调用该`taskId`已有的`POST /task/{taskId}/instructions`（轻量追加）或`POST /task/{taskId}/takeover`（重量级接管），`F-COLLAB-001`前端只是把这两个已有端点包在会话视图里，按`taskId`路由，不代理/不重新实现这两个动作的业务逻辑。

**与`F-DELEGATION-001`的边界**：完全正交、互不侵入。如果`memberTaskIds`里的某几个`AiTask`背后确实存在委派关系（比如A员工把任务一部分委派给B员工，B自己也在跑一个`AiTask`），委派的权限收窄/预算传递/循环检测逻辑照常在`F-DELEGATION-001`内部发生，`F-COLLAB-001`不关心、不改变这层安全语义，只是恰好把这两个`AiTask`一起放进同一个人类监督视图。如果`memberTaskIds`里的几个`AiTask`之间根本没有委派关系（各自独立被`F-ORCHESTRATOR-001`路由创建，只是恰好服务同一个客户项目），`F-COLLAB-001`一样能工作——它不依赖委派关系存在，只依赖"人类想把哪些任务放进同一个监督视图"这个分组意图。

### 3.3 Matrix协议是否复用——核查结论（本报告新查证，非复用00j旧结论）

用GitHub API直接核查Java/Kotlin生态的Matrix协议实现现状（2026-09-02）：

| 候选 | 语言 | Star | 状态 | 结论 |
|---|---|---|---|---|
| `matrix-org/matrix-java-sdk` | — | — | **不存在**（官方组织下没有这个仓库） | matrix.org官方从未提供过Java SDK |
| `matrix-org/matrix-android-sdk` | Java | 365 | **已归档（archived），最后更新2022-02**，官方标注DEPRECATED | 曾经最接近的候选已经死亡4年 |
| `Cosium/matrix-communication-client` | Java | 47 | 活跃（最近push 2026-08-24），MIT | 规模太小，第三方个人/小团队维护，无法验证是否支撑过生产级多房间并发场景 |
| `benkuly/trixnity` | Kotlin（Multiplatform，含JVM目标） | 49 | 活跃（最近push 2026-09-01），Apache-2.0 | 同样规模很小，是目前查到**相对最活跃**的候选，但49星、真实生产验证案例未查到，不足以让Matbox把核心协作可见性层的技术依赖压在它身上 |

**结论**：Java/JVM生态里没有一个够格的、成熟的Matrix协议实现——这不是"因为Matbox坚持Java单语言栈所以主观排除"，是**客观查证后确认这条技术路线本身在Java生态里就没有成熟选项**，即便Matbox愿意为这一个模块破例引入JVM兼容的Kotlin库（Trixnity），也是把核心协作层的可靠性押注在一个49星、缺乏生产验证的项目上，风险和收益不成比例。

**协议模型本身的适配性问题**（独立于有没有SDK）：Matrix协议的核心假设是"客户端与服务端之间的sync长连接/长轮询是房间状态（成员、消息时间线、权限等级）的真相来源"，这与Matbox`F-TASK-001`已经写入正式文档的不可变原则第1条——"不让HTTP长连接承载业务任务，任务状态必须能在客户端断线重连后从服务端真实状态补齐，不依赖前端内存"——在设计哲学上是**两条不同的路**。Matbox已经确认的路线是"业务状态永远以服务端持久化记录为准，连接只是获取状态的一种方式、随时可断可重连"，Matrix房间模型则更接近"房间本身是一个需要持续同步的有状态会话"。采用真实Matrix协议意味着要在Matbox已经统一的状态管理哲学之外，为这一个模块单独引入一套不同的状态一致性模型，这是额外的架构复杂度，不是免费的。

### 3.4 实时通道怎么做——复用`F-VIZ-006`先例，不引入新基础设施

Matbox在`F-VIZ-006`（代码问题定位与人工修复台Realtime模块）里**已经有一个成熟、经过正式开发文档确认的先例**：`GET /viz/events/stream`——SSE/WebSocket网关，转发`F-QUEUE-001`（Temporal）的事件，按`EventID`/`occurredAt`排序重放，断线重连不丢事件、不乱序（对应`VIZ-T04`验收测试）。

`F-COLLAB-001`的`GET /collab/sessions/{sessionId}/events/stream`应该走**同一套模式**：网关层转发的是`AiTaskEvent`（来自F-TASK-001所在的Temporal基础设施，同样通过`F-QUEUE-001`共享的物理部署），聚合逻辑是"把`memberTaskIds`范围内多个任务的事件流合并成一条时间线"，技术形态（SSE/WebSocket网关+按EventID重放）直接复用`F-VIZ-006`已验证的设计，不需要为这个模块另起一套实时推送基础设施，更不需要Matrix。

### 3.5 人类干预语义——复用RBAC，不移植Matrix的"Power Level"

AgentTeams用Matrix协议自带的"power level"机制控制房间内谁能做什么（README/commit记录里的"grant Matrix power levels to human members on room join"）。Matbox不需要移植这套机制——`humanParticipantIds[]`里谁能对哪个`taskId`插话/接管，直接复用`F-TENANT-001`已有的RBAC（EmployeeOwner管自己名下AI员工、Operator管被授权范围内的AI员工），`F-COLLAB-001`只是在展示层把这些已有权限判断应用到"能不能在这个会话里对某个任务插话"这个具体动作上，不新建平行的权限模型。

---

## 4｜License/技术栈交叉核实（2026-09-02，与`专项00j`同日复核）

用GitHub API重新直查`agentscope-ai/AgentTeams`（与00j报告同一天核查，用于验证00j结论是否存在漂移，结果：**无漂移，结论一致**）：

| 指标 | 本报告核查值（2026-09-02） | `专项00j`记录值 | 是否一致 |
|---|---|---|---|
| Stars | 5,537 | 5,537 | 一致 |
| Forks | 678 | 678 | 一致 |
| License | Apache-2.0 | Apache-2.0 | 一致 |
| 主语言 | Go（2,647,019字节）+ Python（2,070,468字节）+ Shell（1,534,291字节）+ PowerShell/Ruby/Makefile/Dockerfile/Go Template | Go为主+Python+Shell | 一致，本报告补充了具体字节数分布 |
| 最近push | 2026-08-22T00:13:12Z | 2026-08-22 | 一致 |
| Open issues | 244 | 244 | 一致 |
| Issue总数（含历史） | 455 | — | 新查证：说明累计issue量级健康，不是刚起步的小项目 |
| PR总数（含历史） | 744，最新编号#1197（`[codex] prepare v1.2.3 installer fallback`） | "issue编号已破1200" | 基本一致（00j说的是issue+PR混合编号，本报告分别核查确认PR编号确实连续排到#1197+） |
| 贡献者结构 | `johnlanni`442、`shiyiyue1102`93、`Jing-ze`43、`max-wc`34、`googs1025`33、`github-actions[bot]`16 | 同一批贡献者，数字一致 | 一致，多人真实协作结构未变 |
| Homepage | `https://www.aliyun.com/product/agentteams` | 同 | 一致，阿里云官方产品背书未变 |

**结论**：`专项00j`对AgentTeams的评估在本报告复核当天（同一天）**完全没有发现任何数据漂移或结论需要修正的地方**，AgentTeams确实是一个真实、被真实机构（阿里）投入、多人健康协作维护的项目，"值得认真对待其设计模式"这个判断本身站得住——但这不改变第3.3节的结论：值得认真对待的是它的**设计模式**，不是它的**代码/协议本身**能被Matbox直接采纳。

**与Matbox架构原则的冲突（复述已反复验证的红线，不构成新发现）**：Go+Python技术栈与架构原则第33条"Java单语言栈"直接冲突，与`专项28`否决LangGraph/CrewAI、`专项00j`否决Distilly（Python）、`专项00e`否决cumora（TypeScript）是同一条已经反复验证过的红线，AgentTeams不构成例外。

---

## 5｜PASS/USE/REFERENCE判断

| 对象 | 判断 | 理由 |
|---|---|---|
| AgentTeams的代码本身（Go controller、Python worker runtime等） | **PASS** | Go+Python与Java单语言栈原则冲突（架构原则第33条），不可引入 |
| Matrix协议本身（作为Matbox要采用的通信协议） | **PASS** | 第3.3节查证：Java生态无成熟SDK（官方无Java SDK、`matrix-android-sdk`已归档、第三方候选均<50★缺乏生产验证）；协议的长连接/sync状态模型与`F-TASK-001`已确认的"业务状态不依赖长连接、服务端可重建"设计哲学存在方向性冲突 |
| K8s + Higress + MinIO + Tuwunel的整体基础设施架构 | **PASS** | 这是AgentTeams自己的部署形态，与Matbox已有的Temporal/F-QUEUE-001基础设施是两套不同体系，没有必要平行引入第二套 |
| "共享可见性会话+人类可对单个Agent插话不打断其他Agent"这条设计模式 | **REFERENCE** | 值得作为`F-COLLAB-001`的设计参照，但落地时用Matbox自己的Java技术栈、复用`F-TASK-001`（AiTask/AiTaskEvent/`/instructions`/`/takeover`）+`F-QUEUE-001`+`F-VIZ-006`同款SSE/WebSocket网关模式重新实现，不移植AgentTeams的任何代码 |
| Worker checkpoint/intervention history端点的设计思路（`#1186 add intervention history and worker checkpoint read endpoints`） | **REFERENCE** | Matbox已有对应的数据基础（`AiTaskStep.checkpointId`、`AiTaskEvent`的`TAKEOVER`/`INSTRUCTION_APPENDED`事件类型），`F-COLLAB-001`的"下钻到某个任务干预历史"功能可以直接从已有数据投影，不需要参照AgentTeams的具体接口形态 |
| Matrix的"Power Level"权限模型 | **PASS（不移植）** | 直接复用`F-TENANT-001`已有RBAC，不新建平行权限体系 |

**没有USE档位适用**：AgentTeams没有任何一个组件处于"可以直接拿来用、只需要少量适配"的状态——语言栈、协议模型、部署形态三个层面都与Matbox已确认的架构方向不兼容，只有"设计模式"这个抽象层面的价值可以迁移，这决定了它只能是REFERENCE，够不到USE的门槛。

---

## 6｜给Matbox的具体建议 & 遗留给用户拍板的问题

### 6.1 建议现在做的事

1. **`F-COLLAB-001`的结构设计现在就可以定稿**（不依赖真实生产流量，跟`F-ORCHESTRATOR-001`当初"Registry+Classifier+Coordinator不依赖真实流量能设计对"是同一类判断）——`CollaborationSession`聚合模型、复用已有`/instructions`/`/takeover`端点、复用`F-VIZ-006`同款SSE/WebSocket网关模式这几条架构决定，逻辑上不需要等真实客户数据。
2. **需要先确认第1.2节指出的边界**：如果用户后续要基于"设计→报价→生产排产→物流"这条完整链条来验收`F-COLLAB-001`的设计，需要先确认Matbox是否真的会把"生产排产""物流跟踪"这两类岗位纳入AI员工岗位族——如果不纳入（Matbox定位停留在品牌市场/设计支持侧，不下探到工厂ERP层），`F-COLLAB-001`的典型使用场景会更偏向"内容运营+设计支持+客户运营+成本监督"这几类岗位在同一个客户项目上的并发协作，而不是完整供应链链条，这直接影响后续正式开发文档里给的示例场景是否准确。

### 6.2 不建议现在做的事（按架构原则第27条"没有真实需求不提前建复杂"）

1. **不建议现在就实现真实的多方"Agent互相可见彼此消息"能力**——第1.3节已论证，Matbox真正的需求是"人类可见多个Agent"，不是"Agent之间也互相可见"，后者是AgentTeams原始设计里更复杂的一部分，Matbox没有证据显示需要它，强行照搬只是徒增复杂度。
2. **不建议现在决定`F-COLLAB-001`要不要做成真正的"低延迟实时会话"体验**（比如打字气泡、亚秒级刷新）——第3.4节的SSE/WebSocket网关方案技术上可行，但延迟目标、UI具体形态（类似AgentTeams的Element Web聊天室视图，还是更偏Matbox已有的任务看板叠加视图）是产品优先级判断，不是研究能替代的决定。

### 6.3 遗留给用户拍板的问题

1. **`F-COLLAB-001`的命名与优先级**——本报告只给出结构设计草案，具体要不要现在转WorkPackage、排在哪个Stage，需要用户结合当前AI员工岗位族的实际并发协作真实需求（是否已经有客户/内部沙盘验证过"一个项目真的会有2个以上AI员工同时在跑"这种场景）来判断，本报告的证据支撑"值得设计"，但"现在就做还是记录留待以后"仍是范围/时机判断。
2. **`CollaborationSession`的归属/创建方**——是`F-ORCHESTRATOR-001`的Coordinator在fan-out时自动创建（技术上更省事，但会让Orchestrator承担一部分"UI层"职责），还是由前端/人类在需要的时候手动组建（更灵活，但需要人类自己判断"这几个任务该不该放一起看"）——这是本报告没有代为决定的具体设计选择，需要在`F-COLLAB-001`正式开发文档阶段确定。
3. **第1.2节指出的岗位族边界问题**——是否需要在`F-AIEMP-001`未来迭代中评估是否纳入"生产排产""物流跟踪"这类更偏工厂ERP层的岗位族，这本身是一个独立于`F-COLLAB-001`的产品范围判断，本报告不越权代为决定，只如实标注这条边界会影响多AI员工协作场景的真实丰富度。

---

## 7｜方法论如实说明

- 第1.1节家具定制行业工作流的证据来自英文行业资料（家具APS/MES/WMS集成研究、家具定制商业流程指南），本报告未找到专门针对**中国**家具制造行业本土化流程（如是否存在与欧美不同的排产/物流习惯）的独立中文信源交叉验证，如实标注为局限——但"设计→报价→生产→交付"这个大的阶段划分是行业通用逻辑，不因地域出现根本性差异的可能性较低，本报告判断不影响核心结论，但如实标注未做中文原生信源交叉核实这一层（不同于`专项00j`对Distilly做过的中英文双重核查深度）。
- 第3.3节Java Matrix SDK候选核查覆盖了GitHub搜索能发现的主要候选（官方SDK、曾经的Android SDK、两个第三方Java/Kotlin实现），但不排除存在本报告搜索未覆盖到的、更小众但可能更成熟的候选，如实标注这条局限——但即便存在，47-49★级别是本次搜索能找到的最高热度第三方候选，判断"Java生态无成熟Matrix SDK"这个方向性结论不太可能被推翻。
- 第1.2节"Matbox当前岗位族不覆盖生产排产/物流"这个判断基于`F-AIEMP-001`文档已确认的岗位族清单，如果用户手上有本报告未看到的、更新的岗位族规划（尚未写入正式文档），这条边界判断需要重新核实，本报告只能依据已落笔的正式文档下结论。

---

## 附录：来源

**AgentTeams一手来源（GitHub API直查，2026-09-02，与`专项00j`同日复核）**：
- 仓库元数据：https://api.github.com/repos/agentscope-ai/AgentTeams
- 语言分布：https://api.github.com/repos/agentscope-ai/AgentTeams/languages
- 贡献者：https://api.github.com/repos/agentscope-ai/AgentTeams/contributors
- 近期commit：https://api.github.com/repos/agentscope-ai/AgentTeams/commits
- Issue/PR总量：`https://api.github.com/search/issues?q=repo:agentscope-ai/AgentTeams+type:issue`、`type:pr`
- 阿里云产品页：https://www.aliyun.com/product/agentteams

**Java/Kotlin Matrix SDK生态核查（GitHub API直查，2026-09-02，本报告新查证）**：
- 官方组织仓库列表：https://github.com/orgs/matrix-org/repositories （确认无`matrix-java-sdk`）
- `matrix-org/matrix-android-sdk`（已归档）：https://api.github.com/repos/matrix-org/matrix-android-sdk
- `Cosium/matrix-communication-client`：https://api.github.com/repos/Cosium/matrix-communication-client
- `benkuly/trixnity`：https://api.github.com/repos/benkuly/trixnity
- Matrix.org官方SDK列表页：https://matrix.org/ecosystem/sdks/

**家具定制行业真实工作流依据（2026-09-02 WebSearch，本报告新查证）**：
- APS/MES/WMS集成研究：ScienceDirect《Investigation of the customized furniture industry's production management systems》
- 智能排产系统：MDPI《Enhancing Efficiency in Custom Furniture Production with Intelligent Scheduling Systems》
- 定制家具流程/时间线：MakersRow、PM Furniture、Rustic Red Door、FOH Furniture、New Gill Furniture等多篇行业资料交叉参照（均指向"需求澄清→报价→生产/物流"分阶段checkpoint模式，细节表述一致）

**Matbox内部交叉引用**：
- `docs/技术选型报告/Matbox_专项00j_Distilly与AgentTeams专项评估_2026-09-02.md`（AgentTeams首次评估，本报告第4节复核其数据未漂移）
- `docs/技术选型报告/Matbox_专项00f_AI员工指令交互流程设计_2026-09-02.md`（看板模式结论、单任务指令交互设计，本报告第1.4/2节确认与之互补不冲突）
- `docs/Matbox_AI员工委派_正式开发文档_V1.0-RC.md`（F-DELEGATION-001，委派安全语义，本报告第1.3/3.2节确认与`F-COLLAB-001`正交）
- `docs/Matbox_中央编排层_正式开发文档_V1.0-RC.md`（F-ORCHESTRATOR-001，Coordinator fan-out/fan-in，本报告第3.2节讨论`CollaborationSession`的成员任务来源）
- `docs/Matbox_AI任务运行时_正式开发文档_V1.0-RC.md`（F-TASK-001，AiTask/AiTaskEvent/`/instructions`/`/takeover`已有能力，本报告确认`F-COLLAB-001`可直接复用而不需新增执行语义；第3.3节引用其不可变原则第1条论证Matrix协议模型冲突）
- `docs/Matbox_AI员工管理控制台_正式开发文档_V1.0-RC.md`（F-CONSOLE-001，本报告第2节确认Control Tower是历史/统计聚合，不覆盖"正在进行时"的多任务监督需求）
- `docs/Matbox_输出监督层_正式开发文档_V1.0-RC.md`（F-SUPERVISOR-001，本报告第2节确认这是内容安全层，与本报告讨论的"多任务监督"是不同问题）
- `docs/Matbox_AI员工身份_正式开发文档_V1.0-RC.md`（F-AIEMP-001，2.3节初始岗位族，本报告第1.2节据此确认岗位族边界）
- `docs/技术选型报告/Matbox_专项07_任务队列_技术选型与开发交接报告_2026-08-30.md`、`docs/技术选型报告/Matbox_专项02_代码问题定位与人工修复台_技术选型与开发交接报告_2026-08-30.md`（F-VIZ-006 Realtime模块的SSE/WebSocket网关+F-QUEUE-001事件订阅设计先例，本报告第3.4节据此确定`F-COLLAB-001`实时通道方案）
- `docs/Matbox_架构设计原则.md`第27条（无真实需求不提前建复杂）、第33条（Java单语言栈原则）
