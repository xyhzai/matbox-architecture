# Matbox 任务队列（F-QUEUE-001）

正式开发文档 · V1.0-RC · 2026-08-29

## 当前定位

本专项解决"WorkPackage 怎么派发给 AI 员工、任务失败了怎么恢复、多个 AI 员工同时干活会不会打架"的问题。是 RC5 多AI并行开发标准（架构原则第13条）能真正落地的技术基础——没有这个模块，"派发WorkPackage给独立AI/Codex"只是纸面流程。

**这是本次自我复查（非用户提出）新发现的缺口**，之前只在 RC5 文档里作为"平台核心共享能力"被提及，从未单独设计。

**DocID**: MATBOX-QUEUE-GATE-20260829-V1.0-RC
**状态**: DRAFT_RESEARCH_COMPLETE
**2026-08-30 重大架构变更（引擎从Hatchet改为Temporal，详见架构原则第31条）**：《Matbox_多端平台_CURRENT_正式开发文档_V3.0》里的F-TASK-001（Durable AI Task Runtime）管的是同类问题（AI员工长任务怎么跑、怎么恢复），却选了Temporal，跟本文档原来选的Hatchet直接冲突。深度核实后发现两个关键点推翻了原判断：①Hatchet官方不支持Java SDK（只支持TypeScript/Python/Go/Ruby），而多端平台文档已经把Java/Spring Boot（RuoYi）定成Matbox的具体技术栈，Temporal有成熟的Java SDK，原生契合；②当初否决Temporal的理由"自建运维负担重"，现在查到Temporal Cloud托管服务最低$100/月起，比自己养人维护集群划算，理由不再成立。**结论：引擎改为Temporal，跟F-TASK-001共用同一套Temporal基础设施（同一个集群/Cloud账号，不是两套），但两个模块的业务逻辑仍然分开——本模块只管WorkPackage派发+冲突检测，不管AI员工的通用长任务生命周期**。

## 1｜不可变原则

1. 任务失败或中断后，必须能从断点恢复，不能"跑一半崩了就永远丢了"。
2. 同一个 Feature 或同一个独占写入资源，同一时间只能有一个活动 WorkPackage 在跑（RC5已定规则），队列系统必须在派发时就拦截冲突，不能等冲突发生了才发现。
3. 每一次任务派发、执行、重试都要留痕（接入F-OBS-001），出问题能查全过程。
4. 编排（决定做什么、什么时候做）和执行（AI员工具体干活）分开，编排层不替AI员工做具体决策，AI员工也不擅自决定整体流程。

## 2｜全球调研结论（2026-08-29）

### 2.1 工具选型（2026-08-30重新核实，结论从Hatchet改为Temporal）

| 候选 | 说明 | 结论 |
|---|---|---|
| Celery | 轻量、短任务、Redis/RabbitMQ生态成熟 | 不采用——缺少"任务失败自动接续"的持久化能力，RC5要求的断点恢复做不到 |
| Hatchet | 开源，基于Postgres，持久化工作流+精细并发控制+自带看板；能力上支持AI场景的暂停/等待审批/恢复 | **2026-08-29曾采用，2026-08-30改为不采用**——官方不支持Java SDK（只有TS/Python/Go/Ruby），跟多端平台文档确定的Java/RuoYi技术栈不原生契合 |
| **Temporal** | 持久化工作流，功能最强，有成熟Java SDK | **2026-08-30改为采用**——①跟Java/RuoYi技术栈原生契合；②Temporal Cloud托管服务$100/月起，"自建运维负担重"这条否决理由不再成立；③真实AI场景证据更扎实：OpenAI自己的Codex（Matbox现在用来写代码的AI）生产环境跑在Temporal上，处理每分钟数百万级请求，2026年3月OpenAI Agents SDK正式GA集成Temporal；④跟F-TASK-001共用同一套引擎，不用维护两套持久化工作流系统，这才是"小团队友好"原则真正该体现的地方 |

### 2.2 真实踩坑（查证到，不是凭空担心）

- **AI员工数量越多，冲突概率是平方级增长**（10个AI员工的潜在冲突组合数是5个AI员工的4.5倍）——验证了 RC5"派发前必须做语义资源冲突检查"这条规则的必要性，不是形式主义。
- **API限流是集体性的**：单个AI员工没超限额，但多个AI员工同时跑加起来可能触发供应商限流——需要队列层面统一管理并发数量，不能让每个AI员工各自为政。
- **编排层本身是单点故障**：编排系统挂了，所有任务停摆——需要编排层本身的健康监控（接入F-OBS-001）。

### 2.3 最佳实践

"编排定义做什么和何时做，执行者只管干活不做流程决策"——直接对应 RC5 的 WorkPackage（编排产物）与 Implementer（执行者）分离原则，技术设计和已确认的管理标准一致，不需要额外调整。

## 3｜Own / Reuse / Must Not Rebuild

| 类型 | 对象 | 说明 |
|---|---|---|
| OWN | WorkPackage派发规则、冲突检测逻辑 | Matbox自己的调度业务规则 |
| REUSE | Temporal 的持久化工作流引擎、并发控制、Web UI（2026-08-30从Hatchet改为Temporal） | 不重新造任务队列引擎，跟F-TASK-001共用同一套Temporal基础设施 |
| MUST NOT REBUILD | 底层消息传递/持久化机制 | 用Temporal现成实现 |

## 4｜Feature Register

| FeatureID | 名称 | 说明 |
|---|---|---|
| QUEUE-F001 | Temporal 集成（2026-08-30从Hatchet改为Temporal） | 自建部署或Temporal Cloud托管，作为WorkPackage派发的执行引擎，跟F-TASK-001共用同一套实例 |
| QUEUE-F002 | 冲突检测前置拦截 | 派发前检查语义资源冲突，验证RC5规则可执行 |
| QUEUE-F003 | 并发限额管理 | 统一管理AI员工整体并发数，避免集体触发供应商限流 |
| QUEUE-F004 | 失败恢复与重试策略 | 任务中断后从断点恢复，重试次数受RepairPolicy约束（呼应F-DQ-009） |
| QUEUE-F005 | 任务自认领机制（2026-09-04补，架构原则第58条） | 可派发的WorkPackage进入共享清单，Implementer AI主动认领而非被动等派发，避免单点调度瓶颈 |
| QUEUE-F006 | Worktree 隔离派工（2026-09-04补，架构原则第58条） | 每个被认领的WorkPackage绑定独立git worktree/branch，多个Implementer AI共用同一仓库不互相覆盖文件 |
| QUEUE-F007 | 运行时资源队列（2026-09-04补，架构原则第58/62条） | 数据库/端口/缓存等运行时资源（而非git文件）的争用排队，worktree隔离管不到这一层，是QUEUE-F002语义冲突检测之外的另一层；场景模拟发现原设计锁无租约会永久死锁，已补租约机制 |
| QUEUE-F008 | 高风险公共文件强制转人工（2026-09-04补，架构原则第62条） | 维护一份全局"高风险公共文件清单"（认证/DB迁移/配置/跨模块API契约），凡WorkPackage改动命中清单，不论①②③Gate判定结果如何，强制转人工Review，这是QUEUE-F002冲突检测之外、专门防"Git不报冲突但语义冲突"的独立机制 |
| QUEUE-F009 | 派发附带架构决定摘要（2026-09-04补，架构原则第62条） | WorkPackage材料包除自身Scope/依赖/施工面/验收标准外，按其涉及的技术领域从[Matbox_架构设计原则](Matbox_架构设计原则.md)筛出相关条目摘要一并派发，不整份文档甩给Implementer AI，防止AI不知道已经定过的架构禁令重新踩坑 |
| QUEUE-F010 | 施工期间实时动作拦截（2026-09-04补，纠正此前对DQ的误判） | 复用OPA，在QUEUE-F006已有的worktree边界上做Implementer AI动作的实时allow/deny/转人工，落实架构原则第59条四级分类+第61/62条依赖包引入治理；此前误以为DQ的Gate已经覆盖这层，核查后确认是真实空白 |

### QUEUE-F001 · Temporal 集成（2026-08-30从Hatchet改为Temporal）
- **目标**：WorkPackage 派发、执行、状态追踪都通过 Temporal Workflow/Activity 完成，Matbox这层做WorkPackage语义到Temporal Workflow的映射。
- **验收标准**：一个WorkPackage从派发到完成的全过程可在Temporal Web UI（自建或Temporal Cloud）查询。

### QUEUE-F002 · 冲突检测前置拦截
- **目标**：两个WorkPackage如果涉及同一Feature或同一独占写入资源，第二个必须在派发前被拦截，其WorkPackage业务状态（RC5定义）转入BLOCKED，不能等冲突发生才发现。
- **验收标准**：人为构造冲突场景，验证系统能在派发阶段拦截。

### QUEUE-F003 · 并发限额管理
- **目标**：设置AI员工整体并发上限，避免集体请求超出供应商速率限制。
- **验收标准**：并发达到上限时，新任务排队而非报错失败。

### QUEUE-F004 · 失败恢复与重试策略
- **目标**：任务失败后按策略重试，重试上限由配置决定（不写死在代码里），超限后QueueRun.runStatus转NEEDS_MANUAL_INTERVENTION。
- **验收标准**：人为制造任务中断，验证能从断点恢复而非从头重来。

### QUEUE-F005 · 任务自认领机制（2026-09-04补）
- **背景**：查证2026年多AI协同真实做法（Claude Code Agent Teams），主流不是中心化"派工"，是把可执行的WorkPackage摆上共享清单让AI自己认领，避免所有任务排队等一个调度员分配，调度层退化成"仅在异常时介入"（对应本文档第2节"编排层是单点故障"这条已识别风险的进一步缓解）。
- **目标**：QUEUE-F001的Temporal Workflow派发语义细化为"进入可认领清单"而非"直接指派某个Agent"；Implementer AI通过Task API主动认领，认领成功即锁定该WorkPackage，其余Agent不可重复认领。
- **2026-09-04场景模拟发现的断点**：推演"两个Implementer AI同时对同一个runId发起claim"——原验收标准只写了结果"只有一个成功"，但`QueueRun`的字段里没有任何东西能真正撑住这句话：没有版本号，没有乐观锁，两个几乎同时到达的claim请求，谁真正先落地完全无法保证。F-TASK-001自己早就定过"所有状态变更必须带`version`/`expected_state`防并发覆盖（乐观锁）"这条规则（本文档也在用同一套Temporal基础设施），QueueRun这边没抄这个作业。**修正**：`QueueRun`新增`version`字段，`claim`操作必须是"读取当前version→CAS（compare-and-swap）更新为RUNNING且claimedBy=自己，同时version+1"，version不匹配（说明状态已被别人改过）直接拒绝，不是简单的"先查询再更新"两步操作（那样两个请求可能都查到QUEUED，都以为自己能抢到）。
- **验收标准**：多个Implementer AI并发尝试认领同一WorkPackage，只有一个成功，其余收到明确的"已被认领"响应，不产生重复施工；且能验证这个互斥是靠`version`字段的CAS机制保证的，不是靠"运气好没撞上"。

### QUEUE-F006 · Worktree 隔离派工（2026-09-04补）
- **背景**：查证2026年真实做法（GitHub Copilot app），多个Agent共用同一仓库靠独立git worktree互不覆盖文件，而非各自clone整个仓库。
- **目标**：WorkPackage被认领时，系统为其绑定一个独立的git worktree/branch，Base Commit锁定（呼应DQ流程图"WorkPackage派发"步骤），Implementer AI只在自己的worktree内写入。
- **2026-09-04场景模拟发现的断点**：推演"几十个WorkPackage一天内陆续跑完"——原设计只写了worktree怎么分配，完全没写**谁负责回收**。worktree只分不收，磁盘迟早被占满，规模越大出问题越快，这是真实的资源泄漏，不是细枝末节。**修正**：①`QueueRun.runStatus`进入终态（`SUCCEEDED`/`FAILED`/`CANCELLED`）后，worktree不立刻删除——保留一段可配置的时间（默认建议24-48小时）方便排查问题，超时后由后台任务自动清理；②`AWAITING_APPROVAL`/`AWAITING_RESOURCE`这类长时间挂起状态，worktree必须保留（不能因为"暂时没在跑"就误清理，人还没做决定）；③磁盘空间紧张时的清理顺序：优先清理保留期已过的终态worktree，不清理仍在等待/运行中的。
- **验收标准**：①两个Implementer AI同时认领互不冲突的WorkPackage，各自的文件改动互不可见、互不覆盖，直到各自完成受控Merge；②人为构造一个进入终态超过保留期的QueueRun，验证worktree被自动清理；③验证`AWAITING_APPROVAL`状态的WorkPackage即便挂起很久，worktree也不会被误清理。

### QUEUE-F007 · 运行时资源队列（2026-09-04补）
- **背景**：worktree隔离只解决git文件层面的冲突，多个WorkPackage并行执行时若争用同一数据库、端口、缓存等运行时资源，仍会互相干扰——这是QUEUE-F002"语义资源冲突检测"（派发前静态判断）之外的另一层问题（运行时争用，动态发生）。
- **目标**：为会争用运行时资源的操作（如跑数据库迁移、占用固定端口的本地服务）提供一个执行队列，同一时刻只放行一个，避免并发直接冲突；不影响不涉及共享运行时资源的WorkPackage并行执行。
- **2026-09-04场景模拟发现的断点（比QUEUE-F010那条链更严重，是真实会死锁的设计）**：推演"两个WorkPackage同时抢同一个数据库迁移锁"发现——原设计的`RuntimeResourceLock`只有`holderRunId`+`acquiredAt`+`releasedAt`，**没有过期时间**。这意味着如果持有锁的那个QueueRun中途崩溃、被Kill、或者Implementer AI掉线，从来没有调用`release`，这把锁会被**永久占住**——`db_migration`这类资源以后再也没有任何WorkPackage能拿到，是真实的死锁，不是理论风险（分布式锁没有租约/TTL是业界公认的经典反模式，Redis/Zookeeper的锁实现都强制要求租约，不允许无限期持有）。另外原描述没写`acquire`拿不到锁时，等待方的Implementer AI具体在干什么——是同步卡住傻等（浪费token/时间），还是异步排队、锁空出来时被唤醒继续跑。**修正**：①`RuntimeResourceLock`新增`leaseExpiresAt`（租约到期时间，持有方必须定期续约，默认租约时长按操作类型配置，比如数据库迁移给更长的租约），租约到期未续约则视为持有方已失效，锁自动释放给`waitingQueue`里排第一个的；②`acquire`调用改为非阻塞——立刻返回`ACQUIRED`（附带`leaseExpiresAt`）或`QUEUED`（附带`waitingQueue`里的排队位置），拿不到锁的QueueRun转入新状态`AWAITING_RESOURCE`（同`AWAITING_APPROVAL`一样是本模块专属状态，不外借），锁真正可用时由本模块向对应Temporal Workflow发signal唤醒，不是让Implementer AI自己傻等或轮询。
- **验收标准**：①人为构造两个WorkPackage同时触发同一运行时资源操作，验证系统排队串行执行而非并发报错，等待方的QueueRun正确转入`AWAITING_RESOURCE`；②人为构造持有锁的一方中途崩溃、不调用release的场景，验证租约到期后锁能自动释放给下一个等待者，不会永久卡死。

### QUEUE-F008 · 高风险公共文件强制转人工（2026-09-04补）
- **背景**：查证2026年真实"contract drift"问题——两个Agent各自修改共享接口，git合并不报冲突，但运行时行为错误，"这种语义判断没有工具能自动做，只能靠人"。QUEUE-F002管的是"同一独占资源不能同时写"，管不到"两个不冲突的改动分别合入后语义上不兼容"这类情况。
- **目标**：维护一份全局"高风险公共文件清单"（认证、数据库迁移、核心配置、跨模块API契约类文件，具体路径待Stage10真实Repo确定后填充），WorkPackage改动命中清单内文件时，不论①②③Gate判定结果如何，其RC5业务状态强制转入需要人工确认的状态，不能自动合并。
- **2026-09-04场景模拟发现的断点**：推演"命中清单的WorkPackage排在Merge Queue最前面，但审核人几小时没空处理，后面还有10个已经Gate全过、没碰高风险文件的WorkPackage在排队"——架构原则第62条定的"Merge Queue必须严格串行"，原意是"同一时刻只真正合入一个，不并行合并"（防止两个改动语义冲突），不是"必须完全按到达顺序死等"，但这条没写清楚，容易被理解成后面的也必须干等，实际会议造成几十个AI并行开工时，一个卡审核的WorkPackage堵死整条合并流水线，跟"高吞吐并行开发"的初衷矛盾。**修正**：命中QUEUE-F008清单、转入人工确认状态的WorkPackage，从Merge Queue的"待合并队列"里移出（不占用合并顺位），后面已就绪的WorkPackage可以继续按串行互斥的规则合并，不用等它；命中清单的WorkPackage人工确认通过后，重新排入队尾，且必须先按"独立Review"步骤已有的"基于latest-main重新rebase检查"规则跑一遍（因为它离开队列这段时间，main分支可能已经因为其他WorkPackage的合并而往前走了），不能直接拿旧的diff去合并。
- **验收标准**：①人为构造一个改动命中清单文件、且三道Gate全部PASS的WorkPackage，验证系统仍然拦下不允许自动合并；②人为构造"命中清单的WorkPackage排在队首但迟迟未审核"的场景，验证后面已就绪的WorkPackage不会被卡住，仍能正常合并；③验证命中清单的WorkPackage人工确认通过后，重新进入队列前会先做rebase检查，不会用过期的diff直接合并。
- **2026-09-04再发现的断点（DQ正式文档同一天两条新规则组合后暴露的缝隙）**：DQ正式文档同一天新增了两条规则——①风险分级自动批准（同时满足四条标准即可跳过独立Review直接合并，其中一条就是"未命中本清单Overlap Zone"）；②F-DQ-008自己的Rego策略改动必须先经opa test跑通PolicyChallengeSet才能合并。这两条分开看都对，组合起来有真实缝隙：如果F-DQ-008的Rego策略文件本身不在本清单内，一次改动策略的diff只要体量不大、没用Suppression、Implementer最近无BLOCKED_MANUAL记录，就可能满足风险分级四条标准直接自动合并——而"必须先过PolicyChallengeSet"这条规则本身只是文字要求，没有绑定到任何强制执行点，等于policy变更有可能绕开这道检查，"低风险自动批准"反而给了绕过"策略自测"的路。**修正**：本清单"核心配置"这一类别，必须明确包含DQ及其他模块自己的Gate判定/审批决策逻辑文件（如F-DQ-008 Rego策略），不能只写"核心配置"这种容易被理解成部署配置、从而漏掉判定逻辑文件的模糊说法；具体路径仍等Stage10真实Repo确定，但类别定义现在就要点名这一类。命中清单会让风险分级第②条标准自动不满足，强制走独立Review，PolicyChallengeSet检查借此在Review环节被真正卡住执行，不再只停留在文字要求。

### QUEUE-F009 · 派发附带架构决定摘要（2026-09-04补）
- **背景**：查证2026年真实痛点——编码Agent"跨会话不记事"，架构决策"活在commit历史和聊天记录里"，团队被迫反复给AI重新解释同样的约束。[Matbox_架构设计原则](Matbox_架构设计原则.md)已积累60余条平台级决定（技术选型否决项、命名规范、安全红线等），但WorkPackage材料包目前只包含该Feature自身的Scope/依赖/施工面/验收标准，没有"这个任务可能踩到的全局架构禁令"这一段。
- **目标**：WorkPackage派发/认领时，系统按该WorkPackage声明涉及的技术领域（如"对象存储"“密钥管理”），从架构设计原则文档中筛出相关条目摘要，随其余材料一并交给Implementer AI，不整份文档甩过去。**摘要格式必须是"结论+一句话理由"的短句列表（如"不用MinIO/Garage——协议改AGPL/许可证复杂，已定SeaweedFS"），不得是原文档的整段复制**——架构设计原则文档本身是写给人审、留痕查证过程用的存档体裁（含背景/查证经过/被推翻过什么），故意写得长，直接把这种长文喂给Implementer AI等于没有筛过，AI要花时间自己提炼，跟没做QUEUE-F009这件事没区别。人审的存档体裁和喂给AI干活的体裁必须是两份不同的东西，不能共用一份。
- **验收标准**：①人为构造一个涉及已有明确架构否决项的WorkPackage（如涉及对象存储选型），验证其材料包中包含对应的否决说明摘要（如"不采用MinIO/Garage，已确定SeaweedFS"）；②验证该摘要是单行短句，不包含原文档的"背景/查证结论/Sources"等长段落内容。

### QUEUE-F010 · 施工期间实时动作拦截（2026-09-04补，纠正此前对DQ的误判）
- **背景**：架构原则第60条曾说"DQ已选定的OPA Gate能干实时拦截的活"——**核查后发现这个说法不准确**。DQ的①②③Gate是在Implementer AI提交一次改动之后评估这次diff，是**提交时点**的判定，不是Implementer AI敲代码/跑命令**当下**的拦截；查过F-ACTION-001（Action Gateway）后确认它管的是AI员工对生产/第三方系统的正式业务动作调用，同样不覆盖Implementer AI在自己worktree里写文件、跑本地命令、装依赖包这类施工动作。**结论：真正"实时"的这一层，此前没有任何模块在管，是真实空白，不是已经被DQ兜住的假空白。**
- **目标**：本模块既然已经拥有WorkPackage的worktree（QUEUE-F006），在这个已有的执行边界上加一层策略拦截，复用已选定的OPA（不新建策略引擎），对Implementer AI在worktree内的动作做实时allow/deny/转人工判断，具体覆盖两类此前查证到、但没有归属模块的场景：
  1. 按架构原则第59条的"动作后果四级分类"，判断当前动作是否需要暂停等待人工——命中Tier3/4的，把对应QueueRun转入等待人工确认的状态；
  2. 按架构原则第61/62条查证到的依赖包引入风险，Implementer AI请求安装新依赖包时，先过一遍OPA策略（包名是否在已知安全源/是否命中已知恶意特征），不是等DQ的Trivy在提交后才扫到。
- **2026-09-04场景模拟后补充四处接口断点（持续追问"再下一步会发生什么"，逐层挖出来的，不是一次查完的）**：
  1. **"转WAITING_APPROVAL"必须真正调用F-APPROVAL-001，不能只改状态字段**——实际推演一次高风险动作被拦截的场景后发现，原描述只说"转入WAITING_APPROVAL"，但这只是个状态标记，真正"生成一条审批请求、通知负责人、记录批准/拒绝决定"这件事，Matbox已经有专门模块（F-APPROVAL-001）在管，不能绕开它自己另搞一套。**修正**：命中Tier3/4时，QUEUE-F010必须调用F-APPROVAL-001创建一条`AiApproval`记录（`actionId`引用本条`ActionInterceptDecision.decisionId`，不止能引用F-ACTION-001的ProposedAction——F-APPROVAL-001需相应放宽这个字段的引用范围，见该文档同步更新），走已有的审批流程，不新建通知/审批机制。
  2. **FILE_WRITE动作命中QUEUE-F008高风险公共文件清单时，必须提前标记，不能等到QUEUE-F008在合并前才第一次发现**——原设计里QUEUE-F010按"动作后果"分级（只读/可逆/外部/不可逆），修改worktree内的文件本身通常是Tier2（可逆），会被自动放行；而QUEUE-F008是在合并前才检查文件路径是否命中清单。这意味着Implementer AI可能辛辛苦苦改完一个高风险文件、跑完自己的测试，到最后合并前才第一次被告知"这个文件必须转人工"，白费功夫。**修正**：QUEUE-F010对FILE_WRITE动作做判断时，除了动作后果分级，必须额外查一次该文件路径是否命中QUEUE-F008的高风险公共文件清单——命中则不阻塞当前编辑（不打断施工），但立刻给这次QueueRun打上`willRequireManualReview`标记并告知Implementer AI，让它一开始就知道这个WorkPackage终归要过人工这一关，不是到最后才发现。
  3. **"把QueueRun状态转入F-TASK-001的WAITING_APPROVAL"这句话本身是错的，已改正**——继续往下推演"批准之后控制权怎么传回去"时发现：`WAITING_APPROVAL`是F-TASK-001自己`ai_task`状态机里的值，不在`QueueRun.runStatus`的枚举里（`QUEUED|RUNNING|RETRYING|SUCCEEDED|FAILED|CANCELLED|NEEDS_MANUAL_INTERVENTION`），且本文档"2.2 与F-QUEUE-001的边界划分"一节自己就写明两个模块的状态各自独立、不能混用——这是跟架构原则第24条"QueueRun.runStatus不能与RC5 WorkPackage状态混用"同一类错误，只是这次是跟F-TASK-001的状态混了。`NEEDS_MANUAL_INTERVENTION`语义上是"重试超限、已经失败"，跟"策略要求暂停等批准、还没失败"不是一回事，不能借用。**修正**：`QueueRun.runStatus`新增专属值`AWAITING_APPROVAL`，命中Tier3/4时转入这个值，不引用别的模块的状态；F-APPROVAL-001的AiApproval有4种终态（APPROVED|REJECTED|TIMEOUT|WITHDRAWN），Outbox Dispatcher对每一种都会发事件，本模块必须对每一种都定义QueueRun该转到哪——**这条不是补充细节，是继续推演"只写了批准通过那一条路径，没写另外三条"时发现的第4处断点**：`APPROVED`→Temporal Workflow收到signal恢复执行，转`RUNNING`；`REJECTED`→转`FAILED`，`decisionReason`原样带回记录在QueueRun关联的Evidence里，不能让Implementer AI装作没发生过重试；`TIMEOUT`→转`NEEDS_MANUAL_INTERVENTION`（审批本身没人处理，性质上确实是"需要人工介入"，这里可以复用这个已有值，不是新造）；`WITHDRAWN`→转回`AWAITING_APPROVAL`的前一个状态（一般是`RUNNING`，因为发起方主动撤回通常是意识到判断错了想重新构造这次动作），不能悬空在一个不再有效的审批请求上等。
- **验收标准**：①人为构造一个属于Tier4（如改权限配置）的动作，验证系统在执行前拦截、`QueueRun.runStatus`转入`AWAITING_APPROVAL`、且能在F-APPROVAL-001查到对应的AiApproval记录，批准后能正确恢复为`RUNNING`；②人为构造一次安装未知/可疑包名的请求，验证系统在真正执行安装前拦截，不是等Trivy扫描commit后才发现；③人为构造一次编辑高风险公共文件清单内文件的动作，验证QueueRun在第一次编辑时就被标记`willRequireManualReview`，不是等到合并前才第一次出现这个信号；④分别人为构造审批被拒绝、审批超时、发起方主动撤回三种场景，验证`QueueRun.runStatus`分别正确转入`FAILED`/`NEEDS_MANUAL_INTERVENTION`/回到发起前状态，不是只测过"批准通过"这一条路径就算完。

## 5｜核心数据 Contract（逻辑模型，可直接建表/建接口）

**QueueRun**（Temporal Workflow执行记录的Matbox侧映射——技术层"这次跑得怎样"，不是业务层WorkPackage状态；2026-08-30从Hatchet映射改为Temporal映射，字段本身不变；2026-09-04补充自认领/worktree字段）
runId, featureId, workPackageId, implementerId(agentId或人类), runStatus(QUEUED|RUNNING|RETRYING|SUCCEEDED|FAILED|CANCELLED|NEEDS_MANUAL_INTERVENTION|**AWAITING_APPROVAL**（2026-09-04新增，QUEUE-F010，本模块专属值，不借用F-TASK-001的ai_task状态）|**AWAITING_RESOURCE**（2026-09-04新增，QUEUE-F007，等待运行时资源锁时的本模块专属值）), temporalWorkflowId（关联Temporal侧的Workflow执行，替代原Hatchet run引用）, exclusiveResourceKeys[]（用于冲突检测）, attemptCount, maxAttempts（来自RepairPolicy配置）, createdAt, startedAt, finishedAt, **claimedBy**（认领的Implementer/agentId，QUEUE-F005）, **claimedAt**, **worktreePath**（QUEUE-F006）, **baseCommitSha**（QUEUE-F006）, **version**（2026-09-04新增，QUEUE-F005场景模拟发现的断点——乐观锁，claim等状态变更操作必须CAS，不能简单读后写）, **worktreeCleanedAt**?（2026-09-04新增，QUEUE-F006场景模拟发现的断点——worktree被自动清理的时间，为空表示仍保留）

**注：与 RC5 的 WorkPackage 业务状态区分**——RC5 已定义 WorkPackage 自己的业务生命周期状态（ACTIVE/BLOCKED/REBASE_REQUIRED/SUPERSEDED/CANCELLED/MERGED，记在Feature Register），描述"这次施工任务本身处于什么阶段"；本模块的 `QueueRun.runStatus` 是队列引擎（Temporal）层面"这一次执行尝试跑得怎样"的技术状态，两者不是一回事，不能混用同一个字段名。QUEUE-F002冲突检测判定BLOCK时，本模块调用方去更新的是RC5 WorkPackage的业务状态，而不是把WorkPackage状态写成"BLOCKED"塞进QueueRun表。

**ConflictCheckResult**
checkId, workPackageId, conflictingResourceKeys[], conflictingWorkPackageId?, decision(BLOCK|ALLOW|SERIALIZE), checkedAt

**ConcurrencyLimit**
limitId, scope(global|perProvider), maxConcurrentTasks, currentActiveCount

**RuntimeResourceLock**（2026-09-04新增，QUEUE-F007——运行时资源排队，区别于ConflictCheckResult管的git文件级冲突；场景模拟后补充租约字段，防止持有方崩溃导致永久死锁）
lockId, resourceKey（如db_migration/fixed_port_8080）, holderRunId, acquiredAt, **leaseExpiresAt**（租约到期时间，到期未续约视为持有方失效）, **leaseDurationConfig**（按resourceKey类型配置的默认租约时长）, releasedAt?, waitingQueue[]（等待中的runId列表，FIFO）

**OverlapZoneFile**（2026-09-04新增，QUEUE-F008——高风险公共文件清单，全局维护，不挂在单个WorkPackage下）
filePathPattern, category(AUTH|DB_MIGRATION|CONFIG|CROSS_MODULE_CONTRACT), addedAt, addedReason；具体路径待Stage10真实Repo确定后填充，现在只定分类标准

**ActionInterceptDecision**（2026-09-04新增，QUEUE-F010——施工期间实时动作拦截记录）
decisionId, runId, actionType(FILE_WRITE|COMMAND_EXEC|DEPENDENCY_INSTALL|OTHER), actionTier（对应架构原则第59条四级分类：1_READONLY|2_REVERSIBLE|3_EXTERNAL|4_IRREVERSIBLE）, decision(ALLOW|DENY|ESCALATE_WAITING_APPROVAL), policyRef（命中的OPA策略规则）, packageName?（DEPENDENCY_INSTALL时填写，对应架构原则第61条依赖包治理）, **overlapZoneHit**（2026-09-04新增，bool，FILE_WRITE命中QUEUE-F008清单时为true）, **approvalId**?（2026-09-04新增，decision为ESCALATE_WAITING_APPROVAL时关联F-APPROVAL-001创建的AiApproval.approvalId，不是自己另存一份审批状态）, decidedAt

**注：QueueRun新增字段**（2026-09-04，配合上面第2处修正）——`willRequireManualReview`(bool，任一ActionInterceptDecision.overlapZoneHit=true时置为true，供Implementer AI和后续Review阶段提前感知，不等QUEUE-F008在合并前才第一次出现这个信号）

**API 端点（最小集合）**
- `POST /queue/dispatch` — 派发WorkPackage，内部先跑ConflictCheck，冲突则回调更新该WorkPackage在RC5中的业务状态为BLOCKED，同时不创建QueueRun（不再向Hatchet发起，改为发起Temporal Workflow）；2026-09-04起，"派发"语义细化为"进入可认领清单"（QUEUE-F005），响应中附带该WorkPackage涉及技术领域对应的架构决定摘要（QUEUE-F009）
- `POST /queue/runs/{runId}/claim` — （2026-09-04新增，QUEUE-F005）Implementer AI认领一个QUEUED状态的WorkPackage，成功后分配worktree（QUEUE-F006）并转入RUNNING，并发认领只有一个成功
- `GET /queue/runs/{runId}` — 查询某次执行的runStatus，含Temporal Web UI链接（自建或Temporal Cloud）
- `POST /queue/runs/{runId}/retry` — 手动触发重试（runStatus为NEEDS_MANUAL_INTERVENTION时才可用，即已超过maxAttempts）
- `PUT /queue/concurrency-limits/{scope}` — 设置/调整并发上限（对应QUEUE-F003，scope为global或perProvider），写入ConcurrencyLimit.maxConcurrentTasks
- `POST /queue/resource-locks/{resourceKey}/acquire` — （2026-09-04新增，QUEUE-F007）非阻塞获取，立刻返回`ACQUIRED`(含`leaseExpiresAt`)或`QUEUED`(含排队位置)；拿不到锁时调用方`QueueRun`转入`AWAITING_RESOURCE`，锁可用时由本模块发signal唤醒
- `POST /queue/resource-locks/{resourceKey}/renew` — （2026-09-04新增，QUEUE-F007）持有方续约租约，不续约则到期自动释放给下一个等待者
- `POST /queue/resource-locks/{resourceKey}/release` — （2026-09-04新增，QUEUE-F007）主动释放
- `GET /queue/overlap-zone-files` — （2026-09-04新增，QUEUE-F008）查询高风险公共文件清单，WorkPackage改动命中时强制转人工
- `POST /queue/runs/{runId}/actions:check` — （2026-09-04新增，QUEUE-F010）Implementer AI在执行动作前调用，返回ALLOW/DENY/ESCALATE_WAITING_APPROVAL；命中Tier3/4或可疑依赖包时，本模块把`QueueRun.runStatus`转入自己专属的`AWAITING_APPROVAL`（不是F-TASK-001的状态），同时调用F-APPROVAL-001创建AiApproval记录

## 6｜P0 冻结规则

1. 两个WorkPackage同时对同一独占写入资源生效，未被拦截：视为设计缺陷，需要立即修复。
2. 任务失败后无限重试没有上限：不允许，必须有配置化的重试上限，超限后runStatus转NEEDS_MANUAL_INTERVENTION兜底。
3. （2026-09-04新增，QUEUE-F005）同一WorkPackage被两个及以上Implementer同时认领成功：视为设计缺陷，必须立即修复，认领操作必须是原子操作。
4. （2026-09-04新增，QUEUE-F008）改动命中高风险公共文件清单的WorkPackage，无论①②③Gate判定结果如何自动合并：不允许，必须强制转人工，这条不能被Gate PASS覆盖。
5. （2026-09-04新增，QUEUE-F010）Tier4（不可逆）动作在对应AiApproval被批准前被实际执行：视为设计缺陷，必须立即修复——这条是防"Replit式"删库事故的真正落点，不能只停留在架构原则文档里当一句话。
6. （2026-09-04新增，QUEUE-F007，场景模拟发现）`RuntimeResourceLock`没有`leaseExpiresAt`或租约过期后未自动释放给下一个等待者：不允许——这是真实会导致永久死锁的设计缺陷，不是细节遗漏。
7. （2026-09-04新增，QUEUE-F005，场景模拟发现）同一WorkPackage的`claim`操作不经过`version`字段CAS校验就直接写RUNNING：不允许——并发场景下无法真正保证"只有一个成功"，等于验收标准写了但没有机制支撑。
8. （2026-09-04新增，QUEUE-F006，场景模拟发现）仍处于`AWAITING_APPROVAL`/`AWAITING_RESOURCE`等待状态的QueueRun，其worktree被清理任务误删：不允许——这类状态代表"人还没做决定"，不是"已经结束"。

## 7｜当前唯一继续断点

Stage 10（真实部署Temporal或接入Temporal Cloud，接通真实WorkPackage派发流程）尚未开始。下一步：把 QUEUE-F001~F010 转成 WorkPackage，部署时跟F-TASK-001协调共用同一套Temporal实例；QUEUE-F008的高风险公共文件清单具体路径、QUEUE-F009的架构摘要筛选规则、QUEUE-F010具体OPA策略规则集，均需真实Repo结构确定后才能填充实际内容，现在只定了机制和分类标准。

## 附录｜来源

- [Modern Queueing Architectures: Celery, RabbitMQ, Redis, or Temporal?](https://medium.com/beyond-the-algorithm/modern-queueing-architectures-celery-rabbitmq-redis-or-temporal-f93ea7c526ec)
- [Celery vs Temporal for AI Agent Tasks](https://suhasbhairav.com/blog/celery-vs-temporal-for-ai-agent-tasks-background-jobs-vs-durable-execution)
- [6 Multi-Agent Orchestration Patterns for Production (2026)](https://beam.ai/agentic-insights/multi-agent-orchestration-patterns-production)
- [Multi-Agent Orchestration: 5 Patterns That Work in 2026](https://www.digitalapplied.com/blog/multi-agent-orchestration-5-patterns-that-work)
- 2026-08-30引擎从Hatchet改为Temporal的核实依据：[Hatchet · Hatchet vs Temporal](https://hatchet.run/versus/hatchet-vs-temporal)、[Temporal Cloud Pricing Update](https://temporal.io/blog/temporal-cloud-pricing-update)、[AI Agents - Hatchet.run](https://hatchet.run/use-cases/ai-agents)（确认Hatchet无官方Java SDK）、[Of course you can build dynamic AI agents with Temporal](https://temporal.io/blog/of-course-you-can-build-dynamic-ai-agents-with-temporal)
- 2026-09-04 QUEUE-F005~F009并入依据（详见[Matbox_架构设计原则](Matbox_架构设计原则.md)第58/62条）：[Inside Claude Code's Shared Task List](https://www.mindstudio.ai/blog/claude-code-agent-teams-shared-task-list)、[How to Use Git Worktrees for Parallel AI Agent Execution](https://www.augmentcode.com/guides/git-worktrees-parallel-ai-agent-execution)、[5 Ways to Stop AI Agents Stepping on Each Other](https://getautonoma.com/blog/parallel-ai-agent-prs)、[Persistent Codebase Memory for Coding Agents 2026](https://www.cognee.ai/blog/guides/ai-coding-agent-persistent-codebase-memory)
- 2026-09-04 QUEUE-F010并入依据（详见架构原则第59/61/62条）：[Human-in-the-Loop Escalation Design for AI Agents 2026](https://www.digitalapplied.com/blog/human-in-the-loop-escalation-design-ai-agents-2026)、[Coding Agents Just Reopened Your Software Supply Chain Blind Spot — JFrog](https://jfrog.com/blog/introducing-agent-package-resolution/)、[AEGIS: Pre-Execution Firewall for AI Agents](https://arxiv.org/html/2603.12621v1)
