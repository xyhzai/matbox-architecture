# Matbox 输出监督层 / Supervisor + Monitor（F-SUPERVISOR-001）

正式开发文档 · V1.0-RC · 2026-08-30

## 当前定位

本专项解决"AI员工生成的对话内容/文案本身，发给人类（内部员工或终端消费者）之前，有没有人/机制检查"的问题——这是本会话"AI员工能力缺口调研清单"#3，直接命中一个现有安全空白：F-ACTION-001只管"有副作用的动作"（调工具、改数据），**AI员工说的话本身完全没有治理**。

**这不是凭空造概念，是给已有policy定义补一个执行层**：F-AIEMP-001的EmployeeTemplate已经定义了`forbidden_actions`/`permission_policy`字段，本模块要做的是"在AI员工的输出真正发给用户之前，检查有没有违反这些已经定义好的规则"。

**是否现在设计的论证（2026-08-30，用户已确认执行）**：Supervisor子层（实时检查，基于已有policy）不依赖真实流量就能设计对；Monitor子层"连贯性/情绪异常"这类具体判断阈值确实依赖真实对话数据才能精调，标注为继续断点，不影响整体架构现在成型。这是#9(独立站匿名访客场景)能否真正上生产的前提——面向陌生公众的AI员工，没有这层就没有安全网。

**DocID**: MATBOX-SUPERVISOR-20260830-V1.0-RC
**状态**: DRAFT_RESEARCH_COMPLETE（内容级核查通过，未进入 Stage 10 真实施工）
**依赖方（已知阻塞）**：F-AIEMP-001（policy规则来源，已建成）、F-OBS-001（检查记录留痕，已建成）、F-EGRESS-001（不可信内容处理原则，已建成）

## 1｜不可变原则

1. 任何AI员工生成的、将要发送给人类（内部员工或终端消费者）的内容，必须先经过Supervisor实时检查，才能真正发出。
2. Supervisor检查基于EmployeeTemplate已定义的forbidden_actions/permission_policy，不允许绕过或另建一套平行规则体系。
3. Monitor异步复查覆盖率必须是100%（每条对话都过一遍），不能抽样，防止问题在抽样盲区里累积。
4. Supervisor/Monitor发现问题时必须留痕（写入F-OBS-001），不能静默拦截或静默放行。
5. 面向匿名终端消费者（独立站等公开场景）的输出，Supervisor检查级别不能低于面向内部员工的级别——反而应该更严格，因为面向公众的错误是公开的品牌风险。
6. Supervisor检查失败或不可用时必须fail-closed（阻断输出），不允许fail-open（放行）。

## 2｜全球调研结论（2026-08-30，两轮调研）

### 2.1 真实架构参照——Sierra的双层设计

Sierra（估值$10B，企业客服AI员工，$150K+/年合同）的真实运行时安全机制是**两套**，不是一套：
- **Supervisor**（实时，在对话过程中当场核实事实/执行policy，能"悄悄纠正"）
- **Monitor**（异步，事后review每一条对话，查连贯性/重复度/事实依据/情绪）

两者搭配"deterministic guardrails"（硬性业务规则，独立于模型自身判断）。真实G2客户评价正面（"AI智能确实帮上了忙"），但有诚实的限制："**这套guardrail只能抓住部分失败模式，不是万能的**"，Sierra还专门配了额外的数据平台和测试工具来补——本模块不指望一次做完就一劳永逸，需要跟未来的Agent Simulation（调研清单#19，已挂账）配套迭代。

### 2.2 紧迫性——真实数据，不是理论担忧

查证到2026年真实数据：Agentic系统里prompt injection攻击成功率达到**84%**，全球损失约23亿美元（同比+340%），**88%的部署了AI Agent的企业报告过确认或疑似的安全事件**，现有检测手段只能抓到约23%的高水平攻击。OpenAI自己2025年12月承认"AI浏览器里的prompt injection可能永远无法被完全解决"。

### 2.3 纵深防御——六层，缺一不可

防御需要**六层**：从输入校验到持续红队测试，没有单一环节能完全防住。三层核心组合：**架构层预防（如本模块的Supervisor）+ 运行时检测（Monitor）+ 治理（policy定义+审计）**。这不是一次性加一个检查点就完事，是体系化的多层防护。

### 2.4 EU AI Act Article 50 透明度义务——从调研清单#25并入，且更正了原判断（2026-08-30，用户确认Matbox未来会服务欧盟客户后深度核查）

**对调研清单#25原记录的更正**：原记录"高风险系统合规截止日2026年8月2日已过"这个说法不准确，需要区分两件不同的事：
1. **Annex III高风险系统的完整合规义务**（风险管理体系、合格评定、技术文档等）——2026年7月27日生效的《Digital Omnibus on AI》（Regulation (EU) 2026/1744，在原定8月2日截止日前6天通过）把这部分**推迟到了2027年12月2日**（独立Annex III系统）/**2028年8月2日**（嵌入受产品安全法规管的Annex I系统）。这部分**不是紧急缺口**，且Matbox的产品是否真的落入Annex III某个具体类别（如"关键基础设施""就业相关决策"）本身需要真实法律判断——不是技术架构能自行论证的问题，本文档不能代替正式法律意见，建议用户后续找律师/合规顾问做正式分类判断。
2. **Article 50透明度义务**——这部分**没有被Digital Omnibus推迟**，2026年8月2日已生效（**已经生效，不是"即将"**）：AI系统直接与自然人交互（如聊天）时，必须让用户知道自己在和AI对话，除非情境已经明显（Article 50(1)）；面向公众发布的AI生成内容需要标注为AI生成（Article 50(4)）；Article 50(2)的内容标记技术义务对已上市系统有到2026年12月2日的宽限期。**这才是Matbox现在真实存在、且已生效的合规缺口**——尤其是#9刚设计的AnonymousVisitor场景（独立站匿名访客直接跟AI员工对话）和未来独立站的AI生成内容分发场景，直接命中Article 50(1)/(4)。不合规的处罚上限是2100万欧元或全球年营收3%（取更高者）。

**结论**：Article 50披露义务的**结构**（AI身份披露检查点、AI生成内容标记）现在就能设计对，不需要等真实欧盟流量；Annex III完整高风险合规工作维持挂账，等法律顾问给出正式分类结论后再启动，这是正确的"不提前做"而不是遗漏。

## 3｜Own / Reuse / Must Not Rebuild

| 类型 | 对象 | 说明 |
|---|---|---|
| OWN | SupervisorService（实时policy/scope检查）、MonitorService（异步复查）、检查规则的具体判定逻辑 | Matbox自己的输出监督业务规则 |
| REUSE | F-AIEMP-001的forbidden_actions/permission_policy作为规则源、F-EGRESS-001"外部内容当不可信处理"的原则 | 不重新定义一套平行的policy体系 |
| MUST NOT REBUILD | 无独立的第二套权限/policy定义系统 | 本模块是已有policy的执行层，不重新造policy本身 |

## 4｜Feature Register

| FeatureID | 名称 | 说明 |
|---|---|---|
| SUPERVISOR-F001 | 实时Supervisor检查 | 输出发送前实时查policy/scope，fail-closed |
| SUPERVISOR-F002 | 异步Monitor复查 | 100%覆盖，事后复查连贯性/事实依据/情绪 |
| SUPERVISOR-F003 | 纵深防御六层（Prompt Injection专项） | 架构预防+运行时检测+治理三层核心组合 |
| SUPERVISOR-F004 | 匿名/公开场景加严策略 | 面向终端消费者的输出用更严格标准，不低于内部员工场景 |
| SUPERVISOR-F005 | AI身份披露检查（EU AI Act Article 50） | 与自然人直接交互必须披露AI身份；面向公众发布的AI生成内容需标注 |

### SUPERVISOR-F001 · 实时Supervisor检查
- **目标**：AI员工的每一条输出（对话回复、生成文案）在真正发送前，实时对照EmployeeTemplate的forbidden_actions/permission_policy检查，违规则阻断或修正。
- **验收标准**：人为构造违反policy的AI输出，验证被实时拦截，不是发出去之后才发现；Supervisor服务不可用时输出必须被阻断（fail-closed），不能因为检查服务挂了就放行。

### SUPERVISOR-F002 · 异步Monitor复查
- **目标**：每一条已发出的对话，事后异步复查连贯性、重复度、事实依据、情绪信号，100%覆盖不抽样。
- **验收标准**：复查发现的问题必须写入F-OBS-001留痕；覆盖率可查询验证，不允许静默漏检。

### SUPERVISOR-F003 · 纵深防御六层（Prompt Injection专项）
- **目标**：不依赖单一检查点，架构层预防（工具输出当不可信内容处理，复用F-EGRESS-001原则）+ 运行时检测（Supervisor/Monitor）+ 治理（policy定义+审计留痕）三层核心组合。
- **验收标准**：人为构造已知的prompt injection攻击模式，验证多层中至少一层能拦截，不依赖单一环节。

### SUPERVISOR-F004 · 匿名/公开场景加严策略
- **目标**：独立站匿名访客场景（调研清单#9）的AI员工输出，检查标准不能低于内部员工场景，涉及价格/承诺类内容需要额外核实。
- **验收标准**：同一AI员工在匿名场景和内部场景下的输出，匿名场景的检查规则集合必须是内部场景的超集，不能更宽松。

### SUPERVISOR-F005 · AI身份披露检查（2026-08-30从调研清单#25并入，EU AI Act Article 50）
- **目标**：AI员工与自然人（内部员工或匿名终端消费者）的每一次直接交互，在交互开始或首条消息里明确披露"这是AI"，除非情境已经明显；AI员工生成、发布到公开渠道（如未来独立站）的内容附带"AI生成"标注。
- **依赖**：F-AIEMP-001（EmployeeTemplate需要标记该岗位是否属于"直接与自然人交互"场景）；面向公开内容分发的具体标注方式待"独立站"业务包到达后细化。
- **Out of Scope（明确排除）**：Annex III高风险系统的完整合规工作（风险管理体系/合格评定/技术文档）——已推迟到2027年12月2日/2028年8月2日，且Matbox是否落入Annex III具体类别需要正式法律判断，不在本条范围内。
- **验收标准**：人为构造一次匿名访客与AI员工的首次对话，验证回复中包含AI身份披露；人为构造一次AI生成内容发布到公开页面的场景，验证内容带有AI生成标注。

## 5｜核心数据 Contract（逻辑模型，可直接建表/建接口）

**SupervisorCheck**（2026-08-30新增checkType区分披露检查）
checkId, outputRef（关联具体AI员工输出，如AiTaskEvent/ActionExecution/对话消息ID）, tenantId, employeeId, channel（内部|独立站匿名等）, checkType(POLICY_SCOPE|AI_DISCLOSURE), checkResult(PASS|BLOCKED|MODIFIED), policyRef, blockedReason?, checkedAt

**MonitorReview**
reviewId, conversationRef, coherenceScore?, repetitionFlag?, factualGroundingScore?, sentimentFlag?, escalated(bool), escalationReason?, reviewedAt

**API 端点（最小集合）**
- `POST /supervisor/check` — 实时检查一次输出（内部调用，在真正发送前，同步返回PASS/BLOCKED/MODIFIED）
- `GET /supervisor/checks?outputRef=` — 查询某次输出的检查记录
- `POST /monitor/review` — 触发异步复查（批处理或事件驱动）
- `GET /monitor/reviews?conversationRef=` — 查询某对话的复查结果

## 6｜P0 冻结规则

1. AI员工输出未经Supervisor检查直接发给终端消费者：不可降级P0。
2. Supervisor检查被绕过，或检查服务不可用时fail-open（放行）：不可降级P0，必须fail-closed。
3. Monitor复查覆盖率低于100%（抽样漏检）：不允许。
4. 面向匿名访客的输出使用比内部员工场景更宽松的检查标准：不允许。
5. AI员工与自然人直接交互未披露AI身份（且情境不明显）：不允许，对应EU AI Act Article 50(1)，已生效。

## 7｜当前唯一继续断点

Stage 10（真实部署、接入真实对话数据）尚未开始。**明确区分**：Supervisor子层（基于已有policy的实时检查）现在已经设计完整，可以转WorkPackage；Monitor子层"连贯性/情绪异常的具体判断阈值"这类需要真实对话数据才能精调的参数，留到Stage 10接入真实流量后迭代，不影响本模块现在整体成型。跟未来的Agent Simulation（调研清单#19）配套持续迭代。

## 附录｜来源

- **Sierra双层架构依据**：[Constellation of models: the architecture powering Sierra's agents](https://sierra.ai/blog/constellation-of-models)、Sierra G2真实客户评价
- **紧迫性数据依据**：[Prompt injection: types, real-world CVEs, and enterprise defenses](https://www.vectra.ai/topics/prompt-injection)、[The Comprehensive Guide to Prompt Injection Attacks in 2026](https://www.sysdig.com/learn-cloud-native/prompt-injection)
- **纵深防御依据**：[A Survey on Agentic Security: Applications, Threats and Defenses](https://arxiv.org/pdf/2510.06445)
- **调研清单依据**：[Matbox_AI员工能力缺口调研清单_2026-08-30.md](Matbox_AI员工能力缺口调研清单_2026-08-30.md)#3#25
- **SUPERVISOR-F005 EU AI Act依据（2026-08-30）**：[The EU AI Act's Transparency Rules: A Practical Guide to Article 50](https://artificialintelligenceact.eu/transparency-rules-article-50/)、[EU AI Act: Transparency Obligations Take Effect 2 August 2026 — Cooley](https://www.cooley.com/news/insight/2026/2026-08-03-eu-ai-act-transparency-obligations-take-effect-2-august-2026)、[EU AI Act's High-Risk Deadline: Deferred, Not Cancelled — Cloud Security Alliance](https://labs.cloudsecurityalliance.org/research/csa-research-note-eu-ai-act-high-risk-deadline-omnibus-20260/)、[The EU AI Act's August 2, 2026 Deadline Just Moved — ComplianceHub.Wiki](https://compliancehub.wiki/eu-digital-omnibus-ai-act-deadline-deferral-annex-iii-2027/)
