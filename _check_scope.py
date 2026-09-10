# -*- coding: utf-8 -*-
"""
M5：查一次改动有没有越出这个包被允许改的范围。

    python docs/_check_scope.py --repo <代码仓库> --base <ref> --head <ref> --mod DQ

═══ 为什么有这个文件（2026-09-09）═══

《Matbox 开发包标准 V2.0》开发中 M5 此前是 ⚪「标准已定、检查未建」。
标准第 0.5.2 条写着：**未建的检查不许显示成绿**。所以要么建出来，要么如实标未建。
这个文件把 M5 建出来。

判据来自 `<mod>_protected_scope.yml`，那份文件里的目录名全部来自源文档
（专项01 §22 目录树），不是谁编的——改动范围这件事必须有源头，
否则"越界"的定义就成了随口说的。

═══ 判什么 ═══

  S1  改的文件必须落在 allowed_root / frontend_root 里
  S2  测试目录（src/test/**）视同允许——测试是必须写的
  S3  白名单之外的任何改动，逐个列出来，**不合并成一句"有越界"**
      （合并成一句话，人就得自己再去翻 diff，等于没报）

═══ 一条边界 ═══

这个检查只判**路径**。"import 了不该 import 的模块"（DEP-1/2/3 那三条
依赖方向铁律）判不了——那要解析 Java import，属于 F-DQ-007
Architecture Guard 的活，不在这里重复实现。**判不了就不假装判了。**
"""

import argparse
import fnmatch
import io
import json
import os
import re
import subprocess
import sys

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

DOCS = os.path.dirname(os.path.abspath(__file__))


def scope_globs(mod_key):
    """从 <mod>_protected_scope.yml 里读出允许改的路径通配。
    不引 yaml 依赖——只取 allowed_root / frontend_root 两行，正则足够，
    少一个依赖就少一个"本机没装所以跳过"的假绿来源。"""
    p = os.path.join(DOCS, "%s_protected_scope.yml" % mod_key.lower())
    if not os.path.exists(p):
        return None, p
    body = io.open(p, encoding="utf-8", errors="replace").read()
    body = re.sub(r"^\s*#.*$", "", body, flags=re.M)
    globs = re.findall(r"^\s*\w*root\w*\s*:\s*[\"']([^\"'\n]+)[\"']", body, re.M)
    return globs, p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--head", required=True)
    ap.add_argument("--mod", required=True, help="模块 key，例 DQ")
    a = ap.parse_args()

    globs, path = scope_globs(a.mod)
    if globs is None:
        raise SystemExit("找不到 %s —— 这个模块还没有机器可读的改动范围，"
                         "按标准 P19 它连开发前都过不了" % path)
    if not globs:
        raise SystemExit("%s 里没有 *root 通配 —— 范围是空的，等于没定义" % path)

    r = subprocess.run(["git", "diff", "--name-only", "%s..%s" % (a.base, a.head)],
                       cwd=a.repo, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise SystemExit("git diff 失败：%s" % r.stderr.strip()[:200])
    changed = [x for x in r.stdout.split("\n") if x.strip()]

    print("=" * 74)
    print("M5 改动范围检查 · %s（%s..%s）" % (a.mod, a.base[:12], a.head[:12]))
    print("=" * 74)
    print("允许改的范围（来自 %s）：" % os.path.basename(path))
    for g in globs:
        print("   %s" % g)
    print("   src/test/**  （测试是必须写的，视同允许）")
    print()

    out = []
    for f in changed:
        ok = any(fnmatch.fnmatch(f, g) for g in globs) or "/src/test/" in "/" + f
        out.append((f, ok))

    bad = [f for f, ok in out if not ok]
    print("本次改动 %d 个文件，其中 %d 个在范围内" % (len(out), len(out) - len(bad)))
    print()
    if bad:
        # 逐个列出来。合并成一句"有越界"，人还得自己去翻 diff，等于没报。
        print("❌ %d 个文件越出允许范围：" % len(bad))
        for f in bad:
            print("   %s" % f)
        print()
        print("越界不等于做错了——可能是这个包确实需要动公共文件。")
        print("但那属于**高风险公共文件**，按 QUEUE-F008 必须转人工审核，")
        print("不能由实现方自己决定。请在交付说明里写清为什么必须动。")
        return 1

    print("✅ 全部改动都在允许范围内")
    print()
    print("⚠️ 本检查只判**路径**。「import 了不该 import 的模块」判不了——")
    print("   那是 F-DQ-007 Architecture Guard 的活，这里不假装判了。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
