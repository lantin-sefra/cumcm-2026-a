"""问题4：附录4 + 收缩移动边界。

主用：Lagrangian 干基质量坐标 s=∫ ρ_d r dr（仿射收缩 r=R(t)√(s/S)），交付时长与表6/result4。
交叉验证：Eulerian Landau ξ=r/R(t)、χ=0（含表观对流项）。
2×2 因子设计（同一 Lagrangian 核）：
    t00 附录3+固定R， t10 附录4+固定R， t01 附录3+收缩， t11 附录4+收缩（交付）。
交互项 I = t11 - t10 - t01 + t00；物性/收缩贡献取两条路径的 Shapley 平均。
Eulerian 补算 t01 仅作交叉对照，不参与交付。
INC1：附录4 ρ(C) 与附件2 R(t) 在严格干物质守恒下不相容，只作诊断。
"""
from __future__ import annotations

import csv

import numpy as np

import params as P
import geometry
import driver as D
import io_out as IO
import props as PR

REPORT_RADII = P.P34_REPORT_RADII_CM
_COLIDX = [P.DIST_COLS_CM.index(round(r, 4)) for r in REPORT_RADII]
SURF_LABEL = "药材表面"


def _row_labels_6h(t_end_s):
    out = []
    k = 1
    while k * P.P34_REPORT_DT_H * P.SEC_PER_HOUR < t_end_s:
        out.append(k * P.P34_REPORT_DT_H * P.SEC_PER_HOUR)
        k += 1
    return out


def _run(name, appendix, geom, *, frame="lagrange", chi=0, t_max_s=None,
         role="deliverable", store_nodes=False):
    if t_max_s is None:
        t_max_s = P.T_END_MAX_S
    cfg = D.CaseConfig(name=name, appendix=appendix, geom=geom, chi=chi,
                       frame=frame, dt_policy="seg", save_dt_s=P.P34_SAVE_DT_S,
                       t_max_s=t_max_s, detect_end=True, role=role,
                       store_nodes=store_nodes)
    return D.run(cfg)


def _surf_at(res, t_query_s):
    return float(np.interp(t_query_s, res["t"], res["Csurf"]))


def _shapley(t00, t10, t01, t11):
    """两条路径的平均贡献（Shapley）与交互项。"""
    I = t11 - t10 - t01 + t00
    prop = 0.5 * ((t10 - t00) + (t11 - t01))
    shrink = 0.5 * ((t01 - t00) + (t11 - t10))
    net = t11 - t00
    return {
        "t00": t00, "t10": t10, "t01": t01, "t11": t11,
        "interaction_h": I,
        "prop_shapley_h": prop,
        "shrink_shapley_h": shrink,
        "net_h": net,
        "path_prop_then_shrink": (t10 - t00, t11 - t10),
        "path_shrink_then_prop": (t01 - t00, t11 - t01),
    }


def solve(write=True):
    moving = geometry.MovingGeometry()
    fixed0 = geometry.FixedGeometry(P.R0_M)
    tmax_slow = 150.0 * P.SEC_PER_HOUR

    # ---- 主用：Lagrangian + 附录4 + R(t) ----
    res = _run("L11", 4, moving, frame="lagrange",
               role="deliverable", store_nodes=True)
    if not res["reached"]:
        raise RuntimeError("问题4 Lagrangian 主用情景未在 120 h 内达标")
    t_end_s = res["t_end_s"]

    # ---- Lagrangian 2×2 其余三格 ----
    r_l00 = _run("L00", 3, fixed0, frame="lagrange")
    r_l10 = _run("L10", 4, fixed0, frame="lagrange", t_max_s=tmax_slow,
                 role="control")
    r_l01 = _run("L01", 3, moving, frame="lagrange")

    # ---- Eulerian Landau 交叉验证（χ=0）+ 补齐 Eulerian t01 ----
    r_e11 = _run("E11", 4, moving, frame="landau", chi=P.CHI_PRIMARY,
                 role="control")
    r_e01 = _run("E01", 3, moving, frame="landau", chi=P.CHI_PRIMARY,
                 role="control")
    r_e00 = _run("E00", 3, fixed0, frame="landau", chi=0)
    r_e10 = _run("E10", 4, fixed0, frame="landau", chi=0, t_max_s=tmax_slow,
                 role="control")

    tL = _shapley(r_l00["t_end_h"], r_l10["t_end_h"],
                  r_l01["t_end_h"], res["t_end_h"])
    tE = _shapley(r_e00["t_end_h"], r_e10["t_end_h"],
                  r_e01["t_end_h"], r_e11["t_end_h"])

    cross_rel = (r_e11["t_end_h"] - res["t_end_h"]) / res["t_end_h"]

    # ---- INC1 干物质自洽诊断 ----
    rs_C0 = float(PR.rho_s_eff(4, np.array([P.C0]))[0])
    rs_Cth = float(PR.rho_s_eff(4, np.array([P.C_TH]))[0])
    ratio_actual = rs_Cth / rs_C0
    ratio_req = (P.R0_CM / P.R_END_CM) ** 2
    R_consistent = P.R0_CM / np.sqrt(ratio_actual)
    inc1_rel = (ratio_req - ratio_actual) / ratio_req

    # 体积收缩系数反演 β(t)=( (R/R0)^2 - 1 ) / (C̄ - C0)，C̄ 为干基质量加权
    beta_series = _shrinkage_beta(res)

    if write:
        _write_table6(res, t_end_s)
        _write_result4(res, t_end_s)
        _write_factorial(tL, tE, res, r_e11, r_l00, r_l10, r_l01,
                         r_e00, r_e10, r_e01, cross_rel)
        _write_mass_consistency(rs_C0, rs_Cth, ratio_actual, ratio_req,
                                R_consistent, inc1_rel)
        _write_beta(beta_series)

    summary = {
        "problem": 4, "appendix": 4, "N": res["N"], "dt_s": "seg(2→4)",
        "frame_primary": "lagrange",
        "t_end_h": res["t_end_h"], "t_end_s": t_end_s,
        "t_end_label": (f"Lagrangian N={res['N']}, Δt=seg(2→4)s "
                        f"→ t_end={res['t_end_h']:.4f} h"),
        "maxC_at_end": float(res["maxC"][int(np.argmin(np.abs(res["t"] - t_end_s)))]),
        "radius_frozen": res["radius_frozen"],
        "R_at_end_cm": float(np.interp(t_end_s, res["t"], res["R"])) / P.CM_TO_M,
        "mass_resid_rel": res["mass_resid_rel"],
        "picard_iters_max": res["picard_iters_max"],
        "picard_nonconv": res["picard_nonconv"],
        "floor_trunc_steps": res["floor_trunc_steps"],
        "lagrange_2x2": tL,
        "euler_2x2": tE,
        "crosscheck": {
            "euler_chi0_h": r_e11["t_end_h"],
            "lagrange_h": res["t_end_h"],
            "diff_h": r_e11["t_end_h"] - res["t_end_h"],
            "diff_rel": cross_rel,
        },
        # 兼容旧字段名，供 main/validate/旧图脚本读取
        "chi_primary": "n.a.(lagrange)",
        "effect_isolation": {
            "t_S0_h": tL["t00"], "t_S1_h": tL["t10"],
            "t_S2_h": tL["t11"], "t_S3_h": r_e11["t_end_h"],
            "t_S4_h": None,
            "t_01_h": tL["t01"],
            "prop_swap_h": tL["prop_shapley_h"],
            "shrink_h": tL["shrink_shapley_h"],
            "net_h": tL["net_h"],
            "interaction_h": tL["interaction_h"],
            "identity_lhs": tL["net_h"],
            "identity_rhs": tL["prop_shapley_h"] + tL["shrink_shapley_h"],
            "identity_resid_h": abs(tL["net_h"]
                                    - (tL["prop_shapley_h"] + tL["shrink_shapley_h"])),
        },
        "chi_closure": {
            "S2_chi0_h": r_e11["t_end_h"],
            "S3_chi1_h": res["t_end_h"],
            "diff_h": r_e11["t_end_h"] - res["t_end_h"],
            "diff_rel": cross_rel,
        },
        "inc1": {"ratio_actual": ratio_actual, "ratio_required": ratio_req,
                 "rel_diff": inc1_rel, "R_consistent_cm": R_consistent,
                 "R_measured_end_cm": P.R_END_CM},
        "shrinkage_beta": beta_series,
        "report_times_h": [t / P.SEC_PER_HOUR for t in _row_labels_6h(t_end_s)],
        "report_radii_cm": list(REPORT_RADII),
    }
    return res, summary


def _shrinkage_beta(res):
    """由实测 R(t) 与干基质量加权含水率反演体积收缩系数，证伪线性收缩律。"""
    R = np.asarray(res["R"])
    t = np.asarray(res["t"])
    Cbar = np.asarray(res["Ccenter"]) * np.nan  # placeholder length
    # 干基质量加权：节点均匀 s 网格上 C 的 Vt 加权；无节点场时退回 (Ccenter+Csurf)/2
    if "nodesC" in res:
        nodes = np.asarray(res["nodesC"])
        N = nodes.shape[1] - 1
        ds = 1.0 / N
        w = np.full(N + 1, ds)
        w[0] = w[-1] = 0.5 * ds
        w = w / w.sum()
        Cbar = nodes @ w
    else:
        Cbar = 0.5 * (np.asarray(res["Ccenter"]) + np.asarray(res["Csurf"]))
    Vratio = (R / P.R0_M) ** 2
    dC = Cbar - P.C0
    beta = np.full_like(Cbar, np.nan, dtype=float)
    mask = np.abs(dC) > 1e-4
    beta[mask] = (Vratio[mask] - 1.0) / dC[mask]
    finite = beta[np.isfinite(beta)]
    return {
        "t_h": (t / P.SEC_PER_HOUR).tolist(),
        "Cbar": Cbar.tolist(),
        "V_over_V0": Vratio.tolist(),
        "beta": beta.tolist(),
        "beta_mean": float(np.mean(finite)) if finite.size else None,
        "beta_std": float(np.std(finite)) if finite.size else None,
        "beta_cv": (float(np.std(finite) / np.mean(finite))
                    if finite.size and np.mean(finite) != 0 else None),
        "linear_rejected": bool(finite.size and
                                (np.std(finite) > 0.15 * abs(np.mean(finite)))),
    }


def _write_table6(res, t_end_s):
    times6 = _row_labels_6h(t_end_s)
    rows = []
    for tq in times6:
        j = int(np.argmin(np.abs(res["t"] - tq)))
        vals = [res["Ccol"][j, ci] for ci in _COLIDX]
        vals.append(float(res["Csurf"][j]))
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
    """result4.xlsx：模板工作表名 Sheet1；A 列从 60s 起；末列药材表面；域外空白。"""
    keep = (res["t"] >= P.P34_SAVE_DT_S - 1e-9) & (res["t"] <= t_end_s + 1e-6)
    arr = np.column_stack([res["Ccol"][keep], res["Csurf"][keep]])
    IO.write_result_xlsx(P.OUTPUT_DIR / "result4.xlsx",
                         {"Sheet1": arr}, res["t"][keep], last_label=SURF_LABEL)


def _write_factorial(tL, tE, res, r_e11, r_l00, r_l10, r_l01,
                     r_e00, r_e10, r_e01, cross_rel):
    path = P.OUTPUT_DIR / "effect_isolation.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        ("L00", "附录3 + 固定R（Lagrangian）", 3, "固定", P.R0_CM, "lagrange",
         "control", r_l00),
        ("L10", "附录4 + 固定R（Lagrangian）", 4, "固定", P.R0_CM, "lagrange",
         "control", r_l10),
        ("L01", "附录3 + 收缩R(t)（Lagrangian）", 3, "R(t)", np.nan, "lagrange",
         "control", r_l01),
        ("L11", "附录4 + 收缩R(t)（主用 Lagrangian）", 4, "R(t)", np.nan, "lagrange",
         "deliverable", res),
        ("E00", "附录3 + 固定R（Eulerian）", 3, "固定", P.R0_CM, "landau",
         "control", r_e00),
        ("E10", "附录4 + 固定R（Eulerian）", 4, "固定", P.R0_CM, "landau",
         "control", r_e10),
        ("E01", "附录3 + 收缩R(t)（Eulerian χ=0）", 3, "R(t)", np.nan, "landau",
         "control", r_e01),
        ("E11", "附录4 + 收缩R(t)（Eulerian χ=0 交叉验证）", 4, "R(t)", np.nan, "landau",
         "control", r_e11),
    ]
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["scenario", "description", "appendix", "domain", "R_cm",
                    "frame", "role", "t_end_h", "reached", "mass_resid_rel"])
        for sid, desc, app, dom, Rcm, frame, role, r in rows:
            w.writerow([sid, desc, app, dom, IO.fmt4(Rcm), frame, role,
                        f"{r['t_end_h']:.4f}" if r["reached"] else "",
                        r["reached"], f"{r['mass_resid_rel']:.3e}"])
        w.writerow([])
        w.writerow(["# Lagrangian 2x2 因子设计（交付分解）"])
        w.writerow(["quantity", "value_h"])
        w.writerow(["t00 附录3+固定", f"{tL['t00']:.4f}"])
        w.writerow(["t10 附录4+固定", f"{tL['t10']:.4f}"])
        w.writerow(["t01 附录3+收缩", f"{tL['t01']:.4f}"])
        w.writerow(["t11 附录4+收缩（交付）", f"{tL['t11']:.4f}"])
        w.writerow(["交互项 I=t11-t10-t01+t00", f"{tL['interaction_h']:.4f}"])
        w.writerow(["物性 Shapley", f"{tL['prop_shapley_h']:.4f}"])
        w.writerow(["收缩 Shapley", f"{tL['shrink_shapley_h']:.4f}"])
        w.writerow(["净差 t11-t00", f"{tL['net_h']:.4f}"])
        w.writerow(["路径A 先换物性", f"{tL['path_prop_then_shrink'][0]:.4f}"])
        w.writerow(["路径A 再加收缩", f"{tL['path_prop_then_shrink'][1]:.4f}"])
        w.writerow(["路径B 先加收缩", f"{tL['path_shrink_then_prop'][0]:.4f}"])
        w.writerow(["路径B 再换物性", f"{tL['path_shrink_then_prop'][1]:.4f}"])
        w.writerow([])
        w.writerow(["# Eulerian 2x2（交叉对照，非交付）"])
        w.writerow(["E t00", f"{tE['t00']:.4f}"])
        w.writerow(["E t10", f"{tE['t10']:.4f}"])
        w.writerow(["E t01", f"{tE['t01']:.4f}"])
        w.writerow(["E t11 χ=0", f"{tE['t11']:.4f}"])
        w.writerow(["E 交互项 I", f"{tE['interaction_h']:.4f}"])
        w.writerow(["E 物性 Shapley", f"{tE['prop_shapley_h']:.4f}"])
        w.writerow(["E 收缩 Shapley", f"{tE['shrink_shapley_h']:.4f}"])
        w.writerow(["Lagrangian vs Eulerian 相对差", f"{cross_rel * 100:.2f}%"])


def _write_mass_consistency(rs_C0, rs_Cth, ratio_actual, ratio_req,
                            R_consistent, inc1_rel):
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
        w.writerow(["# 结论",
                    "ρ(C)与R(t)严格干物质守恒下不相容；仅诊断量，不修正R(t)、不作收敛判据",
                    "", ""])


def _write_beta(beta_series):
    path = P.OUTPUT_DIR / "shrinkage_beta.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["t_h", "Cbar", "V_over_V0", "beta"])
        for t, c, v, b in zip(beta_series["t_h"], beta_series["Cbar"],
                              beta_series["V_over_V0"], beta_series["beta"]):
            w.writerow([f"{t:.4f}", f"{c:.6f}", f"{v:.6f}",
                        "" if b != b else f"{b:.6f}"])  # NaN check
        w.writerow([])
        w.writerow(["beta_mean", f"{beta_series['beta_mean']}"])
        w.writerow(["beta_std", f"{beta_series['beta_std']}"])
        w.writerow(["beta_cv", f"{beta_series['beta_cv']}"])
        w.writerow(["linear_rejected", beta_series["linear_rejected"]])


if __name__ == "__main__":
    _, s = solve()
    L = s["lagrange_2x2"]
    cc = s["crosscheck"]
    print("P4 done:", {
        "t_end_h": round(s["t_end_h"], 4),
        "R@end_cm": round(s["R_at_end_cm"], 4),
        "mass_resid_rel": s["mass_resid_rel"],
        "I_h": round(L["interaction_h"], 3),
        "prop_shapley": round(L["prop_shapley_h"], 3),
        "shrink_shapley": round(L["shrink_shapley_h"], 3),
        "euler_h": round(cc["euler_chi0_h"], 4),
        "cross_rel": round(cc["diff_rel"], 4),
    })
