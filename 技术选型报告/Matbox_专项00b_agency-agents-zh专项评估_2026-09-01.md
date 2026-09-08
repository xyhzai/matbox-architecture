# Matbox 专项00b｜agency-agents-zh（jnMetaCode）专项评估——补查用户直接发现的候选

技术选型报告 · V1.0 · 2026-09-01

**DocID**: MATBOX-CROSSCUT-TECHSELECT-20260901-V1.0-B
**审计对象**: `github.com/jnMetaCode/agency-agents-zh`（267/276个角色定义包，GitHub API查证20,179 stars/3,270 forks/6 open issues/MIT）+ 其配套编排器 `github.com/jnMetaCode/agency-orchestrator`（独立仓库，非同一个repo）。
**触发原因**: 用户在`Matbox_专项00_完整AI员工平台横向调研_2026-09-01.md`（跨模块品类级横向调研，已核查StaffDeck/DeerFlow 2.0/agency-swarm三个用户点名候选）交付后，自己另外发现了这个未出现在该报告里的项目。**这是一次真实的调研覆盖缺口**：专项00的方法论说明（第1.1节）已经如实承认"每次搜索只能看到候选的一个切面"这个结构性盲区，本次缺口进一步说明——专项00的GitHub Topics遍历（`ai-employees`/`digital-employee`两个话题）和"AI workforce platform"品类关键词搜索，都不会命中agency-agents-zh，因为它的GitHub Topics标签和自我定位是"AI编程工具的角色扩展包"（面向Claude Code/Cursor/Copilot等18种工具的subagent定义），不是"AI employee platform"或"digital employee"这两个关键词会命中的品类——**这是专项00方法论盲区的第二次真实验证，不是第一次的巧合**：专项00发现"按Matbox模块名搜索找不到跨模块候选"，本次进一步发现"按'AI员工平台'品类词搜索，同样找不到'AI编程工具角色扩展包'这个相邻但用词完全不同的品类"，两次缺口性质不同，值得在专项00的方法论认知基础上补一条。
**报告性质**: 与专项00同类型的补查性专项评估，不产生新FeatureID，不重跑Stage 9冻结决策，产出是"该项目是否需要让已完成的专项12/15/19/21a任一份报告重新开门"的明确答案。

---

## 0｜给忙碌读者的结论摘要

1. **先回答任务书原始描述里最大的一处偏差**：任务书把这个项目描述成"AI专家角色 + DAG编排器"的一体化平台，但**源码级核查确认这实际上是两个独立仓库、性质完全不同的两样东西**，必须分开评估：
   - `agency-agents-zh` 本身**是一个纯角色/提示词定义包**（package.json自述"276 个即插即用的 AI 专家角色定义"，主语言标记为Shell，核心内容是267个Markdown文件，每个文件只有4个机器可读的YAML frontmatter字段`name/description/emoji/color`，正文是给LLM直接读的自然语言系统提示词），**不包含任何执行/推理/编排代码**。它不是"267个Agent"意义上的Agent（不会自己跑起来），是"267份写好的system prompt"，需要外部工具（Claude Code/Cursor/Copilot等）加载后才有行为。
   - `agency-orchestrator`（github.com/jnMetaCode/agency-orchestrator，**独立仓库**，非同一个repo下的子目录）才是真正的执行引擎：TypeScript编写，2,180 stars/288 forks/Apache-2.0/npm已发布（`agency-orchestrator`包），源码审查确认`src/core/dag.ts`是真实的拓扑排序DAG构建器（按层分组、编译期检测循环依赖直接抛错、`loop.back_to`要求指向前置层级），`src/core/executor.ts`/`parser.ts`/`verify.ts`等文件证实这是一个真实、可运行、非空壳的工作流编排引擎，不是文档堆砌出来的空气项目。
   - **对Matbox的意义**：这个区分直接决定了整份评估怎么做——评估"角色内容能不能当EmployeeTemplate种子数据用"要看`agency-agents-zh`；评估"编排/委派架构有没有新东西"要看`agency-orchestrator`；任务书原始描述把两者当一个东西介绍，本报告在正文按两个独立对象分别核查。
2. **`agency-agents-zh`本身不是原创项目，是英文上游`msitarzewski/agency-agents`的中文本地化衍生仓库**——`UPSTREAM.md`原文确认267个角色中215个是"已译自上游"，只有约51-63个（README不同版本口径为51/63，`AGENT-LIST.md`统计以文件为准）是"中国市场原创"。**更值得记录的是：英文上游本身规模远超本次评估的中文衍生版**——GitHub API查证`msitarzewski/agency-agents`：**149,381 stars / 24,083 forks**（2026-09-01查证），创建于2025-10-13，MIT协议，比专项00里的DeerFlow（81,211 stars）还高出近一倍，**这个体量本应该在专项00的品类级搜索里被发现**，是专项00方法论盲区的又一个真实例证（详见第1节）。但star数大不代表品类相关——上游项目定位是"AI编程工具的角色扩展包"（GitHub描述"specialized expert with personality, processes, and proven deliverables"，面向Claude Code等编程агent工具），不是"AI employee platform/digital employee"这个专项00搜索的品类词，这解释了为什么两轮搜索都没命中它，不是调研马虎。
3. **`agency-agents-zh`本身的内容质量评估：抽查的中国市场角色定义（如小红书运营专家）是真实、具体、可用的高质量提示词**，包含身份设定、核心职责拆解、平台合规红线（"绝不使用违禁词""不刷量不买赞"）、可交付物模板（爆款笔记模板/投放排期表）、四步工作流程、成功指标（KPI量化），不是"改几个词的通用模板"。但**Matbox的实际业务域（家居制造业+室内/景观/建筑设计）在267个角色里没有任何专门覆盖**——`AGENT-LIST.md`全文检索"室内/家居/建筑/景观/家具/装修"，唯一命中的是`gis-bim-specialist`（BIM/GIS整合专家，涉及"室内地图"，是建筑信息模型/地理信息系统的技术整合角色，不是家居设计/家具零售业务角色）。52个中国市场角色清一色是**通用电商/社媒运营/合规/垂直细分**（小红书/抖音/微信/飞书/钉钉、跨境电商、政务ToG、医疗合规、Qt工业上位机、畜禽养殖档案核对等），可以被家居品牌的营销团队直接复用（因为营销/电商运营是通用能力），但不存在"室内设计助理""家具选品匹配专员"这类Matbox AIEMP-F001初始岗位族里已经点名的家居/设计垂直角色。
4. **License：MIT，风险等级低，且是本次核查过的候选中License最干净的一个**——GitHub API直查`jnMetaCode/agency-agents-zh`和`jnMetaCode/agency-orchestrator`两个仓库均为MIT/Apache-2.0（后者含专利授权条款），根目录LICENSE文件覆盖全仓库文件（含.md角色定义文件），不存在AGPL网络著佐权条款那类专项09/专项00已经反复处理过的问题。**这意味着如果第9节评估结论是"部分内容值得直接采纳"，License本身不构成障碍**，这是本次评估与StaffDeck（AGPL-3.0，专项00/专项21a均已判定License本身就是独立否决理由）的关键差异点。
5. **对4个受影响Matbox模块的最终判定（详见第4节完整表格）**：F-AIEMP-001（专项15，已完成）**REFERENCE-ONLY-WITH-CONCRETE-STARTER-VALUE**——不是简单的参考，是本报告认为专项15/21应该记录的一条具体可执行建议：小红书/抖音/微信等通用内容运营角色的"关键规则"（禁止事项）与"成功指标"（KPI）两个板块结构，可以作为AIEMP-F001初始岗位族"内容运营"分支起草EmployeeTemplate时的**内容起点**（不是直接导入，需要按Matbox九字段schema重新拆解，见第5节），能实质性减少从零起草的工作量；F-ORCHESTRATOR-001（专项12，已完成）**REFERENCE-ONLY，不改变结论**；F-DELEGATION-001（专项19，已完成）**REFERENCE-ONLY，不改变结论**；F-CONSOLE-001雇佣中心（专项21待建，21a已完成训练中心子部分）**REFERENCE-ONLY但UX参考价值真实**——网页Studio的角色浏览/收藏/一句话AI自动组队交互，是本次评估里对CONSOLE-F001产品体验设计最具体的参照对象。
6. **对专项00结论的回应（任务书要求不回避的问题）**：**专项00"没有一份已完成报告需要重新打开Stage 9冻结架构决策"这条结论，经本次补查后依然成立**，但专项00第8节"这次调研真正的价值……"这段总结性论述里隐含的"跨模块搜索已经做到位"的自信需要打一个补丁——不是结论错了，是方法论覆盖面被再次证明有盲区（第1条已展开），本报告建议专项00在下次修订或专项00c/00d一类后续补查中，把搜索关键词族再扩展一层："AI编程工具角色/subagent扩展包"（agency-agents类）、"提示词角色库"（persona library）这两类此前完全没有搜索过的关键词，不是因为怀疑还有第4个候选，是因为方法论本身现在有两次独立证据说明关键词族不够全。

---

## 1｜专项00方法论盲区的第二次验证（回应任务书"如实说明覆盖缺口"的要求）

专项00第1.1节已经承认"每个模块级搜索只能看到候选的一个切面"，并给出StaffDeck/DeerFlow/agency-swarm三个候选分别命中不同模块搜索切面的例子。本次用户直接发现agency-agents-zh，核查后确认这是**性质不同的第二类盲区**：

- StaffDeck/DeerFlow/agency-swarm三者，**都自我定位为"AI员工/Agent工作力平台"这个品类**，只是各自命中Matbox不同模块的搜索切面——本质是"品类内的模块切片盲区"。
- agency-agents-zh（及其149k star的英文上游`msitarzewski/agency-agents`）**根本不自我定位为"AI员工平台"**，它的GitHub描述、README定位词、npm关键词（`ai-agents`/`prompts`/`system-prompts`/`multi-agent`/`llm`/`claude`/`deepseek`/`roles`）全部指向"AI编程工具的角色/提示词扩展包"这个相邻但用词完全不同的品类——这是**"品类边界本身的盲区"**，不是"同一品类内切片没搜全"。专项00的搜索关键词（"open-source AI employee platform"/"digital employee framework"/"agent workforce platform"/"enterprise agent OS"）没有一个会命中这类项目，不是搜索深度不够，是关键词族本身的选择就排除了这个相邻品类。

**这条区分的实际意义**：专项00第8节的结论"没有一个候选改变任何一份已完成报告的技术结论"经本次补查依然成立（详见第4节），但如果Matbox未来还要做第三轮补查，应该把"AI编程工具角色扩展包/subagent库/提示词角色库"作为一个独立于"AI employee platform"的关键词族去搜，不能假设"跨模块搜索已经把相邻品类也覆盖了"。

**149k star上游的核查（`msitarzewski/agency-agents`）**：GitHub API 2026-09-01直查确认149,381 stars/24,083 forks/155 open issues/MIT协议/创建于2025-10-13/主语言Shell，描述"A complete AI agency at your fingertips - From frontend wizards to Reddit community ninjas...Each agent is a specialized expert with personality, processes, and proven deliverables"——这个体量本身值得记录，但**不构成对Matbox任何模块结论的新证据**，理由与`agency-agents-zh`本身完全一致（第2节展开），因为两者内容结构同源（中文版是上游的翻译+本地化衍生），不需要重复评估两遍。

---

## 2｜`agency-agents-zh`本身：真实技术性质核查（框架 vs 提示词库）

### 2.1 源码级结构核查

通过GitHub API直接抓取仓库文件树（非转述第三方文章）：根目录下`academic/company/design/engineering/finance/game-development/gis/hr/integrations/legal/marketing/paid-media/product/project-management/sales/scripts/security/spatial-computing/specialized/strategy/supply-chain/support/testing`共20+个按部门分类的目录，每个目录下是`部门前缀-角色名.md`命名的角色定义文件。`package.json`自述：`"description": "276 个即插即用的 AI 专家角色定义"`，`"scripts": {"check:counts": "node scripts/check-counts.mjs"}`——唯一的脚本是一个计数校验脚本（保证`AGENT-LIST.md`的统计数字与实际文件数一致），不存在任何执行、推理、工具调用相关的代码。

### 2.2 抽查角色定义文件的真实内容结构

抽查`marketing/marketing-xiaohongshu-operator.md`（52个中国市场角色之一，完整原文见附录来源）：

```yaml
---
name: 小红书运营专家
description: 专注小红书平台的内容运营专家，擅长种草笔记创作、达人合作策略、爆款内容公式、以及通过数据驱动实现品牌在小红书的高效获客和口碑建设。
emoji: 📕
color: "#FF2442"
---
```

frontmatter只有4个字段（`name/description/emoji/color`），是典型的Claude Code风格subagent定义头（供工具做角色列表展示用），**不含任何权限/工具白名单/预算/审批相关的结构化字段**。正文分为：身份与记忆、核心使命（3个子板块）、关键规则（平台合规+内容真实性两类禁止事项）、技术交付物（含具体模板：爆款笔记模板、投放排期表）、四步工作流程、沟通风格、成功指标（5条量化KPI）——**这是一份写得认真、具体、可直接拿给LLM当system prompt使用的高质量提示词文档，不是"改几个关键词的空洞模板"**，但**结构上是自由格式的Markdown说明文，不是Matbox EmployeeTemplate需要的结构化字段（见第5节的字段映射分析）**。

### 2.3 结论：`agency-agents-zh`是提示词/角色定义库，不是执行框架

与任务书要求回答的"是真实软件框架还是提示词模板集合"这个问题的直接答案：**是后者**。这个判断不影响其对Matbox的参考价值（第4/5节展开），但决定了它不能被拿来和StaffDeck/DeerFlow/agency-swarm这类"执行框架"用同一套评估维度（源码质量/依赖安全/成熟度）横向比较——它没有"能不能跑"这个问题，它的评估维度是"内容写得好不好、能不能被复用"。

---

## 3｜`agency-orchestrator`：真实的编排引擎核查（任务书要求的DAG机制核实）

### 3.1 仓库真实性与规模

GitHub API直查（2026-09-01）：`jnMetaCode/agency-orchestrator`，**独立仓库**（不是`agency-agents-zh`的子目录或同一仓库），创建于2026-03-21，2,180 stars / 288 forks / 6 open issues，**Apache-2.0**（含专利授权条款），主语言TypeScript，仓库体积65,966 KB（约64MB，含真实的src/web/desktop/docs/test/eval等完整目录结构），已发布到npm（`agency-orchestrator`包）。

### 3.2 源码级核查：DAG机制是真实实现，不是文档描述的空气功能

`src/core/`目录下确认存在`dag.ts`/`executor.ts`/`parser.ts`/`verify.ts`/`condition.ts`/`compare.ts`/`assert.ts`/`template.ts`八个核心文件（非demo/占位文件）。直接抓取`dag.ts`源码核实：

- `buildDAG()`函数从`WorkflowDefinition`（YAML工作流定义，`step.depends_on`声明依赖关系）构建DAG，用`topologicalLevels()`做拓扑排序，**按层分组**（同层节点互不依赖，可并行执行）——这是fan-out/fan-in模式的真实实现，不是营销描述。
- **循环依赖在构建期直接抛错**（`"工作流存在循环依赖，无法拓扑排序"`），且`loop.back_to`语法要求显式指向"当前层级之前的层级"，构建期验证不满足则抛错——是一种真实的、编译期静态循环防护机制。
- `src/`目录下另有`agents/`（角色适配）、`connectors/`（第三方IM/工具接入）、`mcp/`（MCP协议接入）、`providers/`（11家LLM供应商适配）、`canvas/`（可视化DAG编辑器，README描述"拖拽节点/连线（自动防环）"）、`cli/`、`notify.ts`（钉钉/飞书/企业微信webhook推送）——这是一个功能完整、非空壳的本地化工作流编排工具，**源码审查结论：真实、可运行、非demo**。

### 3.3 关键的架构性质差异（这是决定它对F-ORCHESTRATOR-001/F-DELEGATION-001是否有参考价值的核心问题）

`agency-orchestrator`的DAG是**用户/系统预先声明的静态工作流图**（YAML里的`steps[].depends_on`），"AI自动组队"功能是"输入一句话→LLM一次性拆解生成完整DAG计划→按DAG执行"——这与专项12/19已经反复论证过的"静态预声明协作拓扑 vs 运行时动态委派安全边界"是**同一组问题的又一个例子**：

- 与ORCHESTRATOR-F002混合路由（Embedding快速匹配+LLM兜底、要求路由决策可复现/可追溯）比较：`agency-orchestrator`的"AI自动组队"是纯LLM一次性生成完整计划，**没有证据显示存在Embedding快速路径或路由结果确定性保证机制**——这与专项12第2.3节已经引用的AutoGen GroupChatManager"同一句话跑两次可能路由到不同结果"是同一类设计风险，不是新证据，是重复验证。
- 与DELEGATION-F005失败模式防护（深度硬上限+已访问节点集合去重的运行时循环检测）比较：`agency-orchestrator`的循环防护是**工作流定义阶段的静态图校验**（防止YAML里写出自相矛盾的依赖声明），不是Matbox需要的"运行时动态委派链循环检测"（Agent在执行过程中临时决定委派给谁，事先不知道完整链路）——这是两种不同层面的循环防护，专项19第3.4节评估AWS Strands `repetitive_handoff_detection_window`时已经确立"要看是不是针对动态运行时交接的检测算法"这条评判标准，`agency-orchestrator`的DAG校验不满足这条标准，不能类比AWS Strands那样被记为"设计参考"级别的新发现。
- 与ORCHESTRATOR-F001 Registry比较：`agency-orchestrator`没有多租户/角色注册中心概念，角色清单是本地文件系统扫描（含`~/.ao/roles`自建角色目录），是单机/单用户场景的角色发现，不是Matbox需要的多租户Registry。

**结论：`agency-orchestrator`是一个真实、工程质量不错的本地工作流编排引擎，但解决的是"个人/小团队本地一次性生成并执行一个工作流计划"这个问题，不是Matbox需要的"多租户SaaS后端里，运行时动态路由+委派+安全边界"这个问题，问题层级不匹配——这是专项12/19已经反复确立的评判框架（vllm-project/semantic-router"问题层级不匹配"、Google ADK"transfer_to_agent是继承非交集"）的又一次成立，不构成对专项12/19结论的推翻依据。**

### 3.4 真实用户与Issue核查

`agency-agents-zh`当前6个open issue（`jnMetaCode/agency-agents-zh/issues`）全部是功能请求类，不是可靠性/安全类缺陷报告：`#113`升级SEO/GEO智能体v2、`#110`建议加跨平台IM协作能力、`#109`建议补充"LongHorizon-Harness长周期任务"方向、`#104`适配智谱ZCode、`#103`建议支持QwenPaw、`#97`嵌入式算法工程师与嵌入式应用工程师角色合并建议。**如实标注**：这个issue列表的性质（清一色功能请求，无一条崩溃/数据丢失/安全类报告）既可以解读为"核心质量稳定"，也可能反映"角色定义类内容本身出问题的空间有限"（不是可执行代码，没有运行时崩溃这一类问题），本报告不夸大这条证据的分量。

中文社区侧检索（CSDN）确认存在独立第三方（非项目维护者）撰写的完整使用教程类文章（如`blog.csdn.net/taoanbang/article/details/160261571`"211 个 AI 专家角色，一键安装到你的 AI 工具：agency-agents-zh 完全使用教程"），属于真实第三方使用记录，但**均为教程/使用说明性质，未检索到掘金/V2EX/知乎上对其质量/局限的批评性讨论**，如实标注这条信息缺口，不编造负面评价来凑"平衡性"。

**维护者身份核查**（任务书要求）：`jnMetaCode`是GitHub个人账户（非组织），GitHub简介"AI 编程实战 · AI Coding Practitioner · 公众号 AI不止语"，127个公开仓库，766 followers，账户创建于2015年（非新注册小号）。**需要如实记录的商业化信号**：`agency-agents-zh`与`agency-orchestrator`两份README均包含大量LLM API中转/代理服务商的付费赞助广告位（APINEBULA/AICodeMirror/Cubence/火山引擎/优云智算/LanoX AI/胜算云/APIMart等，多数带推荐返利码），以及指向`aiolaola.com`付费课程（"AI 专家团队实战"33节/"从零学会 AI 编程"180节等）的多处导流链接——这是一个**个人开发者运营的、有明确内容变现/API分销商业模式的开源项目**，不是企业或研究机构背书的项目，这与StaffDeck（面壁智能/清华THUNLP等机构联合研发）、DeerFlow（字节跳动）在信誉背书类型上不是同一量级，如实记录供判断参考，不代表内容质量必然更低（第2.2节的内容抽查结论仍然是"具体可用"）。

---

## 4｜按模块的影响评估表

| Matbox模块 | 对应专项/FeatureID | 已完成报告状态 | 判定 | 理由 |
|---|---|---|---|---|
| **F-AIEMP-001**（EmployeeTemplate Registry） | 专项15，AIEMP-F001~F005，已完成（2026-08-30） | DRAFT_RESEARCH_COMPLETE，Stage 9冻结 | **REFERENCE-ONLY，但有具体可执行的内容起点价值** | 267个角色定义中的52个中国市场角色（尤其小红书/抖音/微信/飞书/钉钉等内容运营类）与AIEMP-F001已确认的初始岗位族"内容运营（小红书/抖音/商品内容专员）"在业务概念上直接对应；角色文档的"关键规则"板块（禁止事项列表）与"成功指标"板块（量化KPI）具备直接映射到`forbiddenActions[]`与`kpiProfile{}`两个Matbox schema字段的内容基础；但`skills[]`/`sopRef`/`qualityProfile`/`budgetPolicy`/`permissionPolicy`五个字段在原始角色文档里没有对应结构化内容，需要Matbox自己重新拆解撰写（详见第5节）。**不构成对专项15Top-1排名结论（Matbox自研EmployeeTemplate Registry）的推翻依据**——专项15的结论是"自建Registry基础设施"，本发现只影响"起草哪些初始模板内容时可以少写一些"这个内容层面，不影响架构层面 |
| **F-ORCHESTRATOR-001**（中央编排层） | 专项12，ORCHESTRATOR-F001~F005，已完成（2026-08-31） | DRAFT_RESEARCH_COMPLETE，Stage 9冻结 | **REFERENCE-ONLY，不改变结论** | `agency-orchestrator`的"AI自动组队"是纯LLM一次性拆解生成完整执行计划，没有Embedding快速路径/路由确定性保证，与专项12已经识别并否决的AutoGen式"纯LLM路由不确定性"是同一类设计局限，是重复验证而非新证据；其DAG拓扑排序+按层并行执行的实现思路与专项12已经确认的"Coordinator做fan-out并行/fan-in汇总"架构方向一致，属于对现有设计方向的又一次独立佐证，不是新发现 |
| **F-DELEGATION-001**（AI员工委派） | 专项19，DELEGATION-F001~F005，已完成（2026-08-31） | DRAFT_RESEARCH_COMPLETE，Stage 9冻结 | **REFERENCE-ONLY，不改变结论** | `agency-orchestrator`的循环检测是工作流定义阶段的静态图校验（防止YAML依赖声明本身自相矛盾），不是DELEGATION-F005需要的运行时动态委派链循环检测（深度计数器+已访问节点集合去重，针对Agent执行过程中临时决定的委派，事先不知道完整链路）——问题层级不匹配，与专项19否决vllm-project/semantic-router、Google ADK的评判逻辑同构；且`agency-orchestrator`不存在权限交集收窄（源Agent权限∩委派权限）、预算传递、跨租户拦截这些DELEGATION-F001~F004的Matbox专属业务语义，同专项19第9.4节"这四条本身不是多候选选一的选型问题"的结论一致 |
| **F-CONSOLE-001雇佣中心**（CONSOLE-F001，专项21待建） | 专项21未整体建，21a（训练中心CONSOLE-F002）已完成（2026-09-01） | CONSOLE-F001本身尚无独立技术选型报告 | **REFERENCE-ONLY，但UX参考价值真实、具体** | `agency-orchestrator`网页Studio的"角色组队"页面（276位专家按部门分组浏览、☆收藏常用、"我的"自建角色分类、一句话AI自动组队匹配、多语言角色库切换）是本次评估里对标CONSOLE-F001"浏览/对比EmployeeTemplate，输入业务需求描述获得可解释推荐匹配，交互复杂度对标业务人员自助可用"这条验收标准**最具体的真实产品形态参照**，值得在专项21正式立项时作为UX设计参考记录；但技术栈不可复用（本地Electron/CLI单机工具 vs Matbox多租户SaaS后端），不构成技术选型层面的候选 |

**本表核心结论**：与专项00第7节"没有一次落在应该重新评估采纳"的判定模式完全一致——四个模块里，三个（Orchestrator/Delegation/Registry架构本身）判定REFERENCE-ONLY且不改变已有结论；F-AIEMP-001多了一条本报告认为值得记录、但同样不改变Top-1自研结论的"内容起点"具体建议。**没有一行判定需要重开专项12/15/19任一份已完成报告的Stage 9冻结架构决策。**

---

## 5｜F-AIEMP-001"内容可复用性"的具体字段映射（回应任务书"如果是adopt-content要具体到怎么用"的要求）

以`marketing/marketing-xiaohongshu-operator.md`为样本，与`Matbox_AI员工身份_正式开发文档_V1.0-RC.md`第5节`EmployeeTemplate`九个核心字段逐一对照：

| Matbox EmployeeTemplate字段 | agency-agents-zh对应内容 | 可复用程度 |
|---|---|---|
| `roleCode`/`role.name` | frontmatter `name`（"小红书运营专家"） | **直接可用**，仅需转写为Matbox命名规范 |
| `role.businessGoal` | 正文"核心使命"段首概括句 | **需要提炼改写**，原文是叙述性文字非单句目标陈述 |
| `role.responsibilities[]` | "核心使命"下3个子板块的要点（内容策略制定/达人合作与投放/社区运营与口碑管理） | **可拆解为列表**，需要人工把段落式描述转成`responsibilities[]`数组项 |
| `role.forbiddenActions[]` | "关键规则"板块（"绝不使用违禁词""不刷量不买赞""达人合作必须走蒲公英平台报备"等） | **直接映射价值最高**，这部分内容本身就是禁止性规则清单，稍加格式化即可入库 |
| `skills[]` | 无对应结构化内容（"技术交付物"板块的模板本身可以启发`skillId`的划分，如"爆款笔记撰写""达人投放排期"两个技能，但需要新建`inputSchema/outputSchema/toolRefs[]`） | **仅提供灵感，需从零建模** |
| `sopRef` | "工作流程"板块（品牌诊断→策略制定→内容执行→数据复盘四步） | **可作为SOP初稿骨架**，需要补充`approvalPoints[]`/`failurePolicy{}`才能满足Matbox SOP实体要求 |
| `kpiProfile` | "成功指标"板块（互动率>5%、CPE<¥3等5条量化指标） | **直接映射价值高**，量化指标可直接转录，需补充数据来源/统计口径定义 |
| `qualityProfile` | 无对应内容 | **需从零建模** |
| `budgetPolicy` | 无对应内容（角色文档里的"预算"字样是业务讨论对象，不是Matbox意义上的Agent自身运行预算策略） | **需从零建模** |
| `permissionPolicy` | 无对应内容（角色定义假设的是"生成建议/文案/排期表"这类无副作用产出，不涉及工具调用权限） | **需从零建模** |

**结论**：九个字段中，`forbiddenActions[]`与`kpiProfile`两项可获得实质性内容加速（数据来自真实、具体的角色文档而非凭空编造），`roleCode/responsibilities/sopRef`三项可获得结构骨架/灵感层面的加速，`skills[]/qualityProfile/budgetPolicy/permissionPolicy`四项需要完全从零建模。**如实的加速幅度评估：对"内容运营/社媒运营"这一类岗位族起草EmployeeTemplate初稿，可能节省30-40%的文案撰写工作量，不构成"直接导入即可用"级别的加速，但比从空白页开始有真实、可衡量的价值**，专项15/未来专项21正式转WorkPackage时可以把这批角色文档列为"内容运营类模板起草时的参考语料"，注明来源与MIT License（无需付费/授权障碍）。

---

## 6｜License风险核查

| 组件 | License | 覆盖范围 | 风险等级 | 判定依据 |
|---|---|---|---|---|
| `jnMetaCode/agency-agents-zh` | MIT | 根目录LICENSE覆盖全仓库（含全部.md角色定义文件），GitHub API直查确认 | 低 | 若第5节的内容映射建议被采纳（把角色文档内容作为起草参考甚至直接摘录禁止事项/KPI条目改写进Matbox自己的EmployeeTemplate），MIT协议完全允许修改、再分发、商用，不构成合规障碍，注明来源即可 |
| `jnMetaCode/agency-orchestrator` | Apache-2.0（含专利授权条款） | 根目录LICENSE覆盖全仓库源码 | 低 | 本报告结论是不整体采纳（第3.3节问题层级不匹配），License层面完全无风险，如未来重新评估也无License障碍 |
| 上游`msitarzewski/agency-agents` | MIT | 英文原始内容 | 低 | 不构成独立候选（第1节已说明与中文衍生版内容同源，不重复评估），License同样无风险 |

**结论：本次评估的三个仓库License均无风险，是专项00/专项21a系列评估里License条款最干净的一批候选（对比StaffDeck/PilotDeck的AGPL-3.0）**，若未来任何一条REFERENCE-ONLY建议升级为实际内容引用，不存在合规障碍。

---

## 7｜最终结论：是否需要重新打开已完成报告

**不需要重新打开专项12/15/19任一份已完成报告的Stage 9冻结架构决策。**

- **专项12（中央编排层）**：结论不变。`agency-orchestrator`的DAG机制是重复验证而非新证据，且存在与专项12已经识别的AutoGen式"纯LLM路由不确定性"同类的设计局限。
- **专项19（AI员工委派）**：结论不变。`agency-orchestrator`的循环防护是工作流定义阶段的静态校验，与DELEGATION-F005需要的运行时动态委派链检测不是同一类机制，问题层级不匹配的评判逻辑与专项19否决vllm-project/semantic-router/Google ADK时使用的框架完全一致。
- **专项15（AI员工身份）**：结论不变，但**本报告建议专项15或未来专项21正式立项时补充一条内容级（非架构级）记录**：52个中国市场角色定义（尤其内容运营类）可作为起草初始EmployeeTemplate内容时的参考语料，第5节已给出具体字段映射和加速幅度评估，这是"内容起草层面的加速"，不是"架构选型层面的改变"，不触发Stage 9重新评审。

**对专项00方法论结论的回应（任务书明确要求不回避）**：专项00"没有一个候选改变任何一份已完成报告的技术结论"这条核心判断，经本次补查依然成立——本次新发现的候选同样落在"REFERENCE-ONLY"这一类判定里。但专项00隐含的"跨模块搜索已经把该覆盖的都覆盖了"这层自信，被本次发现证明**还需要再打一次补丁**：不是搜索深度不够，是"AI员工平台"这个品类关键词族本身没有覆盖到"AI编程工具角色扩展包/提示词角色库"这个相邻品类，这是专项00第1.1节已经承认的"模块级搜索有切面盲区"之外的**第二类盲区（品类边界盲区）**，建议记录为专项00方法论的正式补充条目，供未来任何专项00c/00d一类后续补查参考，不需要现在重跑专项00全文。

---

## 8｜信息来源清单

- agency-agents-zh：[GitHub仓库](https://github.com/jnMetaCode/agency-agents-zh)、[README.md](https://github.com/jnMetaCode/agency-agents-zh/blob/main/README.md)、[UPSTREAM.md](https://github.com/jnMetaCode/agency-agents-zh/blob/main/UPSTREAM.md)、[AGENT-LIST.md](https://github.com/jnMetaCode/agency-agents-zh/blob/main/AGENT-LIST.md)、[CATALOG.md](https://github.com/jnMetaCode/agency-agents-zh/blob/main/CATALOG.md)、[package.json](https://github.com/jnMetaCode/agency-agents-zh/blob/main/package.json)、[marketing-xiaohongshu-operator.md抽查样本](https://github.com/jnMetaCode/agency-agents-zh/blob/main/marketing/marketing-xiaohongshu-operator.md)、[Issues列表](https://github.com/jnMetaCode/agency-agents-zh/issues)（2026-09-01查证6个open issue，均为功能请求类）
- agency-orchestrator：[GitHub仓库](https://github.com/jnMetaCode/agency-orchestrator)、[README.md](https://github.com/jnMetaCode/agency-orchestrator/blob/main/README.md)、[src/core/dag.ts源码](https://github.com/jnMetaCode/agency-orchestrator/blob/main/src/core/dag.ts)（拓扑排序+循环检测逐行核实）、[npm包](https://www.npmjs.com/package/agency-orchestrator)
- 英文上游：[msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents)（GitHub API 2026-09-01直查：149,381 stars/24,083 forks/155 open issues/MIT/创建于2025-10-13）
- 中文社区独立第三方教程（CSDN，非项目方发布）：[《211 个 AI 专家角色，一键安装到你的 AI 工具：agency-agents-zh 完全使用教程》](https://blog.csdn.net/taoanbang/article/details/160261571)、[《agency-agents：211 个即插即用的 AI 专家角色》](https://blog.csdn.net/skywalk8163/article/details/160196731)
- 维护者身份：[jnMetaCode GitHub Profile](https://github.com/jnMetaCode)（GitHub API直查：个人账户，2015年创建，766 followers，127个公开仓库）
- GitHub API原始查证记录（本报告全部stars/forks/issues/license/创建时间/推送时间数字均为2026-09-01当天通过`api.github.com`直接查证的实时快照，非转述第三方文章旧数字）
- 内部交叉引用：`Matbox_专项00_完整AI员工平台横向调研_2026-09-01.md`第1.1/7/8节（方法论盲区与已确认结论）、`Matbox_AI员工身份_正式开发文档_V1.0-RC.md`第5节（EmployeeTemplate九字段schema）、`Matbox_专项15_AI员工身份_技术选型与开发交接报告_2026-08-30.md`（专项15原报告，AIEMP-F001~F005 Top-3结论）、`Matbox_中央编排层_正式开发文档_V1.0-RC.md`与`Matbox_专项12_中央编排层_技术选型与开发交接报告_2026-08-30.md`（ORCHESTRATOR-F001~F005边界与Top-3结论）、`Matbox_AI员工委派_正式开发文档_V1.0-RC.md`与`Matbox_专项19_AI员工委派_技术选型与开发交接报告_2026-08-30.md`（DELEGATION-F001~F005边界与Top-3结论）、`Matbox_AI员工管理控制台_正式开发文档_V1.0-RC.md`（CONSOLE-F001~F005边界）、`Matbox_专项21a_AI员工训练中心_技术选型与开发交接报告_2026-09-01.md`第3.3节（StaffDeck同类型评估先例，方法论参照）
