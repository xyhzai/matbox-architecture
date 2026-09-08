# -*- coding: utf-8 -*-
"""
AC-LOC-008 / AC-LOC-009 真实 resolver 级测试 —— 关闭 G-LOC-MATBOX-004。

    python docs/全球多语言与本地化/matbox_ac_loc_008_009_real_test.py

═══ 为什么有这个文件 ═══

交接包自带的 poc.py 声称 12/12 PASS，但其中第 10、11 条**不测任何被测代码**：

    # 第10条：先自己写一个 dict 字面量，再断言这个 dict 等于它自己
    user_profile = {"language": "en", "locale": "en-IN", "currency": "INR", ...}
    check("AC08 language/locale separated",
          user_profile["language"] == "en" and user_profile["locale"] == "en-IN" ...)

    # 第11条：断言 ("en" or "vi-VN") == "en" —— 这是 Python 的 or 语义，不是被测代码
    ai_default = conversation_override or preferred
    check("AC09 AI conversation override", ai_default == "en")

把这两条原样复制到零依赖空环境（不 import 任何模块、不定义任何被测函数）
仍然 PASS。它们分别声称覆盖 AC-LOC-008 与 AC-LOC-009，实际一行 resolver
都没跑过。

本文件补上真正调用 `resolve_language()` / `canonicalize()` 的版本。

**交接包不改**：其 MANIFEST 已冻结 SHA-256，本文件放在包外，只 import 它。

═══ 怎么证明这两条测试不是又一个同义反复 ═══

按架构原则第74条：要检验一个测试是不是真的，就把被测代码拿掉，看它还通不通过。
本文件末尾的 `prove_tests_are_real()` 会把被测函数替换成坏实现，确认两条测试
都会因此失败——不会失败的测试不算测试。
"""

import io
import os
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
POC = os.path.join(HERE, "Matbox_全球多语言与本地化_交接包_V1.0", "poc.py")


def load_poc():
    spec = importlib.util.spec_from_file_location("loc_poc", POC)
    mod = importlib.util.module_from_spec(spec)
    # 必须先登记进 sys.modules 再执行：poc.py 里用了 @dataclass，
    # dataclasses 会反查 cls.__module__ 对应的模块，查不到就报
    # AttributeError: 'NoneType' object has no attribute '__dict__'
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))


# ══ AC-LOC-008：Language 与 Locale 必须可独立共存 ══════════════════════
# 真实场景：一个在印度工作的用户，界面语言要英文（en），但地区是印度
# （en-IN）——货币 INR、时区 Asia/Kolkata、日期 dd/MM/yyyy。
# 「可独立共存」的含义就是：把 language 归一成 en 的同时，locale 里的
# 「印度」不能丢。
def test_ac_loc_008(poc):
    # 语言维度：en-IN 的 UI 语言就该归一到 en —— 这一步是对的
    lang = poc.resolve_language(saved_user="en-IN")
    check("AC-LOC-008 (a) 语言维度：en-IN 的界面语言归一为 en",
          lang == "en", "实得 %r" % lang)

    # 地区维度：locale 必须保住 en-IN，不能被抹平成 en
    loc = poc.canonicalize("en-IN")
    check("AC-LOC-008 (b) 地区维度：en-IN 作为 locale 必须保住印度信息",
          loc == "en-IN",
          "实得 %r —— canonicalize() 把地区抹平了，INR/Asia/Kolkata 无从推导" % loc)

    # 同一个函数同时承担两种归一，必然二选一——这正是 G-LOC-MATBOX-005 的内容
    check("AC-LOC-008 (c) language 归一与 locale 归一必须是两个独立函数",
          poc.canonicalize("en-IN") != poc.resolve_language(saved_user="en-IN")
          or loc == "en-IN",
          "两者都走 canonicalize()，结果相同（都是 %r），地区维度无处存放" % loc)


# ══ AC-LOC-009：AI 会话内覆盖不改全局偏好 ══════════════════════════════
# 真实场景：用户的长期偏好是越南语；某次对话里临时要求用英文回答。
# 「不改全局偏好」的含义是：这次会话用英文，但会话结束后，再解析一次
# 仍然必须回到越南语——临时覆盖不能污染保存的偏好。
def test_ac_loc_009(poc):
    saved = "vi-VN"

    in_conversation = poc.resolve_language(explicit_choice="en", saved_user=saved)
    check("AC-LOC-009 (a) 会话内的显式覆盖生效",
          in_conversation == "en", "实得 %r" % in_conversation)

    after_conversation = poc.resolve_language(saved_user=saved)
    check("AC-LOC-009 (b) 会话结束后回到保存的偏好，覆盖没有污染它",
          after_conversation == "vi-VN", "实得 %r" % after_conversation)

    # 优先级链本身：显式 > 保存 > 租户 > 浏览器 > 市场 > 平台。
    # 如果哪天有人把顺序改错（比如让 tenant 盖过 explicit），下面这条会失败。
    mixed = poc.resolve_language(explicit_choice="en", saved_user="vi-VN",
                                 tenant_default="zh-CN", browser="zh-CN")
    check("AC-LOC-009 (c) 显式选择的优先级高于保存/租户/浏览器",
          mixed == "en", "实得 %r" % mixed)


# ══ 证明这两条测试是真的（架构原则第74条） ═════════════════════════════
def prove_tests_are_real(poc):
    """把被测函数换成坏实现，确认测试会因此失败。不会失败的测试不算测试。"""
    proofs = []

    real_resolve = poc.resolve_language
    poc.resolve_language = lambda **kw: "zh-CN"          # 坏实现：永远返回中文
    before = len(results)
    test_ac_loc_009(poc)
    broke = any(not ok for _, ok, _ in results[before:])
    del results[before:]
    poc.resolve_language = real_resolve
    proofs.append(("AC-LOC-009 在 resolve_language 被换坏后会失败", broke))

    real_canon = poc.canonicalize
    poc.canonicalize = lambda x: x                        # 坏实现：完全不归一
    before = len(results)
    test_ac_loc_008(poc)
    broke = any(not ok for _, ok, _ in results[before:])
    del results[before:]
    poc.canonicalize = real_canon
    proofs.append(("AC-LOC-008 在 canonicalize 被换坏后会失败", broke))

    return proofs


def main():
    if not os.path.exists(POC):
        print("找不到交接包里的 poc.py：%s" % POC)
        print("交接包必须在仓库里——这正是 _check_docs_consistency.py 的 C7 在盯的事。")
        return 2

    poc = load_poc()
    test_ac_loc_008(poc)
    test_ac_loc_009(poc)

    print("=" * 70)
    print("AC-LOC-008 / AC-LOC-009 真实 resolver 级测试")
    print("=" * 70)
    passed = 0
    for name, ok, detail in results:
        print("%s | %s%s" % ("PASS" if ok else "FAIL", name,
                             ("  ← " + detail) if detail else ""))
        passed += ok
    print()
    print("结果：%d/%d PASS" % (passed, len(results)))

    print()
    print("— 这两条测试本身是不是真的（把被测代码换坏，看它会不会失败）—")
    for what, broke in prove_tests_are_real(poc):
        print("  %s %s" % ("✅" if broke else "❌ 换坏了也不失败，是同义反复！", what))

    if passed != len(results):
        print()
        print("上面的 FAIL 不是本文件写错了，是被测代码确实做不到——")
        print("即 G-LOC-MATBOX-005 记录的那件事：language 归一与 locale 归一")
        print("共用同一个 canonicalize()，地区信息必然被抹平。")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
