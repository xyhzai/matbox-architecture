# Matbox 租户渠道实例 / Tenant Channel Instance / Brand / Theme / Template / Domain / App Identity（F-CHANNEL-001）

正式开发文档 · V1.0-RC · 2026-08-30

## 当前定位

本专项解决"每个企业的网站/独立站/小程序/App/iPad/H5怎么作为受控的Channel Instance管理——共享Matbox Core，但各自有品牌/模板/域名/客户端身份/发布配置"的问题，支持白标（white-label）和集中运营而不复制业务平台。依赖已建成的 [F-CRED-001](Matbox_密钥管理_正式开发文档_V1.0-RC.md)（签名凭证）、[F-RELEASE-001](Matbox_发布与基线系统_正式开发文档_V1.0-RC.md)（发布追溯）、[F-PAGE-001](Matbox_页面内容Schema_正式开发文档_V1.0-RC.md)（内容源）。

**这是核查《Matbox_多端平台_CURRENT_正式开发文档_V3.0》F-CHANNEL-001章节后确认的模块**。源文档提到的GoodBarber只是"白标/集中运营产品形态"的参考对象，不是要接入的具体技术，不构成需要独立验证的厂商选型。

**DocID**: MATBOX-TENANT-CHANNEL-INSTANCE-20260830-V1.0-RC
**状态**: DRAFT_RESEARCH_COMPLETE（内容级核查通过，未进入 Stage 10 真实施工）
**依赖方（已知阻塞）**：F-PLAT-001、F-CRED-001（已建成）、F-RELEASE-001（已建成）、[F-PAGE-001](Matbox_页面内容Schema_正式开发文档_V1.0-RC.md)（本轮同步建成）

## 1｜不可变原则

1. 不复制Tenant/Page/Product数据——ChannelInstance只是配置层引用，业务数据仍是单一事实源。
2. 证书/私钥/secret不得明文写入业务DB或Git——必须经F-CRED-001管理，本模块只存CredentialRef。
3. 模板升级不得覆盖企业已定制的内容——模板是基线，定制部分必须保留（template customization preserved）。
4. App Store/微信平台的metadata不当作业务SoT——这些是外部平台的登记信息，本模块只存引用和状态同步。

## 2｜全球调研结论

本模块是纯业务schema设计（ChannelInstance/Brand/Theme/Template/Domain/App Identity管理），源文档"源码/外部基线"栏提到的GoodBarber是"白标+模板+集中运营"这类产品形态的参考坐标，不是要接入的具体SDK或服务，不需要独立验证厂商选型；核心风险点是"多租户配置隔离"和"密钥/证书不落地明文"，这两条已有Matbox已建成的F-TENANT-001（数据隔离）和F-CRED-001（凭证管理）作为基础设施，本模块直接复用，不重复设计底层安全机制。

## 3｜Own / Reuse / Must Not Rebuild

| 类型 | 对象 | 说明 |
|---|---|---|
| OWN | ChannelInstanceService、DomainBinding、BrandTheme、BuildIdentity metadata校验 | Matbox自己的渠道实例配置业务规则 |
| REUSE | F-CRED-001（签名证书/密钥管理）、F-RELEASE-001（构建产物追溯）、F-TENANT-001（多租户隔离） | 不重复造凭证管理和数据隔离机制 |
| MUST NOT REBUILD | DNS/CDN/微信/App Store/Play等外部平台自身的分发机制 | 通过CredentialRef+标准adapter对接，不重新实现这些平台协议 |

## 4｜Feature Register

| FeatureID | 名称 | 说明 |
|---|---|---|
| CHANNEL-F001 | ChannelInstance管理 | 每个企业每种渠道类型（网站/小程序/App等）作为独立受控实例 |
| CHANNEL-F002 | Brand/Theme/Template绑定 | 品牌token版本化、模板引用，升级不覆盖企业定制 |
| CHANNEL-F003 | Domain/App身份绑定 | 自定义域名+TLS、微信AppID、iOS bundleId/Android package引用，经CredentialRef不存明文secret |
| CHANNEL-F004 | 发布/构建身份 | build profile、签名凭证引用、per-tenant构建产物到实例的可追溯 |

### CHANNEL-F001 · ChannelInstance管理
- **目标**：每个企业的每个渠道（网站/独立站/小程序/App/iPad/H5）作为独立的ChannelInstance管理，共享Matbox Core能力。
- **验收标准**：租户只能看到自己的渠道实例；跨租户配置不泄露。

### CHANNEL-F002 · Brand/Theme/Template绑定
- **目标**：品牌主题（颜色/字体等token）版本化管理，模板引用可升级；模板升级不覆盖企业已做的定制内容。
- **验收标准**：模板升级后，企业此前的定制部分仍保留，可对比预览/diff。

### 4.2.1 与"管理控制台品牌定制"的边界区分（2026-09-02补充，见架构原则第42条#22）

**必须明确区分两种不同性质的品牌定制，不能混为一谈**：
- **客户端渠道品牌定制**（本节CHANNEL-F002）——面向企业自己的网站/独立站/小程序/App等**对外客户端**，是完整的白标能力（颜色/字体/模板全套可定制），因为这是企业自己的产品门面。
- **管理控制台品牌定制**（新增，范围有限，不属于CHANNEL-F002管辖，是F-CONSOLE-001管理后台的定制能力，登记在本模块只为避免与CHANNEL-F002的完整白标能力混淆）——面向企业管理员自己登录使用的**Matbox后台管理界面**（F-CONSOLE-001），**只支持局部定制：登录页背景/Logo、导航栏Logo与主题色**，不是完整白标——管理后台的整体布局/组件/功能页面对所有租户保持一致，不允许租户把管理后台改造成看不出是"Matbox后台"的程度。两者对应不同的Brand/Theme数据实体，不允许复用同一套ChannelInstance的Brand token，防止未来"客户端全套白标能力"被误用/误期望延伸到管理后台上。

### CHANNEL-F003 · Domain/App身份绑定
- **目标**：自定义域名+TLS证书、微信AppID、iOS bundleId/Android package这些身份信息统一登记，实际证书/密钥经F-CRED-001管理，本模块只存引用。
- **验收标准**：自定义域名需验证所有权（domain verification）；secret在业务DB/Git中出现次数为0。

### CHANNEL-F004 · 发布/构建身份
- **目标**：每次构建/发布产物能追溯到具体的ChannelInstance，签名凭证引用F-CRED-001，构建产物追溯引用F-RELEASE-001。
- **验收标准**：构建产物到渠道实例的追溯链完整；prod/staging环境隔离。

## 5｜核心数据 Contract（逻辑模型，可直接建表/建接口）

**ChannelInstance**
channelInstanceId, tenantId, channelType(WEB|MINIPROGRAM|IOS|ANDROID|IPAD|H5), status(ACTIVE|DISABLED), brandThemeVersionRef, templateRef, createdAt

**DomainBinding**
bindingId, channelInstanceId, domain, tlsCredentialRef(关联F-CRED-001), verificationStatus(PENDING|VERIFIED|FAILED)

**BuildIdentity**
buildIdentityId, channelInstanceId, platform, appIdRef/bundleIdRef/packageRef, signingCredentialRef(关联F-CRED-001), releaseArtifactRef(关联F-RELEASE-001)

**API 端点（最小集合）**
- `POST /channel/instances` — 创建渠道实例
- `POST /channel/instances/{id}/domain` — 绑定自定义域名（触发verification）
- `POST /channel/instances/{id}/build-identity` — 登记App身份（微信AppID/bundleId/package）
- `GET /channel/instances/{id}` — 查询渠道实例完整配置（不返回明文secret，只返回CredentialRef状态）

## 6｜P0 冻结规则

1. 证书/私钥/secret明文写入业务DB或Git：不允许。
2. 跨租户渠道配置泄露（一个企业看到另一个企业的渠道信息）：不可降级P0（对应Gate G-P0-CHANNEL-001）。
3. 模板升级覆盖企业已定制内容：不允许。
4. 域名/App身份冲突未被显式拦截（如两个租户绑定同一自定义域名）：不允许。

## 7｜当前唯一继续断点

Stage 10（真实DNS/CDN配置、真实微信/App Store/Play接入）尚未开始。下一步：把 CHANNEL-F001~F004 转成 WorkPackage，依赖F-PAGE-001、F-MULTIEND-001先就绪。

## 附录｜来源

- 内容来源：《Matbox_多端平台_CURRENT_正式开发文档_V3.0》F-CHANNEL-001 章节（2026-08-30核对确认）
- **管理控制台品牌定制范围依据（2026-09-02）**：[Matbox_架构设计原则.md](Matbox_架构设计原则.md)第42条#22（27道产品/商业定义问题确认记录）
