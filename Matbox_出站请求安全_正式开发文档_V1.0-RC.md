# Matbox 出站请求安全 / Outbound Fetch SSRF Policy（F-EGRESS-001）

正式开发文档 · V1.0-RC · 2026-08-30

## 当前定位

本专项解决"所有服务端发起的外部URL请求，怎么统一防止SSRF（服务端请求伪造）攻击"的问题——不让每个业务模块（BPM/AI Action/资产扫描/Provider回调）各自写URL校验逻辑，容易漏、容易不一致。是Platform Core的共享安全边界，被 [F-ACTION-001](Matbox_Action网关_正式开发文档_V1.0-RC.md)（Tool/MCP/第三方Action执行）、[F-PROVIDER-001](Matbox_Provider_Router_正式开发文档_V1.0-RC.md)（供应商Webhook回调）等所有涉及服务端外呼的模块依赖。

**这是核查《Matbox_多端平台_CURRENT_正式开发文档_V3.0》F-EGRESS-001章节后确认的模块**——源文档源码基线直接引用了RuoYi的真实SSRF相关漏洞issue（#1181/#1176/#1177），与架构原则第31条独立核实RuoYi时记录的漏洞清单是同一批，不是凭空新增的安全需求。

**DocID**: MATBOX-EGRESS-SSRF-20260830-V1.0-RC
**状态**: DRAFT_RESEARCH_COMPLETE（内容级核查通过，未进入 Stage 10 真实施工）
**依赖方（已知阻塞）**：无阻塞，可独立先行设计（源文档标注 READY_FOR_STAGE10_BINDING）

## 1｜不可变原则

1. 任何业务模块不得自建URL校验逻辑（禁止BPM/AI/资产/Provider各自写"是不是内网IP"的判断），必须经本模块统一的 `OutboundUrlPolicyService` 处理。
2. 禁止裸用 `RestTemplate`/`HttpUtil` 直接处理用户可控的URL——这正是RuoYi真实漏洞（#1181/#1176/#1177）的成因，必须走EgressClient封装。
3. 私有IP段（RFC1918）、link-local、云元数据端点（如169.254.169.254）默认全部阻断，不允许业务模块申请例外绕过。
4. 重试前必须重新解析并校验URL（防止DNS-rebinding攻击：首次校验通过后DNS记录被恶意改指向内网）。

## 2｜全球调研结论（复用架构原则第31条已确认的RuoYi漏洞核实）

本模块要防的攻击类型（SSRF/DNS-rebind/云元数据泄露）是Web安全领域的成熟共识，不是新出现的风险类型；源文档已给出真实漏洞证据而非假设性威胁，架构原则第31条独立核实RuoYi时确认这些issue真实存在——两者一致，不需要额外调研攻击类型本身，重点是把校验逻辑做成"唯一入口，不可绕过"的强制架构约束。

## 3｜Own / Reuse / Must Not Rebuild

| 类型 | 对象 | 说明 |
|---|---|---|
| OWN | OutboundUrlPolicyService、EgressClient、allowlist/policy管理 | Matbox自己的URL安全校验业务规则 |
| REUSE | DNS解析库、HTTP客户端底层实现 | 不重新造HTTP协议栈 |
| MUST NOT REBUILD | 无 | 本模块本身就是"防止别人绕过校验"的强制边界，不存在可复用的现成第三方SSRF防护SaaS适合直接嵌入 |

## 4｜Feature Register

| FeatureID | 名称 | 说明 |
|---|---|---|
| EGRESS-F001 | URL安全校验服务 | scheme/host/IP/私有网段/云元数据端点/重定向/DNS-rebind统一校验 |
| EGRESS-F002 | Egress Proxy/共享客户端 | 所有异步worker/Provider回调复用同一出站客户端，不建第二套 |
| EGRESS-F003 | Admin Allowlist配置 | 管理员可配置允许的外部域名白名单，变更留痕 |

### EGRESS-F001 · URL安全校验服务
- **目标**：任意业务模块发起外部请求前，URL先经本服务校验，拒绝指向私有网段/元数据端点/未经允许重定向目标的请求。
- **验收标准**：127.0.0.1、169.254.169.254、RFC1918网段、DNS-rebinding、开放重定向链路全部被真实阻断（对应RuoYi #1181/#1176/#1177已知漏洞模式）。

### EGRESS-F002 · Egress Proxy/共享客户端
- **目标**：所有异步worker、Provider webhook回调处理，统一走同一个EgressClient，不允许绕过。
- **验收标准**：重试前重新resolve+校验URL，防止校验通过后DNS被恶意改指向内网。

### EGRESS-F003 · Admin Allowlist配置
- **目标**：管理员可配置/查看当前允许外呼的域名白名单及变更历史。
- **验收标准**：被拒绝请求返回可解释但不泄露内部拓扑的错误原因。

## 5｜核心数据 Contract（逻辑模型，可直接建表/建接口）

**OutboundUrlPolicy**
policyId, tenantId?, allowedDomains[], deniedReason枚举(PRIVATE_IP|METADATA_ENDPOINT|UNVERIFIED_REDIRECT|NOT_IN_ALLOWLIST), version, updatedAt

**EgressAuditRecord**
recordId, requesterModule(如F-ACTION-001), targetUrl, resolvedIp, decision(ALLOWED|DENIED), denyReason?, occurredAt

**API 端点（最小集合）**
- `POST /egress/validate` — 内部服务间调用，校验一个URL是否允许外呼，返回ValidatedRequest或拒绝原因
- `GET /egress/policy` — 查询当前allowlist策略
- `PUT /egress/policy` — 管理员更新allowlist（写审计记录）

## 6｜P0 冻结规则

1. 任何模块绕过EgressClient直接发起外部HTTP请求：不允许。
2. 私有网段/云元数据端点默认放行：不可降级P0。
3. 重试不重新校验URL（DNS-rebind窗口）：不允许。

## 7｜当前唯一继续断点

Stage 10（真实部署，接入真实DNS解析器、真实网络策略层双重校验）尚未开始。下一步：把 EGRESS-F001~F003 转成 WorkPackage，作为F-ACTION-001等模块的前置依赖优先施工。

## 附录｜来源

- 内容来源：《Matbox_多端平台_CURRENT_正式开发文档_V3.0》F-EGRESS-001 章节（2026-08-30核对确认）
- 漏洞证据来源（架构原则第31条已确认）：RuoYi-Vue-Pro真实issue #1181、#1176、#1177
