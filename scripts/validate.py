#!/usr/bin/env python3
"""validate.py — hands-on-loop 技术跑通/学习计划七维校验器

输入: 技术跑通/学习计划 JSON（schema 见 tests/sample_good.json）
  {
    "loop": {
      "target": "新技术名",
      "timebox_minutes": 10,              // 时间盒 ≤10
      "single_output": "一条跑通的接口",    // 单一明确产出（非空、非"研究/了解"类）
      "objective_criteria": "返回 200 且 body 含 token 字段",  // 客观判据
      "prereq_ready": true                // 预置环境/样例/Token 就绪
    },
    "cookbook": {
      "kept": true,                        // 跑通后留三件套
      "env_doc": true,                     // 1. 预配置环境说明或镜像
      "minimal_code": true,                // 2. 可复制最小代码
      "known_input_sample": true,          // 3. 已知可跑的输入样例
      "cookbook_count": 12                 // 已攒份数（≥1 才谈复用；≥10 = 自己的工坊）
    },
    "handoff": {
      "needed": true,                      // 跨天/跨人/跨工具？
      "current_progress": "已完成环境+最小代码，卡在样例输出偏差",
      "failed_paths": ["方案A：改依赖版本→失败原因：API 不兼容"],
      "next_single_action": "把样例输入第 3 行改成 JSON 格式后重跑",
      "next_action_criteria": "输出与预期一致（exit 0）",
      "constraints": "Token 剩 500 次；今晚 22:00 前；不动鉴权模块"
    },
    "roles": {
      "task_needs_split": true,            // 大任务？（进决策/事实密集/长文/重复交付 任一）
      "roles_assigned": ["检索", "执行", "校验", "呈现"],
      "verifier_independent_context": true, // 校验独立上下文
      "verifier_only_list_not_edit": true,  // 校验者只出差异清单不改稿
      "max_rounds": 2                       // 校验轮次 ≤2
    },
    "vibe_coding": {
      "picked_pain_point": "周报生成",
      "high_freq": true,
      "low_risk": true,
      "internal_use": true,
      "domain_expert_drives": true         // 最懂场景的人动手（不是写需求等排期）
    },
    "artifacts": {
      "verifiable_output": "作品页新增卡片：周报生成器截图+可运行链接",
      "verifiable_in_30s": true,           // 30 秒可验证"这是你做的且能跑"
      "digital_profile_updated": true      // 数字名片/能力简介已更新（连接资产化）
    }
  }

七维校验（任一 FAIL → exit 1）：
  D1 最小闭环: timebox_minutes 为正且 ≤10；single_output 非空且不含"研究/了解/调研/学习"
     类词（这些不是产出）；objective_criteria 非空（客观判据）；prereq_ready=true
  D2 Cookbook 三件套: kept=true 且 env_doc/minimal_code/known_input_sample 全 true
     （缺一=一次性 demo，闭环未完成）；cookbook_count 为非负整数
  D3 handoff 四要素: needed=true 时 current_progress/next_single_action/
     next_action_criteria/constraints 全非空 且 failed_paths 非空（一条都没有=可疑）；
     next_single_action 不得含"优化/看看/研究"方向词（方向不是唯一动作）；
     needed=false 时豁免
  D4 4 角色分工: task_needs_split=true 时 roles_assigned 须含全部四角色
     且 verifier_independent_context=true 且 verifier_only_list_not_edit=true
     且 max_rounds≤2；task_needs_split=false 时豁免（小任务不强制拆）
  D5 Vibe Coding 三条件: high_freq/low_risk/internal_use 全 true
     （缺一不选）且 picked_pain_point 非空 且 domain_expert_drives=true
  D6 产出可展示: verifiable_output 非空 且 verifiable_in_30s=true
     （没有可验证产出物=没做完）
  D7 连接资产化: digital_profile_updated=true（数字名片/能力简介随时可发）

退出码：0=通过 / 1=有缺陷 / 2=文件/格式错误
"""
import json
import sys

NON_OUTPUT_WORDS = ("研究", "了解", "调研", "学习", "熟悉", "看看")
DIRECTION_WORDS = ("优化一下", "研究", "考虑", "评估一下", "看看")
REQUIRED_ROLES = {"检索", "执行", "校验", "呈现"}


def fail(checks, code, msg):
    checks.append(("FAIL", code, msg))


def ok(checks, code, msg):
    checks.append(("OK", code, msg))


def is_nonempty_str(v):
    return isinstance(v, str) and v.strip() != ""


def validate(plan):
    checks = []

    # D1 最小闭环
    lp = plan.get("loop") or {}
    tb = lp.get("timebox_minutes")
    if not isinstance(tb, (int, float)) or tb <= 0:
        fail(checks, "D1", f"timebox_minutes={tb!r}——时间盒必须 >0（超时=门槛缺陷记录，不是无限重试）")
    elif tb > 10:
        fail(checks, "D1", f"timebox_minutes={tb}——超过 10 分钟说明产出定义太大或环境没预置")
    else:
        so = lp.get("single_output")
        if not is_nonempty_str(so):
            fail(checks, "D1", "single_output 为空——'研究一下'不是闭环，须单一明确产出")
        elif any(w in so for w in NON_OUTPUT_WORDS):
            fail(checks, "D1", f"single_output=' {so}' 含过程词——产出物必须是可打开/可执行/可判定的东西")
        elif not is_nonempty_str(lp.get("objective_criteria")):
            fail(checks, "D1", "objective_criteria 为空——跑没跑通需要客观判据，不是'感觉通了'")
        elif lp.get("prereq_ready") is not True:
            fail(checks, "D1", "prereq_ready=false——预置环境/样例/Token 没就绪，门槛在开始前配置，先清掉再计时")
        else:
            ok(checks, "D1", f"最小闭环成立（{tb} 分钟，单一产出: {so}）")

    # D2 Cookbook 三件套
    cb = plan.get("cookbook") or {}
    missing = [k for k in ("env_doc", "minimal_code", "known_input_sample")
               if cb.get(k) is not True]
    cnt = cb.get("cookbook_count")
    if cb.get("kept") is not True:
        fail(checks, "D2", "kept=false——跑通即沉淀，不留三件套=一次性 demo，闭环未完成")
    elif missing:
        fail(checks, "D2", f"三件套缺: {missing}——缺一=下次还是两小时不是 10 分钟")
    elif not isinstance(cnt, int) or cnt < 0:
        fail(checks, "D2", f"cookbook_count={cnt!r}——须为非负整数")
    else:
        note = "，≥10 份=你自己的工坊" if cnt >= 10 else f"（距自己的工坊还差 {10 - cnt} 份）"
        ok(checks, "D2", f"Cookbook 三件套齐全（已攒 {cnt} 份{note}）")

    # D3 handoff 四要素
    hd = plan.get("handoff") or {}
    if hd.get("needed") is not True:
        ok(checks, "D3", "无跨天/跨人/跨工具交接，D3 豁免")
    else:
        missing_hd = [k for k in ("current_progress", "next_single_action",
                                  "next_action_criteria", "constraints")
                      if not is_nonempty_str(hd.get(k))]
        fps = hd.get("failed_paths") or []
        nsa = hd.get("next_single_action") or ""
        if missing_hd:
            fail(checks, "D3", f"handoff 缺: {missing_hd}——缺一=接的人要重讲一遍")
        elif not any(is_nonempty_str(x) for x in fps):
            fail(checks, "D3", "failed_paths 为空——一条失败路径都没有=今天什么都没卡住（可疑），或没记录")
        elif any(w in nsa for w in DIRECTION_WORDS):
            fail(checks, "D3", f"next_single_action='{nsa}' 是方向不是唯一动作——接的人还要规划，规划是你的责任")
        else:
            ok(checks, "D3", f"handoff 四要素齐全（{len(fps)} 条失败路径，下一步: {nsa[:20]}…）")

    # D4 4 角色分工
    rl = plan.get("roles") or {}
    if rl.get("task_needs_split") is not True:
        ok(checks, "D4", "小任务不强制拆分（后果/密度未达拆分线），D4 豁免")
    else:
        assigned = set(rl.get("roles_assigned") or [])
        missing_r = REQUIRED_ROLES - assigned
        if missing_r:
            fail(checks, "D4", f"角色缺: {sorted(missing_r)}——大任务四角色缺一不可")
        elif rl.get("verifier_independent_context") is not True:
            fail(checks, "D4", "verifier_independent_context=false——校验自产自销=系统性盲区查不出，质量闸门形同虚设")
        elif rl.get("verifier_only_list_not_edit") is not True:
            fail(checks, "D4", "verifier_only_list_not_edit=false——校验者改稿=挑错的人改完没人挑他的错")
        else:
            mr = rl.get("max_rounds")
            if not isinstance(mr, int) or mr < 1 or mr > 2:
                fail(checks, "D4", f"max_rounds={mr!r}——校验轮次须 1-2（>2 循环校验=成本失控）")
            else:
                ok(checks, "D4", "四角色独立分工（校验独立上下文+只出清单，≤2 轮）")

    # D5 Vibe Coding 三条件
    vc = plan.get("vibe_coding") or {}
    bad_vc = [k for k in ("high_freq", "low_risk", "internal_use") if vc.get(k) is not True]
    if not is_nonempty_str(vc.get("picked_pain_point")):
        fail(checks, "D5", "picked_pain_point 为空——没选定痛点，Vibe Coding 无从谈起")
    elif bad_vc:
        fail(checks, "D5", f"三条件缺: {bad_vc}——高频+低风险+内部使用缺一不选（内部试错成本低）")
    elif vc.get("domain_expert_drives") is not True:
        fail(checks, "D5", "domain_expert_drives=false——最懂场景的人没动手（在写需求等排期）=把懂场景的人挡在工具外")
    else:
        ok(checks, "D5", f"Vibe Coding 立项合规（{vc['picked_pain_point']}：高频+低风险+内部用，领域专家动手）")

    # D6 产出可展示
    ar = plan.get("artifacts") or {}
    if not is_nonempty_str(ar.get("verifiable_output")):
        fail(checks, "D6", "verifiable_output 为空——做完的事没有可展示成品=没做完（作品即简历）")
    elif ar.get("verifiable_in_30s") is not True:
        fail(checks, "D6", "verifiable_in_30s=false——别人 30 秒验证不了'这是你做的且能跑'=履历描述不是作品")
    else:
        ok(checks, "D6", "产出已作品化（30 秒可验证）")

    # D7 连接资产化
    if ar.get("digital_profile_updated") is not True:
        fail(checks, "D7", "digital_profile_updated=false——数字名片/能力简介没更新，偶遇=加了微信再无下文")
    else:
        ok(checks, "D7", "连接已资产化（数字名片随时可发）")

    return checks


def main():
    if len(sys.argv) != 2:
        print("usage: python validate.py plan.json", file=sys.stderr)
        return 2
    try:
        with open(sys.argv[1], encoding="utf-8") as f:
            plan = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: 无法读取/解析: {e}", file=sys.stderr)
        return 2
    if not isinstance(plan, dict):
        print("ERROR: 顶层必须是 JSON 对象", file=sys.stderr)
        return 2

    checks = validate(plan)
    fails = [c for c in checks if c[0] == "FAIL"]
    for status, code, msg in checks:
        if status == "FAIL":
            print(f"[{code}] FAIL {msg}")
    print(f"== {len(checks) - len(fails)} OK / {len(fails)} FAIL ==")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
