# Matbox 专项00i｜OpenWorker（andrewyng/openworker）专项评估

技术选型报告 · V1.0 · 2026-09-02

**DocID**: MATBOX-OPENWORKER-TECHSELECT-20260902-V1.0
**审计对象**: [github.com/andrewyng/openworker](https://github.com/andrewyng/openworker)（2026-09-02 API直查：**17,177 stars / 2,398 forks / 451 open issues**，MIT，2026-07-20创建，2026-08-31仍有push，作者Andrew Ng + 联合创始人Rohit Prasad）
**报告性质**：聚焦影响评估报告，不是新模块技术选型——核查该候选对Matbox**已完成**的专项28（Agent Runtime）、专项00f（AI员工指令交互流程设计）、F-ACTION-001（Action网关）三个模块/文档的具体影响，不产生新FeatureID，不改变任何已冻结架构决策。
**触发背景**：OpenWorker的产品定位（"不只是聊天，而是交付完成的工作"）与Matbox架构原则第41条（2026-09-02刚确认，参照OpenAI Work模式、不做纯聊天驱动）在叙事层面高度重合，且其"4类工具风险分级"与F-ACTION-001的10步Enforcement Pipeline是同一类问题的两种解法，值得逐条核实是营销措辞还是真实工作机制。方法论沿用专项00c/00d已确立的标准：不是有星就行、有名人背书就行，要看真实源码、真实issue、真实第三方讨论。

---

## 0｜给忙碌读者的结论摘要

1. **三个宣传点逐一核实：规划/执行机制、4类风险分级、"不止聊天"的定位，三个都是真实工作的机制，不是营销话术，但每一个都比宣传材料呈现得更粗糙、且都能在Matbox已有设计里找到对应的更严谨版本。** 这不是"没做到位所以否决"——OpenWorker是一个真实、可运行、6周内拿到17K星的成熟工程项目（3,988个文件的Python+TypeScript+Rust代码库，非demo），本报告核实了它该拿的分，也如实指出它没有的东西。
2. **风险分级机制的真实细节比公开报道更细，且本报告发现代码库当前实际是5层不是4层**：报道口径统一是"read/write_local/exec/external"四层（[Marktechpost](https://www.marktechpost.com/2026/07/23/andrew-ng-just-released-openworker-an-open-source-local-first-desktop-ai-coworker-that-returns-finished-deliverables-instead-of-chat/)、[MoClaw](https://moclaw.ai/blog/what-is-openworker)等多篇独立报道口径一致），但本报告直接核实`coworker/risk.py`源码，当前`RiskClass`枚举实际是**READ / EGRESS / WRITE_LOCAL / EXEC / EXTERNAL共5个值**——`EGRESS`（"reaches the network — the request itself can carry data off-machine"）是报道未覆盖的一个更细粒度分层，本报告核查后判断这是该项目在真实SSRF类安全issue（见第2/3节）压力下后补的分层，**这本身是一条独立证据，证明"4层够用"这个说法连OpenWorker自己的维护者都在实践中推翻了**，与本报告第3节对Matbox blast-radius设计更细粒度的判断方向一致。
3. **真实、当前仍未修复的高危安全issue，比"451个open issue里没发现红旗"的快速扫描判断更严重**：本报告抽样核查到一批2026-08-19由同一名审计者（`ns-rajats`）提交的、代码级可复现的高/中危漏洞（approval审批流程可被"no, don't approve"这种否定句解析成同意执行——ALLOW判定fail open；跨IM通道审批绕过——Telegram能解锁Slack专属的审批项且能铸造永久授权），**截至报告完成时（提交后约2周）仍是0评论、未修复的open状态**——与另一条更早（7月26日）的同等严重程度RCE issue（#213，工作区级`.coworker/mcp.json`未做信任检查、clone一个仓库即可静默执行代码）4天内被联合创始人`rohitprasad15`亲自关闭修复形成对比，说明这个项目对安全issue的响应**不是稳定的"响应快"，是有真实的、当前存在的处理不均衡**。
4. **对Matbox的核心结论：`RiskClass`模型能对应F-ACTION-001 10步Pipeline里的"风险半径检查"这一步，但只是其中一步的粗粒度近似，不是整套Pipeline的替代，且OpenWorker真实踩过的坑（审批fail-open、崩溃后外部副作用重放#443、子代理粗暴降级而非权限交集收窄）恰好一一对应F-ACTION-001已经用更严谨方式设计过的P0规则（commit时重新鉴权、幂等去重、委派权限不放大）——这是一批高质量的"验证性反面案例"，不是"我们该学它"的案例。**
5. **China可达性核查结果与任务书假设相反，是一条需要更正的发现**：任务书假设OpenWorker"可能是西方模型为中心"，本报告直接核实`coworker/providers/registry.py`源码，发现**火山引擎Ark、智谱GLM（Z.ai）、月之暗面Kimi、阿里Qwen四家均已预置国际站+中国大陆双端点**（如Kimi同时注册`api.moonshot.ai`国际端点和`api.moonshot.cn`大陆端点），DeepSeek/MiniMax原生支持——供应商注册表本身对中国模型生态的覆盖不弱，**真实的缺口不在模型接入层，而在UI本地化层**：GitHub issue中有至少6条独立的"需要中文界面"请求（#191/#427/#478/#498/#537/#538），且截至核查时**均未合入**，说明中国开发者社群对这个项目有真实关注，但当前UI仍是纯英文，这是一条比"模型层面是否西方中心"更精确的China-fit判断，详见第4节。
6. **推荐**：**不整体采纳、不作为依赖嵌入，但作为"结构化任务输入+审批分级+人工检查点"这套产品模式的真实可运行参考实现，值得回填两条具体内容到专项00f和F-ACTION-001的正式文档**，具体怎么改见第6节，不是空泛的"值得参考"。

---

## 1｜技术本质核查：规划/执行机制是真实代码还是营销包装

### 1.1 代码库规模与结构：真实工程，非demo

直接核查`git/trees/main?recursive=1`确认：核心Python包`coworker/`下有**超过110个模块文件**，按职责清晰分层——`engine.py`（TurnEngine主循环）、`risk.py`（风险分级）、`permissions.py`（权限引擎）、`inbox.py`/`inbox_routing.py`（人工审批收件箱及解析）、`mcp/`（MCP client/config/oauth，4个文件）、`connectors/`（25+集成，含`gateway.py`统一入口）、`providers/`（8个供应商adapter：openai/anthropic/gemini/bedrock/vertex/codex，另有router.py统一路由）、`memory/`（含`sqlite_store.py`持久化记忆）、`personas/`、`teams/`（多代理协作，10个文件）、`tools/plan.py`/`tools/subagent.py`/`tools/todo.py`（规划/子代理/任务清单工具）、`automation/scheduler.py`（定时唤醒）、`unattended.py`/`selfwake.py`（无人值守心跳机制）。语言构成（`languages` API）：Python 3.40MB（主体）+ TypeScript 1.55MB（GUI）+ Rust 61KB（语音输入sidecar）+ HTML/CSS。**这不是一个包装ChatGPT API的薄壳demo，是一个有真实持久化、真实多进程/多transport（Slack/Telegram/GUI/CLI）架构的成熟工程项目**。

### 1.2 规划机制的真实实现：事件驱动的人工检查点，不是结构化Plan/Step数据模型

核查`coworker/tools/plan.py`源码确认：规划工具`propose_plan(plan: str)`本质是**一个被TurnEngine拦截的特殊工具调用**——Agent探索完成后调用它，传入一段自由文本摘要（"summarize what you'll change, in which files, and how you'll verify it"），TurnEngine捕获这次调用后**发出`PLAN_PROPOSED`事件、暂停执行、等待用户out-of-band的批准/拒绝决定**；批准后"flips the live PermissionEngine out of plan mode"进入真正执行，拒绝则把反馈喂回去让Agent重新规划。

**这个机制是真实、能工作的人工检查点闭环，但不是结构化的任务分解算法**——没有查到任何`Plan`/`Step`类或结构化的子任务数据模型，"计划"本质是一段LLM生成的自由文本，由人类肉眼判断是否合理后放行，不是把目标机器可读地拆解成有依赖关系的步骤图。**对比Matbox已有设计**：专项28 Agent Runtime的`AiTaskStep`是结构化持久化实体（有`stepIndex`/`status`/关联的`ReasoningTurn`），TASK-F001状态机、TASK-F008自我纠错闭环都建立在这个结构化模型之上；OpenWorker的"plan"更接近一次性的人工审阅关卡，不具备Matbox已经设计好的"按step逐个track执行/失败重试/中途插入"能力。**结论**：OpenWorker验证了"人工确认计划后再放手执行"这个交互模式在生产中确实可行、确实被真实使用者接受，但它的实现深度不如Matbox自己已经设计的`AiTaskStep`模型，不构成"应该学它怎么拆解任务"的理由。

### 1.3 执行循环与"不止聊天"定位的真实性

`TurnEngine`（`coworker/engine.py`）承载多轮"调用模型→解析tool_use→按风险分级决定是否需要人工批准→执行→回填结果→继续"的循环，与Matbox专项28 RUNTIME-F002描述的通用Agent循环结构一致（模型厂商无关，供应商层已抽出到`providers/`，与Matbox F-PROVIDER-001的`invoke()`统一入口思路相同）。"不止聊天"这个定位在实现上体现为：会话本身仍是对话式session（保留上下文/多轮追问能力），但**产品UX刻意把"最终产出一个可用交付物"作为默认预期**（文档摘要、发送到Slack的消息、更新的日历事件），而不是把模型的最后一句回复当作结束态——这与Matbox架构原则第41条"结构化任务输入+可跟踪执行过程+交付真正的成果物"方向一致，是一条独立收敛证据（详见第5节评估表）。

**但需要澄清一个容易被误读的地方**：OpenWorker并没有放弃"聊天"这个交互形态本身（依然是session式对话），它反对的是"纯聊天+把最后一条回复当结果"，而不是反对对话式交互——这与专项00f第3.1节引用的研究结论（"聊天框结构性失败"指的是不透明+二元控制+无状态可见性，不是"不能用自然语言输入"）是同一个精确区分，两个独立信源指向同一个结论，互相印证。

---

## 2｜真实用户证据：比451个issue的快速扫描更深一层

### 2.1 GitHub Issues深度抽样：一批未修复的高危安全问题（本报告核心新发现）

抽样近50条issue（按创建时间及按评论数两种排序各取样，非只看热度前5），发现一组**2026-08-19由审计账号`ns-rajats`提交、标注"Found during a SAST review (verified reachable call paths only)"的连续11个issue（#516~#527）**，均给出具体文件行号和可复现调用链，性质是真实代码审计发现，不是猜测：

- **#520（严重度Medium）：审批回复解析器把否定句解析成同意** —— `_ALLOW_WORDS`先于`_DENY_WORDS`匹配，回复`"no, don't approve"`因为字符串里含`approve`被判定为`allow`，且`InboxStore.resolve`是一次性生效，误判无法挽回，**审批网关在这个场景下是fail open而不是fail closed**。
- **#519（严重度High）：跨IM通道审批绕过** —— owner身份校验只在`platform == "slack"`时生效，Telegram回复可以解锁绑定在Slack上的审批项且完全跳过owner校验；更严重的是消息通道能接受的回复词汇表比按钮宽——自由文本里的`always`/`always_tool`等词会被解析成**永久授权**（而不只是一次性批准），且目录授权JSON里的`path`/`writable`字段可被攻击者指定，等价于让一个只能"批准一次"的审批人意外拿到"永久授予任意可写目录"的权限。
- **#213（已修复）：工作区级配置文件未做信任检查，clone仓库即可静默RCE** —— `<repo>/.coworker/mcp.json`会在session打开、**任何消息/工具调用/审批之前**被合并进MCP配置并spawn其`stdio`server，`WorkspaceTrustStore`机制虽然存在（且已经在拦截`allowed_commands`）但**这条路径完全没有接入**；复现证明恶意配置甚至不需要完成合法的MCP握手就能执行payload。提交于7月26日，**4天内被联合创始人`rohitprasad15`亲自关闭修复**，是响应快的正面案例。
- **#100（仍open）：`web_fetch`无SSRF防护** —— 该工具被分类为低风险READ、无需审批，但实际执行不限制loopback/私网/link-local地址且跟随重定向，"An attacker who influences a model turn (e.g. via connector content / prompt injection) can read cloud instance metadata"——**这条issue本身就是"READ=无副作用"这个假设不总成立的真实反例**，直接支撑第3节的比较论点。7月24日提交，8月25日仍在更新讨论但未合入修复。
- **#443（仍open）：崩溃后可能重放已批准的外部副作用** —— 审批状态先于执行结果被持久化，若在外部调用成功但结果尚未写入checkpoint前进程崩溃，durable resume会把这次调用当作"未完成"重新执行，导致邮件等外部动作被**重复发送两次**，issue作者已用故障注入测试确定性复现（`deliveries == 2`），并给出了完整的"at-least-once"到"精确恢复语义"改造方案待维护者对齐。

**截至本报告完成时（2026-09-02，即#516~#527提交后约2周），这一批issue全部保持0评论、open状态**，与#213的4天修复速度形成明确对比。

### 2.2 中国用户的真实、独立提出的诉求（本报告新增，任务书未预判到具体内容）

- `#191`（标题直接是中文"需要中文"）、`#427`（"Lack of Simplified Chinese support and missing DeepSeek context integration"，提出者明确说明愿意贡献PR）、`#478`（"中文汉化和skill界面"）、`#498`（"develop a user-friendly interface for the Chinese market?"）、`#537`（"I've created a Chinese localization for personal use"——已有用户自制本地化但未合入官方）、`#538`（"Add Simplified Chinese (zh-CN) UI localization"）——**6条独立提出的中文本地化诉求，跨越项目生命周期从早期(#191)到近期(#538)持续出现，且有用户已经自行做了本地化仍未被合并**，说明中国开发者对这个项目有真实、持续的关注和使用尝试，当前唯一的短板在UI层不在模型接入层（详见第4节）。
- `#231`：真实的Bug报告——"Active API keys obtained from Qwen Cloud fail to authenticate"，反映即便供应商registry里已经预注册了Qwen端点，实际认证流程仍有真实的、当前未修复的连通性问题，不能假设"registry里有=能直接用"。

### 2.3 第三方独立评测（非本报告首次核实，作为交叉印证）

第三方评测站点`openworker.site/review/`（"OpenWorker Review 2026 — Honest Test After 100+ Tasks"）给出8.1/10的"qualified positive"结论：认可邮件分类、日历优化、跨HubSpot+邮件生成客户简报（"under 30 seconds"）等场景的真实可用性，认可"the most sophisticated permission system we have seen"；但明确记录**"complex multi-step tasks with 5+ tool calls can fail silently if intermediate steps produce unexpected results"**（多步任务在中间步骤出问题时会静默失败，缺乏清晰的错误上报）、本地Ollama模型质量明显低于云端模型、macOS首次启动有Gatekeeper摩擦、无内建任务调度UI。**这条"5+工具调用的多步任务可能静默失败"的独立评测发现，与#443（崩溃后外部副作用可能重放）、#520/#519（审批解析可能出错且无法挽回）三条证据方向一致**——都指向"多步、有真实副作用的执行链路，在异常路径上的健壮性不如宣传材料给人的印象"，不是孤证。

### 2.4 HN/Reddit真实讨论：核查后发现讨论热度远低于"Andrew Ng发布通常引发大量讨论"这个预期

直接查询HN Algolia API（`hn.algolia.com/api/v1/search?query=OpenWorker&tags=story`）核实：与"andrewyng/openworker"直接相关的HN帖子共3条——[`openworker.com`](https://news.ycombinator.com/item?id=49027382)（5分，0评论）、[Andrew Ng Launches OpenWorker](https://news.ycombinator.com/item?id=49027225)（转发Twitter链接，2分，0评论）、["Andrew Ng made an open source agent"](https://news.ycombinator.com/item?id=49032886)（2分，2评论）。**第三条的完整评论内容如实记录**：唯一两条评论是"How is it different from literally any other wrapper?"和作者本人的回复"IDK, and it only uses Slack. Just wanted to show the community about this (and how bad it is lol)."——**这与任务书"Andrew Ng发布的HN讨论通常很扎实"的预设假设不符，本报告如实更正**：OpenWorker并未在HN上引发实质性技术讨论，热度和评价均低于预期，唯一的真实评论是质疑其与同类"wrapper"产品的差异化程度。Reddit方向核查`r/LocalLLaMA`/`r/MachineLearning`亦未找到专门讨论OpenWorker的独立帖子（搜索只返回项目本身的通用报道链接，非社区自发讨论帖）。**这条"发现讨论热度不如预期"本身是一条有信息量的负面证据**：17K星的增速主要来自Andrew Ng个人的传播效应（Twitter公告），而非社区自发的技术圈层讨论扩散，这与专项00c/00d里对"star数≠社区认可深度"的一贯判断标准一致。

---

## 3｜4类（实际5类）风险分类详解，与F-ACTION-001 10步Enforcement Pipeline逐点对比

### 3.1 OpenWorker风险分类的真实代码细节

核查`coworker/risk.py`确认`RiskClass`枚举定义：

```python
class RiskClass(str, Enum):
    READ = "read"                # 无副作用 — 始终允许
    EGRESS = "egress"             # 触网 — 请求本身可能携带数据离开本机
    WRITE_LOCAL = "write_local"   # 修改工作区 — 路径限定+模式门控
    EXEC = "exec"                 # 执行命令 — 模式门控
    EXTERNAL = "external"         # 本机以外的副作用 — 触发无人值守收件箱钩子
```

分类逻辑`classify()`是一套优先级链：①内建工具硬编码映射（`write_file`→WRITE_LOCAL，`run_shell`→EXEC，`web_fetch`→EGRESS）②用户可以**收紧**但不能放松内建write/exec/egress工具的分级（可以把一个工具判得更严，不能判得更松）③连接器目录里的写操作默认下限是EXTERNAL且不可调低④标注`requires_approval=True`的工具默认落EXTERNAL⑤兜底默认READ。`is_consequential()`函数是审批触发开关——除READ外全部需要经过PermissionEngine。五种权限模式（discuss/plan均只读、interactive默认逐次询问、auto在限定路径内全自动、custom可白名单特定工具）叠加在这5个风险类之上，决定"审批要不要问、问了要不要一直问"。

**一条本报告主动核查出的细节，公开报道未覆盖**：`web_fetch`当前被硬编码归类到`EGRESS`而非`READ`，但2.1节的issue #100原文明确显示该issue提交时（7月24日）`web_fetch`"falls through to `RiskClass.READ`"，"requires_approval": False——**说明`EGRESS`这个分类是在#100/#524/#527等一系列SSRF类issue的压力下后补进代码的真实演进**，本报告认为这条"事后加了第5层"的演进本身，比"公开材料说是4层"这个静态事实更有信息量：**它证明连OpenWorker自己的团队都在真实运营后发现"4层不够用，READ这个类别里混进了实际有副作用的工具"，这条经验教训和Matbox在设计ACTION-F005 blast-radius检查时选择"风险半径"这种连续/多因子判断（而非固定小枚举）是同一个方向的印证**，不是巧合。

### 3.2 逐点对比F-ACTION-001 10步Enforcement Pipeline

| 维度 | OpenWorker | Matbox F-ACTION-001（ACTION-F005） | 本报告判断 |
|---|---|---|---|
| 风险维度粒度 | 5个固定枚举值（READ/EGRESS/WRITE_LOCAL/EXEC/EXTERNAL），工具静态映射为主 | `riskLevel(0-5)`连续分级 + `blast-radius`风险半径检查（第④步）作为Pipeline中独立的一步，可结合资源范围/租户边界动态判定 | OpenWorker的分类更粗，Matbox的设计能表达"同一个工具在不同调用参数下风险不同"，OpenWorker目前是工具级静态映射，不是调用级动态判定（`#463`提出的PHYSICAL新增类正是在反映这个粗粒度的真实局限） |
| 审批判定 | 单一二元开关`is_consequential()`：非READ即需要人工过一遍PermissionEngine | 审批要求检查（第⑤步）与风险半径检查（第④步）是**独立的两步**，允许"高风险但不需要人工审批（走自动化补偿）"或"低风险但需要审批（合规要求）"这类更灵活的组合 | Matbox把"风险有多大"和"要不要人批"拆成两个独立判断维度，OpenWorker把两者耦合在一个风险类上，灵活性更低 |
| 租户/身份边界 | 无租户概念（单用户本机应用），审批owner身份校验依赖IM平台自身身份（且已被#519证明这层校验本身有跨平台绕过漏洞） | 租户边界检查（第②步）+ Identity/RBAC/ABAC检查（第③步）是Pipeline里独立的两步，专为多租户SaaS设计 | 结构性差异，非成熟度差异——OpenWorker从设计根基上就是单用户本机工具，没有为多租户场景设计过身份边界检查这一层 |
| 二次鉴权 | 审批一次性生效（`InboxStore.resolve`是one-shot），且#520证明解析逻辑本身可能fail open | commit-time重新鉴权是P0不可变原则（第2条）：**execute前的权限判断不能当作执行时刻仍然有效的唯一依据，必须真正提交副作用前重新校验** | 这是本报告认为Matbox设计明确更严谨的一点——如果Matbox按自己的P0原则实现，#520这类"审批当时被误判、之后无法挽回"的场景会在commit时的第二次校验里被重新拦下，而不是像OpenWorker现在这样一次性生效、错了就真的执行了 |
| 幂等与可逆性 | 无独立的幂等ledger，`InboxStore`按`(session_id, tool_call_id)`去重，但#443证明这个机制在崩溃窗口内不足以防止外部副作用重放 | ACTION-F004幂等与可逆性是独立Feature，`idempotencyKey`强制要求，P0规则第5条"重试产生重复副作用：不允许"不可降级 | Matbox已经把这个问题当作独立设计对象处理，#443恰好是"没有独立设计这个问题、依赖执行循环自身状态推断"会踩的真实的坑，是一条高质量的验证性反面案例 |
| 委派/子代理权限收窄 | `tools/subagent.py`核实：子代理拿到全新的、**统一降级为只读PLAN模式**的PermissionEngine（不是与父代理权限求交集），且硬编码禁止子代理再注册`explore`工具防止递归 | DELEGATION-F005：`permissionEnvelope=源Agent权限∩委派显式授权`权限交集收窄计算 + `depth`+`visitedEmployeeIds`数学可判定循环检测 | OpenWorker的"一刀切降级为只读"是安全但粗糙的解法（对单用户桌面场景够用），Matbox的交集计算能表达"子代理保留父代理授权范围内的部分能力"这种更精细的业务场景，是结构性的能力差距，不是实现细节差距 |
| 不可信内容边界 | issue #526原文明确指出"no untrusted-content boundary in the LLM loop — origin stripped, email/web reads never gated, web_fetch doubles as approval-free exfiltration" | ACTION-F005验收标准明确写入"Web/browser/tool输出必须当作不可信内容处理"，是Pipeline的P0验收项 | 这是本报告认为最值得记录的一条对照——Matbox在设计阶段就把这条写成了验收标准，OpenWorker是运营半年后才被外部审计发现这个洞还开着，说明"提前把这条原则写进不可变清单"这个做法本身被验证是必要的，不是过度设计 |

**3.2节核心结论**：OpenWorker的`RiskClass`模型可以理解为F-ACTION-001第④步"blast-radius风险半径检查"的一个粗粒度、单用户场景简化实现，而不是整套10步Pipeline的替代品——它没有租户边界、没有独立的二次鉴权、幂等保护薄弱、委派权限管理粗糙，且这些薄弱点都已经在真实运营中暴露成了具体的、可复现的安全issue。**这不构成"Matbox设计过度复杂"的反面证据，恰恰相反——OpenWorker踩过的每一个坑，都精确对应F-ACTION-001已经提前用更严谨方式设计掉的一条P0规则**，是一批高质量的独立验证证据。

---

## 4｜License、多租户适配性、中国可达性

### 4.1 License核查

`api.github.com/repos/andrewyng/openworker`直查`license.spdx_id: "MIT"`，`LICENSE`文件原文确认标准MIT文本，版权方"Copyright (c) 2024 Andrew Ng"（注：版权年份写2024，与仓库2026-07-20创建的事实不一致，本报告如实记录这个细节但不代为解释，不影响License本身有效性）。**依赖树核查（`pyproject.toml`）发现一条值得记录的正面细节**：项目选择`pypdfium2`（BSD协议的pdfium）而非更常见的PyMuPDF做PDF处理，代码注释原文写明理由——"PyMuPDF, whose AGPL license can't ride in the DMG"（PyMuPDF的AGPL协议不能随桌面安装包分发）——**说明OpenWorker团队自己对依赖License有主动排查意识，不是随手引入依赖**，这是一条独立的、非自证的可信证据。核心LLM抽象层`aisuite`（`andrewyng/aisuite`，同为Andrew Ng团队项目，非Anthropic Claude Agent SDK，两者无关）同样是MIT协议，16,226 stars，本身也是成熟独立项目。**结论：MIT协议对Matbox不构成任何商用/自托管障碍，且依赖链license卫生状况良好，未发现AGPL/SSPL类风险依赖**。

### 4.2 多租户适配性：结构性不适配，非成熟度问题

架构确认（README+源码）：OpenWorker是**桌面应用+本机FastAPI server**架构，凭证/会话/记忆全部存于本机加密secret store，`session_id`是唯一的会话标识维度，**代码库/文档中没有查到任何租户（tenant）/组织（org）级别的隔离概念**——这与Paperclip（专项00d已评估，好歹有部署级"公司"隔离维度）相比，OpenWorker连这一层都没有，是**彻头彻尾的单用户单机工具**，不是"简化版多租户"。若要把它的具体机制（而非整体架构）迁移进Matbox的多租户环境，至少需要新增：①每条`ToolRegistration`/风险判定加上`tenantScope`维度（当前完全没有）；②`InboxStore`审批收件箱需要按租户+角色重新设计owner校验（当前的owner校验本身还有#519这个跨平台绕过漏洞，不能直接照搬）；③子代理"降级为只读"这种单一策略需要替换成Matbox已有的权限交集计算才能支持业务场景里"子代理需要保留部分写权限"的真实需求。**这不是"值不值得做"的问题，是"这些机制从根本设计假设上就是为单用户场景写的，迁移成本接近重写"**，与专项28对Google ADK"需要一层削足适履改造"的判断是同一类结论，但OpenWorker连"官方Java支持"这种加分项都没有，参考价值集中在"产品交互模式"而非"可迁移的代码/架构"。

### 4.3 中国市场可达性：核查结果与任务书假设相反，模型层不弱，UI层是真实短板

直接核查`coworker/providers/registry.py`源码（非转述宣传材料）确认：

- **火山引擎方舟（BytePlus Ark）**：国际站`ark.ap-southeast.bytepluses.com`，另有`Volcengine Ark Agent Plan`国内端点`ark.cn-beijing.volces.com`；
- **智谱GLM（Z.ai）**：国际`api.z.ai/api/paas/v4`，大陆`open.bigmodel.cn/api/paas/v4`；
- **月之暗面Kimi（Moonshot）**：国际`api.moonshot.ai/v1`，大陆`api.moonshot.cn/v1`；
- **阿里通义千问（Qwen）**：国际`dashscope-intl.aliyuncs.com`，北京区`dashscope.aliyuncs.com`；
- **DeepSeek**（`api.deepseek.com`）、**MiniMax**（`api.minimax.io/v1`）原生登记。

**四家中国主流模型厂商均已预置国内+国际双端点，这是本报告核实后需要对任务书假设做的一条明确更正**：OpenWorker在模型接入层并非"西方模型为中心"，反而对中国模型生态的原生支持完整度高于本报告核查过的多数国际开源Agent项目。**真实的可达性缺口在两处，均有真实issue佐证**：①**UI本地化缺失**——第2.2节列出的6条独立中文本地化诉求（`#191`/`#427`/`#478`/`#498`/`#537`/`#538`）横跨项目全生命周期，且`#537`显示已有用户自制本地化仍未被合并，当前界面仍是纯英文；②**认证连通性的真实bug**——`#231`报告Qwen Cloud的有效API Key在OpenWorker里认证失败，说明"registry里注册了端点"不等于"接入链路真的打通了"，这条bug本身未修复。**对Matbox的意义**：不构成"应该采纳OpenWorker做中国模型接入参考"的理由（Matbox已有F-PROVIDER-001统一Provider Adapter抽象，且架构principle已经决定不整体采纳任何Python Agent框架），但这条核查纠正了"local-first/BYOK模式对中国市场天然复杂"这个预设——**问题从来不是模型层，中国主流模型厂商自己已经把国内合规端点铺好了，Matbox F-PROVIDER-001要解决的是UI/合规/结算这些更上层的问题，不是"能不能连上中国模型"这个已经被行业解决的问题**。

---

## 5｜按模块的影响评估表

| Matbox模块/文档 | 对照的既有设计 | 判定 | 具体理由 |
|---|---|---|---|
| **架构原则第41条**（Work模式，2026-09-02确认） | "结构化任务输入+项目边界+可跟踪执行过程+交付真正成果物"，参照OpenAI Work模式否决纯聊天驱动 | **REFERENCE-ONLY，独立验证证据** | OpenWorker是这套模式一个真实、可运行、开源可审计的实现（不同于闭源的ChatGPT Work），"outcome而非prompt"+人工检查点+最终产出可用交付物的产品叙事与principle 41方向一致，是又一个独立收敛信源；但其"计划"是自由文本人工检查点，不是结构化任务分解，实现深度不如Matbox已有的`AiTaskStep`设计 |
| **专项00f**（AI员工指令交互流程设计） | 三类人设（企业操作者/设计师/匿名访客）+ 5处已识别契约缺口（附件字段/多文件结构化输入/显式指定AI员工/中途轻量追加指令/公开可见性标记） | **REFERENCE-ONLY，两条具体可回填内容，一条需谨慎处理的伪参考** | ①OpenWorker的"Inbox"统一收件箱模式（把所有待批准项——不论来自哪个session/哪个工具——汇总到一个界面，未及时处理的排队等人工review）对00f第4.4节"审批中断点"的具体UI形态有参考价值；②五档权限模式（discuss/plan/interactive/auto/custom）是一套真实产品验证过的"自主程度"UI词汇表，对00f遗留问题1"企业操作者v1要不要做精细化控制"有具体参照；③**需要谨慎的一点**：OpenWorker解决"中途轻量追加指令"（00f第6.4节缺口）的方式是"本来就是同一个对话session，直接多说一句话"——这看起来简单，但代价是把"聊天session"当成执行的持久化主线索，这正是principle 41刚刚否决的架构（Matbox的AiTask是无状态对话贯穿的结构化任务实例，不是可以无限追加的会话）。**这条不构成可直接采纳的方案，反而说明"中途轻量追加"这个需求和"不做纯聊天驱动"这条已确认原则之间存在真实张力，00f第6.4节的方案选型需要显式意识到这一点，不能简单照搬OpenWorker的做法** |
| **F-ACTION-001**（Action网关，专项16） | ACTION-F005 10步Enforcement Pipeline，P0规则（commit时重新鉴权/幂等/委派权限不放大） | **REJECT整体机制采纳，高质量验证性反面案例** | 详见第3节逐点对比表；`RiskClass`可作为"风险半径检查"的粗粒度参照，但5大薄弱点（无租户边界、审批一次性生效且解析可fail open、幂等保护不足#443、子代理权限一刀切降级而非交集计算、不可信内容边界缺失#526）均已在真实运营中暴露成具体安全issue，逐一验证了Matbox对应P0规则的必要性，建议补充进专项16风险登记 |
| **Agent Runtime**（专项28） | RUNTIME-F002 Java+Temporal；架构原则第33条Java单语言栈；已否决LangGraph/CrewAI/OpenAI Agents SDK等Python-only候选 | **REJECT整体采纳，验证性证据** | Python（`aisuite`+FastAPI）架构与专项28已否决的一切Python候选是同一类语言栈冲突，不构成新增否决理由；`TurnEngine`的durable resume机制存在#443揭示的真实"至少一次执行"缺陷，反过来印证专项28选择Temporal Workflow/Activity原生checkpoint（而非自己在应用层拼凑一套持久化恢复逻辑）这条路线的正确性——OpenWorker踩的坑正是Temporal官方Cookbook模式本来要避免的坑 |

---

## 6｜若"参考模式"，具体怎么做

本报告结论是**不采纳任何代码/依赖/整体架构**，以下是具体到"哪份文档、加什么内容"级别的建议，均为对现有已冻结设计的补充说明，不改变任何FeatureID的技术路线：

1. **`Matbox_专项00f_AI员工指令交互流程设计`第4.4节"审批中断点"补充一条UI参照**：引用OpenWorker的"Inbox"统一收件箱模式（跨session/跨工具汇总所有待批准项，未处理项持续挂起等待人工review）作为"发起指令的人应该在任务卡片里实时看到审批状态"这条设计判断的具体产品先例，与3.1节Agentforce/ChatGPT Work并列引用。
2. **`Matbox_专项00f`第7节遗留开放问题1补充一条参照**：引用OpenWorker真实验证过的五档权限模式命名（discuss/plan/interactive/auto/custom）作为"企业操作者v1要不要做精细化自主程度控制"这个产品判断的具体命名/分级参照，仍需用户拍板是否v1采用。
3. **`Matbox_专项00f`第6.4节"中途轻量追加指令"缺口补充一条风险提示**：明确记录OpenWorker解决这个问题的方式（保留对话session作为执行主线索）与principle 41"不做纯聊天驱动"存在真实张力，提醒下一次修订在设计具体API（`append-instruction`端点 vs 放宽`PLAN_EDITED`触发条件）时不要无意中把AiTask做成"可以无限追加的聊天会话"。
4. **`Matbox_专项16_Action网关`风险登记补充"审批解析fail open"与"幂等/崩溃重放"两条具体外部案例**：引用issue `#520`（否定句被解析成同意，审批网关fail open）和`#443`（崩溃后外部副作用可能被重放）原文，作为Matbox P0规则"commit时重新鉴权"与ACTION-F004幂等设计必要性的独立佐证，与已引用的Paperclip CVE-2026-41679并列，强化外部证据密度。
5. **`Matbox_专项19_AI员工委派`可选补充一条子代理权限设计的对照案例**：OpenWorker子代理"统一降级为只读、无递归"的粗粒度做法可作为DELEGATION-F005`permissionEnvelope`交集计算设计合理性的一个反面对照（"更简单的替代方案在真实场景下会不够用"），非必须项，供下次修订时按需引用。

---

## 7｜信息来源清单

- OpenWorker GitHub仓库：[github.com/andrewyng/openworker](https://github.com/andrewyng/openworker)、[API直查](https://api.github.com/repos/andrewyng/openworker)（2026-09-02，stars 17,177/forks 2,398/open_issues 451/created_at 2026-07-20/pushed_at 2026-08-31/language Python）、[完整文件树](https://api.github.com/repos/andrewyng/openworker/git/trees/main?recursive=1)、[languages breakdown](https://api.github.com/repos/andrewyng/openworker/languages)、[contributors API](https://api.github.com/repos/andrewyng/openworker/contributors)、[LICENSE原文](https://raw.githubusercontent.com/andrewyng/openworker/main/LICENSE)、[pyproject.toml](https://raw.githubusercontent.com/andrewyng/openworker/main/pyproject.toml)
- 核心源码直读：[`coworker/risk.py`](https://raw.githubusercontent.com/andrewyng/openworker/main/coworker/risk.py)（RiskClass枚举/classify逻辑）、[`coworker/tools/plan.py`](https://raw.githubusercontent.com/andrewyng/openworker/main/coworker/tools/plan.py)（规划工具实现）、[`coworker/tools/subagent.py`](https://raw.githubusercontent.com/andrewyng/openworker/main/coworker/tools/subagent.py)（子代理权限模型）、[`coworker/providers/registry.py`](https://raw.githubusercontent.com/andrewyng/openworker/main/coworker/providers/registry.py)（供应商端点注册，含中国厂商双端点）
- 安全issue（本报告深度抽样，均通过`api.github.com/repos/andrewyng/openworker/issues/{number}`直接抓取原文）：[#520](https://github.com/andrewyng/openworker/issues/520)、[#519](https://github.com/andrewyng/openworker/issues/519)、[#213](https://github.com/andrewyng/openworker/issues/213)（已修复）、[#100](https://github.com/andrewyng/openworker/issues/100)、[#443](https://github.com/andrewyng/openworker/issues/443)、[#29](https://github.com/andrewyng/openworker/issues/29)（已修复）、[#463](https://github.com/andrewyng/openworker/issues/463)、另#516/#517/#518/#521~#527同批次SAST发现（`ns-rajats`，2026-08-19）
- 中国相关issue：[#191](https://github.com/andrewyng/openworker/issues/191)、[#231](https://github.com/andrewyng/openworker/issues/231)、[#427](https://github.com/andrewyng/openworker/issues/427)、[#478](https://github.com/andrewyng/openworker/issues/478)、[#498](https://github.com/andrewyng/openworker/issues/498)、[#537](https://github.com/andrewyng/openworker/issues/537)、[#538](https://github.com/andrewyng/openworker/issues/538)
- 隐私/其他issue：[#116](https://github.com/andrewyng/openworker/issues/116)（默认开启的遥测未在Privacy说明中披露）
- 第三方独立评测：[openworker.site/review/](https://openworker.site/review/)（"Honest Test After 100+ Tasks"，8.1/10）
- HN真实讨论核实（Algolia API直查，[hn.algolia.com/api/v1/search?query=OpenWorker](https://hn.algolia.com/api/v1/search?query=OpenWorker&tags=story)）：[story 49027382](https://news.ycombinator.com/item?id=49027382)（0评论）、[story 49027225](https://news.ycombinator.com/item?id=49027225)（0评论）、[story 49032886](https://news.ycombinator.com/item?id=49032886)（2评论，原文引用于第2.4节）
- 官方发布材料：[Andrew Ng Twitter公告](https://x.com/AndrewYNg/status/2080333504446108104)、[MarkTechPost](https://www.marktechpost.com/2026/07/23/andrew-ng-just-released-openworker-an-open-source-local-first-desktop-ai-coworker-that-returns-finished-deliverables-instead-of-chat/)、[Marktechpost风险分级摘要](https://x.com/Marktechpost/status/2080377910494384576)、[MoClaw Blog](https://moclaw.ai/blog/what-is-openworker)、[aisuite仓库](https://github.com/andrewyng/aisuite)（16,226 stars，MIT）
- 前置Matbox文档：[`Matbox_专项28_AgentRuntime_技术选型与开发交接报告_2026-08-30.md`](Matbox_专项28_AgentRuntime_技术选型与开发交接报告_2026-08-30.md)、[`Matbox_专项00f_AI员工指令交互流程设计_2026-09-02.md`](Matbox_专项00f_AI员工指令交互流程设计_2026-09-02.md)、[`Matbox_Action网关_正式开发文档_V1.0-RC.md`](../Matbox_Action网关_正式开发文档_V1.0-RC.md)、[`Matbox_专项16_Action网关_技术选型与开发交接报告_2026-08-30.md`](Matbox_专项16_Action网关_技术选型与开发交接报告_2026-08-30.md)、[`Matbox_架构设计原则.md`](../Matbox_架构设计原则.md)第41条、[`Matbox_专项00d_Paperclip专项评估_2026-09-02.md`](Matbox_专项00d_Paperclip专项评估_2026-09-02.md)（方法论与格式参照）
