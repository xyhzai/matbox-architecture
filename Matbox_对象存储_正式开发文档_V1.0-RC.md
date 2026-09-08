# Matbox 对象存储（F-STORAGE-001）

正式开发文档 · V1.0-RC · 2026-08-29

## 当前定位

本专项解决"知识库原始数据、AI生成的图片/视频素材、各类文档"这类非结构化文件该存在哪里的问题。是 Platform Core 的共享能力，直接支撑架构原则第7条"知识库原始数据必须完整保留"的落地，也是 Harbor（F-RELEASE-001）之外另一类文件存储需求（Harbor专管构建产物，本模块管业务数据文件）。

**这是本次自我复查（非用户提出）新发现的最后一个缺口**。

**DocID**: MATBOX-STORAGE-GATE-20260829-V1.0-RC
**状态**: DRAFT_RESEARCH_COMPLETE
**2026-08-30 补充**：新增 STORAGE-F004~F006，来自《Matbox_多端平台_CURRENT_正式开发文档_V3.0》F-ASSET-001 章节——核对后确认这不是新模块，是本模块缺的"资产生命周期管理"这层业务逻辑（原来只有STORAGE-F001~F003管"文件存哪、怎么隔离"，没有"上传怎么签名、怎么扫毒、怎么软删除"这层），并入本文档，不单独立项（详见架构原则第31条）。

## 1｜不可变原则

1. 知识库的原始数据（转成向量之前的那份，架构原则第7条已定）必须存在这里，不能只存在数据库的某个字段里应付了事。
2. 存储服务本身要用真开源、License干净的方案，参考下方"查证到的教训"，不能默认选最有名气的工具而不查License。
3. 存进来的文件要能追溯到属于哪个租户（配合F-TENANT-001做隔离），不能所有租户的文件堆在一个不分彼此的空间里。

## 2｜全球调研结论（2026-08-29）

### 2.1 关键教训：不能凭"知名度"选工具，MinIO 是前车之鉴

原本"自建对象存储"的默认选择通常是 MinIO，但查证后发现：**MinIO 2025-2026年经历了和 HashiCorp Vault 相同的剧本**——2021年就把核心协议从宽松的 Apache 2.0 改成限制更严的 AGPLv3，2026年上半年干脆把开源版仓库冻结（不再更新、不再出安全补丁、不再提供现成安装包），逼迫用户转向商业版。

这再次验证了架构原则第3条"技术选型必须查License，不能因为效果好/名气大就直接绑定"的必要性——如果不查证直接选了MinIO，现在就要面临被迫迁移的困境。

### 2.2 工具选型

| 候选 | License | 结论 |
|---|---|---|
| MinIO | AGPLv3，社区版事实上停止维护 | **淘汰** |
| Garage | AGPL-3.0 | 备选，但AGPL对Matbox这种不开源自己代码的商业产品，法律审查复杂度和MinIO一样 |
| **SeaweedFS** | **Apache 2.0（真开源，商业友好）** | **采用**——12年历史，Kubeflow等知名项目采用，擅长存海量小文件，单二进制部署简单 |

## 3｜Own / Reuse / Must Not Rebuild

| 类型 | 对象 | 说明 |
|---|---|---|
| OWN | 文件归属租户的元数据规则、访问控制 | Matbox 自己的业务归属规则 |
| REUSE | SeaweedFS 存储引擎、S3兼容接口 | 不重新造存储引擎 |
| MUST NOT REBUILD | S3协议本身 | 用现成标准协议，工具可替换 |

## 4｜Feature Register

| FeatureID | 名称 | 说明 |
|---|---|---|
| STORAGE-F001 | SeaweedFS 集成 | 自建部署，S3兼容接口对接 |
| STORAGE-F002 | 知识库原始数据落地 | 承接架构原则第7条，存储转向量前的原始数据 |
| STORAGE-F003 | 租户隔离的文件归属 | 配合F-TENANT-001，文件按租户隔离存取 |
| STORAGE-F004 | 签名上传/下载 | Presigned URL，不暴露真实bucket地址，2026-08-30从多端平台文档并入 |
| STORAGE-F005 | 病毒扫描与隔离检疫 | 上传文件先隔离扫描，未通过不进入可用状态，2026-08-30并入 |
| STORAGE-F006 | 资产生命周期状态机 | UPLOADING→QUARANTINED→SCANNING→READY/REJECTED→DELETED_SOFT→PURGED，2026-08-30并入 |

### STORAGE-F001 · SeaweedFS 集成
- **目标**：Matbox 后端统一通过 S3 兼容接口读写文件，不直接依赖某个特定云厂商的私有 SDK。
- **验收标准**：以后如果要换存储方案，只要保持S3兼容接口不变，上层代码不用改。

### STORAGE-F002 · 知识库原始数据落地
- **目标**：知识库模块的原始数据（Embedding前的那份）存进这里，作为以后重建索引的"源头"。
- **依赖**：架构原则第7条已确认的知识库原则。
- **验收标准**：任意一条知识库记录，能找到对应的原始数据文件。

### STORAGE-F003 · 租户隔离的文件归属
- **目标**：每个文件明确归属哪个租户，配合 F-TENANT-001 做访问控制。
- **验收标准**：跨租户访问文件的尝试必须被拒绝。

### STORAGE-F004 · 签名上传/下载（2026-08-30新增）
- **目标**：上传/下载文件不暴露真实的SeaweedFS bucket地址，用短时效的Presigned URL代替；前端拿不到能长期复用的直连地址。
- **验收标准**：Presigned URL过期后必须失效；不能通过泄露的URL永久访问文件。

### STORAGE-F005 · 病毒扫描与隔离检疫（2026-08-30新增）
- **目标**：任何上传的文件先进隔离区扫描（病毒/恶意软件/压缩炸弹/EXIF风险），扫描通过才转为可用状态，不能上传即用。
- **依赖**：需要接入AV扫描Provider（具体工具Stage10选型）。
- **验收标准**：故意上传测试用的恶意样本文件，验证被正确拦截且不进入可用存储区。

### STORAGE-F006 · 资产生命周期状态机（2026-08-30新增，原样保留自多端平台文档；2026-09-02补充恢复路径，见附录说明）
- **目标**：每个上传的资产都有明确的生命周期状态，不是"存进去就完事"。
- **状态机**：`UPLOADING → QUARANTINED → SCANNING → READY / REJECTED → DELETED_SOFT → PURGED`，**`DELETED_SOFT`在保留期（默认30天，可配置）内可恢复回`READY`，超过保留期才真正转入`PURGED`（不可逆）**——此前版本只画了单向箭头到PURGED，但验收标准明确要求"软删除后一段时间内可恢复"，两者对不上，2026-09-02制作流程演示图时核查发现并修正。
- **验收标准**：未到READY状态的资产不能被发布/被AI检索(RAG)使用；软删除后在保留期内调用恢复接口必须能拿回READY状态且内容不丢失；保留期过后的资产不允许再被恢复，只能转入PURGED；PURGED状态不可逆，不存在"清除后又恢复"的路径。

## 5｜核心数据 Contract（逻辑模型，可直接建表/建接口）

**FileObject**（2026-08-30补充lifecycleStatus/lineage字段，承接STORAGE-F004~F006；2026-09-02补充软删除恢复窗口所需字段）
objectId, tenantId, bucket, key（SeaweedFS路径）, contentType, sizeBytes, checksum(sha256), sourceType(knowledge_base_raw|ai_generated_asset|user_upload|other), lifecycleStatus(UPLOADING|QUARANTINED|SCANNING|READY|REJECTED|DELETED_SOFT|PURGED), lineage（记录来源/衍生关系）, uploadedAt, uploadedBy, **deletedAt?**（软删除发生时间）, **deletedBy?**, **purgeScheduledAt?**（deletedAt+保留期，到期后由定时任务转入PURGED，供恢复窗口判断依据）

**KnowledgeBaseRawLink**（承接架构原则第7条，知识库记录与原始文件的绑定）
linkId, knowledgeRecordId, objectId, embeddingModelVersion（记录当时用哪个模型生成的向量，换模型时据此批量重建）

**API 端点（最小集合）**
- `PUT /storage/objects` — 上传文件，返回objectId（S3兼容接口，内部转发SeaweedFS）
- `GET /storage/objects/{objectId}` — 下载文件，经TENANT-F004校验租户归属
- `GET /storage/knowledge-base/{knowledgeRecordId}/raw` — 按知识库记录查原始文件（供重建索引用）
- `POST /storage/objects/presigned-upload` — 获取短时效的签名上传URL（STORAGE-F004）
- `GET /storage/objects/{objectId}/presigned-download` — 获取短时效的签名下载URL（STORAGE-F004）
- `POST /storage/objects/{objectId}/soft-delete` — 软删除资产（STORAGE-F006），同时写入`purgeScheduledAt`
- `POST /storage/objects/{objectId}/restore` — 在保留期内把`DELETED_SOFT`恢复回`READY`（2026-09-02补充，此前只有soft-delete没有对应的restore端点，验收标准里的"可恢复"承诺无法兑现，属真实契约缺口）；超过`purgeScheduledAt`后调用此接口必须拒绝

## 6｜P0 冻结规则

1. 知识库原始数据丢失或未落地存储：等同违反架构原则第7条，视为严重缺陷。
2. 文件跨租户可被访问：不可降级 P0（与F-TENANT-001的P0规则一致）。
3. 未通过病毒扫描的文件进入READY可用状态：不可降级P0（2026-08-30新增）。

## 7｜当前唯一继续断点

Stage 10（真实部署SeaweedFS）尚未开始。下一步：把 STORAGE-F001~F006 转成 WorkPackage。

**至此，本次自我复查发现的4个缺口（F-COST-001、F-TENANT-001、F-QUEUE-001、F-STORAGE-001）全部完成正式开发文档。**

## 附录｜来源

- [MinIO CE Is Effectively Dead in 2026 — Here's What to Run Instead](https://medium.com/@rosgluk/minio-ce-is-effectively-dead-in-2026-heres-what-to-run-instead-2210130445c7)
- [Self-Hosted S3 Storage in 2026: RustFS, SeaweedFS, Garage, or Ceph?](https://rilavek.com/resources/self-hosted-s3-compatible-object-storage-2026)
- [MinIO's community edition is archived. What still runs in 2026](https://stormdevelopments.ca/blog/minio-s-community-edition-is-archived-what-still-runs-in-2026/)
- [Self-Hosted Object Storage in 2026: SeaweedFS, Garage, and Why MinIO is Done](https://www.offshoreserverhosting.com/blog/self-hosted-object-storage-2026-seaweedfs-garage-minio-replacement/)
- STORAGE-F004~F006 内容来源：《Matbox_多端平台_CURRENT_正式开发文档_V3.0》F-ASSET-001 章节（2026-08-30核对合并，详见架构原则第31条）
- **DELETED_SOFT恢复路径修正依据（2026-09-02）**：制作STORAGE-F006专属流程演示图（`storage_asset_lifecycle_flow.html`）时核查发现，原状态机只有单向箭头到PURGED，与验收标准"软删除后一段时间内可恢复"矛盾，且API端点列表只有soft-delete没有restore，是真实契约缺口，非解读分歧；修正参照通用对象存储软删除+保留期恢复窗口的标准做法（S3/GCS等主流对象存储均采用"软删除→保留期内可恢复→保留期过后转永久删除"三段式设计）
