# 全球多语言（LOC）

**FeatureID**：LOC-F001 ~ LOC-F020（共 20 份）　　**Implementer**：opencode

> 这一页是**取件处**，不是介绍页。要开工的 AI 从这里下载自己那一份，不需要去别的地方翻。

---

## 先核对新鲜度（重要）

本页生成自主仓库提交 **`78a56f97e863`**（2026-09-10 20:49）。

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
| LOC-F001 | [下载 .md](../工作包/LOC/LOC-F001.md) | [下载 .docx](../导出_Word/LOC-F001.docx) |
| LOC-F002 | [下载 .md](../工作包/LOC/LOC-F002.md) | [下载 .docx](../导出_Word/LOC-F002.docx) |
| LOC-F003 | [下载 .md](../工作包/LOC/LOC-F003.md) | [下载 .docx](../导出_Word/LOC-F003.docx) |
| LOC-F004 | [下载 .md](../工作包/LOC/LOC-F004.md) | [下载 .docx](../导出_Word/LOC-F004.docx) |
| LOC-F005 | [下载 .md](../工作包/LOC/LOC-F005.md) | [下载 .docx](../导出_Word/LOC-F005.docx) |
| LOC-F006 | [下载 .md](../工作包/LOC/LOC-F006.md) | [下载 .docx](../导出_Word/LOC-F006.docx) |
| LOC-F007 | [下载 .md](../工作包/LOC/LOC-F007.md) | [下载 .docx](../导出_Word/LOC-F007.docx) |
| LOC-F008 | [下载 .md](../工作包/LOC/LOC-F008.md) | [下载 .docx](../导出_Word/LOC-F008.docx) |
| LOC-F009 | [下载 .md](../工作包/LOC/LOC-F009.md) | [下载 .docx](../导出_Word/LOC-F009.docx) |
| LOC-F010 | [下载 .md](../工作包/LOC/LOC-F010.md) | [下载 .docx](../导出_Word/LOC-F010.docx) |
| LOC-F011 | [下载 .md](../工作包/LOC/LOC-F011.md) | [下载 .docx](../导出_Word/LOC-F011.docx) |
| LOC-F012 | [下载 .md](../工作包/LOC/LOC-F012.md) | [下载 .docx](../导出_Word/LOC-F012.docx) |
| LOC-F013 | [下载 .md](../工作包/LOC/LOC-F013.md) | [下载 .docx](../导出_Word/LOC-F013.docx) |
| LOC-F014 | [下载 .md](../工作包/LOC/LOC-F014.md) | [下载 .docx](../导出_Word/LOC-F014.docx) |
| LOC-F015 | [下载 .md](../工作包/LOC/LOC-F015.md) | [下载 .docx](../导出_Word/LOC-F015.docx) |
| LOC-F016 | [下载 .md](../工作包/LOC/LOC-F016.md) | [下载 .docx](../导出_Word/LOC-F016.docx) |
| LOC-F017 | [下载 .md](../工作包/LOC/LOC-F017.md) | [下载 .docx](../导出_Word/LOC-F017.docx) |
| LOC-F018 | [下载 .md](../工作包/LOC/LOC-F018.md) | [下载 .docx](../导出_Word/LOC-F018.docx) |
| LOC-F019 | [下载 .md](../工作包/LOC/LOC-F019.md) | [下载 .docx](../导出_Word/LOC-F019.docx) |
| LOC-F020 | [下载 .md](../工作包/LOC/LOC-F020.md) | [下载 .docx](../导出_Word/LOC-F020.docx) |

## 2 · 整份开发文档（总账）

- [DEV.docx](../全球多语言/Matbox_全球多语言_交接包_V1.0/DEV.docx)
- [Matbox_全球多语言_开发交接补全_V1.0.md](../全球多语言/Matbox_全球多语言_开发交接补全_V1.0.md)

## 3 · 边界与状态（机器可读）

- 能改哪、禁止碰哪：[loc_protected_scope.yml](../loc_protected_scope.yml)
- 资料准备度：🔴 **还没有**（应为 `loc_ready_state.json`）——不是忘了放链接，是这份文件在主仓库里就不存在。

## 4 · 流程演示图

- [loc_gate_flow.html](../loc_gate_flow.html)
- 也可以从[架构地图](../architecture_dependency_diagram.html)点开

---

**取件之后**：开工五步写在每份工作包的 §0.5，照着敲即可，不用再问人。
