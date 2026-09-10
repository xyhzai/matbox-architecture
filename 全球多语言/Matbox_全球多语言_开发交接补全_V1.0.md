# Matbox 全球多语言 · 开发交接补全 V1.0

**模块**：F-LOC-001 全球多语言　　**Feature**：LOC-F001 ~ LOC-F020
**生成于**：2026-09-10 23:36，由 `python docs/_build_loc_supplement.py` 生成，不要手改

> ## 这份文件是什么
> 
> 按《Matbox 开发包标准 V1.0》机检，本模块原本只有 **10/21**，缺 P4/P5/P7/P8/P9/P12/P14/P15/P16/P18/P19。
> 
> 但它**不是没有设计** —— 交接包 DEV.docx 62 千字里，实体字段、契约方法、状态机、错误分类、路由、权限、20 个功能全都有，只是**没有写成标准要求的形式**（没有 DDL 语句、没有 OpenAPI、验收标准不是 Given-When-Then）。
> 
> **所以本文件做的是换形式，不是造内容。** 每一节都标了它推自 DEV.docx 的哪一节。
> 
> **唯一带估算性质的是 §25 工作量** —— DEV.docx 没有工作量数字，那一节写明了估算方法并标注「待人确认」，**不得当作原文引用**。

---

## 13｜API接口清单

> 推自 DEV.docx §7（Logical Route / Entry）与 §4.4（Contract）。
> **路由是逻辑入口，物理 URL 在 Stage 10 绑真实仓库时确定**——这是 DEV.docx 原文的约束，不是这里偷懒。

| 方法 | 路径 | 幂等键 | 对应 Feature |
|---|---|---|---|
| GET | /loc/context/effective | — | LOC-F001 |
| PUT | /loc/preferences/me | user_id | LOC-F002 |
| GET | /loc/preferences/me | — | LOC-F002 |
| PUT | /loc/tenants/{tenantId}/defaults | tenant_id | LOC-F002 |
| GET | /loc/catalog/{locale} | — | LOC-F003, LOC-F015 |
| POST | /loc/catalog/candidates | catalog_version | LOC-F003 |
| POST | /loc/catalog/{version}/publish | catalog_version | LOC-F015 |
| GET | /loc/translations | — | LOC-F008 |
| POST | /loc/translations | sha256(tenant+object_type+object_id+field_key+source_hash+target_locale) | LOC-F008, LOC-F009 |
| POST | /loc/translations/batch | batch_ref | LOC-F009 |
| GET | /loc/translations/{translationId} | — | LOC-F008 |
| POST | /loc/translations/{translationId}/review | translation_id+review_seq | LOC-F012 |
| GET | /loc/providers/health | — | LOC-F009, LOC-F016 |
| POST | /loc/quality/validate | content_or_message_ref | LOC-F019 |
| GET | /loc/terminology/{profileRef} | — | LOC-F012 |
| POST | /loc/ai/session/language | conversation_ref | LOC-F014, LOC-F018 |
| POST | /loc/tms/sync | tms_sync_ref | LOC-F006 |

**幂等键公式来自 DEV.docx §4.4 原文**：
`sha256(tenant + object_type + object_id + field_key + source_hash + target_locale)`。

---

## 14｜Request/Response Schema

> 推自 DEV.docx §4.4 TranslationRequest / Result Contract（字段名取自原文）。

### TranslationRequest

| 字段 | 类型 | 约束 |
|---|---|---|
| tenant_ref | uuid | 必填，强制 tenant scope |
| actor_ref | uuid | 必填 |
| object_type | enum | 受控 registry；不得任意字符串穿透（原文约束） |
| object_id | string | 原 Domain 对象 ID，**只引用不复制 Source** |
| field_key | string | 受控可翻译字段，如 `product.title` |
| source_text | text | **snapshot only**，不作为 SoT |
| source_language | string | BCP-47 |
| source_hash | char(64) | sha256(normalized source text) |
| target_locale | string | BCP-47 |
| idempotency_key | char(64) | 见 §13 公式 |

```json
{
  "request": {
    "tenant_ref": "uuid", "actor_ref": "uuid",
    "object_type": "product", "object_id": "uuid",
    "field_key": "product.title",
    "source_text": "…", "source_language": "zh-CN",
    "source_hash": "sha256…", "target_locale": "vi-VN",
    "idempotency_key": "sha256…"
  },
  "response": {
    "translation_ref": "uuid", "target_locale": "vi-VN",
    "translated_text": "…", "status": "translated",
    "provider_ref": "qwen-mt", "model_version": "…",
    "usage_ref": "uuid", "quality_ref": "uuid"
  }
}
```

### 状态机（DEV.docx §4.5 原文）

```
pending → translated → review_required → reviewed → released
异常：pending/translated → failed
source_hash 变化 → translated/review_required/reviewed 全部转 outdated
outdated 不得作为 current 返回
```

---

## 15｜OpenAPI 3.0文档

```yaml
openapi: 3.0.3
info:
  title: Matbox Global Localization API
  version: 1.0.0
  description: 全球多语言（F-LOC-001）对外契约。路径为逻辑入口，Stage 10 绑定真实仓库时确定物理前缀。
paths:
  /loc/context/effective:
    get:
      operationId: getEffectiveLocaleContext
      responses: { "200": { description: EffectiveLocaleContext } }
  /loc/preferences/me:
    put:
      operationId: updateMyPreference
      responses: { "200": { description: OK }, "400": { description: INVALID_LOCALE } }
  /loc/translations:
    post:
      operationId: requestTranslation
      parameters:
        - in: header
          name: Idempotency-Key
          required: true
          schema: { type: string }
      responses:
        "202": { description: accepted, pending }
        "409": { description: 幂等冲突，返回既有 translation_ref }
        "429": { description: PROVIDER_RATE_LIMITED }
  /loc/providers/health:
    get:
      operationId: providerHealth
      responses: { "200": { description: health snapshot } }
components:
  schemas:
    TranslationRequest:
      type: object
      required: [tenant_ref, object_type, object_id, field_key, source_hash, target_locale]
      properties:
        tenant_ref: { type: string, format: uuid }
        object_type: { type: string }
        object_id: { type: string }
        field_key: { type: string }
        source_hash: { type: string, maxLength: 64 }
        target_locale: { type: string }
```

---

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

## 18｜Webhook、回调及异步任务规范

> 推自 DEV.docx §4.4 batchTranslate / TMS pullTranslations 与 §4.6 重试策略。

| 异步任务 | 触发 | 回调/完成信号 | 复用 |
|---|---|---|---|
| 长批量翻译 | POST /loc/translations/batch | 回调事件 `loc.translation.batch.completed`（含 batch_ref、成功/失败计数） | F-TASK-001 + F-QUEUE-001（DEV.docx §3 REUSE 原文） |
| TMS 拉取 | POST /loc/tms/sync 或定时 | `loc.catalog.candidate.ready` | F-TASK-001 |
| Catalog 发布 | POST /loc/catalog/{version}/publish | `loc.catalog.released`（Release Artifact） | F-RELEASE-001 |
| Provider 健康探测 | 定时 | `loc.provider.health.changed` | F-OBS 客户端 |

**重试策略（DEV.docx §4.6 原文）**：
`PROVIDER_TIMEOUT/TEMP_UNAVAILABLE` 指数退避 + 上限，可切 fallback provider；
`PROVIDER_RATE_LIMITED` 尊重 retry-after + Circuit Breaker，**不无限同步阻塞 UI**；
`PROVIDER_AUTH_FAILED/INVALID_SECRET` 不重试直到配置修复，**禁止把 secret 打日志**。

**Webhook 签名与重放**：复用 F-ACTION-001 的 Action/Tool Gateway 授权（DEV.docx §3 REUSE），
本模块不自建第二套签名机制。

---

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

## 25｜开发阶段、优先级和预计工作量

> ⚠️ **本节是估算，不是原文。** DEV.docx 没有工作量数字。
> 估算方法写在下面，**必须由人确认后才能用于排期**，不得当作原文引用。

**估算方法**：按每个 Feature 在 DEV.docx §6 七类施工面里被登记的施工面数量分档 ——
1~2 个施工面记 2 人日，3~4 个记 4 人日，5 个及以上记 6 人日；
标 `POC_ONLY / NOT_PARALLEL_READY` 的额外 +2 人日（要先把 POC 转成可并行的实现）。

| 阶段 | 内容 | 估算 |
|---|---|---|
| 第 1 批 | LOC-F001, F002（解析与偏好，其余全部依赖它） | 8 人日 |
| 第 2 批 | F003, F004, F005, F007, F013 | 20 人日 |
| 第 3 批 | F006, F008, F009, F012 | 18 人日 |
| 第 4 批 | F010, F011（POC_ONLY，需先转正） | 12 人日 |
| 第 5 批 | F014, F015, F016, F017 | 16 人日 |
| 第 6 批 | F018, F019 | 10 人日 |
| 第 7 批 | F020（**阻塞中，不排期**） | — |
| **合计** | 不含 F020 | **84 人日（估算，待确认）** |

---

## 26｜风险、阻塞项及备用方案

> 全部取自交接包 readiness.json 与 DEV.docx，**不是这里想出来的**。

| 风险/阻塞 | 出处 | 影响 | 备用方案 |
|---|---|---|---|
| **LOC-F020 被 G-LOC-MATBOX-002 阻塞** | readiness.json | 在线聊天 Messaging Owner **在架构图里不存在** | 无 —— 必须等该模块建立，不能绕 |
| **LOC-F008 依赖尚不存在的 Product Master** | 架构图卡片 | 业务内容翻译库无法绑定真实对象 | 先按 object_type/object_id 只引用不复制，Product Master 就位后回填 |
| LOC-F010 / F011 为 `POC_ONLY` | readiness.json | 两个 Provider 适配器不可并行派工 | 先转正再派，或先只上一个 Provider |
| LOC-F004/F005/F006 `RELEASE_GATE_OPEN` | readiness.json | 发布关未关 | 走 F-RELEASE-001 的 Release Artifact 流程 |
| Betterleaks 类不成熟依赖 | DEV.docx §2 | 上游 EOL / 停服 | vue-i18n 已从 9.1.9(EOL) 升至 11.4.10；Tolgee 停服时已发布 Catalog 仍可用（AC-LOC-012） |
| Provider 停服 / 限流 / 超额 | DEV.docx §4.6 | 翻译不可用 | fallback provider + Circuit Breaker + 已发布 Catalog 降级 |
| 6 个 Stage10 过程 Gate 未关闭 | readiness.json | 物理绑定未完成 | 绑真实仓库时逐条关闭 |

---

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

## 13-AC｜验收标准（Given-When-Then）

> **本节由 `_build_loc_supplement.py` 从 DEV.docx §9 机械转写**，不是手打的。
> 原文一个字没改，只是放进标准要求的句式里。每条都附了原文供核对。

**AC-LOC-001**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** 首次访问 browser=vi-VN、无用户偏好
- **Then** 解析到允许的 vi-VN（若 Tenant 未指定更高优先级）。
- 原文（DEV.docx §9，一字未改）：`首次访问 browser=vi-VN、无用户偏好；解析到允许的 vi-VN（若 Tenant 未指定更高优先级）。`

**AC-LOC-002**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** 用户明确选择 English 后
- **Then** 刷新/跳页/退出重登/另一浏览器账号登录仍为 English。
- 原文（DEV.docx §9，一字未改）：`用户明确选择 English 后，刷新/跳页/退出重登/另一浏览器账号登录仍为 English。`

**AC-LOC-003**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** Tenant default=en，browser=vi
- **Then** 无 user preference 时结果=en。
- 原文（DEV.docx §9，一字未改）：`Tenant default=en，browser=vi；无 user preference 时结果=en。`

**AC-LOC-004**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** P0 页面必须翻译 UI String completeness=100%
- **Then** Brand/SKU/用户原文等 exempt 明确登记。
- 原文（DEV.docx §9，一字未改）：`P0 页面必须翻译 UI String completeness=100%；Brand/SKU/用户原文等 exempt 明确登记。`

**AC-LOC-005**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** 同一 Product 在 zh/en/vi 下 ProductID 不变
- **Then** 不得生成语言副本。
- 原文（DEV.docx §9，一字未改）：`同一 Product 在 zh/en/vi 下 ProductID 不变；不得生成语言副本。`

**AC-LOC-006**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** 翻译/切换不会修改 Source 原文。
- **Then** 结果与上述描述一致
- 原文（DEV.docx §9，一字未改）：`翻译/切换不会修改 Source 原文。`

**AC-LOC-007**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** Source 文本变更后旧译文自动 Outdated
- **Then** 且不能作为 current 返回。
- 原文（DEV.docx §9，一字未改）：`Source 文本变更后旧译文自动 Outdated，且不能作为 current 返回。`

**AC-LOC-008**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** Language=en、Locale=en-IN、Currency=INR、Timezone=Asia/Kolkata、Metric 可独立共存。
- **Then** 结果与上述描述一致
- 原文（DEV.docx §9，一字未改）：`Language=en、Locale=en-IN、Currency=INR、Timezone=Asia/Kolkata、Metric 可独立共存。`

**AC-LOC-009**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** preferred vi 的用户开启 AI 会话默认 vi
- **Then** session override=en 后只当前会话 en，新会话恢复 vi。
- 原文（DEV.docx §9，一字未改）：`preferred vi 的用户开启 AI 会话默认 vi；session override=en 后只当前会话 en，新会话恢复 vi。`

**AC-LOC-010**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** zh/en/vi P0 页面关键 CTA 可见、可点、不遮挡
- **Then** 不因文本长度导致功能不可用。
- 原文（DEV.docx §9，一字未改）：`zh/en/vi P0 页面关键 CTA 可见、可点、不遮挡，不因文本长度导致功能不可用。`

**AC-LOC-011**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** 后台 UI=zh-CN 时，可编辑 content_locale=en/vi
- **Then** 内容语言变化不改变后台 UI language。
- 原文（DEV.docx §9，一字未改）：`后台 UI=zh-CN 时，可编辑 content_locale=en/vi；内容语言变化不改变后台 UI language。`

**AC-LOC-012**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** TMS/Tolgee 完全不可用时
- **Then** 已发布 Catalog 的 Web/uni-app 固定 UI 仍正常工作。
- 原文（DEV.docx §9，一字未改）：`TMS/Tolgee 完全不可用时，已发布 Catalog 的 Web/uni-app 固定 UI 仍正常工作。`

**AC-LOC-013**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** Translation Provider 超时/限流时：bounded retry 或切换 provider
- **Then** UI 不被阻塞；同 idempotency 不重复计费。
- 原文（DEV.docx §9，一字未改）：`Translation Provider 超时/限流时：bounded retry 或切换 provider；UI 不被阻塞；同 idempotency 不重复计费。`

**AC-LOC-014**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** ICU/placeholders 翻译前后变量集合完全一致
- **Then** 任何缺失/新增/改名触发 Hard Fail。
- 原文（DEV.docx §9，一字未改）：`ICU/placeholders 翻译前后变量集合完全一致；任何缺失/新增/改名触发 Hard Fail。`

**AC-LOC-015**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** 跨 Tenant 请求 object_id 即使相同也不能读取/写入对方 Translation。
- **Then** 结果与上述描述一致
- 原文（DEV.docx §9，一字未改）：`跨 Tenant 请求 object_id 即使相同也不能读取/写入对方 Translation。`

**AC-LOC-016**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** 日志、trace、Evidence、错误消息中 0 明文 Provider/TMS secret。
- **Then** 结果与上述描述一致
- 原文（DEV.docx §9，一字未改）：`日志、trace、Evidence、错误消息中 0 明文 Provider/TMS secret。`

**AC-LOC-017**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** 每次付费翻译产生 usage/cost ref
- **Then** 重复 cache hit/已存在译文不新增 provider cost。
- 原文（DEV.docx §9，一字未改）：`每次付费翻译产生 usage/cost ref；重复 cache hit/已存在译文不新增 provider cost。`

**AC-LOC-018**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** Catalog Release 可回滚到 Previous Stable
- **Then** 回滚不改 Product/Page/用户事实。
- 原文（DEV.docx §9，一字未改）：`Catalog Release 可回滚到 Previous Stable；回滚不改 Product/Page/用户事实。`

**AC-LOC-019**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** Provider DTO/外部状态/外部 ID 不出 Adapter contract
- **Then** Domain contract snapshot 检查通过。
- 原文（DEV.docx §9，一字未改）：`Provider DTO/外部状态/外部 ID 不出 Adapter contract；Domain contract snapshot 检查通过。`

**AC-LOC-020**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** GoodBarber 不被标记为 same-app dynamic locale runtime
- **Then** 相关能力若启用必须显式 Channel limitation。
- 原文（DEV.docx §9，一字未改）：`GoodBarber 不被标记为 same-app dynamic locale runtime；相关能力若启用必须显式 Channel limitation。`

**AC-LOC-021**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** preferred=vi-VN、locale=vi-VN 的客户开启销售 AI：首轮及后续默认越南语
- **Then** 不经过“强制翻中文再翻回”的主链。
- 原文（DEV.docx §9，一字未改）：`preferred=vi-VN、locale=vi-VN 的客户开启销售 AI：首轮及后续默认越南语；不经过“强制翻中文再翻回”的主链。`

**AC-LOC-022**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** Language=en + Locale=en-IN + Currency=INR：AI 用英语回复，但日期/金额/单位/市场表达遵守 India locale policy
- **Then** 不能自动变成美国语境。
- 原文（DEV.docx §9，一字未改）：`Language=en + Locale=en-IN + Currency=INR：AI 用英语回复，但日期/金额/单位/市场表达遵守 India locale policy；不能自动变成美国语境。`

**AC-LOC-023**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** Tenant/Brand terminology 规定特定 SKU/材料术语后，客服/销售/内容 AI 在 zh/en/vi 输出中遵守已发布 terminology profile
- **Then** 冲突按受控 precedence 处理。
- 原文（DEV.docx §9，一字未改）：`Tenant/Brand terminology 规定特定 SKU/材料术语后，客服/销售/内容 AI 在 zh/en/vi 输出中遵守已发布 terminology profile；冲突按受控 precedence 处理。`

**AC-LOC-024**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** Brand Voice 在不同 locale 可定义正式度/称谓/风格
- **Then** AI 输出必须引用 policy_version，policy 变更后新会话采用新版本，旧 Run Evidence 可复现。
- 原文（DEV.docx §9，一字未改）：`Brand Voice 在不同 locale 可定义正式度/称谓/风格；AI 输出必须引用 policy_version，policy 变更后新会话采用新版本，旧 Run Evidence 可复现。`

**AC-LOC-025**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** AI Runtime retry/resume 不改变原 Run 的 LanguageContext/policy_version
- **Then** 用户显式切换会话语言后才生成新 context revision。
- 原文（DEV.docx §9，一字未改）：`AI Runtime retry/resume 不改变原 Run 的 LanguageContext/policy_version；用户显式切换会话语言后才生成新 context revision。`

**AC-LOC-026**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** AI LanguageContext 缺失/加载失败时不得硬编码中文/英文
- **Then** 按受控 fallback/degraded policy 并记录 Evidence。
- 原文（DEV.docx §9，一字未改）：`AI LanguageContext 缺失/加载失败时不得硬编码中文/英文；按受控 fallback/degraded policy 并记录 Evidence。`

**AC-LOC-027**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** AI 外发内容若修改 SKU/价格/数量/尺寸/订单状态等 canonical facts，Language Quality Gate 必须 Hard Fail
- **Then** 不能以“语句更自然”为理由放行。
- 原文（DEV.docx §9，一字未改）：`AI 外发内容若修改 SKU/价格/数量/尺寸/订单状态等 canonical facts，Language Quality Gate 必须 Hard Fail；不能以“语句更自然”为理由放行。`

**AC-LOC-028**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** AI 外发内容存在 glossary/placeholder/Brand Voice 严重冲突时，按风险策略阻断自动发送或进入人工 Review
- **Then** Agent 自己说“检查通过”不算 PASS。
- 原文（DEV.docx §9，一字未改）：`AI 外发内容存在 glossary/placeholder/Brand Voice 严重冲突时，按风险策略阻断自动发送或进入人工 Review；Agent 自己说“检查通过”不算 PASS。`

**AC-LOC-029**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** MCP/TMS 语言工具不可用时，AI 员工仍可使用已发布 LanguagePolicy/Terminology bundle 运行
- **Then** 不能因 Tolgee/MCP down 导致核心会话不可用。
- 原文（DEV.docx §9，一字未改）：`MCP/TMS 语言工具不可用时，AI 员工仍可使用已发布 LanguagePolicy/Terminology bundle 运行；不能因 Tolgee/MCP down 导致核心会话不可用。`

**AC-LOC-030**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** Agent 通过 MCP/Tool 调语言资产时必须使用 Matbox service credential + least privilege
- **Then** 日志/prompt/evidence 中 0 明文 secret。
- 原文（DEV.docx §9，一字未改）：`Agent 通过 MCP/Tool 调语言资产时必须使用 Matbox service credential + least privilege；日志/prompt/evidence 中 0 明文 secret。`

**AC-LOC-031**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** 跨 AI 员工协作时 ProductID/SKU/Quantity/Intent/Status 等以 canonical structured refs 传递
- **Then** 任何 A2A/消息协议的自然语言文本不得成为 Product/Task/Order SoT。
- 原文（DEV.docx §9，一字未改）：`跨 AI 员工协作时 ProductID/SKU/Quantity/Intent/Status 等以 canonical structured refs 传递；任何 A2A/消息协议的自然语言文本不得成为 Product/Task/Order SoT。`

**AC-LOC-032**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** 相同 Golden Challenge Set 在 zh/en/vi 上执行：语言正确、术语、事实保真、品牌语气、Locale、工具失败恢复均有独立 PASS/FAIL 与 Evidence。
- **Then** 结果与上述描述一致
- 原文（DEV.docx §9，一字未改）：`相同 Golden Challenge Set 在 zh/en/vi 上执行：语言正确、术语、事实保真、品牌语气、Locale、工具失败恢复均有独立 PASS/FAIL 与 Evidence。`

**AC-LOC-033**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** 越南客户在在线聊天用 vi-VN 连续多轮沟通：每条原始 Message 保留，AI 默认 vi-VN
- **Then** 人工坐席若切中文查看，只生成 derived translation view，不覆盖原消息。
- 原文（DEV.docx §9，一字未改）：`越南客户在在线聊天用 vi-VN 连续多轮沟通：每条原始 Message 保留，AI 默认 vi-VN；人工坐席若切中文查看，只生成 derived translation view，不覆盖原消息。`

**AC-LOC-034**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** 同一 Conversation 从 Web 切到手机/小程序后继续指挥 AI：language context revision、conversation_ref、task_ref 连续
- **Then** 不得因端切换回平台默认语言。
- 原文（DEV.docx §9，一字未改）：`同一 Conversation 从 Web 切到手机/小程序后继续指挥 AI：language context revision、conversation_ref、task_ref 连续；不得因端切换回平台默认语言。`

**AC-LOC-035**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** 用户手机用中文下令“把产品发布到美国独立站”：command_language=zh-CN，但 target_output_language=en、target_locale=en-US
- **Then** 最终客户内容按美国语境输出，不能把中文指令语言误当发布语言。
- 原文（DEV.docx §9，一字未改）：`用户手机用中文下令“把产品发布到美国独立站”：command_language=zh-CN，但 target_output_language=en、target_locale=en-US；最终客户内容按美国语境输出，不能把中文指令语言误当发布语言。`

**AC-LOC-036**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** 手机文字命令与语音命令进入同一 Command Contract
- **Then** ASR 低置信度/语言不确定时必须澄清，不能猜测后执行高风险动作。
- 原文（DEV.docx §9，一字未改）：`手机文字命令与语音命令进入同一 Command Contract；ASR 低置信度/语言不确定时必须澄清，不能猜测后执行高风险动作。`

**AC-LOC-037**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** 网络断开/手机重连/重复点击发送相同 command_id 或 idempotency_key：AI Task/外发动作只执行一次
- **Then** 聊天消息/任务状态不重复。
- 原文（DEV.docx §9，一字未改）：`网络断开/手机重连/重复点击发送相同 command_id 或 idempotency_key：AI Task/外发动作只执行一次；聊天消息/任务状态不重复。`

**AC-LOC-038**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** 客户在线聊天的翻译服务/TMS/MCP 宕机时：原始聊天和 AI 原生多语言主链仍可运行
- **Then** 人工坐席译文进入 degraded/暂不可用，不阻断 Message SoT。
- 原文（DEV.docx §9，一字未改）：`客户在线聊天的翻译服务/TMS/MCP 宕机时：原始聊天和 AI 原生多语言主链仍可运行；人工坐席译文进入 degraded/暂不可用，不阻断 Message SoT。`

**AC-LOC-039**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** 在线聊天/手机指挥过程中切换语言不得改变 ProductID/SKU/Quantity/Price/Order/Task 等 canonical facts
- **Then** 任何事实写入必须经过原 Domain Action/权限/审批。
- 原文（DEV.docx §9，一字未改）：`在线聊天/手机指挥过程中切换语言不得改变 ProductID/SKU/Quantity/Price/Order/Task 等 canonical facts；任何事实写入必须经过原 Domain Action/权限/审批。`

**AC-LOC-040**
- **Given** 全球多语言模块已按本包契约部署，租户与用户上下文已就绪
- **When** 同一客户从在线聊天提出需求→手机指挥销售 AI→AI员工协作执行：Message/Conversation/Command/Task refs 可追溯
- **Then** Agent 间传 structured facts，语言文本不得成为 Task/Product/Order SoT。
- 原文（DEV.docx §9，一字未改）：`同一客户从在线聊天提出需求→手机指挥销售 AI→AI员工协作执行：Message/Conversation/Command/Task refs 可追溯，Agent 间传 structured facts，语言文本不得成为 Task/Product/Order SoT。`


---

**共 40 条验收标准，全部转写自 DEV.docx §9。**

**出处**：DEV.docx（SHA-256 已由 MANIFEST 校验，C7 逐字节验过）、features.json、readiness.json。本文件不引用任何交接包以外的来源。