# -*- coding: utf-8 -*-
"""开工前，**在你自己那台机器上**跑一遍：第一步能不能动。

    python _check_toolchain.py

═══ 为什么有这个文件（2026-09-11）═══

opencode 拿到材料、核完戳、clone 成功、基线 MATCH，然后卡在开工五步第 ④ 步：
`mvn -B verify` —— 它那边 **java 无、mvn 无、postgres 无、docker 无、
sudo 免密不可用**。而 `_check_delivery.py` 读的是 Surefire XML，
XML 要 mvn 才有，所以**交付判定链的起点就断了**。

原话：「33 条全绿 + 材料齐备 + 基线 MATCH + CI 绿，实现方仍然在第 5 步动不了。」

**这不是材料缺口，是判据的作用域盲区。**
那 33 条全部是从**材料侧**视角查的 —— 查材料齐不齐、仓库有没有、CI 绿不绿。
**没有一条查「实现方那边能不能执行第一步」。** 记为假绿 F23。

判据不能只查自己够得着的那一侧。够不着的那一侧，就把判据**送过去让对方跑**，
这就是这个文件：它由材料侧出，在实现方那侧执行，判的是实现方的执行环境。

它不装任何东西，不改任何东西，只看和报。
"""

import os
import re
import socket
import subprocess
import sys

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")


def which(cmd, args, want=None):
    """跑一下拿版本。拿不到就是没有 —— 不猜、不看 PATH 字符串。"""
    try:
        r = subprocess.run([cmd] + args, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    out = ((r.stdout or "") + (r.stderr or "")).strip()
    return out.split("\n")[0] if out else None


def java_major(v):
    m = re.search(r'"?(\d+)(?:\.(\d+))?', v or "")
    if not m:
        return None
    a, b = int(m.group(1)), int(m.group(2) or 0)
    return b if a == 1 else a          # 1.8 → 8；17.x → 17


def db_reachable(url):
    """只做 TCP 连通，不带驱动、不连真库 —— 这一步只回答「有没有人在那个端口上」。"""
    m = re.search(r"//([^/:]+):(\d+)", url or "")
    if not m:
        return None, "MATBOX_DB_URL 没设，或者不是 jdbc:postgresql://host:port/db 的样子"
    host, port = m.group(1), int(m.group(2))
    s = socket.socket()
    s.settimeout(5)
    try:
        s.connect((host, port))
        return True, "%s:%d 通" % (host, port)
    except OSError as e:
        return False, "%s:%d 连不上（%s）" % (host, port, e.__class__.__name__)
    finally:
        s.close()


# 每一条都写清：**卡住的是哪一步**。只说"缺 X"，人不知道它挡了什么。
NEEDS = [
    ("git", ["--version"], None, "①", "clone 仓库、切分支",  True),
    ("java", ["-version"], 17, "④", "编译与跑测试",          True),
    ("mvn", ["-v"], None, "④", "`mvn -B verify` 本身",       True),
    ("gh", ["--version"], None, "⑤", "开 PR（也可以在网页上开）", False),
]


def main():
    print("=" * 70)
    print("开工前环境自检 —— 判的是**你这一侧**能不能执行开工五步")
    print("=" * 70)
    print()
    missing_hard = []
    for cmd, args, minver, step, why, hard in NEEDS:
        v = which(cmd, args)
        if v is None:
            print("  %s %-6s 没有        —— 卡住第 %s 步：%s"
                  % ("❌" if hard else "⚪", cmd, step, why))
            if hard:
                missing_hard.append(cmd)
            continue
        if minver:
            mj = java_major(v)
            if mj is None or mj < minver:
                print("  ❌ %-6s 版本不够（要 %d+，现在是 %s）—— 卡住第 %s 步"
                      % (cmd, minver, mj, step))
                missing_hard.append("%s>=%d" % (cmd, minver))
                continue
        print("  ✅ %-6s %s" % (cmd, v[:52]))

    url = os.environ.get("MATBOX_DB_URL", "")
    ok, msg = db_reachable(url)
    if ok:
        print("  ✅ 数据库 %s" % msg)
    else:
        print("  ❌ 数据库 %s" % msg)
        print("       —— 卡住第 ④ 步：契约/Schema 测试是 @SpringBootTest，"
              "启动时就要连真库，**没有库不会跳过，是直接失败**")
        missing_hard.append("postgresql")

    print()
    print("=" * 70)
    if not missing_hard:
        print("✅ 开工五步在你这台机器上跑得动。")
        return 0
    print("❌ 缺这些，第一步就动不了：%s" % "、".join(missing_hard))
    print()
    print("**别硬跑，也别绕过。** 照材料里的做法：")
    print("  · java / mvn：装到自己家目录即可，不需要 sudo")
    print("  · postgresql：CI 用的是 `services: postgres:16`。本地怎么起，"
          "由用户定（容器 / 装本机 / 或者接受真库测试只在 CI 跑）——")
    print("    **这条不该实现方自己决定**，它会改变整趟的节奏。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
