# 密钥与凭据管理（CRED）

**FeatureID**：CRED-F001 ~ CRED-F009（共 9 份）　　**Implementer**：opencode

> 这一页是**取件处**，不是介绍页。要开工的 AI 从这里下载自己那一份，不需要去别的地方翻。

---

## 先核对新鲜度（重要）

本页生成自主仓库提交 **`b5b13bc4312f`**（2026-09-11 01:52）。

开工前请确认这个 commit 与主仓库最新一致；不一致说明网站没跟上，**先让它更新再开工**，不要拿旧材料动手。

---

## 0 · 这个包按什么标准验收

**先看这一份**，它定了「材料齐到什么程度才算能开工」「在建过程中不许发生什么」「做完了的唯一定义是什么」。你会被这份标准里的程序按 diff 和 CI 判，不看自述。

- [Matbox_开发包标准_V2.0.md](../Matbox_开发包标准_V2.0.md)　·　Word 版：[下载 .docx](../导出_Word/Matbox_开发包标准_V2.0.docx)

> **卡住了是我们的问题，不是你的。** 该标准 §0.5 写明：最终验收标准是「你拿到材料能不能马上开发」，我们那套检查只是代理指标。你每卡一次就说明材料漏了一条 —— **说出来，我们补进标准；不要自己脑补补全**。

---

## 1 · 拿你自己那一份工作包

每份都是自包含的：开工五步（clone 地址、切分支、编译命令、包名）、你要实现的 API 端点、你要建的表（完整 SQL）、代码放哪、七类施工面、你的验收标准、开工前必读的架构禁令、完工交付清单。

| 工作包 | Markdown | Word |
|---|---|---|
| CRED-F001 | [下载 .md](../工作包/CRED/CRED-F001.md) | [下载 .docx](../导出_Word/CRED-F001.docx) |
| CRED-F002 | [下载 .md](../工作包/CRED/CRED-F002.md) | [下载 .docx](../导出_Word/CRED-F002.docx) |
| CRED-F003 | [下载 .md](../工作包/CRED/CRED-F003.md) | [下载 .docx](../导出_Word/CRED-F003.docx) |
| CRED-F004 | [下载 .md](../工作包/CRED/CRED-F004.md) | [下载 .docx](../导出_Word/CRED-F004.docx) |
| CRED-F005 | [下载 .md](../工作包/CRED/CRED-F005.md) | [下载 .docx](../导出_Word/CRED-F005.docx) |
| CRED-F006 | [下载 .md](../工作包/CRED/CRED-F006.md) | [下载 .docx](../导出_Word/CRED-F006.docx) |
| CRED-F007 | [下载 .md](../工作包/CRED/CRED-F007.md) | [下载 .docx](../导出_Word/CRED-F007.docx) |
| CRED-F008 | [下载 .md](../工作包/CRED/CRED-F008.md) | [下载 .docx](../导出_Word/CRED-F008.docx) |
| CRED-F009 | [下载 .md](../工作包/CRED/CRED-F009.md) | [下载 .docx](../导出_Word/CRED-F009.docx) |

## 2 · 整份开发文档（总账）

- [Matbox_密钥管理_正式开发文档_V1.0-RC.md](../Matbox_密钥管理_正式开发文档_V1.0-RC.md)

## 3 · 边界与状态（机器可读）

- 能改哪、禁止碰哪：[cred_protected_scope.yml](../cred_protected_scope.yml)
- 资料准备度：🔴 **还没有**（应为 `cred_ready_state.json`）——不是忘了放链接，是这份文件在主仓库里就不存在。

## 4 · 这个模块的三段页面

- 从[架构地图](../architecture_dependency_diagram.html)点这个模块的节点，会弹出它的开发前 / 开发中 / 依赖关系 / 运行中四段；点 × 回到图上。

---

**取件之后**：开工五步写在每份工作包的 §0.5，照着敲即可，不用再问人。
