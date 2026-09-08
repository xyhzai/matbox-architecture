# Matbox 全球多语言与本地化 · 正式开发文档 V1.0-RC

FeatureID：**F-LOC-001**
建立日期：2026-09-08
层级定位：**基础层（底层）公共能力** —— 不是 AI 员工的下属模块
上游交接包：`语言包.zip`（MATBOX-LOCALIZATION-DEV-20260902，Stage 9 PASS / READY_FOR_STAGE10）

---

## 0｜这份文档是什么

用户侧已交付一份完整的 Stage 9 开发包（DEV.docx 2,028 段 + 4 个 JSON + 可运行 POC），本文**不重抄它**。本文只做三件事：

1. **记录本会话对该包的独立核验结果**（做了什么、查到什么）
2. **记录 Matbox 侧对其技术选型的调整决定**（升版本，含理由与证据）
3. **登记该包声称可复用、但 Matbox 尚不存在的 Owner 依赖**

交接包本身作为不可变证据保留，**不修改**（其 MANIFEST 已冻结 SHA-256，改动会破坏完整性）。

> **交接包在仓库里的位置**（2026-09-08 补）：
> - 解压件：[docs/全球多语言与本地化/Matbox_全球多语言与本地化_交接包_V1.0/](全球多语言与本地化/Matbox_全球多语言与本地化_交接包_V1.0/)（9 个文件）
> - 原始压缩包（字节级证据）：[语言包_原始交接包.zip](全球多语言与本地化/语言包_原始交接包.zip)，整包 SHA-256 `b8580c9bddd4bed4827d2953d7a0104d99a551f0694d08e2c2ba8d1e873802a0`
> - 包自称：`Matbox_Localization_V3`，日期 2026-09-02
> - ⚠️ 仓库根目录的 [.gitattributes](../.gitattributes) 已把这两个目录标为 `-text`：git 不得对它们做任何换行符转换。**这不是洁癖**——2026-09-08 实测过，不加这条，`git clone` 出来的副本里 `README.txt` / `evidence.json` / `features.json` 的 SHA-256 会全部对不上 MANIFEST，证据链当场断掉且毫无提示。另外 `poc.log` 曾被仓库 `.gitignore` 里的 `*.log` 挡掉、没能入库，已用 `git add -f` 强制补上。
>
> ⚠️ **这一段此前是空缺的，且不是笔误——包根本没进过仓库。** 本文档 §1 白纸黑字写着「MANIFEST 8/8 SHA-256 全部一致」「实际执行 poc.py，12/12 PASS」，但被验的那个包只存在于用户本机，git 历史里从没出现过。后果是：这些核验结论**任何人都无法复现**；「作为不可变证据保留」保留在哪也没有答案；G-LOC-MATBOX-004 / -005 要改的代码，Stage 10 的人根本找不到。这同时撞在项目的原始创立规则上——**不留本地孤本**。
>
> 2026-09-08 已把包放进仓库，并**当场重新核验 MANIFEST，8/8 一致**，确认入库副本与本文 §1 当初所验为同一份、逐字节相同。同时新增机器检查 C7（见 [_check_docs_consistency.py](_check_docs_consistency.py)）：登记在册的交接包目录缺失、或包内任何文件被改动一个字节，都会当场 FAIL——不再依赖谁记得去放、谁记得去查。

---

## 1｜独立核验结果（2026-09-08）

| 核验项 | 方法 | 结果 |
|---|---|---|
| 包完整性 | 逐个重算 MANIFEST 里 8 个文件的 SHA-256 | ✅ **8/8 全部一致**（含 1.7MB PDF） |
| POC 真实性 | **实际执行 `python poc.py`** | ✅ **12/12 PASS，exit 0** —— 声称属实，非编造 |
| 锁定 commit 真实性 | GitHub API 逐个拉取 | ✅ **3/3 真实且与声称版本精确对应**（见 §2） |
| 正文完整性 | DEV.docx 全文提取 | ✅ 2,028 段 100% 通读 |
| FeatureID 冲突 | 全仓检索 `LOC-F0` / `F-LOC-` | ✅ 未占用 |
| 是否覆盖既有模块 | 检索 Feature Register | ✅ **既有 32 个模块中无本地化/多语言模块**，本模块为全新增，不覆盖任何现有设计 |

**核验结论（事实陈述）**：该包在完整性、可执行性、源码可追溯三个维度上均经得起独立复核。

### 1.1 ⚠️ 但 12/12 里有 2 条不测任何被测代码

将 `poc.py` 第 10、11 条测试原样复制到**零依赖空环境**（不 import 任何模块、不定义任何被测函数）后执行，**两条仍然 PASS**：

```python
# 第10条：断言的是紧邻上一行自己写的 dict 字面量
user_profile = {"language": "en", "locale": "en-IN", "currency": "INR", ...}
check("AC08 language/locale separated", user_profile["language"] == "en" and ...)

# 第11条：断言的是紧邻上一行自己的赋值
ai_default = conversation_override or preferred   # conversation_override = "en"
check("AC09 AI conversation override", ai_default == "en")
```

两条均未调用 `resolve_language` / `canonicalize` / `ContentStore` 的任何一行。

**真实契约覆盖 = 10 条，不是 12 条。**

**影响**：这两条分别声称覆盖 **AC-LOC-008**（Language/Locale 必须可独立共存）与 **AC-LOC-009**（AI 会话内覆盖不改全局偏好），而其对应的 **LOC-F013 / LOC-F014 在包中标记为 `READY_FOR_STAGE10_BINDING` 且无 Open Gate**。等于两个"无门禁"Feature 由两条空测支撑。

**Matbox 侧处置**：AC-LOC-008 / AC-LOC-009 **不得计入已验证**；Stage 10 必须补两条真实 resolver 级测试（locale/currency/timezone 独立解析；session override 不写回 UserPreference）后方可关闭。

> **2026-09-08 更新：真实测试已补上，见 §1.3。** 结果分两半——**AC-LOC-009 现在可以计入已验证**（3/3 PASS，每条都真实调用 `resolve_language()`）；**AC-LOC-008 仍不可计入**，但已从「怀疑」变成一条能跑的失败测试，失败点定位到 `canonicalize("en-IN") → "en"` 这一行。本段上面那句「两条都不得计入」以 §1.3 为准。

### 1.2 ⚠️ `canonicalize()` 是一个会静默抹平 Locale 的陷阱

POC 中：

```python
aliases = { "en-US": "en", "en-GB": "en", "en-IN": "en", ... }
```

作为**语言**归一没问题。但 **AC-LOC-022** 明确要求 `Language=en + Locale=en-IN` 共存并遵守印度语境（日期/金额/单位/市场表达）。实现者若把此函数直接用于 locale 处理，会**静默把 en-IN 抹成 en**，AC-LOC-022 必然失败且难以定位。

**Matbox 侧处置**：Stage 10 实现时 **language 归一与 locale 归一必须是两个独立函数**，禁止复用同一个 `canonicalize`。

---


### 1.3 ✅ 已补上真实 resolver 级测试（2026-09-08，关闭 G-LOC-MATBOX-004）

交接包入库后，§1.1 指出的那两条同义反复终于有真代码可以对着写。新增
[matbox_ac_loc_008_009_real_test.py](全球多语言与本地化/matbox_ac_loc_008_009_real_test.py)（放在包外，**交接包一个字节没动**，只 import 它的 `poc.py`）：

```
PASS | AC-LOC-008 (a) 语言维度：en-IN 的界面语言归一为 en          ← 实得 'en'
FAIL | AC-LOC-008 (b) 地区维度：en-IN 作为 locale 必须保住印度信息  ← 实得 'en'
FAIL | AC-LOC-008 (c) language 归一与 locale 归一必须是两个独立函数 ← 两者都走 canonicalize()，结果相同
PASS | AC-LOC-009 (a) 会话内的显式覆盖生效                         ← 实得 'en'
PASS | AC-LOC-009 (b) 会话结束后回到保存的偏好，覆盖没有污染它       ← 实得 'vi-VN'
PASS | AC-LOC-009 (c) 显式选择的优先级高于保存/租户/浏览器          ← 实得 'en'

结果：4/6 PASS
```

**这两条测试本身经过了自证**（架构原则第74条：把被测代码拿掉，看测试还通不通过）——测试文件末尾的 `prove_tests_are_real()` 把 `resolve_language` 换成"永远返回 zh-CN"、把 `canonicalize` 换成"完全不归一"，两组测试都因此失败。**会失败，才算测试。**

#### 结论一：AC-LOC-009 现在可以计入已验证

3/3 全过，且每一条都真实调用了 `resolve_language()`。测的是三件事：会话内显式覆盖生效、会话结束后回到保存的偏好（覆盖没有污染全局）、显式选择的优先级高于保存/租户/浏览器。**LOC-F014 的这一半不再挂在假测试上。**

#### 结论二：AC-LOC-008 仍不可计入，但性质变了

从「我怀疑有问题」变成「**有一条能跑的失败测试**」。失败点是具体的一行：

```python
canonicalize("en-IN")  →  "en"     # 别名表里 en-US / en-GB / en-IN 全部映射到 en
```

对界面语言来说这是对的（印度用户的 UI 就该是英文）；但同一个函数同时被当作 locale 归一用，**"印度"这个信息就没有任何地方存放**——INR 货币、Asia/Kolkata 时区、dd/MM/yyyy 日期格式全部无从推导。这正是 §1.2 描述的陷阱，现在有了可执行证据。

#### 顺带：G-LOC-MATBOX-005 有验收标准了

原本 `-005` 只写着一句要求「language 归一与 locale 归一必须是两个独立函数」，没有可判定的完成标志。现在有了：

> **把 `matbox_ac_loc_008_009_real_test.py` 跑成 6/6 PASS，`-005` 即为完成。**

具体要求：拆出两个独立函数——`canonicalize_language()` 保持现有行为（`en-IN → en`，供 UI 语言选择用），`canonicalize_locale()` 保住地区（`en-IN → en-IN`，供货币/时区/日期格式用）。两者不得互相替代。


---

## 2｜技术选型调整（本文的核心决定）

### 2.1 调整结论

| 组件 | 交接包锁定 | **Matbox 采用** | 变更理由 |
|---|---|---|---|
| **vue-i18n** | 9.1.9<br>`6154508272590ddd1b65ac297c2690b7cd1cca53`<br>发布 **2021-10-06** | **11.4.10**<br>`87510e2f9344e0734bfe9fbc7e0a2c509042e159`<br>发布 2026-08-25 · MIT | 见 §2.2 |
| **next-intl** | 4.13.7<br>`4e5d46b00320e76e953c41e23afcabc675e14974`<br>发布 2026-08-17 | **4.14.2**<br>`3259beb76120614af8b48e814c56324ad71ccb61`<br>发布 2026-09-01 · MIT | 同大版本，差 1 个小版本 / 15 天；冻结时上游已发布 |
| **Tolgee Platform** | 3.218.3<br>`4f733b47e0978b5da9327e618c90d9eec4db49ba`<br>发布 2026-08-18 | **v3.221.0**<br>`3bae7f3d4076b4f7de9073f7101c153b6e3c44f2`<br>发布 2026-09-07 | 同大版本，差 3 个小版本；许可证边界不变（`ee/` 外 Apache 2.0） |

三个新 commit 均已通过 GitHub API 核实真实存在。

### 2.2 vue-i18n：为什么从 9.1.9 直接跳到 11.4.10

**(a) 9 系列官方已 EOL。** vue-i18n 官方维护页原文：

> `Vue I18n v9 and Vue I18n v10 has reached EOL and is no longer actively maintained.`

**(b) 9.1.9 是 2021 年的版本，且远非该线最新。** npm registry 数据：9.x 共 46 个正式版，9.1.9 排第 11 位，后面还有 35 个。该线最后稳定版是 **9.14.5（2025-07-16）**，官方打了 `stable9` / `legacy9` 标签。即使只在 9 线内，也落后近 4 年。

**(c) ⚠️ 交接包给的锁定理由，在依赖树上查不到支撑。** 包中原文：「锁定 DCloud 实际版本线；禁止 Codex 擅自升 v11」。本会话核查 npm 实际依赖：

| 包 | 与 vue-i18n 的依赖关系 |
|---|---|
| `@dcloudio/uni-app`（latest，Vue2 线） | **无 vue-i18n 依赖** |
| `@dcloudio/uni-app`（`vue3` tag） | 依赖 **`@dcloudio/uni-i18n`（DCloud 自有包）**，非 vue-i18n |
| `@dcloudio/uni-mp-weixin` | **无 vue-i18n 依赖** |

**uni-app 不依赖 vue-i18n；DCloud 自带 i18n 实现。** 因此 vue-i18n 版本是项目级选择，非框架约束，"DCloud 卡版本"不成立。

**(d) v11 的破坏性改动对 Matbox 成本为零。** v11 破坏性改动为：`tc`/`$tc` 移除、Legacy API 模式废弃（v12 移除）、`v-t` 指令废弃（v12 移除）。这些**仅在存在待迁移存量代码时构成成本**。Matbox 本地化**尚未写入任何一行代码**（该包是开工前交接）。

**(e) 反向风险更大。** 若按包中锁定开工，等于**从第一天起就站在官方宣布 EOL 的线上**，未来必然迁移，届时才产生真实迁移成本。

> **决定**：采用 **vue-i18n 11.4.10**。同时废止包中「禁止升 v11」规则——该规则的事实前提（DCloud 约束）不成立。

### 2.3 ⚠️ 必补项：整份交接包未记录任何被淘汰的候选

全文检索 `Weblate` / `Crowdin` / `Lokalise` / `i18next` / `FormatJS` / `候选` / `淘汰` / `备选` / `为什么不用` —— **零命中**。`Phrase` 仅出现 1 次，且是作为"市场趋势证据"，非候选评估。

这违反 Matbox 开发包标准第 9 条（每个技术选择必须记录考虑过的其它选项及否决理由）。**前面九家供应商报告全部做了这件事，本包未做。**

**Matbox 侧处置**：列为 **P0 必补项**。在 Stage 10 物理绑定前，必须补齐至少三组对比：
1. **TMS**：Tolgee vs Weblate vs Crowdin vs Lokalise —— 自托管能力、许可证边界、ICU 支持、API/Webhook、停服影响
2. **Web i18n**：next-intl vs next-i18next vs 直接用 `Intl` —— App Router 支持、SSR/静态化影响、包体积
3. **翻译 Provider**：Qwen-MT vs Google vs DeepL vs Azure Translator —— 中文/越南语质量、家居术语、价格、区域可用性

（第 3 组已有冻结的基准测试方法与"按每条合格结果成本排名"规则，只缺候选面。）

---

### 2.4 被淘汰候选对比（2026-09-08 补齐，关闭 G-LOC-MATBOX-003）

§2.3 列为 P0 必补项的三组对比，本节补齐。**本节只补"候选面"**——本模块已有冻结的基准测试方法与「按每条合格结果成本排名」规则，最终排名必须用 Matbox 自己的家居术语语料实测，不能用通用榜单代替。

#### 组 1：TMS（翻译管理平台）

| 候选 | 能否自托管 | 许可证边界 | 关键限制 | 处置 |
|---|---|---|---|---|
| **Tolgee**（交接包已选 v3.221.0） | 能 | 核心 **Apache-2.0**；`ee/` 与 `webapp/src/ee` 目录为 Tolgee **EE License** | ⚠️ **官方 Docker 镜像与官方二进制始终打包 EE 模块**——即便不买 license（EE 功能未激活），部署本身仍受 EE License 约束。而 EE License 明文禁止「把本软件作为托管或受管服务提供给第三方，使第三方由此获得本软件相当部分的功能」。**Matbox 是多租户 SaaS，这条禁令正对着我们**。另：免费自托管有 **10 seats 上限**，SSO 与细粒度权限属付费功能 | **保留为首选，但附两个硬前提**：① 要真正落在 Apache-2.0 上，必须删掉 `ee/` 目录**自行从源码构建**，不能直接用官方镜像；② 若 Matbox 打算把翻译界面直接暴露给租户使用，Stage 10 绑定前必须先做 EE License 合规判定 |
| **Weblate** | 能 | **GPL**（copyleft） | copyleft 只在「把它的代码编进 Matbox 自己的程序」时传染；作为独立服务通过 API 调用不适用——与质检文档对 SonarQube / OpenGrep 的 LGPL 判断（该文卡片⑥「5 个工具全部是外部进程调用」）是同一个逻辑，可直接复用，不必重新论证。官方托管版 €47/月或 €470/年 | **合格备选**。若 Tolgee 的 EE 边界在 Stage 10 被判定为阻塞，Weblate 是唯一同时满足「可自托管 + 无 SaaS 转售禁令」的候选 |
| **Crowdin** | **不能** | 商业 SaaS | 只有云托管，不提供自托管部署 | **落选**：违反 Matbox 已确立的「自托管开源优先于商业 SaaS」模式（Infisical / Langfuse / SigNoz+immudb 走的都是这条路），且中国区数据落地不可控 |
| **Lokalise** | **不能** | 商业 SaaS | 只有云托管，不提供自托管部署 | **落选**：同上 |

> **这一组查出来的真实风险，此前完全没有记录**：Tolgee 被选中却没人注意到它的官方镜像自带 EE 模块、而 EE License 恰好禁止转售为托管服务。对一个多租户 SaaS 来说这不是细节。**这正是"必须记录被淘汰候选"这条规矩存在的意义——不写对比，就不会去读许可证。**

#### 组 2：Web i18n

| 候选 | 客户端包体积 | App Router 支持 | 处置 |
|---|---|---|---|
| **next-intl**（已选 4.14.2） | **~2KB**；在 Server Components 里渲染的翻译**对客户端包体积零增加** | 为 React Server Components 从头设计 | **保留**：实测数据支持原选择 |
| **next-i18next** | ~14KB gzipped | App Router 支持是 **2026-03 的 v16 才加上的**，属新功能，已知粗糙点（开发时改了翻译 JSON 不会自动刷新，需绕过） | **落选**：体积大约 7 倍，且 App Router 支持成熟度落后一代 |
| **直接用 `Intl`** | 0 | 不适用 | **落选**：`Intl` 只提供格式化原语（日期／数字／复数规则），不提供消息目录、命名空间、按需加载、ICU 消息解析。选它等于自己从头写一个 next-intl，违反「不重建已有成熟能力」 |

#### 组 3：翻译 Provider

> ⚠️ **先说口径**：下表两种价格单位**不可直接比较**——按**字符**计费与按 **token** 计费是两个量纲，中文一个字通常≈1 token 但英文一个 token≈4 字符，跨语种折算比例还不一样。必须先把口径归一到「每条合格译文的成本」再排名（同专项00r §7 确立的口径归一纪律）。

| 候选 | 价格 | 语言覆盖 | 中国大陆可达性 | 处置 |
|---|---|---|---|---|
| **Qwen-MT** | $2.50 / $7.50 每百万 **token** | 中日韩等亚洲语种表现最强 | ✅ 可用 | **中国区候选** |
| **Azure Translator** | $10 每百万**字符** | 100+ | ✅ **21Vianet 主权云可用**（`https://api.translator.azure.cn/`），但开通需**中国法人 + ICP 证 + 境内实体**，且 Azure China 与 Azure Global 是完全隔离的两套账号/计费/门户 | **中国区与欧盟区双侧候选** |
| **Google Cloud Translation** | $20 每百万字符 | 249 语言；2025 年末以 Gemini 模型升级，成语与口语场景改善明显 | ❌ **大陆无区域、境内不可达**，最近只能落香港／新加坡再做跨境组网 | **中国区落选**，欧盟区可保留 |
| **DeepL API Pro** | $25 每百万字符 | **支持中文、越南语、韩语**（见下方更正） | ❌ 大陆不可达 | **中国区落选**，欧盟区候选 |
| Amazon Translate | $15 每百万字符 | — | ❌ 大陆无区域 | 同 Google |

> **⚠️ 更正一条错误来源（这次差点写错）**：本轮第一次检索到的第三方比价文章称「DeepL 不支持中文、阿拉伯语、印地语、泰语、越南语、韩语」，若采信会直接把 DeepL 整个判出局。**该说法与 DeepL 官方不符**——DeepL 官方博客有越南语／泰语／希伯来语上线公告，官方支持语言页也明确列有中文与韩语。已改用官方来源，不采纳该二手说法。**记在这里是为了留证：二手比价文章的"不支持"结论必须回官方核对，否则会淘汰掉本来合格的候选。**

**结合架构原则第40条（中国区+欧盟区混合架构）的结构性结论**：Google 与 DeepL 都不覆盖中国大陆，Azure 覆盖但需中国法人与 ICP。因此翻译 Provider **大概率不是一家通吃，而是分区选型**。**F-LOC-001 的 Provider 抽象必须从第一天就支持「按区域路由到不同引擎」，不能设计成单一 Provider**——这一条现在就能定，不用等基准测试结果。

**Sources**：[Open-Source TMS Comparison 2026: Weblate vs Tolgee vs Pontoon](https://intlpull.com/blog/open-source-tms-comparison-2026)、[Tolgee Licensing 官方文档](https://docs.tolgee.io/platform/self_hosting/licensing)、[Tolgee EE License 原文](https://tolgee.io/ee-license)、[tolgee-platform/ee/LICENSE](https://github.com/tolgee/tolgee-platform/blob/main/ee/LICENSE)、[next-intl vs next-i18next（Locize）](https://www.locize.com/blog/next-intl-vs-next-i18next)、[next-intl 完整指南 2026](https://intlpull.com/blog/next-intl-complete-guide-2026)、[Translation API Pricing 2026: DeepL vs Google Cloud vs Azure](https://chatscontrol.com/blog/translation-api-pricing-2026-deepl-google-azure)、[DeepL 支持越南语／泰语／希伯来语官方公告](https://www.deepl.com/en/blog/vietnamese-thai-hebrew-launch)、[DeepL 官方支持语言页](https://support.deepl.com/hc/en-us/articles/360019925219-DeepL-Translator-languages)、[Azure Translator 主权云文档](https://learn.microsoft.com/en-us/azure/ai-services/translator/reference/sovereign-clouds)、[Azure 中国服务可用性](https://learn.microsoft.com/en-us/azure/china/concepts-service-availability)

---

## 3｜⚠️ 该包声称可复用、但 Matbox 尚不存在的 Owner

包中 §3 明确列出 `REUSE / Must Not Rebuild` 的上游 Owner。其中两个在 Matbox 现状下**不存在**：

| 包中声称的 Owner | 服务的 Feature | Matbox 实况 |
|---|---|---|
| `Platform Product Master`<br>（Product/SKU/Variant/Material 原文） | **LOC-F008** 业务内容翻译库<br>**LOC-F009** 翻译网关<br>`PRODUCT_TRANSLATION_PANEL` 路由 | **商家与产品档案（Catalog/PIM）= ⚪ NOT_STARTED**，FeatureID 未分配。见 Feature Register 第 135 行——用户 2026-09-05 明确要求暂缓 |
| `Shared Messaging / Communication Runtime`<br>（在线聊天 Message/Thread/Delivery State） | **LOC-F020** 实时多语言聊天 + 手机指挥（**P0**） | **Feature Register 中无此模块**。最接近的 F-NOTIFY-001 已在登记中明确写"管终端用户通知，与系统集成事件分发是两层"；F-CHANNEL-001 是品牌/主题/域名，均非 Message SoT |

**包的自觉程度差异**：LOC-F008 的 Gate 写了「Product/Page owner refs」，算部分承认；**LOC-F020 的 Gate 只写了 G-LOC-ST8-007 运行时回归，未提"Messaging Owner 不存在"**。

**Matbox 侧处置**：
- 新增 **G-LOC-MATBOX-001**：`Platform Product Master` Owner 建立前，LOC-F008 / LOC-F009 的 product 类目不得进入 Stage 10 物理绑定（page/content 类目不受影响，F-PAGE-001 已存在）
- 新增 **G-LOC-MATBOX-002**：`Messaging/Conversation` Owner 建立前，**LOC-F020 不得进入 Stage 10 物理绑定**。该 Feature 在包中为 P0，但其 SoT 依赖在 Matbox 侧完全缺失

> **2026-09-08 全仓审计补充：这不是 LOC 独有的问题，它和另外三个功能在等同一样东西。** [Feature Register](Matbox_Feature_Register.md) 早已记录「暂不加入、等待用户后续提供的3份外部包：F-INTERVIEW-001 / F-EXTERNALVIEW-001 / F-SYNDICATION-001，依赖 Conversation/Data Acquisition 引擎、**Communication Runtime** & Meeting、Product Core」——**这里的 Communication Runtime 就是 G-LOC-MATBOX-002 缺的那个 Owner**。也就是说 LOC-F020 不是孤立缺口，而是「等 Communication Runtime」这条队里的第 4 个功能。同理 G-LOC-MATBOX-001 缺的 `Platform Product Master`，对应的是同一条记录里的 **Product Core**。
>
> **对处置的实际影响**：这两道 Gate 不需要 Matbox 单独立项去补，也不应该由 F-LOC-001 自己重建（会直接违反包中自己写的 Must Not Rebuild）。正确做法是**挂到已有的那条外部包队列上**——用户提供 Communication Runtime / Product Core 相关外部包时，一次性解锁 4 个功能，而不是为 LOC 单开一个模块。

---

## 4｜版本号自相矛盾（须先定死再冻结 BaselineID）

同一交付物中出现四处三个版本号：

| 位置 | 值 |
|---|---|
| DEV.docx 标题 | **V1.2-RC** |
| DEV.docx DocID 字段 | `MATBOX-LOCALIZATION-DEV-20260902-`**`V1.1-RC-AILI`** |
| DEV.docx BaselineID 字段 | `MATBOX-LOC-BL-20260902-`**`RC2-AILI`** |
| DEV.docx §14 自审 Gate 正文 | 「本文件 **V1.0-RC**」 |
| features.json `doc_id` | `...-`**`V1.2-RC-CHAT-MOBILE`** |
| features.json `stage9_baseline_candidate_id` | `...-`**`RC3-CHAT-MOBILE`** |

另：`evidence.json` 中 POC 记录路径为 `matbox_localization_contract_poc.py` / `..._stage8_contract_poc.log`，实际打包为 `poc.py` / `poc.log`（README 说明为规避 Windows 路径长度而改名），且 **POC 是唯一没有 sha256 的 artifact**。

**Matbox 侧处置**：以 **features.json 的 `V1.2-RC-CHAT-MOBILE` / `RC3-CHAT-MOBILE` 为准**（内容上 F020 聊天/手机指挥确已写入正文，V1.2 与实际内容相符）。DEV.docx 正文的三处旧号视为未同步的残留，在 Matbox 侧记录为已知不一致，不回改上游包。

---

## 5｜与九家供应商横向收口的交叉印证

该包由用户侧独立产出，**不知晓** [专项00r 九家供应商横向收口](技术选型报告/Matbox_专项00r_九家供应商横向收口_2026-09-08.md) 的存在。但其已关闭的架构冲突中，有三条与 00r 的多家独立收敛**撞到同一结论**：

| 包中已关闭冲突 | 对应 00r 收敛 |
|---|---|
| **C-LOC-013**：Agent 自己检查自己并宣布语言质量 PASS → 复用 Platform Quality/Evidence，**Agent self-check 只能作为 signal** | **收敛⑧**（Fin / Microsoft / Workato 三家独立到达：AI 变更必须走 Eval→Release→Monitor，质量由平台判定而非生成方自判） |
| **C-LOC-015**：A2A/跨 Agent 自然语言成为业务事实 → **跨 Agent 优先传 canonical IDs / structured facts**，A2A 仅 transport | Microsoft A2A + `conversation_history_policy`（**收敛①③**） |
| **C-LOC-011 / C-LOC-012**：每次 Run 注入 immutable `AiLanguageContext` snapshot，retry 沿用同一 `policy_version`；术语/Brand Voice 统一版本化，禁止每个 AI 员工复制一套 | Microsoft Memory 按 Agent×User 隔离 + **收敛③**（执行身份与 Runtime Profile 必须显式且可追溯） |

**LOC-F018 / F019 / F020 的 P0 定位与 00r 的 P0 清单不冲突，属同向加强。**

---

## 6｜Matbox 侧新增 Gate 汇总

| GateID | 内容 | 阻塞对象 |
|---|---|---|
| G-LOC-MATBOX-001 | `Platform Product Master` Owner 建立 | LOC-F008 / F009 的 product 类目 |
| G-LOC-MATBOX-002 | `Messaging/Conversation` Owner 建立 | **LOC-F020（P0）** |
| ~~G-LOC-MATBOX-003~~ **已关闭 2026-09-08** | 补齐三组被淘汰候选对比（TMS / Web i18n / 翻译 Provider）→ 见 §2.4 | ~~全模块 Stage 10 物理绑定~~ 不再阻塞 |
| ~~G-LOC-MATBOX-004~~ **已关闭 2026-09-08** | AC-LOC-008 / AC-LOC-009 补真实 resolver 级测试 → 见 §1.3，测试已写并跑通自证；AC-LOC-009 计入已验证，AC-LOC-008 留下可执行的失败证据 | ~~LOC-F013 / F014 关闭~~ 改由 -005 承接 |
| G-LOC-MATBOX-005 | language 归一与 locale 归一拆成两个独立函数。**验收标准（2026-09-08 补）**：把 [matbox_ac_loc_008_009_real_test.py](全球多语言与本地化/matbox_ac_loc_008_009_real_test.py) 跑成 6/6 PASS 即为完成 | LOC-F001 / F013 实现 |

上游包原有 6 个 Gate（G-LOC-ST8-002~007）继续有效，不因本文调整而改变。

---

## 7｜不变的部分（本文不重复，直接继承交接包）

以下内容**原样采纳**，详见交接包 DEV.docx：

- §0 八条不可违背原则（三链路分离、Language/Locale/Region/Timezone/Currency/Measurement 分开建模、用户显式选择优先、外部 Provider 不得成为 SoT 等）
- §3 完整 Own / Reuse / Must Not Rebuild 表
- §4 三个 Context 分离（UI / Content / AI Session / Agent Collaboration）+ `BusinessContentTranslation` 字段级 schema + `TranslationRequest/Result` + `AiLanguageContext` + 状态机 + 15 类错误分类与重试策略
- §5 LOC-F001~F020 Feature Registry
- §6 七类施工面（每 Feature 的 Owner / Allowed / Protected / Contract / Acceptance）
- §7 路由映射、§8 Permission/Action Contract
- §9 AC-LOC-001~040 + Provider 基准测试方法
- §10 回滚灾备、§12 15 条已关闭架构冲突

---

## 变更记录

| 日期 | 变更 |
|---|---|
| 2026-09-08 | 建立。基于用户侧交接包 `语言包.zip` 的独立核验 + Matbox 侧选型调整。三个组件升至上游 latest（vue-i18n 9.1.9→11.4.10 跨 EOL 线、next-intl→4.14.2、Tolgee→v3.221.0）；登记 2 处缺失 Owner、1 处 POC 空测、1 处 locale 抹平陷阱、1 处未记录被淘汰候选、1 处版本号不一致；新增 5 个 Matbox 侧 Gate。 |
