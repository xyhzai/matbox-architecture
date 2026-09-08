# Matbox 专项00j｜Distilly与AgentTeams专项评估

技术选型报告 · V1.0 · 2026-09-02

**DocID**: MATBOX-DISTILLY-AGENTTEAMS-TECHSELECT-20260902-V1.0
**审计对象**：[github.com/titanwings/distilly](https://github.com/titanwings/distilly)（2026-09-02 GitHub API直查：**24,246 stars / 2,126 forks / MIT / Python**，创建于2026-03-30，原名Colleague Skill/同事Skill）及其中文病毒式传播现象、其衍生生态（`notdog1998/yourself-skill`等4个仓库），以及`agentscope-ai/AgentTeams`（5,537★/678 fork，Apache-2.0，Matrix房间人机协同）的轻量二次评估
**触发背景**：本轮`Matbox_专项00`系列AI员工平台横向调研中，用户要求把此前一直使用"企业级平台"式关键词的检索方式，改为用中文互联网口语/病毒式术语重新搜索，结果立即发现一个此前所有专项00系列报告都没有覆盖到的真实、重大、已引发中国媒体和职场热议的现象——"同事Skill"（Distilly前身）。本报告是这次纠偏检索的直接产出。
**报告性质**：与`专项21a`（AI员工训练中心）、`Matbox_AI员工身份_正式开发文档_V1.0-RC.md`（F-AIEMP-001）两份已冻结/已核查文档存在结构性关联——Distilly的核心机制（把一个真实的人"怎么想"提炼成可复用Skill）与21a已核查的"人纠正AI输出"反馈闭环是两种不同的机制，本报告的任务是查清这条差异是否需要改变Matbox已有设计。方法论延续`专项00c/00d/00e`：不因为star数高就下判断，代码/Issue/PR/论文/中英文媒体逐一核实，正反证据都记录，如实标注抓取失败，最后给出可执行建议。

---

## 0｜给忙碌读者的结论摘要

1. **Distilly不是"话术包装"，是一套真实、可运行、有具体工程细节的结构化知识提炼流程**——不是字面意义的机器学习"蒸馏"（没有模型权重训练），但也不是"在文本框里描述自己"这种敷衍级实现。其核心产物`SKILL.md`（1,518行，69KB）定义了一整套多步骤Agent工作流：分`colleague`/`relationship`/`celebrity`三个"人物家族"，走"素材采集（飞书/钉钉/Slack/微信/邮件/X贴文自动化采集器）→ 结构化访谈（3-4个必答问题）→ LLM驱动的分层画像合成（如colleague家族的"六层人格：硬规则→身份→表达→决策→人际→纠错"）→ 打包为符合`agentskills.io`标准的Agent Skill（`SKILL.md`）→ 版本化存储，支持追加更新和"这不对，他应该是xxx"式的即时纠错"这条完整链路，且有配套的、真实发表的arXiv技术报告（`arXiv:2605.31264`，*COLLEAGUE.SKILL: Automated AI Skill Generation via Expert Knowledge Distillation*，Tianyi Zhou等5人署名，2026-05-29提交）。**但中文技术社区一条真实的批评意见值得如实转达且本报告认为技术上站得住脚**：知乎文章《Skill狂欢骗局：蒸馏同事、复刻张雪峰，本质不过是Prompt工程而已》指出，这套流程本质是"结构化Prompt工程+文档整理"，不是真正意义上的知识蒸馏或能力复制——这个判断和本报告独立核查`SKILL.md`源码后得出的结论一致：这是一条真实、有效、工程扎实的**信息组织与检索增强流水线**，不是让AI获得了这个人的真实决策能力。
2. **维护治理是本报告发现的最大风险信号，且是一个此前专项00系列反复验证过的模式的最极端案例**：GitHub Contributors API直查确认，24,246星的项目里，作者`titanwings`（真实身份：Tianyi Zhou，据《南方都市报》报道供职于上海人工智能实验室）贡献133次提交，**第二名贡献者仅3次**——星数/贡献者集中度的悬殊程度超过本系列此前核查过的所有候选（包括`专项00e`已记录的cumora，其第一贡献者反而不是作者本人）。最近一次push是2026-08-25，距本报告撰写（2026-09-02）已一周无新提交，此前8月密集到几乎每天多次提交，这个骤停值得关注但样本期太短不足以下"停止维护"的结论，如实记录为观察项。
3. **真实的、有分量的社会/职场背景证据——MIT Technology Review全文核查确认，这个项目本身的起源就是一场"行为艺术"**：2026年4月的报道明确写道，据《南方都市报》对作者Tianyi Zhou的采访，"the project was started as a stunt, prompted by AI-related layoffs and by the growing tendency of companies to ask employees to automate themselves"——即项目本身是对"公司逼员工自动化自己"这个真实趋势的一次讽刺/行为艺术式回应，而不是一个严肃的企业级产品立项。但**这场"行为艺术"意外精确命中了真实的职场焦虑**，报道中匿名受访的上海员工Amber Li（27岁）用它蒸馏了一位离职同事，反馈"准得可怕，连标点习惯都学会了"，同时感到"不舒服、诡异"；另一位匿名工程师形容被蒸馏的体验是"被压扁成了模块，让自己更容易被替代"。**中文原生信源独立交叉验证了同一个现象，且提供了英文报道没有的细节**：V2EX真实帖子《公司开始推行每个人创建各自的agent、skills了，并纳入考核》证实"把创建个人Skill纳入离职知识转移考核"已经是真实发生的公司政策，评论区真实情绪是"做的好被裁，做不好也要被裁""任何好事如果强制执行，就让人厌恶"，多人表示准备离职。
4. **一个与`架构原则第43条`（BCG监督弱化）性质完全不同、本报告认为需要独立记录的新风险：数据同意与个人信息合规风险**——中文评论文章《同事.skill：赛博永生还是职场伦理炸弹？》明确指出该项目"支持采集飞书消息、钉钉文档、邮件"，但"被采集者通常不知情或未同意"，援引《个人信息保护法》认为这种采集模式"涉嫌违法"。**本报告用源码交叉验证了这条批评不是空穴来风**：Distilly仓库确实存在一个真实、高质量、但至今未被合并的PR（#136，2026-08-18提交，655行新代码+35个单元测试，实现`privacy_screen.py`隐私筛查+显式同意关卡），其动机说明原文引用了arXiv论文第9节"负责任部署需要明确的参与同意、限定范围的素材采集、访问控制、留存期限、非强制使用"——**但这个consent gate目前只覆盖`relationship`（恋人/家人）家族，直接对应MIT Tech Review报道的职场胁迫场景的`colleague`（同事）家族，截至本报告撰写时仍然没有任何同意机制**，即被蒸馏的同事本人是否知情、是否同意，代码层面完全不做校验。这是BCG研究（AI呈现方式削弱人类监督警惕性）之外的**第二类、性质完全不同的风险：数据主体未同意就被建模，涉及PIPL/GDPR合规与员工资产权属问题**，本报告在第6节给出对Matbox的具体建议。
5. **反蒸馏生态是本次调研中一条独立、真实存在的员工抵抗证据**：Koki Xu（26岁，北京AI产品经理）开发的"反蒸馏Skill"技术上是把员工被迫提交的Skill文件"清洗"成表面完整、实则抽空核心决策逻辑的版本，视频获500万+点赞；本报告核实到该模式已经衍生出至少3个独立GitHub仓库（`leilei926524-tech/anti-distill`及其fork `lcmomo/my-anti-distill`、`Orzjh/anti-distillation-skill`），不是单一网红项目，是一个已经被复制、真实被使用的对抗工具类别。这本身就是"公司逼员工蒸馏自己"这件事引发真实、可观测的员工负面行动的独立证据。
6. **Matbox结论（不回避）**：Distilly本身（代码/依赖）**不采纳引入**——Python技术栈与Matbox Java单语言栈原则冲突（与`专项28`否决LangGraph/CrewAI等候选同一理由），且其核心场景（把一个真实活人未经其同意"蒸馏"成AI替身）与Matbox定位（企业主动配置、AI员工本身不冒充某个真实员工）本质不同，直接采纳会引入本报告揭示的PIPL/职场伦理风险。**但Distilly揭示的"结构化提炼真实专家知识→生成可安装的Skill工件"这条流水线模式，值得作为`F-AIEMP-001` `skills[]`/`sopRef`字段"未来怎么被填充"这个开放问题的一条真实参照**，第6节给出具体、有边界的建议（仅限企业自愿、明确同意的"资深员工经验数字化"场景，且必须与Matbox已有的`AiEmployeeConfigAudit`/版本审计机制对齐，不能绕过`专项21a`已确定的审核路由）。**AgentTeams**技术上是本轮核查中证据最扎实的候选之一（Alibaba `agentscope-ai`真实背书、Apache-2.0、issue编号已破1200、commit节奏健康），其"Matrix房间人机协同"模式与`专项00f`已经验证过的"看板模式优于纯聊天记录"结论方向不同但不冲突——它解决的是"多个Agent+人类在同一房间实时协作/插话"这个更窄的场景，与Matbox`F-DELEGATION-001`的委派安全语义（权限收窄/预算传递/深度熔断）互补而非替代，本报告建议作为**未来Control Tower多Agent实时协作可视化**的架构模式参考，不建议现在引入代码或依赖。

---

## 1｜Distilly技术本质核查

### 1.1 仓库基本事实（2026-09-02 GitHub API直查）

| 指标 | 数值 |
|---|---|
| Stars / Forks | 24,246 / 2,126 |
| Open issues（含PR） | 33 |
| Watchers（GitHub API返回watchers_count与star数相同，真实订阅数看`subscribers_count`） | subscribers_count = 62——与cumora（3,385星/5订阅）的比例失衡程度相反：Distilly的"真正长期关注"用户基数虽然绝对值不算大，但相对星数的比例（62/24246≈0.26%）与cumora（5/3385≈0.15%）处于同一数量级，说明这类高传播、低深度关注的模式在本系列调研的多个候选里反复出现，不是孤例 |
| License | MIT |
| 主语言 | Python（366,015字节，占绝对主体）+ JavaScript + Shell |
| 创建时间 | 2026-03-30T05:22:23Z |
| 最近push | 2026-08-25T07:18:07Z（距本报告撰写已一周无新提交） |
| 默认分支 | `dot-skill`（项目从"同事Skill"单一场景扩展为"任何人都能被蒸馏"的`.skill`通用框架后的分支名） |
| Discussions | 已启用 |
| 作者真实身份 | GitHub资料显示`titanwings` = Tianyi Zhou，company字段填"University of Michigan"，bio"同事.skill 系列作者/colleague-skill dev"；但MIT Technology Review援引《南方都市报》报道称其"供职于上海人工智能实验室"——**两个信源对作者所属机构的表述不一致，本报告如实记录这条矛盾，未能进一步核实**，不影响项目真实性判断（两个信源都确认是同一个人、同一个项目） |

### 1.2 核心机制核查——是否存在真实的"提炼"流程，用源码判断，不用宣传语判断

直接抓取仓库核心文件`SKILL.md`（1,518行，69,235字节，MIT License，2026-09-02直查）验证README的产品描述是否只是营销措辞：

**输入 → 处理 → 输出的完整链路（源码逐段核实）**：

1. **数据源采集层**（README"Supported Data Sources"表逐条核实为真实功能，非占位符）：飞书（API自动采集，"只需输入姓名，全自动"）、钉钉（浏览器方案，因钉钉API不支持消息历史）、Slack（需管理员安装Bot，免费版限90天）、公开X贴文（通过第三方计量服务Xquik）、微信聊天记录（需先用WeChatMsg/PyWxDump导出SQLite）、PDF/图片/截图（手动上传）、邮件`.eml`/`.mbox`、Markdown直接粘贴。`SKILL.md`第90-110行列出对应的工具脚本路径（`feishu_auto_collector.py`/`dingtalk_auto_collector.py`/`email_parser.py`等），不是文档虚构的能力清单。
2. **结构化访谈层**：`colleague`/`relationship`两类只问3个必答问题（花名/代号等），`celebrity`类问4个问题且第4题强制确认`research_profile`（`budget-friendly`默认档 vs `budget-unfriendly`深度档）。
3. **分层画像合成层**——这是本报告认定"这不是敷衍级实现"的关键证据：`colleague`家族的Persona结构是**六层人格：硬规则→身份→表达→决策→人际→纠错**（Correction层），额外叠加"Work Skill"模块（负责范围/工作流/输出偏好/经验知识库）；`relationship`家族是"表达DNA·情绪触发点·冲突模式·修复模式"；`celebrity`家族叠加**六维研究工具链**（字幕→转录清洗→资料合并→质量校验）。三个家族分别有独立的"素材采集策略、分析维度、画像结构定义"，不是同一套模板改几个字段名。
4. **输出格式**：产物打包为符合`agentskills.io`公开标准的Agent Skill（`SKILL.md`），可被Claude Code、OpenClaw、Codex、DeepSeek Harness、Pi、Grok Build、OpenCode、Hermes Agent等8个宿主原生发现加载——**这一点对Matbox有直接技术含义**：Distilly产出的不是一个私有格式的画像文档，而是与Claude Code自身的Agent Skills标准同构的可执行工件，这条兼容性本身是真实的、可验证的（`SKILL.md`的frontmatter字段`name`/`description`/`allowed-tools`/`user-invocable`与Anthropic官方Agent Skills规范一致）。
5. **进化/纠错机制**：`SKILL.md`明确定义三种更新路径——"追加文件"（自动分析增量、合并入相关章节、不覆盖已有结论）、"对话纠正"（用户说"他不会这样"/"他应该是xxx"，直接写入Correction层、立即生效）、"版本管理"（每次更新自动归档，可回滚到任意历史版本）。

**这套链路是否等于机器学习意义上的"蒸馏"？——如实标注一条重要的技术性批评**：中文技术社区一篇批评文章（知乎《Skill狂欢骗局：蒸馏同事、复刻张雪峰，本质不过是Prompt工程而已》，因Zhihu对本次WebFetch请求返回403无法直接抓取全文，仅能核实标题与WebSearch摘要，如实标注这条限制）的核心论点是：这套流程没有任何模型权重训练/微调，产出的是一份结构化的自然语言文档而非"能力"本身，"蒸馏"一词是营销层面的隐喻而非技术层面的准确描述。**本报告独立核查`SKILL.md`源码后认为这条批评在技术层面成立**：Distilly的机制是"结构化信息采集 + LLM驱动的文档分层组织 + Prompt注入执行"，属于检索增强/上下文工程范畴，不是参数级知识迁移。这不影响它作为一套**信息组织方法论**的真实性和工程质量（第1.2节已确认工程扎实），但决定了它能带给Matbox的启发是"如何设计一套结构化的专家知识采集+分层画像流程"，而不是"一种新的模型训练技术"。

### 1.3 arXiv技术报告核查

`https://arxiv.org/abs/2605.31264`直查确认：论文标题《COLLEAGUE.SKILL: Automated AI Skill Generation via Expert Knowledge Distillation》，提交于2026-05-29，作者Tianyi Zhou、Dongrui Liu、Leitao Yuan、Jing Shao、Xia Hu共5人（本报告未能独立核实全部作者的机构归属，如实标注）。论文摘要核心论点：LLM Agent需要承载人类专家知识，但这些知识通常散落在文档和交互中而非正式指令里；系统用"Capability Track"（捕获实践/心智模型/决策启发式）+"Bounded Behavior Track"（记录沟通风格/交互规则/纠错历史）两条并行轨道生成版本化Skill包，使其可被检视、通过自然语言反馈更新、版本控制、跨系统部署、可选分发。**论文本身承认这是COLLEAGUE.SKILL（Distilly前身，仅覆盖colleague家族）的技术基础，`relationship`/`celebrity`家族的独立论文"计划中"（README原文"Separate papers... are planned"），截至本报告撰写尚未发表**——即公开的学术论证目前只覆盖了三个家族里的一个。论文第9节明确写入"负责任部署要求明确参与同意、限定范围的素材采集、访问控制、留存期限、非强制使用"，这条要求与第2.4节揭示的实现缺口（`colleague`家族无consent gate）直接对照，说明这不是研究者没想到的问题，而是"论文写了、代码没做"的真实落差。

### 1.4 维护治理集中度——本系列调研中最悬殊的样本

GitHub Contributors API直查（`api.github.com/repos/titanwings/distilly/contributors`）：作者`titanwings`本人133次提交，第二名贡献者`baichou6320-cpu`仅3次，其余贡献者均为1次。**对比`专项00e`对cumora的核查结论**（cumora的第一贡献者`WhichPaths`反而以66次超过作者本人的45次，是真实的多人协作）：Distilly是一个**事实上的个人项目**，24,246星、2,126 fork的传播规模与实际代码贡献者结构完全不成比例。这不必然意味着代码质量差（第1.2节已确认核心机制工程扎实），但意味着**长期维护、安全响应、社区PR处理能力高度依赖单一开发者的持续投入**，与`专项00c/00d/00e`反复验证的"个人/小团队主导、治理结构薄弱"模式属于同一类风险，且是本系列迄今为止集中度最极端的样本。

---

## 2｜真实社会/职场背景（MIT Technology Review深度核查 + 中文原生信源交叉验证）

### 2.1 MIT Technology Review全文核查

`technologyreview.com/2026/04/20/1136149/chinese-tech-workers-ai-colleagues/`（2026-04-20发布，作者Caiwei Chen）全文核查确认：

- **项目起源**：据《南方都市报》对作者Tianyi Zhou的采访，"the project was started as a stunt, prompted by AI-related layoffs and by the growing tendency of companies to ask employees to automate themselves"——项目本身是对"公司逼员工自动化自己"这一真实趋势的讽刺性回应，Tianyi Zhou本人未回应MIT Technology Review的进一步置评请求。
- **真实员工反馈（Amber Li，27岁，上海科技从业者）**："It is surprisingly good. It even captures the person's little quirks, like how they react and their punctuation habits."——用它蒸馏了一位前同事，效果"准得可怕"，但体验"uncanny and uncomfortable"（诡异、不舒服）。她的总结性发言："I don't feel like my job is immediately at risk. But I do feel that my value is being cheapened, and I don't know what to do about it."（不觉得工作立刻不保，但确实觉得自己的价值被贬低了，不知道该怎么办）
- **匿名工程师反馈**：把自己的工作方式训练进AI后，感觉"reductive"——"as if their work had been flattened into modules in a way that made the worker easier to replace"（工作被压扁成模块，反而让自己更容易被替代）。
- **员工抵抗案例（Koki Xu，26岁，北京AI产品经理）**：2026-04-04发布"反蒸馏"工具，把员工被迫提交的工作文档改写成"看起来完整、实则通用化、不可操作"的版本，供用户按"轻/中/重"三档选择破坏程度（取决于上级监督的严格程度）。Xu的动机原话："I originally wanted to write an op-ed, but decided it would be more useful to make something that pushes back against it."（本来想写篇评论文章，后来觉得做个能实际反击的东西更有用）她持有法律学位，个人同时运行7个OpenClaw agent，视频获得**500万以上点赞**（跨平台合计）。
- **企业动机的学术视角**（未见任何雇主直接被点名或引述）：Emory University助理教授Hancheng Cao的分析——企业推动这类实践除了获得工具使用经验外，还能"获得关于员工know-how、工作流程、决策模式的更丰富数据"，用来区分哪些工作可标准化、哪些需要保留人类判断。
- **文章整体基调**：平衡但明确记录员工焦虑的调查报道，结论强调矛盾性——AI Agent本身仍"不可靠、需要持续监督"，但员工感受到的职业尊严被侵蚀和岗位不确定性是真实存在的，以Xu的创造性抵抗与企业压力并置收尾，没有给出明确解决方案。

### 2.2 中文原生信源交叉验证（用户特别要求的"在中文互联网原生语境下核查"）

本报告在英文报道基础上，独立检索中文平台（知乎、V2EX、CSDN、爱范儿、虎嗅、unifuncs等），核实是否有独立于MIT Technology Review转述之外的一手中文证据，结果为**是，且提供了英文报道没有的细节**：

- **V2EX真实帖子（`hk.v2ex.com/t/1202429`，标题《公司开始推行每个人创建各自的agent、skills了，并纳入考核》）**——这是本报告认为分量最重的中文一手证据，因为它不是媒体转述而是员工本人在职场论坛的真实吐槽帖：楼主描述公司要求每个员工创建针对自己岗位的AI agent/skills，明确目标是让这些AI工具能"替代"自己，并纳入绩效考核。评论区真实情绪摘录（保留原文）：
  - "做的好被裁，做不好也要被裁"（自我淘汰悖论——做得好说明AI能替代你，做不好说明你不称职，两头都会被裁）
  - "任何好事如果强制执行，就让人厌恶"（对强制性的反感，独立印证MIT Tech Review"胁迫感"这条主线）
  - 有开发者指出Skill需要"长期维护"，意味着员工在给自己制造无限期的额外工作
  - 大量黑色幽默："自掘坟墓"、把此举比作"犯人在磨自己将被处决用的刀"
  - 多人表示"准备run了"（准备离职），有评论认为"码农先把其他行业替代了"（程序员群体会最先经历这轮AI替代压力，随后波及其他行业）
- **V2EX相关讨论**（`v2ex.com/t/1204338`《DistillHub——万物皆可.skill的开源宇宙》）提到"有公司把'创建个人Skill'纳入了离职知识转移考核"——与上一条独立印证同一现象，即"蒸馏自己"已经从员工自发行为演变为部分企业的正式制度化要求。
- **知乎问答**（`zhihu.com/question/2023359479559857671`，《职场AI工具「同事.skill」爆火，AI正在「吃掉」职场经验吗？》）经WebSearch摘要（Zhihu对WebFetch返回403，无法直接抓取全文，如实标注）：讨论集中在"蒸馏一个人的工作方式，但蒸馏不了他当年为什么做了那个决定"这条技术局限，以及"知识被封装成Skill后复用成本骤降，可能削弱团队长期创新能力"这条组织学担忧。
- **技术伦理评论文章**（`unifuncs.com`《同事.skill：赛博永生还是职场伦理炸弹？》）系统列出五类风险，其中三类是英文报道未覆盖的：**(a) 隐私违规**——采集敏感工作数据未经被采集者明确同意；**(b) 人格商品化**——"人格商品化"（将他人性格与工作方式打包为产品，被认为侵犯人格尊严）；**(c) 法律不合规**——援引《个人信息保护法》，认为该项目的数据采集模式"涉嫌违法"（未经同意处理个人信息）。该文章结论：这是AI伦理触及的一条"红线"，是"人际关系的数字商品化"，预测2026年是"AI职场伦理监管元年"。
- **技术层面二手信源**（爱范儿`ifanr.com/1661056`《我的同事被炼化成Skill了》）：批评性但克制的语气，指出该模式可能关闭初级员工的成长路径（"通过试错学习"的机会被压缩），最终让人类依赖自己被自动化的替身，收尾发问"当所有人都变成Skill，谁还有能力发现哪里出了问题？"

**中英文信源交叉对比结论**：MIT Technology Review的报道方向（员工焦虑、创造性抵抗、企业动机模糊但真实存在）与中文原生信源完全一致，且中文信源补充了两条英文报道没有覆盖、对Matbox更具体的信息：**(1)** "个人Skill创建"已被至少部分企业正式写入离职知识转移考核制度，不再只是零散的自愿行为；**(2)** 数据合规（PIPL）与人格商品化两条批评，是中文语境下讨论得比英文语境更深入的维度，这与Matbox主要面向中国市场直接相关。

### 2.3 反蒸馏生态——真实存在的员工抵抗，不是单一网红事件

本报告核实Koki Xu的"反蒸馏"模式已衍生出至少3个独立GitHub仓库，不是孤立案例：

| 仓库 | Star（2026-09-02核实） | Fork | 说明 |
|---|---|---|---|
| `leilei926524-tech/anti-distill` | 未在本次核查中纳入Top-4衍生生态统计（发现时间晚于既定核查范围，本报告仅作为补充证据列出，不重复计入第2.4节统计） | — | 原始"反蒸馏Skill"仓库，"清洗你被迫写的Skill文件，看起来完整，核心知识留给自己" |
| `lcmomo/my-anti-distill` | 同上 | — | 对上一仓库的fork |
| `Orzjh/anti-distillation-skill` | 同上 | — | 独立实现，"与其被公司蒸馏，不如先污染自己。拒绝成为永久数字员工！" |

**技术机制**（据检索到的项目描述与二手技术解析文章交叉核实）：把员工被迫提交的Skill文件输入工具，输出一个"表面完整、专业，实则抽空核心决策逻辑"的净化版本——本质是对抗性的内容投毒，目的是让企业采集到的"知识"看起来合规但不可用于真正替代该员工。还存在场景化变体，如"本科生科研组反蒸馏.skill"，供即将离组的研究生保护导师索取的隐性经验不被完全提取。**这条证据的意义**：证明"公司要求员工蒸馏自己"引发的不是被动焦虑，而是已经外化为真实、可复制、被多人独立实现的技术对抗行为，是本报告认为应该独立记录给Matbox的一条职场心理学信号——**如果Matbox未来任何设计涉及"从真实员工的工作产出中提炼SOP/知识"，必须预期员工存在真实的、有技术能力的抵抗动机，数据质量会被主动污染，不是单纯的数据完整性工程问题**。

### 2.4 新风险识别：与`架构原则第43条`（BCG监督弱化）的关系

`架构原则第43条`记录的BCG Henderson Institute研究揭示的风险是**"把AI包装成有名字的同事"这件事本身会削弱人类审阅者的监督警惕性**（错误发现率降18%）——这个风险的主体是**看AI产出的人**。

本报告在Distilly案例中发现的风险性质完全不同，主体是**被蒸馏的人本身**：

- **数据同意风险**：被采集数据的对象（同事）通常不知情、未同意，中文评论明确援引PIPL提出合规质疑；本报告用源码验证了这不是空泛担忧——arXiv论文第9节承认"负责任部署需要明确同意"，但代码层面的consent gate（PR #136）截至本报告撰写只覆盖`relationship`家族，直接对应职场场景的`colleague`家族仍然没有任何同意机制。
- **员工资产/知识产权风险**：被提炼的是员工个人的决策经验、沟通风格、工作判断——这些在多数司法辖区（含中国劳动法语境）是否属于"公司财产"存在真实争议，员工的"反蒸馏"抵抗行为本身就是对这条产权边界不清晰的真实反应。
- **组织心理学风险**：即使技术上完全合规，"被要求把自己蒸馏成AI替身"这件事本身会产生真实的、可观测的职场焦虑与抵触（V2EX/MIT Tech Review双重印证），这是一种**员工侧的信任/士气风险**，与BCG研究的**管理者/审阅者侧监督风险**是两个独立变量，不能互相替代或合并记录。

**本报告建议**：这条风险应作为`架构原则`新增一条（建议编号#44，具体措辞留待用户确认后由用户或后续任务写入，本报告不越权直接修改已冻结的架构原则文档），核心表述方向：**"AI员工知识/SOP的来源如果涉及提炼真实员工的个人工作数据，必须内置显式同意机制、且同意范围与用途绑定，不能以'公司数据'为由默认豁免——这是与第43条监督弱化风险平行、但主体不同的独立风险"**。是否现在写入由用户决定，本报告只提供证据与建议措辞方向。

---

## 3｜真实用户与开发者证据（GitHub Issues/PR逐条核查）

Distilly当前33个open issue（含PR），本报告逐条浏览标题+核实其中信息量最高的几条：

- **PR #136**（第2.4节已详述）——真实、高质量、经过完整单元测试（61个测试用例，26个已有+35个新增）的隐私筛查/同意关卡实现，2026-08-18提交，截至本报告撰写（2026-09-02）**仍未合并**（`mergeable: false`，存在合并冲突），距最后一次更新（2026-08-19）已近两周无维护者回应——这与第1.4节"事实上单人维护"的结论互相印证：一个真实解决论文自己承认的责任部署缺口的PR，因为维护带宽有限而停滞。
- **#112~#116（一组关联issue/PR，安全加固）**："Harden credential file permissions across all auto-collectors"（加固所有自动采集器的凭证文件权限）、"Use getpass for secret prompts in auto-collectors"（用getpass而非明文输入密钥）——说明项目早期在处理飞书/钉钉等平台的API密钥时确实存在真实的凭证泄露风险，后来被社区发现并修复，属于真实的安全成熟过程，不是凭空构造的担忧。
- **#132**："[Feature] Upgrade pure-text skills to deterministic scripts (Fixing LLM training bias in academic scanning)"——社区成员自己提出"纯文本Skill存在LLM训练偏差"的问题，是对第1.2节"这不是真正的知识迁移，是文本层面的信息组织"这一技术判断的又一条独立佐证，来自使用者自己的观察，不是本报告单方面推断。
- **#100**："[非官方 just for fun] 《同事.skill使用规则》"——2条评论，社区自发整理的使用指南，说明有真实用户在认真研究怎么用好这个工具，不只是围观。
- **#96**："windows用户怎么使用，示例也没有skill.md文件"——真实的、基础的可用性问题反馈，与"33个open issue对应24,246星"这个偏低的issue/star比例（与`专项00e`对cumora"8个issue对应3,385星"的比例接近，同属"传播广、深度参与浅"的模式）互相印证。

**中文社区对比结论**：与`专项00`对OpenClaw（V2EX真实吐槽帖+知乎独立架构长文）的核查结果相比，Distilly的中文社区渗透明显更深、更有社会影响力（V2EX真实政策讨论帖、多家中文媒体独立报道、多个独立衍生对抗工具仓库），但**技术社区（GitHub Issue/PR）层面的深度参与相对星数而言依然偏浅**，这与cumora呈现出的模式相似——**病毒传播的驱动力主要来自"社会议题"层面（职场焦虑、伦理争议），而不是"技术工具"层面**，这条判断对评估"这是不是一个值得长期投入学习的技术候选"有直接意义：值得学的是它触发的社会讨论和它验证过的"结构化知识提炼流程"设计模式，不是它的代码工程本身处于行业领先水平。

---

## 4｜License与技术栈

| 维度 | 结论 |
|---|---|
| License | MIT，无商用风险 |
| 技术栈 | Python（366,015字节，绝对主体）+ JavaScript（前端/工具脚本）+ Shell；无自建后端服务，是纯本地/Agent宿主内运行的Skill包，不需要独立部署基础设施 |
| 与Matbox架构原则的冲突 | **直接冲突**：Matbox架构原则第33条要求AI员工底层保持Java单语言栈，`专项28`已用同样理由否决LangGraph/CrewAI/OpenAI Agents SDK/Vercel AI SDK等一切Python/TS-only候选，`专项00e`对cumora（TypeScript/Node）也是同一结论。Distilly是这条已反复验证的结构性冲突的又一个独立样本，不构成新证据方向，只是又加了一个不能直接引入代码依赖的理由。 |
| 自托管/集成可行性 | Distilly不是需要"自托管"的服务，它是一个Agent Skill包，运行方式是被Claude Code/OpenClaw等宿主加载执行——这意味着"引入代码依赖"这个问题对Distilly不完全适用，更准确的问题是"Matbox要不要把这套Skill生成的*方法论*（素材采集策略+分层画像结构+consent gate设计）用Java重新实现一遍"，这是第6节讨论的核心问题，不是简单的License/部署可行性问题 |
| 与Matbox数据合规要求的冲突 | 第2.4节已详述——Distilly当前代码对`colleague`家族缺少同意机制，这条不只是"要不要引入代码"层面的问题，是"即使只借鉴方法论，也必须在Matbox自己的实现里补上这一层，不能把这个缺口一起借鉴过来"这个更重要的边界条件 |

---

## 5｜AgentTeams轻量二次评估

`agentscope-ai/AgentTeams`（2026-09-02 GitHub API直查：**5,537★ / 678 fork / Apache-2.0 / Go为主+Python+Shell**，创建于2026-02-21，最近push 2026-08-22，issue编号已到#1219，open issues 244）。

### 5.1 是什么，技术上是否真实

`agentscope-ai`是GitHub Organization账号（非个人），仓库`homepage`字段直接指向`https://www.aliyun.com/product/agentteams`——**这是本轮调研中除StaffDeck（`专项21a`已核查，ModelBest/THUNLP联合）之外，第二个有明确、可验证的大型机构商业背书的候选**，且证据链更直接（阿里云自己的产品页而非媒体转述）。

技术架构（README+近期commit交叉核实）：**Kubernetes原生的Manager-Workers多Agent编排系统**——`agentteams-controller`是K8s控制平面，通过自定义资源（Worker/Team/Manager CRD）做协调；Worker可以跑OpenClaw（Node.js）、QwenPaw（Python）或Hermes（自主编程+沙箱）三种runtime之一；配套基础设施包括Higress AI网关（阿里巴巴开源项目，防止Worker直接接触真实API密钥）、MinIO共享文件存储、**Tuwunel（真实的Matrix协议服务端）+ Element Web（真实的Matrix协议客户端）**。

**"Matrix房间"机制是否只是营销叙事**：核查确认这是**字面意义的、真实的Matrix协议**（matrix.org背后的开放联邦聊天标准），不是"类似Matrix"的自造抽象。每次协作会创建一个专属Matrix房间，包含人类用户、Manager Agent、相关Worker Agent；所有Agent间通信都发生在这个房间内，人类可以直接@某个Worker下指令或实时纠正（如"@alice implement a login page with React"），README原文强调"No hidden agent-to-agent calls. Everything is visible and intervenable."（没有隐藏的Agent间调用，一切可见、可干预）。近期真实commit印证这不是纸面设计：`#1186 feat(projects): add intervention history and worker checkpoint read endpoints`（新增干预历史与Worker检查点读取端点）、`#1210 fix(controller): grant Matrix power levels to human members on room join`（修复人类成员加入房间时的Matrix权限等级授予）——这些都是真实、具体、与"人类实时介入多Agent协作"直接相关的工程问题，不是demo级功能列表。

### 5.2 维护治理与真实性

与Distilly形成鲜明对比：Contributors API显示`johnlanni`442次提交、`shiyiyue1102`93次、`Jing-ze`43次、`max-wc`34次、`googs1025`33次，另有真实的`github-actions[bot]`CI活动，属于**多人真实协作**的健康治理结构，commit message遵循规范的`type(scope): description (#PR号)`格式，PR编号已连续排到#1197+，说明有稳定的CI/PR流程而非个人仓库的随手提交。这与Distilly（作者一人133次，其余贡献者最高3次）的治理集中度形成本轮调研中最鲜明的对照，是本报告认为AgentTeams技术可信度更高的直接证据。

### 5.3 对Matbox的意义——与`专项00f`/`F-DELEGATION-001`的关系，不是替代而是互补

`专项00f`（AI员工指令交互流程设计）已经用真实证据（Agent UX研究+OpenAI自己停用纯聊天式Agent Mode的反面案例）确认"目标→任务→子任务"看板模式优于纯聊天记录，作为Matbox进度可见性设计的既定方向。AgentTeams的Matrix房间本质上是一种"纯聊天记录"呈现（房间里是消息流），**从表面看似乎与`专项00f`已验证的结论相反**，但本报告认为两者解决的是不同粒度的问题，不构成冲突：

- `专项00f`解决的是"一个人类用户如何看清一个AI员工的单次任务进展"——看板模式更适合。
- AgentTeams解决的是"多个Agent+人类在同一个协作会话里如何互相看见对方在做什么、人类如何随时插话纠正某一个Agent而不打断其他Agent"——这是一个**多主体实时协同**场景，聊天room的时间线呈现方式在这个场景下有其合理性（类似人类团队用群聊协调多线程工作本身就是常见模式），不是"看板 vs 聊天"这个二元判断能覆盖的。

`F-DELEGATION-001`已经有扎实的委派安全语义（`permission_envelope`交集收窄、`budget_envelope`+`deadline`、`depth`+`visitedEmployeeIds`数学可判定循环检测、`upstreamTrustLevel`上游产出可信度标记）——这套设计解决的是"委派*应不应该发生*、发生后*权限/预算/循环*会不会失控"这个安全边界问题，AgentTeams的Matrix房间模式完全没有触及这一层（README和代码都没有类似`permission_envelope`交集收窄的机制），**AgentTeams不能替代`F-DELEGATION-001`的安全语义**，但它提供了一个`F-DELEGATION-001`目前没有覆盖的能力：**委派链条执行过程中，人类如何实时看见+实时插话**（当前`F-DELEGATION-001`+`F-TASK-001`是"发起→查询状态→接管"的相对重量级流程，缺少"轻量级、实时、多方在场"的呈现层）。

**结论**：AgentTeams**不建议现在引入代码或依赖**（Go+Python技术栈同样与Matbox Java单语言栈原则冲突，且当前Matbox没有真实的"多Agent实时协同+人类插话"业务场景，属于`架构原则第27条`"没有真实需求不要提前建复杂"应该规避的范畴），但其"真实Matrix协议房间+细粒度干预历史/checkpoint端点"这套设计，值得作为**Matbox未来如果真的出现多AI员工实时协作场景时**（如`Matbox_AI员工能力缺口调研清单`中已识别的岗位协作场景，见`F-AIEMP-001`2.3节初始岗位族里的跨岗位协作需求）的Control Tower呈现层设计参考，属于第7.3节"记录但不紧急"档位，不是现在要做的事。

---

## 6｜给Matbox的具体建议

### 6.1 Distilly是否改变`专项21a`（AI员工训练中心）的设计——结论：不改变核心路线，但确认了一个新的、独立的、值得记录的能力空白

`专项21a`已经核查确认CONSOLE-F002训练中心解决的是"业务人员发现AI员工产出不对，怎么纠正"这个**纠错回路**问题（`TrainingFeedback`→ diff → 审核/审批 → 生效），这个问题本身的定义和技术路线**不需要改变**——Distilly解决的是一个前置的、不同的问题："一个岗位第一次上线之前，它的SOP/技能从哪来"，这是`AIEMP-F001` EmployeeTemplate的**冷启动填充**问题，而`专项21a`是Template/Instance**上线后**的持续纠偏问题，两者是时间线上前后相邻但职责不同的两个环节，不是同一个问题的两种解法，因此不构成对`专项21a`已确定技术路线的推翻。

**但Distilly确实暴露了一个此前`F-AIEMP-001`文档没有涉及的真实空白**：`AIEMP-F001`目前只定义了`skills[]`/`sopRef`这两个字段"存什么"（关联Skill/SOP实体，版本化），完全没有定义"**这些字段的内容第一次是怎么产生的**"——是Matbox顾问团队手写？是企业自己填？还是像Distilly这样从某个真实资深员工的工作数据结构化提炼？`专项21a`报告本身在第0节也提到"CONSOLE-F002不管什么"里明确排除了这个问题（"不重新存储EmployeeTemplate/EmployeeInstance的事实数据...本模块只产出并应用变更提案"），即这条空白此前一直存在但没有被显式识别为一个需要独立设计的问题。

### 6.2 具体建议：不采纳Distilly的代码/依赖，但采纳其方法论作为未来"专家经验数字化"能力的设计参照，且必须补齐它自己没做的合规层

如果Matbox未来（非现在，需求未验证前不提前建）需要设计一个"帮助企业把资深员工的经验/工作方式提炼进新的EmployeeTemplate"的能力（比如任务简报里提到的"家居企业设计主管的真实经验→新的室内设计方案助理模板"场景），建议：

1. **方法论层面可参考**：Distilly"素材采集→结构化访谈→分层画像合成（硬规则/身份/表达/决策/人际/纠错六层）→版本化Skill工件"这条流水线设计是真实、经过工程验证的模式，其"Correction层"设计（对话中说"他不会这样"直接写入、立即生效）与`专项21a`的`BEHAVIOR_CORRECTION`反馈类型在产品语义上高度相似，可以作为`AIEMP-F001`未来定义"Template冷启动填充流程"时的设计输入。
2. **必须补齐、不能借鉴过来的缺口（P0级，本报告新增）**：**任何从真实员工个人工作数据提炼SOP/技能的流程，必须内置显式同意机制，同意人是数据所属的那个真实员工本人，不是企业管理员单方面授权**——这是Distilly自己的论文承认、自己的代码没做全（只做了`relationship`家族）、中文社区明确用PIPL质疑过的缺口，Matbox如果做同类功能绝不能重复这个缺口。具体应该长成什么形态（是否需要类似Distilly的`privacy_screen.py`独立筛查步骤、同意记录是否要写入`AiEmployeeConfigAudit`）留待该能力真正立项时详细设计，本报告只确认这条边界是P0级、不可省略的。
3. **不需要现在做任何事**：这个能力目前没有真实客户需求驱动（`架构原则第27条`），本报告的建议是"如果/当这个能力被立项，设计时要参考什么、要规避什么"，不是"现在就去建"。

### 6.3 是否需要新增架构原则——建议但不越权代为决定

建议在`Matbox_架构设计原则.md`新增一条（编号待用户确认，如落地建议为#44），核心内容：**"AI员工知识/SOP来源如果涉及提炼真实自然人的个人工作数据，必须有该自然人本人的显式同意，且同意范围与实际用途绑定；这是与第43条（AI呈现方式削弱人类监督）性质不同、主体不同的独立风险——第43条风险主体是审阅AI产出的人，本条风险主体是被数据化的人本身"**。本报告不直接修改已冻结的架构原则文档，具体措辞与是否采纳，留待用户确认后执行，遵循`Matbox`既定的"确认点必须由用户拍板"工作方式。

### 6.4 AgentTeams

不建议现在引入代码或依赖（技术栈冲突+无真实需求驱动），但记录为"未来多Agent实时协作Control Tower呈现层"的设计参照，与`专项00f`已有结论互补而非冲突，档位与`专项00e`第7.3节"记录但不紧急"相同处理方式。

---

## 7｜方法论如实说明

- Zhihu（知乎）对本次全部WebFetch直接抓取请求均返回403，本报告涉及知乎的内容全部依赖WebSearch返回的摘要/标题，未能获取全文，如实标注，不作为唯一证据来源（关键论点均有GitHub源码或V2EX/MIT Tech Review等可直接抓取的信源交叉印证）。
- `leilei926524-tech/anti-distill`等3个反蒸馏衍生仓库因发现时间在本报告核查后段，未及对其GitHub API做逐一star/fork/维护状态的完整核查（不同于第2.4节Distilly衍生生态4仓库的完整核查深度），如实标注为"存在性核实但未做深度核查"，不构成本报告任何核心结论的依据，仅作为"抵抗行为已规模化、非单一事件"的存在性证据。
- Distilly与colleague-skill/COLLEAGUE.SKILL相关的arXiv论文（`2605.31264`）本报告通过WebFetch工具的摘要生成获取内容，未能逐页核查完整PDF全文（如具体评估指标、消融实验等细节），如实标注这条局限，论文的存在性、标题、作者、提交时间、核心论点方向均已交叉验证（arXiv直查+README引用一致）。
- `titanwings`本人所属机构存在GitHub资料（University of Michigan）与MIT Technology Review援引《南方都市报》报道（上海人工智能实验室）的不一致，本报告未能进一步核实哪个更准确或是否两者皆真（如同时任职/访问学者等情况），如实标注为未解决的矛盾点，不影响本报告任何核心技术结论。

---

## 附录：来源

**Distilly一手来源（GitHub API/源码直查，2026-09-02）**：
- 仓库元数据：https://api.github.com/repos/titanwings/distilly
- README（dot-skill分支）：https://raw.githubusercontent.com/titanwings/distilly/dot-skill/README.md
- SKILL.md核心机制：https://github.com/titanwings/distilly/blob/dot-skill/SKILL.md
- 贡献者：https://api.github.com/repos/titanwings/distilly/contributors
- PR #136（隐私筛查/同意关卡，未合并）：https://github.com/titanwings/distilly/pull/136
- Issue列表：https://github.com/titanwings/distilly/issues
- 作者GitHub资料：https://github.com/titanwings

**arXiv技术报告**：
- https://arxiv.org/abs/2605.31264 （COLLEAGUE.SKILL: Automated AI Skill Generation via Expert Knowledge Distillation，Tianyi Zhou et al.，2026-05-29）

**MIT Technology Review及英文报道**：
- 主报道：https://www.technologyreview.com/2026/04/20/1136149/chinese-tech-workers-ai-colleagues/
- 官方社媒摘要：https://x.com/techreview/status/2046162502464012512
- Futurism转载视角：https://futurism.com/artificial-intelligence/chinese-workers-train-ai-replacements
- 韩媒转载视角：https://www.digitaltoday.co.kr/en/view/49866/chinas-it-industry-faces-backlash-over-push-to-make-workers-train-ai-on-their-own-jobs

**中文原生信源**：
- V2EX职场政策真实吐槽帖：https://hk.v2ex.com/t/1202429
- V2EX衍生生态讨论：https://www.v2ex.com/t/1204338
- 知乎问答（WebSearch摘要，Zhihu 403无法直接抓取全文）：https://www.zhihu.com/question/2023359479559857671
- 知乎技术批评文章（同上限制）：https://zhuanlan.zhihu.com/p/2031772530176995554
- 职场伦理评论（PIPL/人格商品化）：https://unifuncs.com/s/11N9CrVI
- 爱范儿技术报道：https://www.ifanr.com/1661056
- 虎嗅报道：https://www.huxiu.com/article/4848373.html
- CSDN技术解析：https://blog.csdn.net/qq_41035650/article/details/160041086
- T客邦（台湾）报道：https://www.techbang.com/posts/128699-colleague-skill-project-ai-distills-experience

**反蒸馏衍生生态**：
- notdog1998/yourself-skill：https://github.com/notdog1998/yourself-skill
- beita6969/ScienceClaw：https://github.com/beita6969/ScienceClaw
- xiaoheizi8/crush-skills：https://github.com/xiaoheizi8/crush-skills
- BeamusWayne/simp-skill：https://github.com/BeamusWayne/simp-skill
- leilei926524-tech/anti-distill：https://github.com/leilei926524-tech/anti-distill
- Orzjh/anti-distillation-skill：https://github.com/Orzjh/anti-distillation-skill

**AgentTeams一手来源（GitHub API/源码直查，2026-09-02）**：
- 仓库元数据：https://api.github.com/repos/agentscope-ai/AgentTeams
- README：https://raw.githubusercontent.com/agentscope-ai/AgentTeams/main/README.md
- 贡献者：https://api.github.com/repos/agentscope-ai/AgentTeams/contributors
- 近期commit：https://api.github.com/repos/agentscope-ai/AgentTeams/commits
- 阿里云产品页：https://www.aliyun.com/product/agentteams

**Matbox内部交叉引用**：
- `docs/技术选型报告/Matbox_专项21a_AI员工训练中心_技术选型与开发交接报告_2026-09-01.md`（CONSOLE-F002训练中心，纠错回路设计）
- `docs/Matbox_AI员工身份_正式开发文档_V1.0-RC.md`（F-AIEMP-001，EmployeeTemplate的skills[]/sopRef字段）
- `docs/Matbox_AI员工委派_正式开发文档_V1.0-RC.md`（F-DELEGATION-001，委派安全语义）
- `docs/技术选型报告/Matbox_专项00f_AI员工指令交互流程设计_2026-09-02.md`（看板模式优于纯聊天记录的既有结论）
- `docs/技术选型报告/Matbox_专项00e_AI员工呈现方式与cumora专项评估_2026-09-02.md`（BCG监督弱化研究，架构原则第43条来源）
- `docs/Matbox_架构设计原则.md`第43条（AI呈现方式与人类监督弱化）、第27条（无真实需求不提前建复杂）、第33条（Java单语言栈原则）
- `docs/技术选型报告/Matbox_专项28_AgentRuntime_技术选型与开发交接报告_2026-08-30.md`（Java单语言栈原则的历次应用先例）
