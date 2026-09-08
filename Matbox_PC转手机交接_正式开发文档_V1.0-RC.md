# Matbox PC 转手机交接 / PC → Mobile Handoff（F-HANDOFF-001）

正式开发文档 · V1.0-RC · 2026-08-30

## 当前定位

本专项解决"用户在PC上正在处理某个project/interview/task/asset/approval/page，怎么安全地交给手机继续，而不是让手机重新导航找"的问题——扫码即达正确上下文，不是回到首页。依赖 [F-MOBILE-001](Matbox_移动端Shell_正式开发文档_V1.0-RC.md)（移动端Shell）承载交接后的会话。

**这是核查《Matbox_多端平台_CURRENT_正式开发文档_V3.0》F-HANDOFF-001章节后确认的模块**。纯安全模式设计（一次性opaque code + 服务端context），不涉及新技术选型。

**DocID**: MATBOX-PC-MOBILE-HANDOFF-20260830-V1.0-RC
**状态**: DRAFT_RESEARCH_COMPLETE（内容级核查通过，未进入 Stage 10 真实施工）
**依赖方（已知阻塞）**：[F-MOBILE-001](Matbox_移动端Shell_正式开发文档_V1.0-RC.md)（本轮同步建成）

## 1｜不可变原则

1. 二维码内不放JWT/tenantId/客户PII——二维码只是一次性opaque code，真实context留在服务端。
2. 二维码本身不能作为授权凭证——扫码后仍需claim流程验证会话/租户/资源权限，不是"扫到就等于登录"。
3. one-time——一个opaque code只能被claim一次，claim后立即失效，防止截图分享导致的越权访问。
4. 必须有TTL和revoke机制——PC端可主动撤销未被claim的交接码。

## 2｜全球调研结论

本模块是纯安全模式设计（借鉴微信小程序scene参数的做法，但不直接依赖某个具体产品），核心风险点（二维码截图泄露、重放攻击、跨租户越权）是移动端安全领域的成熟共识而非新出现的风险类型，不需要独立验证第三方技术，重点是"一次性、不携带敏感信息、服务端持有真相"这三条设计约束的正确落地。

## 3｜Own / Reuse / Must Not Rebuild

| 类型 | 对象 | 说明 |
|---|---|---|
| OWN | opaque code生成/claim/revoke/expiry、handoff_session模型、presence事件 | Matbox自己的交接安全业务规则 |
| REUSE | 微信小程序scene参数机制的设计思路（非强制依赖具体产品） | 参考已有成熟模式，不是接入某个SDK |
| MUST NOT REBUILD | 无 | 本模块是Matbox特有的PC-Mobile交接业务层，没有可直接套用的现成开源方案 |

## 4｜Feature Register

| FeatureID | 名称 | 说明 |
|---|---|---|
| HANDOFF-F001 | Opaque Code生成与Claim | 一次性交接码创建/兑换，不含JWT/PII |
| HANDOFF-F002 | TTL与Revoke | 交接码过期时间和PC端主动撤销能力 |
| HANDOFF-F003 | Presence与状态回传 | claim成功后PC端收到状态更新，不需要轮询 |
| HANDOFF-F004 | 防滥用限流 | claim尝试的anti-replay和rate limit |

### HANDOFF-F001 · Opaque Code生成与Claim
- **目标**：PC端生成一次性opaque code（二维码），手机扫码后claim，claim成功后跳转到正确的资源上下文，不回首页。
- **验收标准**：opaque code只能被claim一次，claim后立即失效；二维码内容本身不含JWT/tenantId/PII。

### HANDOFF-F002 · TTL与Revoke
- **目标**：交接码有过期时间；PC端可在过期前主动撤销未被使用的交接码。
- **验收标准**：过期或被撤销的交接码claim时返回明确错误，不返回资源上下文。

### HANDOFF-F003 · Presence与状态回传
- **目标**：手机claim成功后，PC端界面实时收到状态更新（如"已在手机上打开"），不需要用户手动刷新。
- **验收标准**：claim事件到PC端状态更新的延迟在可接受范围内，不是纯轮询实现。

### HANDOFF-F004 · 防滥用限流
- **目标**：claim尝试有rate limit，防止暴力枚举opaque code；同一code的并发claim请求做race-safe处理（只有一个成功）。
- **验收标准**：并发claim同一code时只有一次成功，其余返回已失效。

## 5｜核心数据 Contract（逻辑模型，可直接建表/建接口）

**HandoffSession**
sessionId, tenantId, sourceUserId, opaqueCodeHash（不存明文code）, resourceType(PROJECT|INTERVIEW|TASK|ASSET|APPROVAL|PAGE), resourceRef, status(PENDING|CLAIMED|EXPIRED|REVOKED), claimedByDeviceId?, expiresAt, createdAt

**HandoffAuditRecord**
recordId, sessionId, action(CREATED|CLAIMED|EXPIRED|REVOKED), occurredAt

**API 端点（最小集合）**
- `POST /handoff/create` — PC端创建一次性交接会话，返回opaque code（用于生成二维码）
- `POST /handoff/claim` — 手机端兑换opaque code，返回目标资源路由（需重新鉴权租户/资源权限）
- `POST /handoff/{sessionId}/revoke` — PC端主动撤销
- `GET /handoff/{sessionId}/presence` — PC端订阅claim状态（用于实时更新UI）

## 6｜P0 冻结规则

1. 二维码内容包含JWT/tenantId/客户PII：不允许。
2. opaque code被claim多次（非one-time）：不允许。
3. claim时不重新校验租户/资源权限（信任二维码本身）：不允许。

## 7｜当前唯一继续断点

Stage 10（真实微信scene参数联调、真实设备扫码测试）尚未开始。下一步：把 HANDOFF-F001~F004 转成 WorkPackage，依赖F-MOBILE-001先就绪。

## 附录｜来源

- 内容来源：《Matbox_多端平台_CURRENT_正式开发文档_V3.0》F-HANDOFF-001 章节（2026-08-30核对确认）
