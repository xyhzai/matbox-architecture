# -*- coding: utf-8 -*-
"""
开发后 D1/D4：从 CI 的测试结果反推「这个包到底做完没做完」。

    python docs/_check_delivery.py --reports <surefire-reports目录> --wp F-DQ-003

═══ 为什么有这个文件（2026-09-09）═══

《Matbox 开发包标准 V2.0》第 7 节写着：

    「做完了」的唯一定义：D1~D5 全绿。**任何一方说做完了都不作数。**

在这个文件出现之前，D1（每条验收标准都有测试且通过）和 D4（无覆盖缺口）
都是 ⚪「标准已定、检查未建」——也就是说「做完了」当时**根本没有判据**，
只能听实现方自述。而实测数据是：编码模型有 12% 的情况会主动破坏
那些用来发现它自己行为不端的代码。听自述是不行的。

═══ 为什么读 surefire XML，不读别的 ═══

因为 `<testcase name="dqT007_...">` 里的方法名是**唯一不依赖任何插件、
任何配置就能从 CI 读回来的载体**。JUnit 5 的 `@Tag` 不会写进 XML
（Surefire 至今不导出），所以标准 M1 要求编号写进方法名，不是写进注解。

═══ 判什么 ═══

  D1  这个包认领的每条验收标准，都至少有一个测试，且**全部通过**
      —— 有测试但挂了、跳过了（skipped），都不算通过
  D4  正向查覆盖缺口：认领了却一个测试都没有的编号，逐条列出

  另外报告（不判故障，供人看）：
      · 跑了多少测试、失败/跳过各多少
      · 出现了但不归本包的编号（孤儿由 _check_test_integrity.py 的 T0/T1 判）
"""

import argparse
import glob
import io
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

DOCS = os.path.dirname(os.path.abspath(__file__))

# 2026-09-10 假装成 opencode 拿 LOC-F001 走一遍撞出来的：
# 这里原来写死 dq_test_ownership.json，方法名反推也写死 "DQ-T" 前缀。
#
# **实测**（跑的是 HEAD 里的旧版本，不是推测），两种错法：
#   ① python _check_delivery.py --wp LOC-F001
#      → 归属表里没有 LOC-F001，有的是：F-DQ-001…F-DQ-013   退出码 1
#      这道判「做完没做完」的关，对第二个模块**根本跑不起来**。
#   ② 拿 LOC 的 surefire 报告配 DQ 的包名跑：
#      locT001_ok 被正则读成 DQ-T001，打印「✅ DQ-T001 通过 1 个测试」
#      → **拿别人模块的测试给自己记了一条绿**。这一条是静默的。
#
# 现在按模块登记表驱动：归属表、编号前缀、方法名前缀都从 modules.json 来。
# 同一份输入，修复后正确判成「❌ DQ-T001 没有任何测试」。
# 反向测试见 _negtest_devphase.py。
MODULES = json.load(io.open(os.path.join(DOCS, "modules.json"),
                            encoding="utf-8"))["modules"]


def module_of(wp):
    """从工作包编号反查它属于哪个模块。F-DQ-003 → DQ；LOC-F001 → LOC。"""
    for key, cfg in MODULES.items():
        if wp.startswith(cfg.get("feature_prefix", "F-%s-" % key)):
            return key, cfg
    raise SystemExit("认不出 %s 属于哪个模块——modules.json 里没有匹配的 feature_prefix。"
                     "**认不出就停，不许猜**：猜错会把别人的测试算到你头上。" % wp)


def ownership_path(key):
    return os.path.join(DOCS, "%s_test_ownership.json" % key.lower())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reports", required=True, help="surefire-reports 目录")
    ap.add_argument("--wp", required=True, help="哪份工作包，例 F-DQ-003")
    a = ap.parse_args()

    key, cfg = module_of(a.wp)
    tpre = cfg.get("test_prefix", "%s-T" % key)
    # 方法名前缀：DQ-T → dqT，AC-LOC- → locT（去掉非字母、取模块 key 小写）
    mpre = key.lower() + "T"
    OWNERSHIP = ownership_path(key)
    if not os.path.exists(OWNERSHIP):
        raise SystemExit("找不到 %s —— 先生成该模块的归属表" % OWNERSHIP)
    doc = json.load(io.open(OWNERSHIP, encoding="utf-8"))
    own = doc["ownership"]
    if a.wp not in own:
        raise SystemExit("归属表里没有 %s，有的是：%s" % (a.wp, "、".join(sorted(own))))
    mine = set(own[a.wp])

    xmls = sorted(glob.glob(os.path.join(a.reports, "**", "TEST-*.xml"), recursive=True))
    if not xmls:
        # 没有报告 ≠ 通过。这一条必须挡住，否则「CI 没跑」会被当成「没问题」。
        raise SystemExit("在 %s 下找不到 TEST-*.xml —— CI 没跑，或者路径给错了。\n"
                         "**没有测试结果不等于通过**，本检查判为不通过。" % a.reports)

    # 收集：编号 -> {通过数, 失败数, 跳过数, 方法名}
    stat = {}
    total = fails = skips = 0
    for x in xmls:
        try:
            root = ET.parse(x).getroot()
        except Exception as e:                                   # noqa
            raise SystemExit("解析不了 %s：%s —— 报告坏了，不能当成通过" % (x, e))
        for tc in root.iter("testcase"):
            name = tc.get("name") or ""
            m = re.match(r"(%s)(\d{3})_" % re.escape(mpre), name)
            total += 1
            bad = tc.find("failure") is not None or tc.find("error") is not None
            skip = tc.find("skipped") is not None
            fails += 1 if bad else 0
            skips += 1 if skip else 0
            if not m:
                continue
            tid = tpre + m.group(2)
            s = stat.setdefault(tid, {"pass": 0, "fail": 0, "skip": 0, "names": []})
            s["names"].append(name)
            s["fail" if bad else ("skip" if skip else "pass")] += 1

    print("=" * 74)
    print("开发后 D1/D4 · %s" % a.wp)
    print("=" * 74)
    print("读到 %d 份报告，共 %d 个测试（失败 %d，跳过 %d）" % (len(xmls), total, fails, skips))
    print("本包认领：%s" % "、".join(sorted(mine)))
    print()

    bad_rows, gap = [], []
    for tid in sorted(mine):
        s = stat.get(tid)
        if not s:
            gap.append(tid)
            print("  ❌ %-9s 没有任何测试" % tid)
            continue
        if s["fail"] or s["skip"]:
            bad_rows.append(tid)
            print("  ❌ %-9s 通过 %d / 失败 %d / 跳过 %d   %s"
                  % (tid, s["pass"], s["fail"], s["skip"], "、".join(s["names"][:2])))
        else:
            print("  ✅ %-9s 通过 %d 个测试" % (tid, s["pass"]))

    extra = sorted(set(stat) - mine)
    print()
    if extra:
        print("  （出现了不归本包的编号：%s —— 孤儿与越权由 _check_test_integrity.py 判）"
              % "、".join(extra))
        print()

    ok = not gap and not bad_rows
    print("  D4 覆盖缺口：%s" % ("无" if not gap else "%d 条没有测试 → %s" % (len(gap), "、".join(gap))))
    print("  D1 全部通过：%s" % ("是" if not bad_rows else "否 → %s" % "、".join(bad_rows)))
    print()
    if ok:
        print("✅ D1 + D4 通过：认领的 %d 条验收标准，条条有测试且全绿" % len(mine))
        print("   （这只说明这两条过了。「做完了」还要 D2/D3/D5 一起绿。）")
        return 0
    print("❌ 未做完。**不是实现方说了算，是这张表说了算。**")
    return 1


if __name__ == "__main__":
    sys.exit(main())
