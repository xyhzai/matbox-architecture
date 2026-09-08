# Matbox 页面内容 Schema / Page Content Schema + Draft/Version（F-PAGE-001）

正式开发文档 · V1.0-RC · 2026-08-30

## 当前定位

本专项解决"企业网站/独立站的内容怎么用一套框架无关的schema管理，支持AI安全编辑、预览/发布/回滚"的问题——内容事实（Page/Block）与渲染技术（Next.js/uni-app）解耦，同一份内容能被多端渲染消费。是 [F-MULTIEND-001](Matbox_多端渲染与能力注册_正式开发文档_V1.0-RC.md) 的上游内容源，被 [F-CHANNEL-001](Matbox_租户渠道实例_正式开发文档_V1.0-RC.md) 依赖。

**这是核查《Matbox_多端平台_CURRENT_正式开发文档_V3.0》F-PAGE-001章节后确认的模块**。纯业务schema设计，源文档提到的Shopify/Sanity只是内容管理形态参考，不是要接入的具体产品/技术，不构成需要独立验证的厂商选型。

**DocID**: MATBOX-PAGE-CONTENT-SCHEMA-20260830-V1.0-RC
**状态**: DRAFT_RESEARCH_COMPLETE（内容级核查通过，未进入 Stage 10 真实施工）
**依赖方（已知阻塞）**：F-PLAT-001、F-STORAGE-001（已建成，原F-ASSET-001已并入）、F-MULTIEND-001（本轮同步建成）

## 1｜不可变原则

1. Puck（可选编辑器）或Next.js/uni-app的component schema不当作核心事实——核心事实是本模块自己定义的Page/Block schema，渲染技术只是消费方。
2. AI不改生产源码——AI对内容的编辑限定在Page/Block schema的Draft层面，不涉及渲染代码本身。
3. Draft与Published版本必须隔离——草稿修改不影响线上已发布内容，直到显式发布。
4. 已发布版本不可变（immutable），回滚是切换到历史版本引用，不是覆写。

## 2｜全球调研结论

本模块是纯业务schema设计（Page/Block/Draft/Version/channel overrides/diff/revision guard），不涉及需要独立验证的第三方技术选型——源文档"源码/外部基线"栏提到的Shopify/Sanity是"这类内容管理产品长什么样"的形态参考，源文档本身也在Provider层明确写"Puck仅为可选编辑器，不是core provider"，不是要接入的具体依赖，故本模块不需要额外技术调研，重点是schema设计本身的完整性。

## 3｜Own / Reuse / Must Not Rebuild

| 类型 | 对象 | 说明 |
|---|---|---|
| OWN | Page/Block schema、Draft/Published版本管理、diff/revision guard、Block Registry | Matbox自己的内容管理业务规则 |
| REUSE | Puck（可选，作为编辑器UI层，非核心） | 如采用，仅作为可视化编辑工具，不影响核心schema |
| MUST NOT REBUILD | 无 | 本模块本身是内容管理的核心业务层，没有可直接复用的现成开源内容schema适合直接套用 |

## 4｜Feature Register

| FeatureID | 名称 | 说明 |
|---|---|---|
| PAGE-F001 | Page/Block Schema | 框架无关的内容结构定义，供F-MULTIEND-001各端Renderer消费 |
| PAGE-F002 | Draft/Published版本管理 | 草稿与已发布版本隔离，已发布版本immutable |
| PAGE-F003 | Diff与Revision Guard | 编辑冲突检测（revision conflict返回409），diff可视化 |
| PAGE-F004 | Channel Overrides | 同一Page在不同Channel（渠道）可有差异化覆盖内容 |

### PAGE-F001 · Page/Block Schema
- **目标**：定义框架无关的Page/Block结构，AI和人类均可安全编辑，编辑对象是schema不是渲染代码。
- **验收标准**：同一Page schema能被F-MULTIEND-001的Web/微信/App/iPad/H5多个Renderer正确消费。

### PAGE-F002 · Draft/Published版本管理
- **目标**：草稿编辑不影响线上内容，显式发布后才生效；已发布版本不可修改，只能发新版本或回滚到历史版本。
- **验收标准**：Draft与Live完全隔离；发布后原版本仍可查询用于回滚。

### PAGE-F003 · Diff与Revision Guard
- **目标**：并发编辑同一Page时检测冲突，返回409而非静默覆盖；提供可读的diff。
- **验收标准**：两个编辑者同时改同一Page的同一部分，后提交者收到明确的冲突提示。

### PAGE-F004 · Channel Overrides
- **目标**：同一Page内容在不同发布目标（Web/小程序/App等）可以有局部差异化覆盖，不需要复制整份内容。
- **验收标准**：targetChannels明确记录该Page版本要发布到哪些渠道，overrides只影响指定渠道。

## 5｜核心数据 Contract（逻辑模型，可直接建表/建接口）

**Page**
pageId, tenantId, slug, blockRegistryVersion, createdAt

**PageVersion**
pageVersionId, pageId, status(DRAFT|PUBLISHED|ARCHIVED), blocks[]（引用Block Registry定义）, channelOverrides{}, revision, publishedAt?, createdBy

**BlockRegistry**
blockType, schemaVersion, supportedChannels[]（关联F-MULTIEND-001的能力注册）

**API 端点（最小集合）**
- `POST /pages/{pageId}/draft` — 创建/更新草稿版本
- `POST /pages/{pageId}/publish` — 发布草稿为正式版本（immutable）
- `POST /pages/{pageId}/rollback` — 回滚到历史版本
- `GET /pages/{pageId}/diff` — 查询草稿与当前已发布版本的diff

## 6｜P0 冻结规则

1. 已发布版本被直接覆写（非immutable）：不允许。
2. 并发编辑冲突被静默覆盖而非返回409：不允许。
3. Page schema与渲染技术（Next.js/uni-app component）强耦合：不允许。

## 7｜当前唯一继续断点

Stage 10（真实建表、真实与F-MULTIEND-001渲染层联调）尚未开始。下一步：把 PAGE-F001~F004 转成 WorkPackage，需与F-MULTIEND-001的BlockRenderer接口同步设计。

## 附录｜来源

- 内容来源：《Matbox_多端平台_CURRENT_正式开发文档_V3.0》F-PAGE-001 章节（2026-08-30核对确认）
