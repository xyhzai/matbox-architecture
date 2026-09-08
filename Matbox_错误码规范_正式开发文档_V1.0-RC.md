# Matbox 错误码规范 / Error Code Specification（跨模块共享契约）

正式开发文档 · V1.0-RC · 2026-08-30

## 当前定位

本专项解决"Matbox各个模块的API出错时，返回什么样的错误码"的问题——不是某一个FeatureID的功能模块，是所有模块（DQ/F-ACTION-001/F-PROVIDER-001/F-TASK-001/F-APPROVAL-001等）共同遵守的跨模块契约，类似于F-OBS-001的evidenceBundleRef、F-CRED-001的AgentCredentialGrant这类"字段名/格式统一"的共享约定。

**这是核对AI员工底层包`06_API_Contract/contracts/error_codes.md`后确认的模块**——此前Matbox没有任何一份文档统一定义过错误码规范，各模块各写各的（如F-COST-001用BUDGET_EXCEEDED的语义但没有正式定义这个码），是一处真实缺口，直接采纳底层包已给出的17个错误码，不重新发明。

**DocID**: MATBOX-ERROR-CODE-SPEC-20260830-V1.0-RC
**状态**: DRAFT_RESEARCH_COMPLETE（内容级核查通过，未进入 Stage 10 真实施工）
**依赖方**：无阻塞，所有模块的API端点均应引用本规范，不自行定义平行错误码

## 1｜不可变原则

1. 所有模块的API错误响应必须使用本规范定义的错误码，不允许自造语义重复的新码（如F-PROVIDER-001不应自己发明PROVIDER_DOWN，应统一用PROVIDER_UNAVAILABLE）。
2. 每个错误响应必须包含`error_code`、安全的`message`（不泄露内部实现细节）、`retryable`（明确该错误是否值得客户端重试）、`trace_id`（关联F-OBS-001的AgentTraceEvent）、可选的结构化`details`。
3. 错误响应永不返回provider密钥、原始敏感payload或任何可能泄露内部拓扑的信息。
4. 新增错误码必须先判断是否已有语义相近的码可以复用，避免错误码列表无限膨胀失去意义。

## 2｜全球调研结论

本规范内容直接采纳AI员工底层包已给出的17个错误码，不重新调研——该规范本身覆盖了鉴权(AUTH_*)、租户边界(TENANT_BOUNDARY_VIOLATION)、状态机(INVALID_STATE_TRANSITION)、审批(APPROVAL_REQUIRED)、预算(BUDGET_EXCEEDED)、限流(RATE_LIMITED)、供应商(PROVIDER_*)、工具(TOOL_*)、任务恢复(CHECKPOINT_CORRUPT)、质量(QUALITY_GATE_FAILED)这些Matbox已建成模块真实会遇到的错误类型，是被验证过的一份实用清单，不是空想。

## 3｜Own / Reuse / Must Not Rebuild

| 类型 | 对象 | 说明 |
|---|---|---|
| OWN | 错误码到具体业务场景的映射（哪个模块在什么条件下返回哪个码） | 各模块自己的业务逻辑决定何时抛出哪个码 |
| REUSE | 错误码清单本身（17个码+HTTP状态+retryable语义），源自AI员工底层包 | 不重新发明一套错误码分类法 |
| MUST NOT REBUILD | 无 | 本规范本身就是最小的、不需要额外基础设施的约定 |

## 4｜错误码清单（跨模块共享，不按FeatureID拆分）

| 错误码 | HTTP状态 | 可重试 | 含义 | 主要使用模块 |
|---|---:|---|---|---|
| AUTH_UNAUTHENTICATED | 401 | 否 | 身份缺失/无效 | F-TENANT-001/F-CRED-001 |
| AUTH_FORBIDDEN | 403 | 否 | 策略拒绝 | F-TENANT-001 |
| TENANT_BOUNDARY_VIOLATION | 403 | 否 | 跨租户访问 | F-TENANT-001（P0） |
| RESOURCE_NOT_FOUND | 404 | 否 | 资源不存在或不可见 | 所有模块 |
| IDEMPOTENCY_CONFLICT | 409 | 否 | 同一idempotencyKey但payload不同 | F-TASK-001/F-ACTION-001/F-APPROVAL-001 |
| INVALID_STATE_TRANSITION | 409 | 否 | 非法状态转移 | F-TASK-001（TaskRun状态机） |
| APPROVAL_REQUIRED | 409 | 否 | 需要审批 | F-APPROVAL-001/F-ACTION-001 |
| BUDGET_EXCEEDED | 402 | 否 | 预算策略阻断 | F-COST-001 |
| RATE_LIMITED | 429 | 是 | 触发限流 | F-PROVIDER-001（PROVIDER-F004） |
| PROVIDER_TIMEOUT | 504 | 是 | 供应商超时 | F-PROVIDER-001 |
| PROVIDER_UNAVAILABLE | 503 | 是 | 供应商不可用 | F-PROVIDER-001 |
| PROVIDER_REJECTED | 422 | 否 | 供应商拒绝合法请求 | F-PROVIDER-001 |
| TOOL_UNREGISTERED | 403 | 否 | 工具未注册 | F-ACTION-001（ACTION-F002） |
| TOOL_POLICY_DENIED | 403 | 否 | 工具调用被策略拒绝 | F-ACTION-001 |
| TOOL_TIMEOUT | 504 | 是 | 工具调用超时 | F-ACTION-001 |
| CHECKPOINT_CORRUPT | 500 | 否 | Checkpoint完整性校验失败 | F-TASK-001（TASK-F005） |
| QUALITY_GATE_FAILED | 422 | 否 | 输出未通过质量门禁 | F-OBS-001/DQ质检系统 |
| INTERNAL_ERROR | 500 | 是 | 未预期的平台内部错误 | 所有模块兜底 |

### 4.1 九家供应商横向收口后的补充错误码（2026-09-08新增，专项00r）

原清单 18 条覆盖了 Matbox 自身的失败面，但**跨外部 Provider 执行**这一层缺口较大。九家供应商报告 100% 通读后，把三家已经产品化的错误语义归一如下。

**证据基础**：Microsoft Copilot Studio 公开九个具名错误码并给出可重试性分类（专项00q §2.2）；Activepieces `FlowRunStatus` 十一态（§4.2）；UiPath 明确 `Faulted ≠ 可安全重试`、`Pending` 是等资源不是失败（§3.2）。

| 错误码 | HTTP状态 | 可重试 | 含义 | 归一自 | 主要使用模块 |
|---|---:|---|---|---|---|
| PROVIDER_QUOTA_EXCEEDED | 402 | 等待/扩容后 | 供应商配额耗尽（**与 BUDGET_EXCEEDED 不同**：那是 Matbox 自己的预算策略，这是外部账户额度） | MS `QUOTA_EXCEEDED`、AP `QUOTA_EXCEEDED` | F-PROVIDER-001/F-ACTION-001 |
| PROVIDER_UNKNOWN | 500 | **有限重试后转人工** | 供应商侧未知失败，**不可假定动作没发生** | MS `SYSTEM_ERROR` | F-ACTION-001 |
| EXECUTION_UNKNOWN | 202 | **禁止盲重试** | **不可逆动作超时**：外部可能已成功。必须进入 read-back reconcile，**绝不能换 idempotencyKey 重发** | Zapier/UiPath 共同结论 | F-ACTION-001（P0） |
| RESOURCE_LIMIT_EXCEEDED | 413 | 否 | 沙箱内存/文件/载荷超限 | AP `MEMORY_LIMIT_EXCEEDED` | F-ACTION-001/F-RUNTIME-001 |
| EVIDENCE_LIMIT_EXCEEDED | 413 | 否 | 日志/证据体积超限（**证据被截断本身必须可见**，不能静默丢） | AP `LOG_SIZE_EXCEEDED` | F-OBS-001 |
| CONTEXT_OVERFLOW | 422 | 否（需压缩/重编排） | 上下文长度超限 | MS `CONTEXT_LENGTH_EXCEEDED` | F-RUNTIME-001 |
| RUN_ALREADY_ACTIVE | 409 | 等待后重试 | 同一会话/任务已有活跃执行 | MS `CONVERSATION_BUSY` | F-TASK-001/F-RUNTIME-001 |
| DATA_RESIDENCY_DENIED | 403 | 否 | 跨区域执行被数据驻留策略拒绝 | MS `CROSS_GEO_NOT_ALLOWED` | F-EGRESS-001/F-TENANT-001 |
| MODEL_POLICY_DENIED | 403 | 否 | 模型未获准使用（管理员策略/未开通） | MS `MODEL_CONSENT_DENIED` | F-PROVIDER-001 |
| MODEL_DEPLOYMENT_NOT_FOUND | 424 | 否（需 fallback） | 模型/部署已下线 | MS `DEPLOYMENT_NOT_FOUND` | F-PROVIDER-001 |
| CONTENT_POLICY_DENIED | 422 | **同输入不重试** | 内容策略拦截 | MS `CONTENT_FILTERED` | F-OBS-001/F-ACTION-001 |
| CONNECTION_REAUTH_REQUIRED | 401 | 否（需用户重新授权） | 凭据过期/被撤销/Scope 变化 | 九家一致 | F-CRED-001/F-ACTION-001 |
| CONNECTION_UNVERIFIED | 409 | 否 | Provider 报 ACTIVE 但 Matbox 独立探测未通过 | Composio #4120 | F-CRED-001/F-ACTION-001 |
| TRIGGER_SIGNATURE_INVALID | 401 | 否 | Webhook 验签失败，**必须显式拒绝并记安全事件**，不得静默回 200 | Activepieces #14808 | F-ACTION-001 |
| NO_EVENT | 204 | — | Polling 返回空结果 —— **正常，不是失败** | Activepieces | F-ACTION-001 |

**三条使用规则（P0）**：

1. **`PENDING`／等资源 ≠ 失败。** UiPath 的 `Pending` 是在等 Robot/Connection/资源，`Faulted` 才是失败且官方说明需手工 restart。Adapter 必须把两者映射到不同 Matbox 状态，**禁止把"排队中"当错误重试**。
2. **`EXECUTION_UNKNOWN` 是独立终态，不是 `PROVIDER_TIMEOUT` 的别名。** 超时只说明 Matbox 没收到回复，**不说明外部没发生**。对创建订单、发消息、退款这类不可逆动作，必须 read-back 确认后才能收口。
3. **`NO_EVENT` 必须与 `PROVIDER_*` 错误分开。** 三家都踩过"轮询空结果被当成故障"的坑。

> **为什么不直接照抄微软的九个码**：微软的码是围绕其 Harness 运行时设计的，缺少「外部不可逆动作超时」「凭据未验证」「Trigger 验签失败」这三类 Matbox 必须区分的语义——前两类来自 Zapier/UiPath/Composio，第三类来自 Activepieces。本表是**九家归一**后的结果，不是单家搬运。


## 5｜核心数据 Contract（逻辑模型）

**ErrorResponse**（所有模块API错误响应统一结构，2026-09-02据专项20核查更新字段）
errorCode（本文档枚举）, httpStatus, **title**（简短错误标题，如"预算超限"）, **detail**（具体说明，安全、不含内部细节，替代原`message`单字段）, retryable(bool), traceId（关联F-OBS-001）, details?(jsonb，**结构化校验错误时建议`[{field, description}]`数组，参照Google API `BadRequest.FieldViolation`模式**)

**变更说明**：原`message`单字段拆分为`title`+`detail`两个字段，对齐RFC 9457（Problem Details for HTTP APIs）的`title`/`detail`区分，同时不改变`errorCode`短字符串枚举风格（核查确认Stripe/GitHub/Twilio等主流API实践上也不采用RFC字面的URI式`type`，本规范维持短枚举更贴合行业实际，非字面照搬RFC）。

## 6｜P0 冻结规则

1. 错误响应包含provider密钥、原始敏感payload或内部堆栈信息：不可降级P0。
2. 模块自造语义重复的新错误码而不复用已有码：不允许，需先检查本规范。
3. retryable标记错误但实际不安全重试（如已产生副作用的操作标记为可重试）：不允许。
4. **HTTP状态码必须使用本规范表中定义的真实状态码（如404/403/429/503），不允许因后端底座框架默认行为而统一返回200**（2026-09-02新增，见第6.1节背景）。

### 6.1 与后端底座框架默认约定的冲突及裁决（2026-09-02，专项20核查发现，已裁决）

**背景**：专项20核查发现，Matbox后端底座（RuoYi-Vue-Pro/yudao-cloud）默认约定是"HTTP状态码统一返回200，真实错误码放在响应体`CommonResult.code`字段里"，与本规范"使用真实HTTP状态码"的既有设计直接冲突，此前未被任何文档记录。

**裁决**：**覆盖yudao默认行为，维持本规范"真实HTTP状态码"的设计**。理由：①F-ACTION-001/F-PROVIDER-001/F-TASK-001三个已建成模块的技术选型报告（专项09/13/16）均已按"真实HTTP状态码"的假设设计错误处理/降级逻辑，如迁就框架默认行为需要反过来修改三份已冻结文档，成本更高；②真实HTTP状态码是本规范17码表设计的基础，行业标准（RFC 9457/Google API模型/Stripe/GitHub/Twilio，见第2节及专项20第3节）均采用真实状态码，不是Matbox一家特例；③Java生态下Spring Boot 3+原生`ProblemDetail`/`ErrorResponse`支持天然基于真实HTTP状态码，覆盖yudao默认行为可以直接复用框架能力，不需要额外适配层。**要求Stage 10施工前，在yudao底座的全局异常处理器（GlobalExceptionHandler）层面显式覆盖此默认行为，不允许遗留混用**。

## 7｜当前唯一继续断点

Stage 10（各模块真实实现时统一引用本规范）尚未开始。下一步：F-ACTION-001/F-PROVIDER-001/F-TASK-001/F-APPROVAL-001/F-TENANT-001/F-COST-001等已建成模块的API端点描述，后续统一补充"使用错误码"字段引用本规范，不逐个模块重复定义；Stage 10施工前需按第6.1节完成yudao底座GlobalExceptionHandler的覆盖实现。

## 附录｜来源

- 内容来源：《Matbox_AI_Employee_System_V6.3_Final_Frozen》底层包`06_API_Contract/contracts/error_codes.md`（2026-08-30核对确认，详见架构原则第33条）
- 2026-09-02字段变更与yudao冲突裁决来源：[`Matbox_专项20_错误码规范_技术选型与开发交接报告_2026-09-02.md`](技术选型报告/Matbox_专项20_错误码规范_技术选型与开发交接报告_2026-09-02.md)（RFC 9457/Google API错误模型/Stripe/GitHub/Twilio真实错误响应格式核查）
