# Matbox 多端渲染与能力注册 / Renderer + Client Capability Registry（F-MULTIEND-001）

正式开发文档 · V1.0-RC · 2026-08-30

## 当前定位

本专项解决"同一份Page/Content事实（F-PAGE-001）怎么在Web/微信/App/iPad/H5被各自Renderer安全消费，并优雅处理旧客户端"的问题。是内容层（F-PAGE-001）与端侧展现的连接层，被 [F-CHANNEL-001](Matbox_租户渠道实例_正式开发文档_V1.0-RC.md) 依赖。

**这是核查《Matbox_多端平台_CURRENT_正式开发文档_V3.0》F-MULTIEND-001章节后确认的模块**。渲染技术栈（Next.js做Web端SSR/SEO、uni-app做移动端渲染）是Matbox此前已定的多端技术选型的自然延伸，非新增判断——Next.js作为SSR/SEO场景的行业标准做法是无争议共识，不构成需要额外调研验证的选型问题。

**DocID**: MATBOX-MULTIEND-RENDERER-20260830-V1.0-RC
**状态**: DRAFT_RESEARCH_COMPLETE（内容级核查通过，未进入 Stage 10 真实施工）
**依赖方（已知阻塞）**：[F-PAGE-001](Matbox_页面内容Schema_正式开发文档_V1.0-RC.md)（本轮同步建成）

## 1｜不可变原则

1. 不追求一份UI代码在各端像素级一致——各端Renderer按自身平台特性实现，共享的是Page/Block schema，不是UI代码。
2. 不下发任意JS/Vue/React代码到客户端——Block渲染必须走注册过的BlockRenderer，不允许动态执行未经审核的远程代码。
3. Preview不能被搜索引擎收录（noindex），只有Published内容才应用SEO metadata。
4. 未知/不兼容的Block类型必须优雅降级（fallback），不能让整个页面渲染崩溃。

## 2｜全球调研结论

本模块的渲染技术选择（Next.js做Web端SSR/SEO、uni-app做移动端多端编译）沿用Matbox已确定的技术栈方向，Next.js作为SSR/SEO场景的行业标准是2026年无争议的成熟共识，不构成需要独立验证的新选型判断，重点是CapabilityRegistry/PublishGuard这层业务设计——如何让同一份内容在不同客户端版本/渠道能力差异下安全降级，这是本模块真正的设计核心。

## 3｜Own / Reuse / Must Not Rebuild

| 类型 | 对象 | 说明 |
|---|---|---|
| OWN | CapabilityRegistry、PublishGuard、BlockRenderer接口、schemaVersion/deprecation管理 | Matbox自己的多端能力兼容业务规则 |
| REUSE | Next.js（Web端SSR/SEO）、uni-app（移动端渲染） | 渲染技术本身不重新造，两者是渲染适配层不是provider |
| MUST NOT REBUILD | 无 | Next.js/uni-app不是provider而是渲染技术本身，本模块的核心价值就是CapabilityRegistry这层业务逻辑 |

## 4｜Feature Register

| FeatureID | 名称 | 说明 |
|---|---|---|
| MULTIEND-F001 | Web端Renderer（Next.js SSR/SEO） | 公开站点/独立站渲染，SSR/canonical/sitemap/structured data |
| MULTIEND-F002 | 移动端Renderer（uni-app） | 微信/App/iPad/H5渲染 |
| MULTIEND-F003 | Client Capability Registry | BlockDefinition的schemaVersion/supportedChannels/minClientVersion/fallback/deprecation |
| MULTIEND-F004 | Publish Guard | 发布前校验目标渠道是否兼容该Page的Block schema版本，不兼容拒绝发布 |

### MULTIEND-F001 · Web端Renderer
- **目标**：公开网站/独立站以Next.js SSR渲染，SEO metadata/canonical/sitemap/structured data正确。
- **验收标准**：搜索引擎可正常抓取；preview页面不被索引（noindex）。

### MULTIEND-F002 · 移动端Renderer
- **目标**：微信小程序/App/iPad/H5基于uni-app渲染同一份Page内容。
- **验收标准**：跨端功能/截图基本一致（非像素级），未知Block类型优雅降级不崩溃。

### MULTIEND-F003 · Client Capability Registry
- **目标**：每个Block定义记录schemaVersion/支持的渠道/最低客户端版本，供发布时校验。
- **验收标准**：旧客户端遇到新schema版本的Block时优雅降级，不崩溃。

### MULTIEND-F004 · Publish Guard
- **目标**：发布Page到某渠道前，校验该渠道的客户端能力是否支持当前Block schema版本，不兼容则拒绝发布并给出明确原因。
- **验收标准**：人为构造不兼容发布场景，验证被拒绝而非发布后端侧崩溃。

## 5｜核心数据 Contract（逻辑模型，可直接建表/建接口）

**BlockDefinition**
blockType, schemaVersion, supportedChannels[], minClientVersion, deprecatedAt?, fallbackBehavior

**RenderTarget**
targetId, pageVersionId(关联F-PAGE-001), channel(WEB|WECHAT|APP|IPAD|H5), capabilityCheckStatus(PASSED|BLOCKED), publishedAt?

**API 端点（最小集合）**
- `GET /multiend/capabilities` — 查询当前Client Capability Registry
- `POST /multiend/publish-check` — 发布前校验目标渠道兼容性（PublishGuard）
- `GET /multiend/render/{pageVersionId}` — 按渠道渲染指定Page版本（内部渲染服务调用）

## 6｜P0 冻结规则

1. 未知Block类型导致整页渲染崩溃：不允许，必须fallback。
2. Preview页面被搜索引擎收录：不允许。
3. 不兼容的Page schema版本被强行发布到不支持的渠道：不允许（对应Gate G-P0-MULTIEND-001）。

## 7｜当前唯一继续断点

Stage 10（真实Next.js/uni-app项目搭建、真实CDN/缓存策略）尚未开始。下一步：把 MULTIEND-F001~F004 转成 WorkPackage，与F-PAGE-001的Block schema设计同步推进。

## 附录｜来源

- 内容来源：《Matbox_多端平台_CURRENT_正式开发文档_V3.0》F-MULTIEND-001 章节（2026-08-30核对确认）
