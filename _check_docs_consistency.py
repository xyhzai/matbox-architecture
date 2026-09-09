# -*- coding: utf-8 -*-
"""
Matbox 文档一致性检查器 —— 一条命令查出"残留"。

    python docs/_check_docs_consistency.py

═══ 为什么有这个文件 ═══

2026-09-08，用户第 N 次替我发现残留后说：

    「你应该彻底去解决代码残留的问题，避免你一次又一次的如此混乱」

以往每次改名/改编号，靠的是"先列出所有写法，再全局替换，再 Grep 复验"。
这个方法有一个致命缺陷：**复验用的清单是我自己列的**，我没想到的写法就
永远查不出来。同一天真实发生的三次漏网都是这个原因：

  1. VIZ 改名，第 7 种写法「代码可视化修复闭环」藏在流程图 <title> 里，
     不在我列的 6 种变体清单内 —— 是打开浏览器看渲染结果才撞见的。
  2. 同一道 Gate 两个编号：G-DQ-ST10-REPO-001（全文 1 次）与
     G-STAGE10-REPO-001（29 次），从来没人发现。
  3. 开发总账里 10 处 (MISSING，阻塞) 停在 2026-08-29 之前，
     半个月里任何人打开看到的都是假信息。

本文件把检查方式从"拿我列的清单去对"换成"从文件本身推出应该一致的东西，
再看它们是否真的一致"——不依赖我事先想全。

═══ 一条设计原则：宁可少报，不可乱报 ═══

第一版跑出来 13 个 FAIL，**全部是误报**——把注释里当例子写的
`src="本地.js"`、JS 里的字符串拼接 `' + d.html_url + '`、以及架构原则第57
条里作为历史记录写的旧编号，都当成了残留。会喊狼来了的检查器，人看两次
就不看了，比没有更糟。所以下面每一项都做了排除：注释和 <script> 先剥掉、
"同一行里旧名和新名都出现"视为改名说明而放行、模块名只出表不判故障。

.docx 也读（正式开发文档全是 .docx，不读等于漏掉真相所在的那一半）。

任何一项 FAIL 就是残留，必须修完再提交。
"""

import hashlib
import io
import json
import os
import re
import sys
from collections import defaultdict

# Windows 控制台默认 GBK，本脚本打印的 ✅ / ⚠️ 之类符号会直接
# UnicodeEncodeError 崩掉——审计其实是绿的，人却只看到一段 traceback。
# 2026-09-09 一次性给全部脚本补上；缘由详见 _build_public_export.py 顶部。
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

DOCS = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(DOCS)
SELF = os.path.basename(__file__)

# ── 已退役的写法：改名之后不允许再出现（值 = 现在应该叫什么） ──────────
# 每次改名请把旧名登记进来，加一行的成本极低，换来的是以后任何人写回旧名
# 都会被当场抓到，而不是等用户撞见。
RETIRED = {
    "代码问题可视化定位与智能修复中心": "代码问题定位与人工修复台",
    "代码可视化修复中心": "代码问题定位与人工修复台",
    "代码可视化中心": "代码问题定位与人工修复台",
    "可视化修复中心": "人工修复台",
    "可视化中心": "人工修复台",
    "代码可视化修复闭环": "代码问题定位与人工修复闭环",
    "G-DQ-ST10-REPO-001": "G-STAGE10-REPO-001",
    "（MISSING，阻塞）": "已有正式文档 …；实现未开工",
    "DQ-F00": "F-DQ-0",       # 架构原则第57条统一过的旧编号格式
    "VIZ-F00": "F-VIZ-0",
    # 2026-09-09 用户定：模块改名 全球多语言与本地化 → 全球多语言。
    # 登记进来，任何人（包括我）再写回旧名都会被当场抓到。
    "全球多语言与本地化": "全球多语言",
}

# 允许写出旧名的场合：更名/纠正说明本身必须写出旧名，否则读者不知道改的是什么。
# 判据有两条，满足其一即放行——① 这一行有"更名/纠正/原名"这类词；
# ② 这一行同时出现了旧名和它对应的新名（那就是在描述一次改名，不是残留）。
RENAME_WORDS = re.compile(r"更正|更名|改名|纠正|原名|原写作|原先|此前|旧写法|旧格式|改成|统一为|残留|RETIRED|retired")

# 明确豁免：这些地方"写着旧名"是对的，因为它们本身就是在记录一次改名的历史，
# 删掉旧名那段话就读不懂了。每条必须写清理由，而且会被打印出来——豁免不藏着，
# 否则下一个人不知道这里为什么绿了。
ALLOW_EXCEPTIONS = [
    ("Matbox_架构设计原则.md", "DQ-F00",
     "第57条正文在陈述改名前的旧编号格式，是这条原则的必要背景"),
    ("Matbox_架构设计原则.md", "VIZ-F00",
     "同上，与 DQ-F00 是同一句话里的一对"),
]

TEXT_EXT = (".md", ".html", ".yaml", ".yml", ".js", ".py")
SKIP_FILES = {"flow_embeds.js"}          # 生成物，单独用 C1 校指纹
SKIP_DIRS = {".git", "node_modules", "__pycache__"}

fails, warns, name_rows, notes = [], [], [], []
exempted = set()


def rel(p):
    return os.path.relpath(p, DOCS).replace("\\", "/")


def read(p):
    return io.open(p, encoding="utf-8", errors="replace").read()


def strip_noise(body, path):
    """剥掉注释和代码样例——里面写的东西不是真链接、真名字。

    HTML：注释和 <script>（R5 的 JS 里有 ' + d.html_url + ' 这种拼接，
    第一版把它当成断链报了出来）。
    Markdown：围栏代码块和行内反引号（文档里写 `src="本地.js"` 是在举例
    说明，不是一个真链接——本检查器自己的架构原则第77条就踩了这一下）。
    """
    if path.endswith((".html", ".htm")):
        body = re.sub(r"<!--.*?-->", " ", body, flags=re.S)
        body = re.sub(r"<script[^>]*>.*?</script>", " ", body, flags=re.S)
    elif path.endswith(".md"):
        body = re.sub(r"```.*?```", " ", body, flags=re.S)
        body = re.sub(r"`[^`\n]*`", " ", body)
    return body


def walk_text_files():
    for root, dirs, files in os.walk(DOCS):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in sorted(files):
            if fn.endswith(TEXT_EXT) and fn not in SKIP_FILES and fn != SELF:
                yield os.path.join(root, fn)


def walk_docx():
    """正式开发文档都是 .docx，不读它就等于只查了一半仓库。"""
    try:
        import docx  # noqa
    except ImportError:
        notes.append("未安装 python-docx，本次跳过所有 .docx（正式开发文档），"
                     "装上后覆盖面才完整：pip install python-docx")
        return
    import docx
    for root, dirs, files in os.walk(DOCS):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in sorted(files):
            if not fn.endswith(".docx") or fn.startswith("~$"):
                continue
            p = os.path.join(root, fn)
            try:
                d = docx.Document(p)
            except Exception as e:                       # noqa
                warns.append("读不了 %s：%s" % (rel(p), e))
                continue
            lines = [q.text for q in d.paragraphs]
            for t in d.tables:
                for r in t.rows:
                    lines.append(" | ".join(c.text for c in r.cells))
            yield p, lines


# ══ C11：GitHub Actions 的 workflow 文件能不能解析 ═════════════════════
# 2026-09-09 加的，起因是一次实打实的失败：publish-site.yml 里有一段
# 跨行的 git commit -m "…"，续行顶格写在第 0 列。`run: |` 是 YAML 块标量，
# 比块缩进浅的行会直接结束这个块，于是整个文件语法就废了。
# GitHub 的反应是连 job 都不建，直接判「workflow file issue」——
# **推一次红一次，而且红得毫无信息量**，从建立起一次都没跑起来过。
# 更糟的是我据此对外说「它只是差个 Secret」，那是错的：先差的是文件本身能不能解析。
#
# 所以这条检查只回答一个问题：**这个文件 GitHub 拿去能读吗**。
# 不装 pyyaml 也要能查出这一类，所以自己写了缩进检查：
# 块标量里任何非空行都不许比块首行还浅。装了 pyyaml 就再整体解析一遍。
def check_workflows():
    wdir = os.path.join(os.path.dirname(DOCS), ".github", "workflows")
    if not os.path.isdir(wdir):
        return
    for fn in sorted(os.listdir(wdir)):
        if not fn.endswith((".yml", ".yaml")):
            continue
        path = os.path.join(wdir, fn)
        lines = read(path).split("\n")

        # ① 无依赖：块标量（run: | / script: | 等）里的浅缩进行
        i = 0
        while i < len(lines):
            m = re.match(r"^(\s*)[\w.-]+:\s*[|>][-+]?\s*$", lines[i])
            if not m:
                i += 1
                continue
            key_indent = len(m.group(1))
            body, j = None, i + 1
            while j < len(lines):
                ln = lines[j]
                if not ln.strip():
                    j += 1
                    continue
                ind = len(ln) - len(ln.lstrip())
                if body is None:
                    if ind <= key_indent:
                        break                       # 空块，正常
                    body = ind
                elif ind < body:
                    if ind <= key_indent:
                        break                       # 正常收尾，回到上一层
                    fails.append(
                        "C11 %s 第 %d 行缩进比所属块浅（块缩进 %d，本行 %d）——"
                        "YAML 会在这里提前结束块标量，整个文件解析就废了。"
                        "GitHub 会直接判 workflow file issue，连 job 都不建。"
                        % (fn, j + 1, body, ind))
                    break
                j += 1
            i = j if j > i else i + 1

        # ② 装了 pyyaml 就整体解析；没装就明说跳过，不算通过
        try:
            import yaml
        except ImportError:
            notes.append("C11 %s 只做了缩进检查——本机没装 pyyaml，"
                         "整体解析没跑（pip install pyyaml 可补上）" % fn)
            continue
        try:
            d = yaml.safe_load(read(path))
        except Exception as e:
            fails.append("C11 %s 解析失败：%s"
                         % (fn, str(e).replace("\n", " ")[:200]))
            continue
        if not isinstance(d, dict) or not d.get("jobs"):
            fails.append("C11 %s 解析出来没有 jobs——GitHub 拿到这个文件不会跑任何东西" % fn)


# ══ C1：flow_embeds.js 是否过期 ════════════════════════════════════════
# 这是 2026-09-08 引入 srcdoc 方案时"我自己新挖的坑"：改了 *_flow.html 但
# 忘了重跑生成器，架构图里嵌的就是旧副本，症状正是用户最怕的那句
# "我明明改了，点开还是老样子"。
def check_flow_embeds():
    bundle = os.path.join(DOCS, "flow_embeds.js")
    if not os.path.exists(bundle):
        fails.append("C1 flow_embeds.js 不存在——架构图点开任何模块都会是空的")
        return
    m = re.search(r"window\.__FLOW_HTML_META__\s*=\s*(\{.*?\});", read(bundle), re.S)
    if not m:
        fails.append("C1 flow_embeds.js 里没有 __FLOW_HTML_META__ 指纹表，无法校验新鲜度")
        return
    meta = json.loads(m.group(1))
    for name, info in sorted(meta.items()):
        path = os.path.join(DOCS, name)
        if not os.path.exists(path):
            fails.append("C1 [%s] 已打包但源文件不存在了" % name)
            continue
        if hashlib.sha256(io.open(path, "rb").read()).hexdigest()[:16] != info["sha256_16"]:
            fails.append("C1 [%s] 改过但没重新生成内嵌副本——架构图里还是旧的。"
                         "跑：python docs/_build_flow_embeds.py" % name)
    for f in sorted({x for x in os.listdir(DOCS) if x.endswith("_flow.html")} - set(meta)):
        warns.append("C1 [%s] 在磁盘上但没进 flow_embeds.js（新流程图要先在 "
                     "_build_flow_embeds.py 的 FLOW_FILES 里登记）" % f)


# ══ C2：退役写法残留（含 .docx） ═══════════════════════════════════════
def _exempt(label, old):
    for f, o, why in ALLOW_EXCEPTIONS:
        if label.endswith(f) and o == old:
            return why
    return None


def _scan_retired(label, lines):
    for i, line in enumerate(lines, 1):
        if RENAME_WORDS.search(line):
            continue
        for old, new in RETIRED.items():
            if old not in line or new.rstrip("…").split(" ")[0] in line:
                continue
            why = _exempt(label, old)
            if why:
                exempted.add("%s 的「%s」——%s" % (label, old, why))
                continue
            fails.append("C2 %s:%d 还留着退役写法「%s」，应为「%s」"
                         % (label, i, old, new))


def check_retired_names():
    for p in walk_text_files():
        _scan_retired(rel(p), strip_noise(read(p), p).split("\n"))
    for p, lines in walk_docx():
        _scan_retired(rel(p) + "(docx)", lines)


# ══ C3：文档内部链接指向的文件真的存在吗 ═══════════════════════════════
# 改目录名/文件名之后最容易断的就是这个，而断链在 Markdown 里毫无提示。
LOOKS_LIKE_PATH = re.compile(r"[/\\]|\.(md|html?|docx?|ya?ml|js|py|png|jpe?g|svg|pdf|csv|txt)$", re.I)


def check_links():
    md_link = re.compile(r"\[[^\]]*\]\(([^)\s]+)")
    attr = re.compile(r'(?:href|src)="([^"]+)"')
    for p in walk_text_files():
        if not p.endswith((".md", ".html")):
            continue
        body = strip_noise(read(p), p)
        for t in md_link.findall(body) + attr.findall(body):
            if re.match(r"^(https?:|mailto:|data:|javascript:|#|//)", t) or not t.strip():
                continue
            t = t.split("#")[0].split("?")[0]
            # 只查看起来真的像路径的（排除 JS 拼接、表格里的 [80,100] 这类）
            if not t or not LOOKS_LIKE_PATH.search(t) or "+" in t or "'" in t:
                continue
            dest = os.path.normpath(os.path.join(os.path.dirname(p), t))
            if not os.path.exists(dest):
                fails.append("C3 %s 链接断了：%s" % (rel(p), t))


# ══ C4：同一个模块在各处叫什么（只出表，不判故障） ═════════════════════
# 不靠我事先列清单，而是从画布自己的 FULL_PAGE_EMBEDS 推出"这个节点对应哪张
# 流程图"，把三处名字摆在一起。DQ 一个模块有 4 个名字，就是这样看出来的。
#
# 为什么不判故障：模块名和流程名本来就允许不同（模块=Action网关，
# 流程=Action网关调用链）。硬判会把正常情况报成错，人就不看了。摆成一张表，
# 不一致的地方肉眼一秒钟就能挑出来，这比一个会乱叫的规则有用。
def check_module_names():
    diagram = os.path.join(DOCS, "architecture_dependency_diagram.html")
    if not os.path.exists(diagram):
        fails.append("C4 找不到 architecture_dependency_diagram.html")
        return
    s = read(diagram)
    embeds = dict(re.findall(r'(\w+):\s*\{\s*hostId:\s*"[^"]+",\s*url:\s*"([^"]+)"', s))
    if not embeds:
        warns.append("C4 没解析出 FULL_PAGE_EMBEDS，画布结构可能改了，本项跳过")
        return
    # 节点 key 不一定等于 embedKey（如节点 cred/tenant 共用 embedKey credTenant），
    # 所以先按 embedKey 反查节点，查不到再按同名节点找。
    by_embed = dict(re.findall(r'\n    "?([\w-]+)"?:\s*\{[^{]*?embedKey:\s*"(\w+)"', s, re.S))
    rev = {v: k for k, v in by_embed.items()}
    for key, url in sorted(embeds.items()):
        node = rev.get(key, key)
        m = re.search(r'\n    "?' + re.escape(node) + r'"?:\s*\{(.{0,600})', s, re.S)
        canvas = None
        if m:
            tm = re.search(r'title:\s*"([^"]+)"', m.group(1))
            canvas = tm.group(1) if tm else None
        fp = os.path.join(DOCS, url)
        if not os.path.exists(fp):
            fails.append("C4 [%s] 画布指向的流程图不存在：%s" % (key, url))
            continue
        flow = read(fp)
        tm = re.search(r"<title>(.*?)</title>", flow, re.S)
        ftitle = tm.group(1).strip() if tm else None
        # 不能直接 search <h1>：流程图顶部的说明注释里也写着 <h1>，非贪婪匹配
        # 会从注释里的开标签一路吃到真正的闭标签，把整个文件当成标题抓出来。
        fh1 = None
        for cand in re.findall(r"<h1[^>]*>(.*?)</h1>", flow, re.S):
            plain = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", cand)).strip()
            if 0 < len(plain) <= 80:
                fh1 = plain
                break
        name_rows.append((key, canvas or "(未解析)", ftitle or "(无)", fh1 or "(无)"))


# ══ C5：同一道门是不是有两个编号 ═══════════════════════════════════════
# 只比"后缀相同但全名不同"这一种情况——G-DQ-ST10-REPO-001 与
# G-STAGE10-REPO-001 就是这样暴露的。
# 不再报"全仓库只出现 1 次"的孤号：很多 Gate 本来就只在自己那份文档里定义
# 一次，报出来全是噪音。
def check_gate_ids():
    counts = defaultdict(int)
    where = defaultdict(set)
    pat = re.compile(r"G-[A-Z0-9]+(?:-[A-Z0-9]+)*-\d{3}")

    # 只统计"不在更名说明那一行"的出现次数——一个已经废掉的编号，如果它
    # 剩下的每一次出现都是在解释"这个编号已经废了"，那就不是残留，不该报。
    def feed(label, lines):
        for line in lines:
            if RENAME_WORDS.search(line):
                continue
            for gid in pat.findall(line):
                counts[gid] += 1
                where[gid].add(label)

    for p in walk_text_files():
        feed(rel(p), read(p).split("\n"))
    for p, lines in walk_docx():
        feed(rel(p) + "(docx)", lines)

    tail = defaultdict(list)
    for gid in counts:
        tail["-".join(gid.split("-")[-2:])].append(gid)
    for suffix, ids in sorted(tail.items()):
        if len(ids) > 1:
            desc = "、".join("%s(%d次, 见 %s)" % (i, counts[i], sorted(where[i])[0])
                            for i in sorted(ids))
            warns.append("C5 后缀「%s」对应 %d 个不同编号，可能是同一道门两种写法：%s"
                         % (suffix, len(ids), desc))


# ══ C6：有没有文档引用了一个查不到登记行的模块编号 ═════════════════════
# 2026-09-08 起因：F-NOTIFY-001 写着"依赖方（已知阻塞）：F-PLAT-001（人类
# 登录会话）"，一查 Feature Register 里根本没有 F-PLAT-001 的登记行——而它
# 被 9 份正式文档引用。整仓做差集后又查出 F-MEM-001 同样情况。
#
# 注意口径：只有"表格行首列是这个编号"才算有登记行。被别人当依赖提一嘴
# 不算——第一版就是把"在 Feature Register 里出现过"当成在册，结果 F-PLAT-001
# 这种最典型的孤儿反而被漏掉了。
def check_feature_ids():
    reg = os.path.join(DOCS, "Matbox_Feature_Register.md")
    if not os.path.exists(reg):
        warns.append("C6 找不到 Matbox_Feature_Register.md，本项跳过")
        return
    body = read(reg)
    registered = set(re.findall(r"^\|\s*\*{0,2}(F-[A-Z0-9]+-\d{3})", body, re.M))
    registered |= set(re.findall(r"^#{2,4}\s*(F-[A-Z0-9]+-\d{3})", body, re.M))
    # 本文件里已逐条写明原因的（那张「被引用但没有登记行」表），不再重复报
    explained = set(re.findall(r"^\|\s*\*{0,2}(F-[A-Z0-9]+-\d{3})\*{0,2}\s*\|\s*\*{0,2}\d+\s*份",
                               body, re.M))
    refs = defaultdict(set)
    for p in walk_text_files():
        fn = os.path.basename(p)
        if not fn.startswith("Matbox_") or fn == "Matbox_Feature_Register.md":
            continue
        for fid in set(re.findall(r"F-[A-Z0-9]+-\d{3}", read(p))):
            refs[fid].add(rel(p))
    for fid in sorted(refs):
        if fid in registered or fid in explained:
            continue
        warns.append("C6 %s 被 %d 份文档引用，但 Feature Register 里既没有登记行、"
                     "也没写明原因：%s" % (fid, len(refs[fid]),
                                          "、".join(sorted(refs[fid]))[:110]))


# ══ C7：正式文档声称核验过的交接包，必须真的在仓库里、且哈希还对得上 ═══
# 2026-09-08 起因：F-LOC-001 正式文档 §1 白纸黑字写着「MANIFEST 8/8 SHA-256
# 全部一致」「实际执行 poc.py，12/12 PASS」——但那个交接包**从来没进过仓库**。
# 用户发过、我读过、验过、照着写完了整份正式文档，唯独漏了把包本身提交进去。
# 后果是：文档里的核验结论谁也复现不了，而且撞在项目的原始创立规则上
#（不留本地孤本——用户曾因只存本地丢过工作）。
#
# 这一项就是为了让"以后再发生怎么办"有一个机器答案，而不是一句"我下次注意"。
# 两部分：
#   a) 登记在册的交接包目录必须存在（少一个就是 FAIL）
#   b) 仓库里每一个 MANIFEST.json 都必须自校验通过（改一个字节就报出来）
EXPECTED_PACKAGES = [
    ("F-LOC-001 全球多语言",
     "全球多语言/Matbox_全球多语言_交接包_V1.0"),
    ("F-VIZ-001~007 代码问题定位与人工修复台",
     "代码问题定位与人工修复台/Matbox_代码问题定位与人工修复台_Codex独立开发包_V1.0"),
]


def git_blob_reader(root):
    """返回一个函数：按文件名取出 **git 仓库里存的那份字节**。

    用 `git show HEAD:<path>` 而不是读工作区文件——工作区可能有未提交的改动，
    也可能因为 .gitattributes 缺失而与入库内容不同（换行符）。别人 clone 到手
    的是 git 里的那份，所以校验必须以它为准。
    """
    import subprocess

    def read_blob(name):
        rel_path = os.path.relpath(os.path.join(root, name), REPO).replace("\\", "/")
        try:
            out = subprocess.run(["git", "-C", REPO, "show", "HEAD:" + rel_path],
                                 capture_output=True)
        except Exception:                                        # noqa
            return None
        return out.stdout if out.returncode == 0 else None

    return read_blob


def check_handoff_packages():
    for label, sub in EXPECTED_PACKAGES:
        d = os.path.join(DOCS, sub)
        if not os.path.isdir(d):
            fails.append("C7 %s 的交接包不在仓库里：docs/%s —— 正式文档引用了它，"
                         "但仓库里没有，别人无法复核也无法施工" % (label, sub))

    found = 0
    for root, dirs, files in os.walk(DOCS):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        if "MANIFEST.json" not in files:
            continue
        mp = os.path.join(root, "MANIFEST.json")
        try:
            man = json.loads(read(mp))
        except Exception as e:                                   # noqa
            warns.append("C7 %s 解析失败：%s" % (rel(mp), e))
            continue
        entries = man.get("files")
        if not isinstance(entries, dict):
            continue
        found += 1
        ok = bad = 0
        # ⚠️ 关键：必须验 **git 里真正存着的字节**，不是本地工作区文件。
        # 第一版只验工作区，结果给出假绿——本地文件好好的，但 git clone 出来
        # 的副本里 README.txt / evidence.json / features.json 的哈希全对不上
        # （autocrlf 换行符转换），poc.log 还被 .gitignore 的 *.log 整个挡掉
        # 没能入库。工作区通过 ≠ 别人拿到的东西通过。
        tracked = git_blob_reader(root)
        for name, exp in entries.items():
            digest = exp if isinstance(exp, str) else (exp or {}).get("sha256", "")
            raw = tracked(name)
            if raw is None:
                fails.append("C7 %s 里登记的 %s 没有进 git（本地有不算——"
                             "别人 clone 下来就少这个文件）" % (rel(mp), name))
                bad += 1
                continue
            if hashlib.sha256(raw).hexdigest().lower() != str(digest).lower():
                fails.append("C7 %s 的 %s 在 git 里的内容与 MANIFEST 不符"
                             "（多半是换行符被转换了，检查 .gitattributes 的 -text）"
                             % (rel(mp), name))
                bad += 1
            else:
                ok += 1
        notes.append("C7 %s 按 git 存储内容自校验 %d/%d 一致" % (rel(mp), ok, ok + bad))
    if found == 0:
        warns.append("C7 仓库里一个 MANIFEST.json 都没找到，交接包完整性无从校验")


# ══ C8：生成的 FINAL 文档有没有比它的源文件旧 ═════════════════════════
# 2026-09-08：DQ 最终开发文档是从 .docx 抽取生成的。源文件一改它就过期，
# 而过期没有任何提示——这正是今天查出一堆矛盾（Gate 编号、6道vs7道、
# 过期 MISSING 标记）的同一个根因。所以生成物必须自带来源指纹，机器来比。
# 一个生成物可以有多个源——DQ 的 FINAL 就有两个（.docx 讲"要做什么"，
# 专项01 讲"代码怎么写"）。任何一个源改了，生成物就过期。
GENERATED_DOCS = [
    ("Matbox_代码持续质检与安全自检_开发文档_FINAL.md",
     ["Matbox_代码持续质检与安全自检_正式开发文档_V1.1-RC_CURRENT_Stage9内容级重验版_2026-08-19.docx",
      "技术选型报告/Matbox_专项01_代码持续质检与安全自检_技术选型与开发交接报告_2026-08-30.md"],
     "python docs/_build_dq_final_doc.py"),
]


def check_generated_docs():
    for gen, srcs, cmd in GENERATED_DOCS:
        gp = os.path.join(DOCS, gen)
        if not os.path.exists(gp):
            fails.append("C8 生成物不存在：%s —— 跑：%s" % (gen, cmd))
            continue
        stamped = [x.lower() for x in re.findall(r"sha256 `([0-9a-f]{64})`", read(gp))]
        if len(stamped) < len(srcs):
            fails.append("C8 %s 只标了 %d 个来源指纹，但它有 %d 个源——"
                         "少标一个就等于少盯一个" % (gen, len(stamped), len(srcs)))
            continue
        ok = 0
        for src in srcs:
            sp = os.path.join(DOCS, src)
            if not os.path.exists(sp):
                fails.append("C8 %s 的源文件不见了：%s" % (gen, src))
                continue
            now = hashlib.sha256(io.open(sp, "rb").read()).hexdigest().lower()
            if now not in stamped:
                fails.append("C8 %s 已过期——源文件 %s 改过但没重新生成。跑：%s"
                             % (gen, os.path.basename(src), cmd))
            else:
                ok += 1
        if ok == len(srcs):
            notes.append("C8 %s 与全部 %d 个源指纹一致" % (gen, len(srcs)))


# ══ C9：样板上显示的东西，跟它的数据源一致吗 ══════════════════════════
# 2026-09-08 起因：用户看着样板问「文件包的下面不是有内容吗？他们是有对应
# 关系的」——本来就该有，只是从来没接上。那 12 块的 ✅/🟡 和「12 项里 10 项
# 已备齐」这个数字，当时全是手写死在 HTML 里的；我补齐了「⑤ 允许/禁止改动
# 范围」之后，页面还显示 🟡、还写着 10 项。**页面在撒谎，而没有任何人会发现。**
#
# 现在状态只写 dq_ready_state.json，样板由脚本渲染。C9 回头比对两边：
#   a) 12 块的状态徽章逐块一致
#   b) 汇总那句话里的数字，跟按 json 现算出来的一致
#   c) 工作包目录里实际有几个文件，跟存放处列出的一致
# 三条任何一条对不上，都说明"某一步生成没跑"——正是今天反复踩的那个坑。
def check_page_matches_state():
    state_p = os.path.join(DOCS, "dq_ready_state.json")
    page_p = os.path.join(DOCS, "quality_gate_flow.html")
    if not (os.path.exists(state_p) and os.path.exists(page_p)):
        warns.append("C9 找不到 dq_ready_state.json 或样板，本项跳过")
        return
    st = json.loads(read(state_p))
    page = read(page_p)
    label = {"ok": "✅ 已备齐", "partial": "🟡 部分", "missing": "❌ 缺"}

    # a) 逐块比对
    for b in st["blocks"]:
        m = re.search(r'href="#%s"[^>]*>\s*<span class="rs-badge">([^<]+)</span>'
                      % re.escape(b["id"]), page)
        if not m:
            fails.append("C9 样板里找不到 %s（%s）的状态徽章——"
                         "多半是 _build_ready_summary.py 没跑" % (b["n"], b["title"]))
            continue
        if m.group(1).strip() != label.get(b["status"], ""):
            fails.append("C9 %s %s：json 里是「%s」，样板上显示「%s」——"
                         "跑：python docs/_build_all.py"
                         % (b["n"], b["title"], label.get(b["status"]), m.group(1).strip()))

    # b) 汇总数字
    n_ok = sum(1 for b in st["blocks"] if b["status"] == "ok")
    m = re.search(r'class="rs-overall">(\d+) 项里 (\d+) 项已备齐', page)
    if not m:
        fails.append("C9 样板里没找到准备度汇总那一句")
    elif int(m.group(1)) != len(st["blocks"]) or int(m.group(2)) != n_ok:
        fails.append("C9 汇总数字对不上：json 现算是 %d 项里 %d 项已备齐，"
                     "样板上写的是 %s 项里 %s 项——跑：python docs/_build_all.py"
                     % (len(st["blocks"]), n_ok, m.group(1), m.group(2)))

    # c) 工作包目录 vs 存放处清单
    wp = os.path.join(DOCS, "工作包", "DQ")
    if os.path.isdir(wp):
        on_disk = sorted(f for f in os.listdir(wp)
                         if os.path.isfile(os.path.join(wp, f)) and not f.startswith("."))
        # 存放处第一行是「总账」（完整开发文档本身），它不在工作包目录里，
        # 是刻意摆在那儿的入口——2026-09-08 用户问「为什么我没有看到开发文档」，
        # 查出样板/架构图/详情卡三处都没有它的链接。比对时要把它排除，
        # 否则会把一个正确的入口当成不一致报出来。
        # 用 📘 前缀识别，不用正则去剥那个 div——第一版写了
        # `<div class="wp-file wp-file-ledger">.*?</div>\s*</div>`，看着是非贪婪，
        # 实际因为多了一个 </div> 而一路吃到容器结尾，把 14 行工作包全删了，
        # 于是报"存放处列出 0 个"。前缀匹配简单，也不会因为 HTML 结构微调就碎掉。
        listed = [x for x in re.findall(r'class="wp-fname"[^>]*>([^<]+)</a>', page)
                  if not x.startswith("📘")]
        if sorted(listed) != on_disk:
            fails.append("C9 工作包目录里有 %d 个文件 %s，但存放处列出的是 %d 个 %s"
                         "——跑：python docs/_build_workpackage_index.py（或 _build_all.py）"
                         % (len(on_disk), on_disk, len(listed), sorted(listed)))
        else:
            notes.append("C9 样板显示与 dq_ready_state.json、工作包目录三者一致"
                         "（%d 块 / %d 份文件）" % (len(st["blocks"]), len(on_disk)))


# ══ C10：假装你是那个开发 AI —— 只看这一份，够不够动手 ═══════════════
# 2026-09-08 用户质问：「你假设过你是个开发的ai，可以直接下载下来马上就可以
# 开发吗？你这些都没有做」。当时第一版工作包只给了一个指向总账的**链接**，
# 让 AI 自己跳去 1310 行里找接口和建表语句——一个 AI 一边看两份文件就会漏。
#
# 所以这一项模拟"只拿到这一个文件"的处境，逐条查它有没有动手所需的东西。
# 不是查"文件存在"，是查"文件里到底有没有那几样"。
WP_MUST_HAVE = [
    # ── 2026-09-09 补的四条 ──────────────────────────────────────────
    # 用户问「是不是可以交给 opencode 了」，我按自己定的规矩没去查文档、
    # 而是假装成 opencode 只拿着一份工作包从零走一遍——立刻发现连
    # **去哪个仓库、切哪个分支、怎么编译、包名叫什么** 都没写。
    # 这四样是它第一分钟就要用的，而前面 11 条检查一条都没覆盖到，
    # 因为那 11 条查的是"资料全不全"，不是"拿着它能不能动手"。
    ("仓库地址", r"git clone https?://\S+"),
    ("从哪个分支切 + 分支怎么命名", r"git checkout -b wp/"),
    ("怎么编译", r"mvn -B verify"),
    ("Java 包名", r"com\.matbox\.devquality"),
    # ── 原有 ──────────────────────────────────────────────────────
    ("要做什么（目标/Scope）", r"\*\*目标\*\*|## 1 · 你要做什么"),
    ("能改哪 / 不能碰哪", r"backend/modules/dev-quality"),
    ("七类施工面齐", r"### Tests/Observability"),
    ("验收标准", r"\| DQ-T\d{3} \|"),
    # 2026-09-09：这是「开发前 ↔ 开发中」唯一的接缝。
    # 工作包一直给了 DQ-T 编号，却从没要求把编号写进测试方法名；
    # 少了这一步，CI 的 surefire XML 里没有编号，就没有任何东西能回答
    # 「13 个功能哪几个做完了」。事后靠人去对 24 条 × 13 个功能，
    # 就是业界公认「手工追溯矩阵 90 天内必死」的那条路。
    ("测试方法名要带 TestID（追溯的接缝）", r"### 4\.1 测试方法名必须带 TestID"),
    # 规则要**事先告诉它**，不能事后拿来抓人。
    # _check_test_integrity.py 会按 diff 自动判这三条，所以三条必须先印在包里。
    ("测试上的三条红线（事先说清，不是事后抓）", r"### 4\.2 测试上的三条红线"),
    ("技术栈写死", r"PostgreSQL"),
    ("鉴权与多租户", r"### 5\.6"),
    ("错误码与重试", r"### 5\.7"),
    ("代码放哪（目录）", r"### 5\.3"),
    ("架构禁令随包附带", r"架构原则第58条"),
    ("交付清单", r"AcceptanceRunID"),
    ("本地环境指引", r"§4\.18|怎么起本地环境"),
]
# 适配器没有自己的端点和表（由 F-DQ-001 调度、F-DQ-002 归一化），
# 它们要照着实现的是 Provider Adapter 接口规范——这一条对它们才是硬要求。
WP_ADAPTERS = {"F-DQ-003", "F-DQ-004", "F-DQ-005", "F-DQ-006",
               "F-DQ-007", "F-DQ-008", "F-DQ-012"}


def check_workpackages_buildable():
    wp = os.path.join(DOCS, "工作包", "DQ")
    if not os.path.isdir(wp):
        warns.append("C10 找不到工作包目录，本项跳过")
        return
    files = sorted(f for f in os.listdir(wp) if re.match(r"^F-DQ-\d{3}\.md$", f))
    if not files:
        warns.append("C10 工作包目录里没有 F-DQ-0NN.md，本项跳过")
        return
    bad = 0
    for f in files:
        fid = f[:-3]
        body = read(os.path.join(wp, f))
        missing = [name for name, pat in WP_MUST_HAVE if not re.search(pat, body)]
        if fid in WP_ADAPTERS and "Provider Adapter 接口规范" not in body:
            missing.append("Adapter 接口规范（它没有自己的端点和表，只能照这个写）")
        if fid not in WP_ADAPTERS:
            if not re.search(r"\| (GET|POST|PUT|DELETE) \| `/dq", body):
                missing.append("API 端点")

        # §4.1 的示例必须用**这一份自己认领的**编号。
        # 2026-09-09 差点埋进去的坑：13 份共用同一段模板，示例方法名一度写死成
        # F-DQ-001 的场景，别的功能照抄就是一个跟自己验收标准无关的名字，
        # 而 AI 是会照抄的。所以不只查「有没有这一节」，还要查「例子对不对得上」。
        owned = set(re.findall(r"\| (DQ-T\d{3}) \|", body))
        shown = set("DQ-T" + n for n in re.findall(r"\bdqT(\d{3})_", body))
        stray = shown - owned
        if owned and stray:
            missing.append("§4.1 示例用了不属于自己的编号 %s（自己认领的是 %s）"
                           % ("、".join(sorted(stray)), "、".join(sorted(owned))))
        if missing:
            bad += 1
            fails.append("C10 %s 只看这一份没法动手，缺：%s"
                         % (fid, "、".join(missing)))
    if not bad:
        notes.append("C10 %d 份工作包逐份自检通过——"
                     "只看其中任意一份就能动手（要做什么/边界/施工面/验收/"
                     "**测试要带TestID**/技术栈/鉴权/错误码/目录/接口或Adapter契约/"
                     "禁令/交付/环境）" % len(files))


def main():
    for fn in (check_flow_embeds, check_retired_names, check_links,
               check_module_names, check_gate_ids, check_feature_ids,
               check_handoff_packages, check_generated_docs,
               check_page_matches_state, check_workpackages_buildable,
               check_workflows):
        fn()

    print("=" * 72)
    print("Matbox 文档一致性检查")
    print("=" * 72)

    if name_rows:
        print("\nC4 模块名对照表（信息，不判故障——不一致的地方肉眼挑）：")
        for k, c, t, h in name_rows:
            print("   %-15s 画布=%-26s title=%-28s h1=%s" % (k, c, t, h))

    if exempted:
        print()
        print('已豁免 %d 处（写着旧名是对的，理由如下——豁免不藏着）：' % len(exempted))
        for e in sorted(exempted):
            print('   ' + e)
    if notes:
        print("\nℹ️  覆盖范围说明：")
        for n in notes:
            print("   " + n)

    if warns:
        print("\n⚠️  提醒 %d 项（不阻塞，但值得看一眼）：" % len(warns))
        for w in warns:
            print("   " + w)

    if fails:
        print("\n❌ FAIL %d 项 —— 这是残留，修完再提交：" % len(fails))
        for f in fails:
            print("   " + f)
        print()
        return 1

    print("\n✅ 硬性检查通过：C1 内嵌副本新鲜度 / C2 退役写法(含docx) / "
          "C3 断链 / C4 流程图存在性 / C5 Gate编号")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
