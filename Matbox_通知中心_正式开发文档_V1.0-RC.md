# Matbox 通知中心 / Notification Center（F-NOTIFY-001）

正式开发文档 · V1.0-RC · 2026-08-30

## 当前定位

本专项解决"站内/IM/邮件/短信/微信订阅消息/APNs/FCM这些通知渠道，怎么统一管理偏好、去重、免打扰时段、deep link"的问题——不让每个业务Feature各自建短信表/推送worker，重复造轮子且容易不一致。是Platform Core的共享能力，被审批（F-APPROVAL-001）、任务（F-TASK-001）等所有需要通知用户的模块依赖。

**这是核查《Matbox_多端平台_CURRENT_正式开发文档_V3.0》F-NOTIFY-001章节后确认的模块**，技术选型部分复用本会话此前已完成的Novu调研结论。

**与AI员工底层包Webhook Contract的关系确认（2026-08-30，架构原则第33条）**：AI员工底层包定义了独立的Webhook Contract（task.created/approval.decided/budget.threshold_reached等系统事件，HMAC签名，面向**外部系统集成方**订阅）。查证2026年主流架构后确认：Webhook系统标准做法是独立组件+独立队列，订阅领域事件、面向B2B系统集成；本模块管的是**终端用户**（企业内部人类用户）多渠道通知（Email/SMS/微信/APNs/FCM/站内），两者是不同层——**不是重复设计，不合并**，但两者可能共享同一个"领域事件"上游来源（如approval.decided这个事件，既可能触发Webhook推给外部系统，也可能触发本模块通知负责人），事件定义应保持一致命名，不要各建一套事件名。

**DocID**: MATBOX-NOTIFY-CENTER-20260830-V1.0-RC
**状态**: DRAFT_RESEARCH_COMPLETE（内容级核查通过，未进入 Stage 10 真实施工）
**依赖方（已知阻塞）**：F-PLAT-001（人类登录会话）、F-OBS-001（已建成）

## 1｜不可变原则

1. 不允许各Feature自建短信/推送表和worker——所有通知必须经本模块的NotificationService统一发送。
2. must-deliver类型的通知（如安全告警）不能被用户偏好设置静默关闭。
3. dedup key必须生效——同一事件不能因为重试或多渠道触发而重复轰炸用户。
4. quiet hours（免打扰时段）必须按用户所在时区计算，不能用服务器时区一刀切。

## 2｜全球调研结论（复用本会话已完成的Novu调研）

本会话此前已针对F-NOTIFY-001需求调研过通知基础设施：**Novu**（开源，38K+ stars，MIT核心协议）支持多渠道（Email/SMS/Push/站内/Slack/Discord/WhatsApp）统一管理，但**没有原生微信支持**，需要自定义adapter对接微信订阅消息/小程序模板消息API。这与本模块In Scope明确要求的"微信订阅消息"渠道有真实缺口，不是可以忽略的细节。

**结论**：采用Novu作为通知基础设施核心（REUSE），自建微信渠道adapter（OWN），不是"Novu能覆盖全部渠道"的误判。

## 3｜Own / Reuse / Must Not Rebuild

| 类型 | 对象 | 说明 |
|---|---|---|
| OWN | 微信订阅消息/小程序模板消息adapter、RouteResolver（业务事件→通知路由映射）、Preference偏好管理 | Novu原生不支持微信，且路由/偏好业务规则是Matbox自己的 |
| REUSE | Novu核心（dedup、delivery worker、retry、Email/SMS/APNs/FCM adapter） | 不重新造通知基础设施 |
| MUST NOT REBUILD | Novu已有的多渠道dedup/collapse机制 | 直接用Novu原生能力 |

## 4｜Feature Register

| FeatureID | 名称 | 说明 |
|---|---|---|
| NOTIFY-F001 | Novu集成 | 站内/Email/SMS/APNs/FCM等渠道接入Novu，复用其dedup/delivery/retry机制 |
| NOTIFY-F002 | 微信通知Adapter | 自建，对接微信订阅消息/小程序模板消息API（Novu原生不支持） |
| NOTIFY-F003 | 偏好与免打扰管理 | quiet hours（按用户时区）、must-deliver类型不可关闭、deep link路由 |
| NOTIFY-F004 | Route Contract | 业务事件到通知渠道/严重度的映射规则，不直接把业务数据复制进通知表 |

### NOTIFY-F001 · Novu集成
- **目标**：站内/Email/SMS/APNs/FCM渠道统一经Novu发送，复用其原生dedup和delivery retry能力。
- **验收标准**：同一业务事件多次触发（如重试）不产生重复通知（dedup key生效）。

### NOTIFY-F002 · 微信通知Adapter（Novu缺口，需自建）
- **目标**：微信订阅消息/小程序模板消息作为独立adapter接入NotificationService，与Novu管理的其他渠道共享同一套业务事件路由规则。
- **验收标准**：微信渠道的通知内容、点击跳转（deep link到正确tenant/resource）与其他渠道行为一致。

### NOTIFY-F003 · 偏好与免打扰管理
- **目标**：用户可设置各通知类型的接收偏好和quiet hours；must-deliver类型（如安全告警）不可被关闭。
- **验收标准**：按用户实际所在时区判断是否处于quiet hours，不用服务器时区。

### NOTIFY-F004 · Route Contract
- **目标**：业务事件（event+recipient+severity+route context）到通知渠道的映射规则统一定义，通知表不直接复制业务resource数据，只存引用。
- **验收标准**：点击通知能跳转到正确的tenant/resource，不出现跳错租户的情况。

## 5｜核心数据 Contract（逻辑模型，可直接建表/建接口）

**Notification**
notificationId, tenantId, recipientId, eventType, severity, channel(INAPP|EMAIL|SMS|WECHAT|APNS|FCM), dedupKey, resourceRef, deepLink, mustDeliver(bool), createdAt

**NotificationDeliveryReceipt**
receiptId, notificationId, channel, status(SENT|FAILED|RETRYING|DELIVERED), providerRef（如Novu的messageId，微信渠道自建的msgId）, attemptCount, lastAttemptAt

**NotificationPreference**
tenantId, userId, eventType, channelEnabled{}, quietHoursStart, quietHoursEnd, timezone

**API 端点（最小集合）**
- `POST /notify/dispatch` — 业务模块触发一次通知（内部调用，非用户直接调用）
- `GET /notify/inbox` — 用户查询站内通知列表
- `GET /notify/preferences` — 查询/更新通知偏好
- `POST /notify/wechat/webhook` — 微信侧回调（如订阅消息授权状态变更）

## 6｜P0 冻结规则

1. must-deliver类型通知被用户偏好静默关闭：不允许。
2. 同一dedupKey重复轰炸用户：不允许。
3. 通知表直接复制业务resource全量数据（而非引用）：不允许。

## 7｜当前唯一继续断点

Stage 10（真实部署Novu、真实对接微信订阅消息API、真实各渠道credential配置）尚未开始。下一步：把 NOTIFY-F001~F004 转成 WorkPackage，微信Adapter作为独立子任务优先设计（因为是Novu的真实缺口）。

## 附录｜来源

- 内容来源：《Matbox_多端平台_CURRENT_正式开发文档_V3.0》F-NOTIFY-001 章节（2026-08-30核对确认）
- 技术选型依据：Novu（开源，38K+ stars，MIT核心）—— 多渠道统一管理，但无原生微信支持，需自建adapter
- **与Webhook Contract关系确认依据（2026-08-30）**：《Matbox_AI_Employee_System_V6.3_Final_Frozen》底层包`06_API_Contract/contracts/webhook_contract.md`；[Building a Webhooks System with Event Driven Architecture](https://codeopinion.com/building-a-webhooks-system-with-event-driven-architecture/)
