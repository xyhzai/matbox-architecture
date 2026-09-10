# CRED-F006 · 访问审计日志

> 本文件由 `python docs/_build_module_pack.py CRED` 生成，不要手改。
> 改内容请改源文档，然后重跑。

---

## 0 · 派工身份（RC5 字段）

| 字段 | 值 |
|---|---|
| FeatureID | **CRED-F006** |
| 模块 | 密钥与凭据管理 |
| Implementer | opencode |
| Owner | Platform |
| 分支前缀 | `wp/` |
| 认领的验收标准 | **CRED-T561** |

## 0.5 · 开工五步（照这个做就行，不用再问）

```bash
# ⓪ 先自检环境 —— 这一步不通过，后面四步一步都动不了
#    别硬跑：缺 java/mvn/库时 mvn 的报错跟「你代码写错了」长得一样
curl -O https://xyhzai.github.io/matbox-architecture/_check_toolchain.py   # 或从网站上下载
python _check_toolchain.py

git clone https://github.com/felixapex/matbox.git
cd matbox
git checkout -b wp/cred-f006
cd backend/modules/credential
mvn -B verify
```

> **第 ⓪ 步是 2026-09-11 补的。** 在此之前，全部 33 条判据都只查**材料这一侧**（材料齐不齐、仓库有没有、CI 绿不绿），没有一条查**你那一侧能不能执行第一步** —— 于是出现过「材料齐备、基线 MATCH、CI 全绿，而实现方在第 ④ 步动不了」。
>
> 契约/Schema 测试是 `@SpringBootTest`，启动时就要连真库，**没有库不会跳过，是直接失败**。所以库要么真起一个，要么这一趟就明确改成「本地只编译、真库测试交给 CI」——**后者要由用户拍板，不是你自己决定**，因为它会改变整趟的节奏。

Java 包名：`com.matbox.credential`。代码只放在 `backend/modules/credential/` 下面。

### 0.6 · 你的工作区（确定的，不要自己找）

| | |
|---|---|
| 仓库 | `https://github.com/felixapex/matbox.git` |
| 落脚目录 | `backend/modules/credential/` —— **只在这里面改**，越界会被 `_check_scope.py` 逐个文件列出来 |
| 分支 | `wp/cred-f006`，从下面那个基线切 |
| 并行 | 一个功能一个分支、各自一份克隆，几十个 AI 同时开工互不干扰 |

### 0.7 · 源码基线（照着核对，不等于就先对齐再动手）

```
base_commit: 116a9ca25242bebd384298c273ccd65e6a916423
分支：      main
```

clone 之后先跑 `git rev-parse HEAD`，**必须等于上面这个 SHA**。
不等于说明你不是在这一版上改的，事后没法复现，也没法说清改动是相对什么的。

### 0.8 · 测试报告交到哪（判你做完没做完就读这个）

```bash
cd backend/modules/credential && mvn -B verify
# 报告产生在：backend/modules/credential/target/surefire-reports/TEST-*.xml
```

判据是 `docs/_check_delivery.py --reports <那个目录> --wp CRED-F006`：
认领的每条编号都要有测试且**通过**——失败、跳过(skipped)、**没有报告**，三种都不算通过。

整套包登记与代码地图（谁在哪、做到哪一步）在 [`code_map.json`](../../code_map.json)，机器可读，一次读全。

## 1 · 你要做什么

**目标**：谁/什么在什么时候访问了什么密钥，接入 F-OBS-001

- **目标**：所有密钥访问都留痕，接入 F-OBS-001（尚未建成前先本地记录，F-OBS-001 建成后迁移）。
- **验收标准**：任意一次密钥访问，能查到"谁/什么身份/什么时间/访问了什么/做了什么操作"。

## 2 · 你能改哪里，不能碰哪里

**能改**：`backend/modules/credential/**`

**不能碰**：其它模块的目录、别人的迁移文件、不归你的测试。
机器可判版见 [`cred_protected_scope.yml`](../../cred_protected_scope.yml)。越界会被 `_check_scope.py` 逐个文件列出来。

## 3 · 七类施工面（RC5 硬条件，少一个不能派发）

### Frontend/UI｜N/A

本功能不含前端页面；如需控制台入口，走 CONSOLE 模块

### Backend/API/Service｜Applicable · CRED-F006 Owner

本功能的服务端实现

### Data/DB/Migration｜Applicable · CRED-F006 Owner

见 §5.2 建表 SQL；新增迁移写 V2__ 递增，**不许改已发布的 V1**

### Async/Runtime｜Applicable · 共享 Reliable Runtime

复用 F-QUEUE-001

### Provider/External｜Applicable · CRED-F006 Owner

见 §5.4b 接口规范

### Infra/Config｜Applicable · Platform Infra

配置项进 §5.5 技术栈那一节

### Tests/Observability｜Applicable · QA

见 §4 验收标准；埋点接 F-OBS-001

## 4 · 你的验收标准

| 编号 | 要验证什么 |
|---|---|
| CRED-T561 | 任意一次密钥访问，能查到"谁/什么身份/什么时间/访问了什么/做了什么操作" |

### 4.1 测试方法名必须带 TestID —— 这是硬要求

测试方法名必须写成 `credT561_说明()` 这种形状，编号就是上面那张表里的编号。

```java
@Test
void credT561_describeWhatThisVerifies() {
    // 断言这一条验收标准真的成立
}
```

**为什么不能用 `@Tag`**：JUnit 5 的 `@Tag` 不会写进 Surefire 的 XML 报告，
而 `<testcase name="...">` 永远在。开发后判「这个包做完没做完」只能从方法名反查编号。

### 4.2 测试上的三条红线（会被自动查）

这三条按 diff 判，**不看自述**，事先说清楚不是事后抓人：

1. **不许动不归你的测试** —— 比对方法原文，给别人的测试加一行注释都算。
2. **不许删掉或禁用已有测试** —— 包括新增 `@Disabled` / `@Ignore`。
3. **不许把测试掏空留空壳** —— 同一方法断言条数变少即拦。

查的程序是 `_check_test_integrity.py`（T0~T3），已按 39 条反向测试验过。

## 5 · 代码怎么写（接口 / 建表 / 目录 / 任务）

### 5.1 你要实现的 API 端点

## 13｜API接口清单

统一前缀 `/cred`。鉴权规范见第16节，错误码规范见第19节（复用跨模块17码，见附录）。

| 方法 | 路径 | 说明 | 对应Feature |
|---|---|---|---|
| POST | `/cred/agent-grants` | 为AgentID+WorkPackageID申请临时授权，返回grantId+短期token | CRED-F003 |
| GET | `/cred/agent-grants/{grantId}` | 查询某Grant的scope/状态（F-TENANT-001 OPA鉴权的唯一事实源） | CRED-F003 |
| DELETE | `/cred/agent-grants/{grantId}` | 提前撤销 | CRED-F003/F005 |
| GET | `/cred/secrets/{secretRefId}` | 按SecretRef取值（内部服务调用，经TENANT-F003策略校验，返回值不落日志） | CRED-F001 |
| POST | `/cred/rotate/{secretRefId}` | 触发轮换（autoRotate=false时走Matbox自建轮换脚本） | CRED-F005 |
| POST | `/cred/integrations` | 发起第三方集成OAuth连接 | CRED-F007 |
| DELETE | `/cred/integrations/{credentialRefId}` | 断开集成，撤销凭证 | CRED-F007 |
| GET | `/cred/integrations/{credentialRefId}/status` | 查询集成健康状态（不返回secret本身） | CRED-F007 |
| POST | `/cred/identities` | 创建AgentIdentity（EmployeeInstance创建时调用） | CRED-F008 |
| PUT | `/cred/identities/{identityId}/revoke` | 撤销/退役AgentIdentity，同步失效名下所有未过期Grant | CRED-F008 |
| POST | `/cred/visitor-sessions` | 为独立站未登录访客签发匿名会话身份，返回visitorSessionId+默认allowlist | CRED-F009 |
| POST | `/cred/visitor-sessions/{visitorSessionId}/link` | 访客留资/下单时升级关联到正式Contact身份 | CRED-F009 |
| GET | `/cred/access-events` | 按secretRefId/actorId/action查询审计事件（供F-OBS-001投影调用） | CRED-F006 |
| GET | `/cred/tool-health` | 存储引擎（Infisical/OpenBao监控项）健康看板数据 | CRED-F001/F005 |

### 5.2 你要建的表

> ⚠️ 下面的表按 Flyway 迁移建。**新增写 `V2__` 递增，不许改已发布的 V1**
> ——改了校验和对不上，别人的库会 Validate failed。

## 20｜数据库及Migration设计

沿用REL-F006已确认的 **Flyway** 迁移工具（Java/Spring Boot技术栈契合），共享表+`tenant_id`字段模式（TENANT-F004）。

```sql
-- V1__cred_core_tables.sql

CREATE TABLE cred_secret_ref (
    secret_ref_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    infisical_project_id VARCHAR(128) NOT NULL,
    infisical_path VARCHAR(256) NOT NULL,
    secret_type VARCHAR(32) NOT NULL, -- scm_token|model_api_key|db_password|other
    owning_module VARCHAR(64) NOT NULL,
    last_rotated_at TIMESTAMPTZ,
    rotation_policy_id UUID,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE', -- ACTIVE|ROTATING|REVOKED
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_cred_secret_ref_tenant ON cred_secret_ref(tenant_id);

CREATE TABLE cred_agent_identity (
    identity_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    principal_type VARCHAR(32) NOT NULL, -- HUMAN|SERVICE|AGENT|PLATFORM_ADMIN
    owner_id VARCHAR(128) NOT NULL,
    scopes JSONB,
    delegated_by UUID REFERENCES cred_agent_identity(identity_id),
    expires_at TIMESTAMPTZ,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE', -- ACTIVE|REVOKED
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_cred_agent_identity_tenant ON cred_agent_identity(tenant_id);

CREATE TABLE cred_agent_credential_grant (
    grant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    agent_id VARCHAR(128) NOT NULL,
    identity_ref UUID NOT NULL REFERENCES cred_agent_identity(identity_id),
    work_package_id VARCHAR(64) NOT NULL,
    scope JSONB NOT NULL,
    issued_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE', -- ACTIVE|EXPIRED|REVOKED
    issued_by_policy_id VARCHAR(64),
    evidence_bundle_ref VARCHAR(128),
    CONSTRAINT chk_grant_expiry CHECK (expires_at > issued_at)
);
CREATE INDEX idx_cred_grant_identity ON cred_agent_credential_grant(identity_ref);
CREATE INDEX idx_cred_grant_wp ON cred_agent_credential_grant(tenant_id, work_package_id);

CREATE TABLE cred_human_access_grant (
    grant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    user_id VARCHAR(128) NOT NULL,
    role VARCHAR(32) NOT NULL, -- admin|member
    granted_projects TEXT[] NOT NULL,
    granted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    granted_by VARCHAR(128) NOT NULL
);

CREATE TABLE cred_rotation_policy (
    policy_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    secret_type VARCHAR(32) NOT NULL,
    rotation_interval_days INT NOT NULL,
    auto_rotate BOOLEAN NOT NULL DEFAULT false, -- Infisical自托管免费版不支持DB密码自动轮换，false时走CRED-F005外部脚本
    last_run_at TIMESTAMPTZ,
    next_run_at TIMESTAMPTZ
);

CREATE TABLE cred_access_event (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    actor_type VARCHAR(16) NOT NULL, -- human|agent
    actor_id VARCHAR(128) NOT NULL,
    secret_ref_id UUID REFERENCES cred_secret_ref(secret_ref_id),
    action VARCHAR(32) NOT NULL, -- read|rotate|revoke
    result VARCHAR(16) NOT NULL, -- ALLOW|DENY
    reason_code VARCHAR(64),
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_cred_access_event_tenant ON cred_access_event(tenant_id, occurred_at);

CREATE TABLE cred_integration_credential_ref (
    credential_ref_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    integration_type VARCHAR(64) NOT NULL,
    kms_key_ref VARCHAR(128) NOT NULL,
    oauth_refresh_token_ref VARCHAR(128) NOT NULL,
    scope TEXT[],
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE', -- ACTIVE|EXPIRED|REVOKED
    last_used_at TIMESTAMPTZ,
    issued_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ,
    rotated_at TIMESTAMPTZ
);
CREATE INDEX idx_cred_integration_tenant ON cred_integration_credential_ref(tenant_id);

CREATE TABLE cred_anonymous_visitor_session (
    visitor_session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    channel VARCHAR(32) NOT NULL DEFAULT 'INDEPENDENT_SITE',
    scope_allowlist TEXT[] NOT NULL,
    linked_contact_id VARCHAR(128),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_active_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE', -- ACTIVE|EXPIRED|LINKED
    CONSTRAINT chk_visitor_link_state CHECK (
        (status = 'LINKED' AND linked_contact_id IS NOT NULL) OR
        (status != 'LINKED' AND linked_contact_id IS NULL)
    )
);
CREATE INDEX idx_cred_visitor_tenant ON cred_anonymous_visitor_session(tenant_id);
```

（EvidenceBundle/审计详情不在本模块建表，全部写入 F-OBS-001，`cred_access_event`只存最小可查询字段，按第2节Contract约束执行。）

### 5.3 你的代码放哪

```
backend/modules/credential/
  src/main/java/com/matbox/credential/
  src/main/resources/db/migration/
  src/test/java/com/matbox/credential/
```

## 22｜源码目录、模块和依赖关系

```
backend/
  modules/
    credential/
      store-adapter/
        infisical/           # CRED-F001：InfisicalAdapter, HealthChecker
      access-control/         # CRED-F002：HumanAccessGrantService
      agent-grant/             # CRED-F003：AgentCredentialGrantService
      agent-proxy/              # CRED-F004
        infisical-proxy/        # 默认实现：复用Infisical Agent Proxy
        agentgateway-proxy/     # 备选实现：agentgateway集成（监控项，非默认启用）
      rotation/                  # CRED-F005：RotationService, 外部DB轮换Worker
      audit/                      # CRED-F006：AccessAuditService（依赖shared/obs-client）
      integration-vault/           # CRED-F007：IntegrationOAuthService
      agent-identity/                # CRED-F008：AgentIdentityService
      visitor-session/                # CRED-F009：VisitorSessionService
      shared/
        contracts/                    # SecretRef/Grant/Identity等DTO
        errors/                        # 复用 Matbox_错误码规范 的统一ErrorResponse
    shared-clients/
      obs-client/                       # F-OBS-001
      tenant-client/                     # F-TENANT-001（authz/check调用）
frontend/
  apps/ops-console/
    features/credential/                 # 对应FE-01~FE-06
```

**依赖方向铁律**：`credential/*` 只允许依赖 `shared-clients/*` 和自己内部子模块；`agent-proxy/infisical-proxy` 与 `agent-proxy/agentgateway-proxy` 互相独立可插拔（AgentProxyAdapter接口抽象保证切换实现不影响上层Grant业务逻辑）；`credential/*` 不允许被其他模块的基础设施客户端反向依赖，只能被引用（`cred-client`）。

### 5.4 拆好的开发任务

## 21｜前后端开发任务拆分

**后端（Java/Spring Boot，RuoYi-Vue-Pro基座）**：
- BE-01 InfisicalAdapter（SecretStoreAdapter封装，含健康检查）（CRED-F001）
- BE-02 HumanAccessGrantService（项目划分+Infisical RBAC映射）（CRED-F002）
- BE-03 AgentCredentialGrantService（签发/校验/收回状态机）（CRED-F003）
- BE-04 AgentProxyAdapter（Infisical Agent Proxy集成 + agentgateway备选实现的接口抽象）（CRED-F004）
- BE-05 RotationService（Infisical原生轮换调用 + Matbox外部轮换脚本，含DB密码专用Worker）（CRED-F005）
- BE-06 AccessAuditService（写入F-OBS-001映射层）（CRED-F006）
- BE-07 IntegrationOAuthService（回调处理/refresh/revoke状态机）（CRED-F007）
- BE-08 AgentIdentityService（含级联撤销事务）（CRED-F008）
- BE-09 VisitorSessionService（签发/升级关联/过期清理）（CRED-F009）

**前端（Ops控制台，复用既有Ops FE框架）**：
- FE-01 Secret项目结构管理界面（不回显明文，CRED-F001/F002）
- FE-02 AI员工Grant时间线/撤销操作界面（CRED-F003/F004）
- FE-03 轮换策略配置/失败告警界面（CRED-F005）
- FE-04 访问审计查询界面（CRED-F006）
- FE-05 第三方集成连接/断开管理界面（`/settings/integrations`，CRED-F007）
- FE-06 AgentIdentity列表/委派链条查看界面（CRED-F008）

### 5.4b Provider Adapter 接口规范

## 17｜Provider Adapter接口规范

CRED-F001的Infisical Adapter与CRED-F005的轮换脚本、CRED-F004的代理转发层统一遵循以下契约，禁止让Infisical原生schema渗透进Matbox Domain：

```yaml
SecretStoreAdapter接口（伪代码/逻辑契约）:
  getSecret(secretRefId: string, callerContext: {actorType, actorId, tenantId}) -> SecretValue
    # 内部调用Infisical API，返回值不落日志；callerContext用于写CredentialAccessEvent

  rotateSecret(secretRefId: string, strategy: "infisical_native" | "matbox_external_script") -> RotationResult
    # infisical_native: 密钥类型在Infisical原生支持范围内（部分云凭据/SSH Key等）
    # matbox_external_script: DB密码等Infisical免费版不支持自动轮换的类型，走CRED-F005自建脚本

  issueAgentGrant(agentId, workPackageId, requestedScope, ttl) -> AgentCredentialGrant
    # 校验requestedScope不超过AgentIdentity授权范围，写入Grant表，不直接暴露真实密钥

AgentProxyAdapter接口（CRED-F004，代理转发层，可插拔实现）:
  # 默认实现：Infisical Agent Proxy（静态密钥场景，REUSE）
  # 备选实现：agentgateway（开源CB4A参考实现，Apache-2.0，监控/备选）
  proxyCall(grantId: string, target: ExternalCallTarget) -> ExternalCallResult
    # AI员工进程只调用这个接口，永不直接持有grantId对应的真实密钥值
    # target: {url, method, headerInjectionPoint}
    # 实现内部：校验Grant未过期未撤销 → 从SecretStoreAdapter取真实密钥 → just-in-time注入 → 发起调用 → 结果剥离密钥回显后返回

IntegrationOAuthAdapter接口（CRED-F007）:
  connect(tenantId, integrationType, oauthCallbackPayload) -> IntegrationCredentialRef
  refresh(credentialRefId) -> RefreshResult
    # 幂等、race受控；AI任务不得自己调用此接口触发refresh
  revoke(credentialRefId) -> void
```

### 5.5 技术栈（不用再查）

Java 17 / Spring Boot 3.3.5（RuoYi-Vue-Pro 基座）/ **PostgreSQL** / Flyway / JUnit 5 + Maven Surefire。

### 5.6 鉴权、权限与多租户（全局规范，每个功能都适用）

## 16｜鉴权、权限与多租户规范

**不新建平行鉴权体系**——完全复用 F-TENANT-001（TENANT-F001~F006）已冻结的模式，与专项01报告第16节采用同一套复用原则：

1. **人类用户访问**：走 `POST /tenant/sessions` 登录获得带 `tenantId` claim 的 JWT；`/cred/*` 端点用同一套JWT校验，不单独发一套CRED token。CRED-F002人类账号权限走Infisical自身RBAC+项目划分，Matbox侧只做"谁能访问哪个项目"的映射，不重复实现密码校验。
2. **AI员工访问**：每次 `POST /cred/agent-grants` 请求，Matbox内部先调用 `POST /tenant/authz/check` 做ABAC判断（`resource_type=credential_grant`, `action=issue`），确认请求方AgentIdentity的委派链条（`delegatedBy`）没有越权（对应ACTION-F005委派权限检查）；Grant签发后，`GET /cred/agent-grants/{grantId}` 是 F-TENANT-001 OPA鉴权判断scope的唯一事实源，TENANT模块不复制一份。
3. **多租户隔离**：所有CRED表强制带 `tenant_id` 字段，遵循TENANT-F004"共享表+租户ID字段"模式，查询层禁止绕过租户过滤。
4. **PlatformAdmin访问租户CRED数据**：必须走TENANT-F002定义的break-glass流程（时限+理由+不可篡改审计），不能静默查看某租户的Grant/审计详情。
5. **匿名访客身份鉴权**：CRED-F009签发的AnonymousVisitorSession默认零信任，只覆盖TENANT-F006定义的只读allowlist；`POST /tenant/authz/check` 的subjectType=visitor场景，直接读CRED-F009的scopeAllowlist做判断，TENANT-F006不新建平行访客身份表。
6. **企业第三方集成凭证鉴权**：`/cred/integrations/*` 端点仅限该租户的TenantOwner/TenantAdmin角色操作，运行时注入调用方必须是已注册的内部服务身份（ServiceAccount），不对AI员工直接开放。

### 5.7 错误码、重试、超时与降级（全局规范）

## 19｜错误码、重试、超时和降级规范

**完全复用** `Matbox_错误码规范_正式开发文档_V1.0-RC.md` 定义的17个跨模块错误码，不新造平行错误码体系。CRED模块典型映射：

| 场景 | 错误码 | HTTP | 可重试 |
|---|---:|---|---|
| 请求身份缺失/无效JWT | AUTH_UNAUTHENTICATED | 401 | 否 |
| Grant请求scope超过AgentIdentity授权范围 | AUTH_FORBIDDEN | 403 | 否 |
| 跨租户读取他人SecretRef/Grant | TENANT_BOUNDARY_VIOLATION | 403 | 否 |
| secretRefId/grantId不存在 | RESOURCE_NOT_FOUND | 404 | 否 |
| 同idempotencyKey但payload不同 | IDEMPOTENCY_CONFLICT | 409 | 否 |
| 访客会话已LINKED后再次尝试link | INVALID_STATE_TRANSITION | 409 | 否 |
| Infisical实例不可用（网络/自身故障） | PROVIDER_UNAVAILABLE | 503 | 是 |
| Infisical API调用超时 | PROVIDER_TIMEOUT | 504 | 是 |
| Infisical拒绝合法请求（如KMS Key缺失，见第6.1节真实Issue） | PROVIDER_REJECTED | 422 | 否 |
| 轮换Job失败 | INTERNAL_ERROR（细分errorClass在details字段） | 500 | 是（有界） |

**降级规范**：任何Infisical不可达/鉴权判断失败一律fail-closed（不得因为存储层不可用就放行Grant签发或密钥读取），与原设计P0规则完全一致，本报告不改变这条。

## 6 · 开工前必读的架构禁令（QUEUE-F009 要求随包附带）

- **架构原则第58条**：施工期间的实时动作拦截 —— 高风险公共文件的写入会被拦并转人工。
- 不许重造平台已有能力（鉴权、队列、存储、密钥、通知），一律复用对应模块。
- 不许把密钥写进代码、日志或 Prompt。
- 源文档里没有的内容，**不许脑补补全**：卡住了就说，那是材料的缺口，不是你的问题。

## 7 · 完工时必须交出什么

| 交付物 | 判据 |
|---|---|
| 代码 + 迁移 | CI 绿 |
| 测试 | 认领的每条编号都有测试且**通过**（失败/跳过/没报告都不算） |
| AcceptanceRunID | CI 那次运行的标识，写进 PR 描述 |
| 不越界 | `_check_scope.py` 无越界文件 |

判「做完了」的是 `_check_delivery.py`（D1/D4），**不是实现方说了算**。

## 8 · 怎么起本地环境

先装两样（缺一样编不了）：JDK **17**、Maven **3.9+**（`mvn -v` 要指向 JDK 17）。
数据库用 PostgreSQL，迁移由 Flyway 自动跑。详见源文档 §4.18。

## 28｜交给未来AI开发人员的完整执行说明

如果你是接手这个模块施工的未来AI开发者（Codex或其他），请按以下顺序阅读和执行，不需要重新做调研或重新选型：

1. **先读原设计文档**（Stage 9正式依据，仍然有效）：`docs/Matbox_密钥管理_正式开发文档_V1.0-RC.md`——定义了9个Feature的完整Feature Register、核心数据Contract、P0冻结规则，是主体施工依据。
2. **再读本报告**（本文件）——本报告不推翻原设计的技术路线（Infisical仍是CRED-F001的选中方案），只做四处修正：
   - CRED-F004"运行时代理注入"优先复用Infisical原生Agent Proxy（静态密钥场景），Matbox只自研Grant签发/scope绑定/收回业务逻辑，不要100%从零实现代理转发通道（第9.2/11/25节）。
   - CRED-F005的"DB密码不支持自动轮换"这条已知限制，精确表述为"Infisical自托管**免费**版不支持，Enterprise License版支持但价格未公开"，不要笼统写成"Infisical做不到"；如果未来轮换需求优先级上升，OpenBao是免费的现成解法，触发条件见第0节（第8/26节）。
   - CRED-F004及任何内部运维/监控自动化工具，必须同样贯彻最小权限原则，不能因为是"内部工具"默认高权限（基于Composio 2026年5月真实事故，第24/27节新增P0验收项）。
   - Stage 10前置任务新增：在真实自托管环境验证Dynamic Secrets/细粒度权限在免费版下的真实可用边界（CRED-T008），以及KMS Key缺失等已知Issue的回归测试（CRED-T009）。
3. **依赖检查**：施工前确认以下专项均已存在且状态为DRAFT_RESEARCH_COMPLETE或更高——`Matbox_证据审计与监控_正式开发文档_V1.0-RC.md`（F-OBS-001）、`Matbox_租户与权限体系_正式开发文档_V1.0-RC.md`（F-TENANT-001）、`Matbox_错误码规范_正式开发文档_V1.0-RC.md`、`Matbox_AI员工身份_正式开发文档_V1.0-RC.md`（F-AIEMP-001，AgentIdentity关联方）。
4. **Stage 10前置条件不可跳过**：必须先有真实自托管Infisical实例（含实际部署、项目/环境结构定义）才能开始任何一条WorkPackage施工（WP-CRED-01~08，第25节）。
5. **施工顺序**：WP-CRED-01（Infisical部署+Adapter）必须最先完成，其余P0项（02/03/04/05/06）可部分并行但都依赖01；WP-CRED-04（代理注入）依赖WP-CRED-03（Grant签发）先行。
6. **不要重新做的事**：不要重新调研Infisical是否应该被HashiCorp Vault/OpenBao替代（本报告已核查，Vault因BSL淘汰、OpenBao记录为有明确触发条件的监控项）；不要重新设计错误码（复用错误码规范）；不要重新设计鉴权模式（复用F-TENANT-001）；不要在没有新证据的情况下重新讨论"是否应该整体采购AI Agent身份管理SaaS平台"（第3.2/3.3节已系统核查并排除，除非出现足以改变结论的全新证据，例如Aembit等推出了可信的自托管选项）。
7. **如果发现本报告或原设计与真实Infisical实例情况冲突**：按原设计不可变原则处理——不允许因为图省事就静默绕过P0规则；发现真实冲突应记录并升级给Security Owner决策，不要自行降级。

---
