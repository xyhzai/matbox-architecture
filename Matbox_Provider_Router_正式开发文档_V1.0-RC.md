# Matbox Provider Router / 模型接入层（F-PROVIDER-001）

正式开发文档 · V1.0-RC · 2026-08-30

## 当前定位

本专项解决"AI员工调用LLM/图片/视频/语音识别这些外部AI供应商时，怎么统一路由、怎么做健康检查和故障转移、怎么防止某个租户把整个资源池打垮"的问题。是 Platform Core 的共享能力，被所有需要调用外部AI供应商的模块（F-DQ-012、F-COST-001、F-AIEMP-001等）依赖。

**这是本次核查《Matbox_多端平台_CURRENT_正式开发文档_V3.0》F-PROVIDER-001章节后确认的模块**——架构依赖图里"Provider Router / 模型接入层"这个占位很久的⚪未开始模块，终于有了正式设计，不再是纯原则性占位。原架构原则第2、9条定的"不绑定单一供应商、支持故障转移+分级路由"和第28条深挖过的"按租户限流方案"，都在本文档里正式落地。

**2026-08-30核对AI员工底层包后确认边界**：底层包把"调用AI模型供应商"独立设计成Model Gateway（WP-006），跟"调用工具/执行动作"的MCP/Tool Gateway（WP-007，对应F-ACTION-001）是两个平级网关——这确认了本模块（Model Gateway语义）的边界：**只处理AI模型/图片/视频/语音供应商调用，不处理工具调用**，F-ACTION-001已同步收窄不再包含AI供应商分支（详见F-ACTION-001文档"当前定位"的结构性修正说明）。同时并入了底层包`provider_adapter_contract.md`定义的Provider Adapter标准接口。

**DocID**: MATBOX-PROVIDER-GATE-20260830-V1.0-RC
**状态**: DRAFT_RESEARCH_COMPLETE（内容级核查通过，未进入 Stage 10 真实施工）
**依赖方（已知阻塞）**: F-CRED-001（凭证）、F-COST-001（成本归因）、F-EGRESS-001（出站请求安全）

## 1｜不可变原则

1. 业务功能不得直接连接某个AI供应商的SDK，必须经过Provider Router统一路由——不绑定单一供应商，换供应商不改业务代码。
2. 未经确认的高成本fallback（比如主供应商挂了自动切换到更贵的备用）不允许静默发生，必须留痕。
3. 跨境/跨区域调用供应商，默认不开放，必须显式配置区域策略（中国客户的敏感数据不能默认送到任意海外供应商）。
4. Webhook回调必须验证签名+nonce+幂等，不能相信任何未经验证的外部回调直接改业务状态。

## 2｜全球调研结论（2026-08-30）

### 2.1 为什么要限流——真实事故，不是假设性担忧

Matbox未来会有多个企业客户共用同一套AI资源池。查证到真实记录的事故：**某SaaS平台一个客户的批量任务打到每分钟5万次请求，几分钟内导致其他所有客户的响应速度变慢3倍**。OpenAI/Anthropic/Azure/AWS Bedrock全球大厂都在真实处理这个问题，不是假设性担忧（架构原则第28条已确认）。

### 2.2 按租户限流具体方案（架构原则第28条深挖结论，本文档正式落地）

1. **按请求数(RPM)+Token数(TPM)双维度限制**，不能只按次数——AI调用的token消耗差异巨大，OpenAI等大厂都是双维度甚至四维度同时限。
2. **额度跟着F-COST-001的历史花费记录自动分层**（参照OpenAI的Tier机制：用得越久/花得越多，额度越高），不用另造判断逻辑。
3. **技术上用令牌桶(客户接入层，允许合理突发)+滑动窗口(共享资源层，严格兜底)分层组合**，这是查证到的行业最佳实践组合，不是二选一。
4. **时间点**：不是"以后随便哪天做"，是本模块一旦开始正式设计就必须在第一版包含，不能等真有客户受影响了才回头补。

### 2.3 多端平台文档原有设计（补强前）

多端平台文档对F-PROVIDER-001的原始定义里，"rate limit"只是In Scope里的一个词，没有展开具体方案——本文档用2.2节的具体方案补强，不是重新发明。

## 3｜Own / Reuse / Must Not Rebuild

| 类型 | 对象 | 说明 |
|---|---|---|
| OWN | ProviderCapabilityRegistry、RegionPolicy、RateLimitPolicy、WebhookVerification | Matbox自己的路由/限流/区域策略业务规则 |
| REUSE | 各AI供应商官方SDK/API（LLM/Image/Video/ASR适配器） | 不重新造供应商调用协议 |
| MUST NOT REBUILD | 供应商自己的模型能力、计费规则本身 | 直接读供应商官方接口，不自己实现模型推理或计价逻辑 |

## 4｜Feature Register

| FeatureID | 名称 | 说明 |
|---|---|---|
| PROVIDER-F001 | Provider能力注册表 | LLM/Image/Video/ASR等供应商能力/区域/成本/健康状态统一登记 |
| PROVIDER-F002 | 区域策略 | 中国/海外供应商调用隔离，敏感数据默认不跨境 |
| PROVIDER-F003 | 健康检查/熔断/故障转移 | 供应商不可用时自动切换，高成本fallback需留痕 |
| PROVIDER-F004 | 按租户限流 | RPM+TPM双维度，按F-COST-001花费自动分层，令牌桶+滑动窗口分层组合（架构原则第28条落地） |
| PROVIDER-F005 | 签名Webhook回调 | signed webhook+nonce+幂等，防重放/伪造回调 |
| PROVIDER-F006 | Provider Adapter标准接口 | 每个供应商适配器必须实现的统一接口（2026-08-30从AI员工底层包并入） |

### PROVIDER-F001 · Provider能力注册表
- **目标**：统一登记每个供应商支持什么能力（LLM/图片/视频/语音识别）、覆盖哪些区域、成本、当前健康状态。
- **验收标准**：新增/下线一个供应商，只需改注册表配置，不需要改调用方代码。

### PROVIDER-F002 · 区域策略
- **目标**：中国客户的敏感请求（比如访谈录音）不被默认发送到任意海外供应商；区域策略可测试、可配置。
- **依赖**：涉及数据合规，需要Legal Owner签字（跟G-P0-REGION-001 Gate一致）。
- **验收标准**：中国区/海外区sandbox环境分离测试通过。
- **PIPL跨境传输具体触发点（2026-08-30从"AI员工能力缺口调研清单"#6并入，细化原有笼统的"区域策略"）**：查证确认——**AI Agent的Model Gateway调用经MCP/API连到海外闭源LLM（如调用OpenAI/Anthropic的API），可能构成PIPL意义上的跨境数据传输**，触发以下义务：①须向数据主体单独同意（不能用笼统的隐私政策一次性覆盖）；②超过监管阈值的数据主体数量，须走安全评估/标准合同备案(SCC)/第三方认证三选一（2026年1月新增认证选项）。技术侧对应方案：ProviderCapability.region字段+RegionPolicy必须能标记"该次调用是否触发PIPL跨境传输义务"，触发时在ModelInvocation记录里留痕（合规审计用）。真实案例参考：某跨境电商同时运营中国/欧盟/美国站点，合规成本激增300%——跨境合规不是"写一条政策"的小事，是会实质推高成本的真实约束，需要Legal Owner在Stage 10选定服务器地区时正式审阅这条。

### PROVIDER-F003 · 健康检查/熔断/故障转移
- **目标**：某个供应商不可用时自动切到备用供应商，不需要人工介入；fallback到更贵供应商时必须留痕，不能静默发生。
- **验收标准**：故意让主供应商失败，验证系统能自动切换且不重复计费/不重复副作用。

### PROVIDER-F004 · 按租户限流（架构原则第28条落地，2026-08-30补强）
- **目标**：防止单个租户的AI员工异常调用（死循环、批量任务）拖垮其他租户共用的资源池。
- **具体方案**：
  1. RPM（请求数/分钟）+ TPM（Token数/分钟）双维度限制
  2. 额度按F-COST-001的历史花费记录自动分层（花得越多/用得越久，额度越高，参照OpenAI Tier机制）
  3. 令牌桶算法用在客户接入层（允许合理的突发流量），滑动窗口算法用在共享资源层（严格兜底，防止总量超限）
- **验收标准**：人为构造单租户异常高频调用，验证其他租户的响应速度不受影响；限流触发时返回明确的限流原因，不是裸的失败错误。

### PROVIDER-F005 · 签名Webhook回调
- **目标**：供应商异步回调（比如长时间的视频生成任务完成通知）必须验证签名+nonce，防止伪造/重放攻击。
- **验收标准**：伪造的webhook请求必须被拒绝；重复的合法webhook不产生重复副作用。

### PROVIDER-F006 · Provider Adapter标准接口（2026-08-30从AI员工底层包`provider_adapter_contract.md`并入）
- **目标**：每个AI供应商适配器必须实现同一套接口，新增/替换供应商不需要改调用方代码。
- **必须实现**：`healthcheck()`、`list_models()`、`invoke(request)`、`estimate_cost(request)`、`cancel(provider_request_id)`（若供应商支持）、`normalize_error(provider_error)`。
- **必填请求字段**：tenant_id/run_id/trace_id/capability/model_route/input/parameters/data_classification/timeout_ms/budget_envelope。
- **必填响应字段**：provider_request_id/provider/provider_model_id/provider_model_version/output/usage/cost/latency_ms/finish_reason/safety_metadata/raw_metadata_ref。
- **验收标准**：Adapter必须emit trace span和成本记录；供应商专有错误必须规范化成本文档统一错误码（对应error_codes.md的PROVIDER_TIMEOUT/PROVIDER_UNAVAILABLE/PROVIDER_REJECTED）；模型升级必须先跑Golden Set回归再上生产路由。

## 5｜核心数据 Contract（逻辑模型，可直接建表/建接口）

**ProviderCapability**
providerId, capability(llm|image|video|asr), region[], costTier, healthStatus(HEALTHY|DEGRADED|DOWN), lastHealthCheckAt

**RegionPolicy**
policyId, tenantId?, dataCategory（如sensitive_audio）, allowedRegions[], enforcedAt

**RateLimitState**（PROVIDER-F004，令牌桶+滑动窗口的运行时状态）
tenantId, tokenBucketCapacity, tokenBucketCurrent, slidingWindowRpm, slidingWindowTpm, costTier（关联F-COST-001的Entitlement）, updatedAt

**ProviderCallEvent**
callId, tenantId, agentId, providerId, capability, requestTokens, responseTokens, latencyMs, status(OK|FALLBACK|RATE_LIMITED|ERROR), fallbackReason?, idempotencyKey, timestamp

**WebhookVerificationRecord**
webhookId, providerId, signatureValid(bool), nonce, receivedAt, processed(bool)

**ModelInvocation**（2026-08-30从AI员工底层包`model_invocation`表并入，与ProviderCallEvent对应但字段更贴近成本核算；2026-08-30补充pipl相关字段落地PROVIDER-F002细化）
invocationId, tenantId, runId, stepId?, modelId（关联ProviderCapability）, providerRequestId?, parametersHash, inputHash, outputHash?, usage(jsonb), cost, currency, latencyMs?, status, piplCrossBorderTriggered(bool)（该次调用是否构成PIPL跨境传输）, piplConsentRef?（若触发，关联的数据主体同意记录）, createdAt

**API 端点（最小集合）**
- `POST /provider/route` — 路由一次AI调用请求，内部先过RateLimitState检查，返回选中的provider+region
- `GET /provider/capabilities` — 查询当前可用的供应商能力注册表
- `POST /provider/webhook/{providerId}` — 供应商异步回调入口，验证签名+nonce后处理
- `GET /provider/rate-limit/{tenantId}` — 查询某租户当前限流状态/额度分层
- `POST /v1/registry/models` — 登记供应商模型（对应AI员工底层API路径，Adapter接入时调用）

## 6｜P0 冻结规则

1. 单个租户的异常调用拖垮其他租户的响应速度：不可降级P0，必须限流生效。
2. 敏感数据默认跨境发送给未经确认的海外供应商：不可降级P0。
3. Webhook回调未验证签名直接改业务状态：不允许。
4. Fallback到更贵供应商且不留痕迹：不允许。

## 7｜当前唯一继续断点

Stage 10（真实接入供应商API、真实部署限流基础设施）尚未开始。下一步：把 PROVIDER-F001~F005 转成 WorkPackage，且PROVIDER-F002需要用户对区域策略拍板（哪些供应商、哪些区域）。

## 附录｜来源

- 内容来源：《Matbox_多端平台_CURRENT_正式开发文档_V3.0》F-PROVIDER-001 章节（2026-08-30核对确认，详见架构原则第31条）
- 限流方案依据（架构原则第28条已确认，2026-08-29深度调研）：AWS Bedrock真实实现（分级用量计划、账户分片）、OpenAI Tier机制
- [8 Strategies for AI Agent Security 2026](https://www.strata.io/blog/agentic-identity/8-strategies-for-ai-agent-security/)
- **Adapter接口/边界确认依据（2026-08-30）**：《Matbox_AI_Employee_System_V6.3_Final_Frozen》底层包`06_API_Contract/contracts/provider_adapter_contract.md`、`04_Domain_Schema/migrations/004_registry_invocation.sql`（model_registration/model_invocation表）、WP-006定义
- **PIPL跨境传输触发点依据（2026-08-30）**：[Matbox_AI员工能力缺口调研清单_2026-08-30.md](Matbox_AI员工能力缺口调研清单_2026-08-30.md)#6；腾讯云KMS国际版数据合规文档；PIPL"本地存储+出境评估/认证/标准合同"三重机制（2026年1月《个人信息出境认证办法》新增认证选项）
