# LOC-F010 · Qwen-MT Provider Adapter

> **这是一份 WorkPackage 交接文件，不是总账。** 只装 LOC-F010 自己那一份。
> 20 个功能的完整材料在 [开发交接补全](../../全球多语言/Matbox_全球多语言_开发交接补全_V1.0.md) 与 [DEV.docx](../../全球多语言/Matbox_全球多语言_交接包_V1.0/DEV.docx)。

由 `python docs/_build_loc_workpackages.py` 生成，不要手改

---

## 0 · 派工身份（RC5 字段）

| 字段 | 值 |
|---|---|
| FeatureID | LOC-F010 |
| 模块 | 全球多语言（F-LOC-001，基础层公共能力）|
| Stage 9 状态 | POC_ONLY / NOT_PARALLEL_READY |
| Implementer | opencode |
| ParallelReadiness | POC_ONLY |

## 0.5 · 开工五步（照这个做就行，不用再问）

```bash
git clone https://github.com/xyhzai/matbox.git
cd matbox
git checkout -b wp/loc-f010
mvn -B verify            # 编译 + 跑测试
```

Java 包名固定为 `com.matbox.localization`；代码写在 `backend/modules/localization/` 下。

## 1 · 你要做什么

**目标**：实现 LOC-F010 —— Qwen-MT Provider Adapter。

## 2 · 你能改哪里，不能碰哪里

- ✅ 可以改：`backend/modules/localization/src/main/java/com/matbox/localization/**`
- ✅ 可以改：`backend/modules/localization/src/test/**`（测试是必须写的）
- ❌ 不许碰：其它模块目录、公共契约、别人的测试

### 0.6 · 你的工作区（确定的，不要自己找）

| | |
|---|---|
| 仓库 | `xyhzai/matbox` |
| 落脚目录 | `backend/modules/localization/` —— **只在这里面改**，越界会被 `_check_scope.py` 逐个文件列出来 |
| 分支 | `wp/loc-f010`，从下面那个基线切 |
| 并行 | 一个功能一个分支、各自一份克隆，几十个 AI 同时开工互不干扰 |

### 0.7 · 源码基线（照着核对，不等于就先对齐再动手）

```
base_commit: 0fb8f1dac5e776b0dea315927eeaef0bb68e23e5
分支：      main
```

clone 之后先跑 `git rev-parse HEAD`，**必须等于上面这个 SHA**。
不等于说明你不是在这一版上改的，事后没法复现，也没法说清改动是相对什么的。

### 0.8 · 测试报告交到哪（判你做完没做完就读这个）

```bash
cd backend/modules/localization && mvn -B verify
# 报告产生在：backend/modules/localization/target/surefire-reports/TEST-*.xml
```

判据是 `docs/_check_delivery.py --reports <那个目录> --wp LOC-F010`：
认领的每条编号都要有测试且**通过**——失败、跳过(skipped)、**没有报告**，三种都不算通过。

整套包登记与代码地图（谁在哪、做到哪一步）在 [`code_map.json`](../../code_map.json)，机器可读，一次读全。

机器可读的完整边界见 `docs/loc_protected_scope.yml`，CI 用 `_check_scope.py` 逐个文件判，越界会被逐条点名。

## 3 · 七类施工面（RC5 硬条件，少一个不能派发）

### Frontend/UI｜N/A

### Backend/API/Service｜Applicable · LOC-F010 Owner

### Data/DB/Migration｜N/A

### Async/Runtime｜Applicable · 共享 Reliable Runtime

### Provider/External｜N/A

### Infra/Config｜Applicable · Infra

### Tests/Observability｜Applicable · QA

## 4 · 你的验收标准

**AC-LOC-019**（归属来源：人裁（附理由））
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** Provider DTO/外部状态/外部 ID 不出 Adapter contract
- **Then** Domain contract snapshot 检查通过。
- 原文（DEV.docx §9，一字未改）：`Provider DTO/外部状态/外部 ID 不出 Adapter contract；Domain contract snapshot 检查通过。`

> ⚠️ **哪几条归你，是推导出来的，不是原文**。DEV.docx §9 给了 45 条 AC，**没有给「哪条考哪个功能」的对应表**；上面的归属按端点表与功能名关键词判定，每条都标了来源。**开工第一件事先反向核对**，对不上**先报出来，不许自己改表**——改了表就没人知道原始推导错在哪。

### 4.1 测试方法名必须带 TestID —— 这是硬要求

上面每一条 AC，都要有**至少一个测试方法**，方法名以该编号开头：

```java
@Test
@Tag("AC-LOC-019")                    // 方便单独跑：mvn test -Dgroups=AC-LOC-019
void locT019_describeWhatThisCriterionVerifies() {   // ← 后半段换成「这条在验什么」，英文小驼峰
    // Given / When / Then 三段照上面那条写，不要自己发挥
}
```

**为什么是方法名，不是只打 `@Tag`**：`@Tag` 不会写进 Maven Surefire 的 XML 报告（Surefire 至今不导出 JUnit 5 的 tag），CI 那边读不到，等于没标。而 `<testcase name="...">` 里一定有方法名——**方法名是唯一不依赖任何插件、任何配置就能从 CI 读回来的载体**。

### 4.2 测试上的三条红线（会被自动查）

1. **不许动不归你的测试** —— 比对方法原文，改一个字符就拦
2. **不许删掉或禁用已有测试** —— 含新增 `@Disabled` / `@Ignore`
3. **不许把测试掏空留壳** —— 同一方法断言条数变少即拦

查它的是 `docs/_check_test_integrity.py`，按 diff 判，不看自述。

## 5 · 代码怎么写（接口 / 建表 / 目录 / 任务）

> **这一节是印在这里的，不是链接。** 一个 AI 一边看两份文件就会漏。

### 5.1 你要实现的 API 端点

_本功能不直接暴露端点（属内部能力/适配层）。_

> 路由是**逻辑入口**，物理 URL 在 Stage 10 绑真实仓库时确定——这是 DEV.docx 原文的约束。

### 5.2 你要建的表

> ⚠️ **这些表已经在 `V1__loc_core_tables.sql` 里建好了，不要再写一份重复的迁移**——Flyway 会直接失败。这里印出来是给你**对照字段**用的：契约类必须跟它逐列一致，`ContractMatchesSchemaTest` 双向比对，多一列少一列都红。
>
> 确实要新增就写 `V2__…` 递增，**不许改已发布的 V1**（改了校验和对不上，别人的库会 Validate failed）。

## 20｜数据库及Migration设计

> 字段全部取自 DEV.docx §4.2 / §4.3 原文；类型与约束按原文的「类型/规则」列落成 SQL。
> **本模块只建自己拥有的表**；UserPreference / Tenant 的扩展列归 Platform Core，
> 由 Core Migration 负责（DEV.docx §4.2 原文明写 Owner 是 Platform Core，不在本包）。

```sql
-- V1__loc_core_tables.sql

CREATE TABLE loc_business_content_translation (
    id                uuid         PRIMARY KEY,
    tenant_id         uuid         NOT NULL,
    object_type       varchar(64)  NOT NULL,
    object_id         varchar(128) NOT NULL,
    field_key         varchar(128) NOT NULL,
    source_language   varchar(35)  NOT NULL,
    source_hash       char(64)     NOT NULL,
    source_version    varchar(64),
    target_locale     varchar(35)  NOT NULL,
    translated_text   text,
    status            varchar(24)  NOT NULL,
    provider_ref      varchar(64),
    model_version     varchar(64),
    usage_ref         uuid,
    quality_ref       uuid,
    idempotency_key   char(64)     NOT NULL,
    created_at        timestamptz  NOT NULL DEFAULT now(),
    updated_at        timestamptz  NOT NULL DEFAULT now(),
    CONSTRAINT loc_bct_status_chk CHECK (status IN
        ('pending','translated','review_required','reviewed','released','failed','outdated'))
);
CREATE UNIQUE INDEX loc_bct_idem_uq ON loc_business_content_translation (idempotency_key);
CREATE UNIQUE INDEX loc_bct_target_uq ON loc_business_content_translation
    (tenant_id, object_type, object_id, field_key, target_locale);
CREATE INDEX loc_bct_outdated_idx ON loc_business_content_translation (tenant_id, status);

CREATE TABLE loc_language_policy_profile (
    id                               uuid        PRIMARY KEY,
    tenant_id                        uuid,
    scope                            varchar(16) NOT NULL,
    default_response_language_policy varchar(64) NOT NULL,
    terminology_release_ref          varchar(128),
    brand_voice_ref                  varchar(128),
    market_policy_ref                varchar(128),
    version_no                       integer     NOT NULL DEFAULT 1,
    created_at                       timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT loc_lpp_scope_chk CHECK (scope IN ('PLATFORM','TENANT','BRAND'))
);
CREATE INDEX loc_lpp_tenant_idx ON loc_language_policy_profile (tenant_id, scope);

CREATE TABLE loc_catalog_release (
    id             uuid        PRIMARY KEY,
    catalog_version varchar(64) NOT NULL,
    locale         varchar(35) NOT NULL,
    state          varchar(24) NOT NULL,
    release_ref    varchar(128),
    published_at   timestamptz,
    CONSTRAINT loc_cat_state_chk CHECK (state IN ('candidate','released','rolled_back'))
);
CREATE UNIQUE INDEX loc_cat_ver_locale_uq ON loc_catalog_release (catalog_version, locale);
```

**不建的表（原文约束）**：不复制 Product/Page/User 主事实；
同一 Product 在 zh/en/vi 下 ProductID 不变，**不得生成语言副本**（AC-LOC-005）。

---

### 5.3 你的代码放哪

```
backend/modules/localization/
  src/main/java/com/matbox/localization/
    f010/          ← 你写这里
  src/test/java/com/matbox/localization/
```

### 5.4 拆好的开发任务

## 21｜前后端开发任务拆分

> 前端任务推自 DEV.docx §7 的 6 个逻辑路由；后端任务对应 20 个 Feature。

| 编号 | 任务 | 对应 Route / Feature |
|---|---|---|
| FE-01 | 个人语言/地区设置页 | SETTINGS_LANGUAGE_REGION（F001/F002/F013） |
| FE-02 | 租户本地化设置页 | TENANT_LOCALIZATION_SETTINGS（F002/F016） |
| FE-03 | 站点/页面内容语言切换与翻译状态 | SITE_PAGE_EDITOR_LOCALE（F007/F015/F017） |
| FE-04 | 产品翻译面板（嵌现有详情页，不复制页面） | PRODUCT_TRANSLATION_PANEL（F008/F009/F012） |
| FE-05 | Tolgee authoring 深链入口（运营内部） | LOCALIZATION_AUTHORING_TMS（F003/F006/F012） |
| FE-06 | AI 会话语言与 session override | AI_CONVERSATION（F014/F018/F020） |
| BE-01 | Effective Locale 解析 | LOC-F001 |
| BE-02 | 偏好读写（用户/租户） | LOC-F002 |
| BE-03 | Catalog 与 Key 治理 | LOC-F003 |
| BE-04 | Web / uni-app 适配 | LOC-F004, LOC-F005 |
| BE-05 | Tolgee TMS 桥 | LOC-F006 |
| BE-06 | 业务内容翻译存储 | LOC-F008 |
| BE-07 | 翻译网关与 Provider 路由 | LOC-F009 |
| BE-08 | Provider Adapter（Qwen-MT / Google） | LOC-F010, LOC-F011 |
| BE-09 | 术语/占位符完整性 | LOC-F012 |
| BE-10 | 格式化 ICU-CLDR | LOC-F013 |
| BE-11 | AI 会话语言桥 + 语言智能策略 | LOC-F014, LOC-F018 |
| BE-12 | 发布/缓存/降级 | LOC-F015 |
| BE-13 | 可观测/成本/审计/密钥 | LOC-F016 |
| BE-14 | 回归与验收 Gate | LOC-F017 |
| BE-15 | 语言质量 Gate + Agent 语言工具 | LOC-F019 |
| BE-16 | 实时多语言聊天与移动 AI 桥 | LOC-F020（**被 G-LOC-MATBOX-002 阻塞**） |

---

### 5.4b Provider Adapter 接口规范

## 17｜Provider Adapter接口规范

> 方法名取自 DEV.docx §4.4 原文，不是这里发明的。

```java
public interface TranslationProviderAdapter {
    Capabilities capabilities();
    TranslationResult translate(TranslationRequest req);
    List<TranslationResult> batchTranslate(List<TranslationRequest> reqs);
    Optional<String> detectLanguage(String text);      // optional
    HealthStatus health();
    Optional<CostEstimate> estimate(TranslationRequest req);   // optional
}

public interface TmsAdapter {
    void pushKeys(CatalogKeySet keys);
    CatalogSnapshot pullTranslations(String locale);
    List<String> listLocales();
    KeyStatus getKeyStatus(String key, String locale);
    CatalogCandidate publishCatalogCandidate(String version);
}
```

**铁律（同 DQ adapters 那条）**：各 Adapter 之间禁止互相依赖。
移除任一个只影响可用 Provider 集合，不影响其余 Adapter 运行。

已定 Provider：Qwen-MT（LOC-F010）、Google Translation（LOC-F011）、Tolgee TMS（LOC-F006）。
LOC-F010/F011 在 readiness.json 里是 `POC_ONLY / NOT_PARALLEL_READY`——**这两个不能并行派工**。

---

### 5.5 技术栈（不用再查）

Java 17 / Spring Boot 3.3.5（RuoYi-Vue-Pro 基座）/ **PostgreSQL** / Flyway。
前端：next-intl 14.14.2（Web）、vue-i18n 11.4.10（uni-app）、Tolgee v3.221.0（TMS）。

### 5.6 鉴权、权限与多租户（全局规范，每个功能都适用）

所有接口强制 tenant scope；`tenant_id` 不得从请求体取，只从鉴权上下文取。Locale 偏好属 Platform Core Identity，**不新建第二身份体系**。

### 5.7 错误码、重试、超时与降级（全局规范）

## 19｜错误码、重试、超时和降级规范

> 全部取自 DEV.docx §4.6 原文表格。

| 错误码 | 可重试 | 行为 |
|---|---|---|
| `LOC_INVALID_LOCALE` / `LOC_UNSUPPORTED_LOCALE` | 否 | 400；受控 fallback；记录 validation evidence |
| `LOC_PROVIDER_TIMEOUT` / `LOC_TEMP_UNAVAILABLE` | 是 | 指数退避 + 上限；可切 fallback provider |
| `LOC_PROVIDER_RATE_LIMITED` | 是 | 尊重 retry-after；Circuit Breaker；不阻塞 UI |
| `LOC_PROVIDER_AUTH_FAILED` / `LOC_INVALID_SECRET` | 否 | 告警；**禁止打日志输出 secret** |
| `LOC_PROVIDER_QUOTA_EXCEEDED` / `LOC_COST_LIMIT_REACHED` | 否 | 转人工/降级；写 usage/cost ref（F-COST-001） |
| `LOC_PLACEHOLDER_MISMATCH` | 否 | **Hard Fail**（AC-LOC-014）；不得发布 |
| `LOC_SOURCE_OUTDATED` | 否 | 旧译文转 outdated，不得作为 current 返回（AC-LOC-007） |

---

## 6 · 开工前必读的架构禁令（QUEUE-F009 要求随包附带）

- **架构原则第58条**：模块之间不许互相 import，只能经契约层。
- **架构原则第74条**：把被测代码拿掉，测试还通过的，不算测试。
- **架构原则第76条**：引用别的模块的枚举/字段，写明唯一来源，**不要抄一份下来写「固定为」**——抄下来那一刻它就开始过期。
- **三条不许违反的**（DEV.docx §4.1 / §4.3 原文）：三个 Context 不得互相覆盖；原文永远归 Domain Owner，翻译只是派生（`source_hash` 一变旧译文自动 outdated，不得作为 current 返回）；Language/Locale/Region/Timezone/Currency/Measurement **分开建模，不许合成一个字段**。

## 7 · 完工时必须交出什么

- 代码 + 测试（每条 AC 至少一个 `locT\d{3}_` 开头的测试方法）
- `mvn -B verify` 全绿，CI 的 surefire 报告可读
- AcceptanceRunID：CI 那次运行的 run id，写进 PR 描述
- 反向核对结果：你那几条 AC 归属对不对，对不上的列出来

**「做完了」不由你说了算**：`_check_delivery.py` 读 CI 的 surefire XML，认领的每条 AC 都要有测试且通过；失败、跳过、没有报告，都不算通过。

## 8 · 怎么起本地环境

**先装两样**（缺一样编不了）：JDK **17**、Maven **3.9+**（`mvn -v` 要指向 JDK 17）。

**再起 PostgreSQL 16**：

```bash
docker run -d --name matbox-pg -p 5432:5432 \
  -e POSTGRES_USER=matbox -e POSTGRES_PASSWORD=matbox \
  -e POSTGRES_DB=matbox postgres:16
```

**装不了也能干活**：只推分支让 CI 跑，`.github/workflows/backend-build.yml` 起真 postgres:16、跑迁移、跑全部测试。**判定以 CI 为准。**

**当前事实**：`backend/modules/localization/` 骨架已建好、CI 绿；已有 pom、应用入口、3 个契约类、V1 迁移与两个测试。你不是从零开始。

## 28｜交给未来AI开发人员的完整执行说明

**开工前先做三件事**：

1. **反向确认验收标准归属**。下面 §13-AC 里每条 AC-LOC 归哪个 Feature，
   是**推导的**（DEV.docx §9 只给了 AC 列表，没给"哪条考哪个功能"的对应表）。
   动手前先照原文核一遍，对不上**先报出来，不许自己改表**。
2. **确认你那个 Feature 的 readiness**。`readiness.json` 里
   `POC_ONLY / NOT_PARALLEL_READY` 和 `RELEASE_GATE_OPEN` 的，
   **不是"可以开工"**，先看 Gate 关没关。
3. **LOC-F020 不要动**。它被 G-LOC-MATBOX-002 阻塞，依赖的 Messaging Owner 模块不存在。

**三条不许违反的**（DEV.docx §4.1 / §4.3 原文）：

- **三个 Context 不得互相覆盖**：UI Context / Content Context / AI Session Context。
  后台 UI 是 zh-CN 时可以编辑 content_locale=en/vi，**内容语言变化不改变后台 UI 语言**。
- **原文永远归 Domain Owner，翻译只是派生**。不复制 Source，只引用 object_id。
  `source_hash` 一变，旧译文自动 outdated，**不得作为 current 返回**。
- **Language / Locale / Region / Timezone / Currency / Measurement 分开建模**，
  不许合成一个字段。（AC-LOC-008 就是考这个）

**测试怎么写**：方法名必须以 `locT<三位数字>_` 开头，编号对应下面 §13-AC 的 AC-LOC 编号。
`@Tag` 不算数——Maven Surefire 不把 JUnit 5 的 tag 写进 XML 报告，CI 读不到。
详见《Matbox 开发包标准 V1.0》M1。

---
