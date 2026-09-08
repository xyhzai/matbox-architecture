# Matbox 移动端 Shell / Mobile Shell / Auth / Progress / Offline Sync（F-MOBILE-001）

正式开发文档 · V1.0-RC · 2026-08-30

## 当前定位

本专项解决"把yudao的移动端能力变成微信/App/iPad/H5的生产级基础"的问题——鉴权加固、深链、进度传输、离线队列、上传分离、设备/会话管理、iPad布局基础。是多端渲染（F-MULTIEND-001）、PC转手机交接（F-HANDOFF-001）的运行基础。

**这是核查《Matbox_多端平台_CURRENT_正式开发文档_V3.0》F-MOBILE-001章节后确认的模块**。技术选型直接复用架构原则第31条已独立验证的yudao-ui-admin-uniapp（commit 00b82424085a02542cc451af14d8d0e051e667f7），不重复调研。

**DocID**: MATBOX-MOBILE-SHELL-20260830-V1.0-RC
**状态**: DRAFT_RESEARCH_COMPLETE（内容级核查通过，未进入 Stage 10 真实施工）
**依赖方（已知阻塞）**：F-PLAT-001

## 1｜不可变原则

1. 不复制业务SoT——移动端不建自己的一份业务数据副本，调用同一套业务API，只加同步元数据。
2. 不假设现有SSE支持App——原生App环境下SSE行为与Web不同，必须验证真实断线重连/重放行为，不能想当然。
3. 不让端侧长任务存活状态决定server task的真实状态——离线队列是传输层，不是任务状态的真相源。
4. 弱网环境下必须可保存——用户输入不能因网络中断而丢失。

## 2｜全球调研结论（复用架构原则第31条已确认的yudao验证）

本模块的技术基线是yudao-ui-admin-uniapp（commit 00b82424085a02542cc451af14d8d0e051e667f7），架构原则第31条已独立核实：真实用户反馈集中在"微信小程序官方文档写得差、开发者工具偶有兼容小问题"，属于文档质量问题，不影响技术选型本身，✅确认可用。本模块直接在此基础上加固鉴权/离线同步/进度传输，不重复调研底层框架选型。

## 3｜Own / Reuse / Must Not Rebuild

| 类型 | 对象 | 说明 |
|---|---|---|
| OWN | auth/tenant/token加固、offline queue/save-resume、progress transport、device/session管理 | Matbox自己的移动端安全与同步业务规则 |
| REUSE | yudao mobile shell（package/interceptor/token/sse/manifest基础） | 不重新造uni-app跨端框架 |
| MUST NOT REBUILD | uni-app本身的跨端渲染能力 | 直接用uni-app原生跨端编译 |

## 4｜Feature Register

| FeatureID | 名称 | 说明 |
|---|---|---|
| MOBILE-F001 | 鉴权加固 | auth/tenant/token在yudao基础上加固，deep link支持 |
| MOBILE-F002 | 离线队列与断点续传 | offline queue/save-resume，弱网可保存，idempotent offline submit |
| MOBILE-F003 | 进度传输 | TaskEvent/WS/SSE transport + offline retry，断线重连补齐真实状态 |
| MOBILE-F004 | 设备能力矩阵 | 微信/iOS/Android/iPad/H5差异化处理，per-channel构建/签名/最低版本 |

### MOBILE-F001 · 鉴权加固
- **目标**：在yudao现有token/interceptor基础上加固租户隔离和deep link路由。
- **验收标准**：deep link跳转到正确的tenant/resource，不越权。

### MOBILE-F002 · 离线队列与断点续传
- **目标**：弱网/离线状态下用户操作先入本地队列，恢复网络后幂等提交，不重复不丢失。
- **验收标准**：模拟断网操作后恢复网络，验证提交不重复（idempotent）且数据不丢失。

### MOBILE-F003 · 进度传输
- **目标**：长任务（如F-TASK-001的AI任务）进度通过WS/SSE传输到移动端，断线重连后补齐真实server状态，不依赖端侧缓存判断进度。
- **验收标准**：断线重连场景下，前端显示与服务端真实状态一致（对应Gate G-P1-PROGRESS-001）。

### MOBILE-F004 · 设备能力矩阵
- **目标**：微信小程序/iOS/Android/iPad/H5按各自能力差异化处理，旧客户端优雅降级而非崩溃。
- **验收标准**：设备测试矩阵覆盖弱网、后台中断场景（对应Gate G-P1-IPAD-001）。

## 5｜核心数据 Contract（逻辑模型，可直接建表/建接口）

**MobileSession**
sessionId, tenantId, userId, deviceId, platform(WECHAT|IOS|ANDROID|IPAD|H5), clientVersion, lastActiveAt

**OfflineSyncQueueItem**
itemId, sessionId, businessApiRef, payload, idempotencyKey, status(PENDING|SYNCED|CONFLICT), createdAt, syncedAt?

**API 端点（最小集合）**
- `POST /mobile/sync/submit` — 提交离线队列中的操作（幂等）
- `GET /mobile/sync/cursor` — 查询同步游标，用于断线重连后补齐状态
- `GET /mobile/deeplink/resolve` — 解析deep link到具体路由/资源

## 6｜P0 冻结规则

1. 离线提交非幂等（重试产生重复副作用）：不允许。
2. 移动端自建第二份业务数据副本作为SoT：不允许。
3. 断线重连后前端显示端侧缓存而非服务端真实状态：不允许（对应Gate G-P1-PROGRESS-001）。

## 7｜当前唯一继续断点

Stage 10（真实设备测试矩阵、真实微信/App构建发布）尚未开始。下一步：把 MOBILE-F001~F004 转成 WorkPackage，与F-MULTIEND-001、F-HANDOFF-001联调。

## 附录｜来源

- 内容来源：《Matbox_多端平台_CURRENT_正式开发文档_V3.0》F-MOBILE-001 章节（2026-08-30核对确认）
- 技术选型依据（架构原则第31条已确认）：yudao-ui-admin-uniapp commit `00b82424085a02542cc451af14d8d0e051e667f7`
