"""问题4：附录4 + 实测 R(t) + χ=1 材料随动 ALE 主模型。

正式结果、表6与result4只由χ=1主模型生成；χ=0仅作为Eulerian/Landau交叉验证。
S0、S1、S4保留为程序内部兼容性诊断，不作为论文正式效应分解结果。
⛔ 表6 末列是「药材表面」r=R(t)（非固定 2cm），域外 r>R(t) 置空（式26，§7.7）。
附加质量自洽量仅作程序诊断，不作收敛判据，也不修正附件2实测半径。
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


def _run(
    name, appendix, geom, chi, t_max_s, role="deliverable", store_nodes=False,
    N=P.N_P4_CV, dt_policy="const", dt_const=P.DT_P4,
):
    """按可独立指定的 Q4 数值参数推进一个情景。"""
    cfg = D.CaseConfig(name=name, appendix=appendix, geom=geom, chi=chi,
                       N=N, dt_policy=dt_policy, dt_const=dt_const,
                       save_dt_s=P.P34_SAVE_DT_S,
                       t_max_s=t_max_s, detect_end=True, event_each_step=True,
                       role=role,
                       store_nodes=store_nodes)
    return D.run(cfg)


def _surf_at(res, t_query_s):
    """在快照时间轴上线性插值「药材表面」ξ=1 浓度（末行「烘干结束时间」用）。"""
    return float(np.interp(t_query_s, res["t"], res["Csurf"]))


def solve(write=True):
    # ---- 正式Q4：附录4 + R(t) + χ=1，保存全节点供表6/result4 ----
    res = _run("S2", 4, geometry.MovingGeometry(), P.CHI_P4_PRIMARY,
               P.T_END_MAX_S, role="deliverable", store_nodes=True)
    if not res["reached"]:
        raise RuntimeError("问题4 主用情景 S2 未在 120 h 内达标（按 §13.3 自查 E1–E10）")
    t_end_s = res["t_end_s"]

    # ---- 兼容诊断；S3为χ=0交叉验证，其他情景不进入论文正式结果 ----
    r_s0 = _run("S0", 3, geometry.FixedGeometry(P.R0_M), 0, P.T_END_MAX_S)
    r_s1 = _run("S1", 4, geometry.FixedGeometry(P.R0_M), 0, 150.0 * P.SEC_PER_HOUR,
                role="control")                         # 对照，需 >120h 才达标
    r_s3 = _run("S3", 4, geometry.MovingGeometry(), P.CHI_P4_CROSSCHECK,
                P.T_END_MAX_S)
    r_s4 = _run("S4", 4, geometry.FixedGeometry(P.R_END_M), 0, P.T_END_MAX_S)

    scen = [
        ("S0", "问题3基线（附录3，固定R=2cm）", 3, "固定", P.R0_CM, "n.a.", "deliverable", r_s0),
        ("S1", "仅换物性（附录4，固定R=2cm）", 4, "固定", P.R0_CM, "n.a.", "control", r_s1),
        ("S2", "换物性+收缩（主用ALE，χ=1）", 4, "R(t)", np.nan, 1, "deliverable", res),
        ("S3", "换物性+收缩（Eulerian/Landau交叉验证，χ=0）", 4, "R(t)", np.nan, 0, "control", r_s3),
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
        "problem": 4, "appendix": 4, "N": res["N"], "dt_s": P.DT_P4,
        "chi_primary": P.CHI_P4_PRIMARY,
        "t_end_h": tS2, "t_end_s": t_end_s,
        "t_end_label": f"S2 χ=1, N={res['N']}, Δt={P.DT_P4:g}s → t_end={tS2:.3f} h",
        "maxC_at_end": float(np.max(res["end_C"])),
        "radius_frozen": res["radius_frozen"],
        "R_at_end_cm": float(res["end_R"]) / P.CM_TO_M,
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
        "chi_closure": {"S2_chi1_primary_h": tS2, "S3_chi0_crosscheck_h": tS3,
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
    """写出内部兼容性诊断；不作为论文正式效应分解结果。"""
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
