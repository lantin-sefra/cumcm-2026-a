"""问题4：附录4 + 移动边界收缩域 + 四情景效应隔离（MODELING_REPORT §7）。

主用情景 S2（附录4、R(t) 收缩、χ=0 含 Landau 对流项）给出交付时长与表6/result4；
效应隔离 S0–S4 在同一离散/环境/判据下运行，得式(24) 的加性分解（K19、H24）：
    t_S2 − t_S0 = (t_S1 − t_S0) + (t_S2 − t_S1)   ——「换物性」+「加收缩」两项。
⛔ S1（附录4 固定 R=2cm）为人为对照、物理不自洽（附录4 描述会收缩的药材），
   role='control'、不受 K9/K10 约束、不作交付（§7.6）。
⛔ 表6 末列是「药材表面」r=R(t)（非固定 2cm），域外 r>R(t) 置空（式26，§7.7）。
INC1：附录4 的 ρ(C) 与附件2 的 R(t) 在严格干物质守恒下差 13.42%，仅作诊断量
   （mass_consistency.csv），不作收敛判据、不修正实测半径（§7.3）。
"""
from __future__ import annotations

import csv

import numpy as np

import params as P
import geometry
import driver as D
import io_out as IO
import props as PR

REPORT_RADII = P.P34_REPORT_RADII_CM               # [0,0.5,1,1.5,2] cm
_COLIDX = [P.DIST_COLS_CM.index(round(r, 4)) for r in REPORT_RADII]   # 0,5,10,15,20
SURF_LABEL = "药材表面"


def _row_labels_6h(t_end_s):
    """6,12,… h（<t_end 的整数倍 6h）时刻列表（秒），与问题3 一致。"""
    out = []
    k = 1
    while k * P.P34_REPORT_DT_H * P.SEC_PER_HOUR < t_end_s:
        out.append(k * P.P34_REPORT_DT_H * P.SEC_PER_HOUR)
        k += 1
    return out


def _run(name, appendix, geom, chi, t_max_s, role="deliverable", store_nodes=False):
    """统一以交付离散（N=40、seg 步长、60 s 输出）推进一个情景。"""
    cfg = D.CaseConfig(name=name, appendix=appendix, geom=geom, chi=chi,
                       dt_policy="seg", save_dt_s=P.P34_SAVE_DT_S,
                       t_max_s=t_max_s, detect_end=True, role=role,
                       store_nodes=store_nodes)
    return D.run(cfg)


def _surf_at(res, t_query_s):
    """在快照时间轴上线性插值「药材表面」ξ=1 浓度（末行「烘干结束时间」用）。"""
    return float(np.interp(t_query_s, res["t"], res["Csurf"]))


def solve(write=True):
    # ---- 主用 S2：附录4 + R(t) + χ=0，保存全节点供表6/result4 ----
    res = _run("S2", 4, geometry.MovingGeometry(), P.CHI_PRIMARY,
               P.T_END_MAX_S, role="deliverable", store_nodes=True)
    if not res["reached"]:
        raise RuntimeError("问题4 主用情景 S2 未在 120 h 内达标（按 §13.3 自查 E1–E10）")
    t_end_s = res["t_end_s"]

    # ---- 效应隔离其余情景（S0/S1/S3/S4）----
    r_s0 = _run("S0", 3, geometry.FixedGeometry(P.R0_M), 0, P.T_END_MAX_S)
    r_s1 = _run("S1", 4, geometry.FixedGeometry(P.R0_M), 0, 150.0 * P.SEC_PER_HOUR,
                role="control")                         # 对照，需 >120h 才达标
    r_s3 = _run("S3", 4, geometry.MovingGeometry(), P.CHI_ALT, P.T_END_MAX_S)
    r_s4 = _run("S4", 4, geometry.FixedGeometry(P.R_END_M), 0, P.T_END_MAX_S)

    scen = [
        ("S0", "问题3基线（附录3，固定R=2cm）", 3, "固定", P.R0_CM, "n.a.", "deliverable", r_s0),
        ("S1", "仅换物性（附录4，固定R=2cm）", 4, "固定", P.R0_CM, "n.a.", "control", r_s1),
        ("S2", "换物性+收缩（主用，χ=0）", 4, "R(t)", np.nan, 0, "deliverable", res),
        ("S3", "换物性+收缩（替代闭合，χ=1）", 4, "R(t)", np.nan, 1, "control", r_s3),
        ("S4", "末态半径界（附录4，固定R=1.198cm）", 4, "固定", P.R_END_CM, "n.a.", "control", r_s4),
    ]
    tS0, tS1, tS2, tS3 = (r_s0["t_end_h"], r_s1["t_end_h"],
                          res["t_end_h"], r_s3["t_end_h"])
    prop_h = tS1 - tS0                                  # 换物性效应
    shrink_h = tS2 - tS1                                # 加收缩效应
    net_h = tS2 - tS0                                   # 净差（问4−问3）
    chi_diff_h = tS3 - tS2
    chi_diff_rel = chi_diff_h / tS2

    # ---- INC1 质量自洽诊断（式24，附录4）----
    rs_C0 = float(PR.rho_s_eff(4, np.array([P.C0]))[0])
    rs_Cth = float(PR.rho_s_eff(4, np.array([P.C_TH]))[0])
    ratio_actual = rs_Cth / rs_C0
    ratio_req = (P.R0_CM / P.R_END_CM) ** 2
    R_consistent = P.R0_CM / np.sqrt(ratio_actual)
    inc1_rel = (ratio_req - ratio_actual) / ratio_req

    if write:
        _write_table6(res, t_end_s)
        _write_result4(res, t_end_s)
        _write_effect_isolation(scen, prop_h, shrink_h, net_h)
        _write_mass_consistency(rs_C0, rs_Cth, ratio_actual, ratio_req,
                                R_consistent, inc1_rel)

    summary = {
        "problem": 4, "appendix": 4, "N": res["N"], "dt_s": "seg(2→4)",
        "chi_primary": P.CHI_PRIMARY,
        "t_end_h": tS2, "t_end_s": t_end_s,
        "t_end_label": f"S2 χ=0, N={res['N']}, Δt=seg(2→4)s → t_end={tS2:.3f} h",
        "maxC_at_end": float(res["maxC"][int(np.argmin(np.abs(res["t"] - t_end_s)))]),
        "radius_frozen": res["radius_frozen"],
        "R_at_end_cm": float(np.interp(t_end_s, res["t"], res["R"])) / P.CM_TO_M,
        "mass_resid_rel": res["mass_resid_rel"],
        "picard_iters_max": res["picard_iters_max"],
        "picard_nonconv": res["picard_nonconv"],
        "floor_trunc_steps": res["floor_trunc_steps"],
        "effect_isolation": {
            "t_S0_h": tS0, "t_S1_h": tS1, "t_S2_h": tS2, "t_S3_h": tS3,
            "t_S4_h": r_s4["t_end_h"],
            "prop_swap_h": prop_h, "shrink_h": shrink_h, "net_h": net_h,
            "identity_lhs": net_h, "identity_rhs": prop_h + shrink_h,
            "identity_resid_h": abs(net_h - (prop_h + shrink_h)),
        },
        "chi_closure": {"S2_chi0_h": tS2, "S3_chi1_h": tS3,
                        "diff_h": chi_diff_h, "diff_rel": chi_diff_rel},
        "inc1": {"ratio_actual": ratio_actual, "ratio_required": ratio_req,
                 "rel_diff": inc1_rel, "R_consistent_cm": R_consistent,
                 "R_measured_end_cm": P.R_END_CM},
        "report_times_h": [t / P.SEC_PER_HOUR for t in _row_labels_6h(t_end_s)],
        "report_radii_cm": list(REPORT_RADII),
    }
    return res, summary


def _write_table6(res, t_end_s):
    """表6：6h 行 + 末行「烘干结束时间」；列 = 5 固定半径 + 「药材表面」。"""
    times6 = _row_labels_6h(t_end_s)
    rows = []
    for tq in times6:
        j = int(np.argmin(np.abs(res["t"] - tq)))
        vals = [res["Ccol"][j, ci] for ci in _COLIDX]     # NaN→置空（式26）
        vals.append(float(res["Csurf"][j]))               # 药材表面 ξ=1
        rows.append(vals)
    end_fixed = D.field_at_time(res, t_end_s, "C")[_COLIDX]
    end_row = list(end_fixed) + [_surf_at(res, t_end_s)]

    col_labels = [f"{r:g}" for r in REPORT_RADII] + [SURF_LABEL]
    row_lbls = [f"{int(round(t / P.SEC_PER_HOUR))}" for t in times6]
    IO.write_table_csv(
        P.OUTPUT_DIR / "table6_problem4.csv",
        row_lbls, col_labels, rows,
        corner="水分浓度(kg/kg)  时间(h)\\距离(cm)",
        extra_last_row=(f"烘干结束时间 {t_end_s / P.SEC_PER_HOUR:.3f}h", end_row))


def _write_result4(res, t_end_s):
    """result4.xlsx：A 列 60 s；21 固定距离列 + 末列「药材表面」；域外置空。"""
    keep = (res["t"] >= P.P34_SAVE_DT_S - 1e-9) & (res["t"] <= t_end_s + 1e-6)
    arr = np.column_stack([res["Ccol"][keep], res["Csurf"][keep]])
    IO.write_result_xlsx(P.OUTPUT_DIR / "result4.xlsx",
                         {"水分浓度": arr}, res["t"][keep], last_label=SURF_LABEL)


def _write_effect_isolation(scen, prop_h, shrink_h, net_h):
    """effect_isolation.csv：S0–S4 五行 + 式(24) 加性分解（K19/H24）。"""
    path = P.OUTPUT_DIR / "effect_isolation.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["scenario", "description", "appendix", "domain", "R_cm",
                    "chi", "role", "t_end_h", "reached", "mass_resid_rel"])
        for sid, desc, app, dom, Rcm, chi, role, r in scen:
            w.writerow([sid, desc, app, dom, IO.fmt4(Rcm), chi, role,
                        f"{r['t_end_h']:.4f}" if r["reached"] else "",
                        r["reached"], f"{r['mass_resid_rel']:.3e}"])
        w.writerow([])
        w.writerow(["# 效应分解 式(24): t_S2-t_S0 = (t_S1-t_S0)+(t_S2-t_S1)"])
        w.writerow(["component", "value_h"])
        w.writerow(["换物性(t_S1-t_S0)", f"{prop_h:.4f}"])
        w.writerow(["加收缩(t_S2-t_S1)", f"{shrink_h:.4f}"])
        w.writerow(["净差(t_S2-t_S0)", f"{net_h:.4f}"])
        w.writerow(["加性恒等残差", f"{abs(net_h - (prop_h + shrink_h)):.2e}"])


def _write_mass_consistency(rs_C0, rs_Cth, ratio_actual, ratio_req,
                            R_consistent, inc1_rel):
    """mass_consistency.csv：INC1 诊断量（§7.3）。⛔ 仅诊断，不作收敛判据。"""
    path = P.OUTPUT_DIR / "mass_consistency.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["quantity", "value", "unit", "note"])
        w.writerow(["rho_s_eff(C0=2.55)", f"{rs_C0:.4f}", "kg/m^3", "附录4 干物质表观密度"])
        w.writerow(["rho_s_eff(Cth=0.15)", f"{rs_Cth:.4f}", "kg/m^3", ""])
        w.writerow(["ratio_actual", f"{ratio_actual:.4f}", "-", "rho_s(Cth)/rho_s(C0)"])
        w.writerow(["ratio_required", f"{ratio_req:.4f}", "-", "(R0/R_end)^2 严格守恒要求"])
        w.writerow(["rel_diff", f"{inc1_rel * 100:.2f}", "%", "INC1 不相容度"])
        w.writerow(["R_consistent", f"{R_consistent:.4f}", "cm", "与 rho(C) 守恒相容的末态半径"])
        w.writerow(["R_measured_end", f"{P.R_END_CM:.4f}", "cm", "附件2 实测末态半径"])
        w.writerow(["# 结论", "ρ(C)与R(t)严格干物质守恒下不相容，差13.42%；仅诊断量，不修正R(t)、不作收敛判据",
                    "", ""])


if __name__ == "__main__":
    _, s = solve()
    ei = s["effect_isolation"]
    print("P4 done:", {
        "t_end_h": round(s["t_end_h"], 3), "R@end_cm": round(s["R_at_end_cm"], 4),
        "mass_resid_rel": s["mass_resid_rel"],
        "net_h": round(ei["net_h"], 3), "prop_h": round(ei["prop_swap_h"], 3),
        "shrink_h": round(ei["shrink_h"], 3),
        "identity_resid_h": ei["identity_resid_h"],
        "chi_diff_rel": round(s["chi_closure"]["diff_rel"], 4)})
