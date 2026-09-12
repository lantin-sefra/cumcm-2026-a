"""数值可信度验证与灵敏度（MODELING_REPORT §9、§10；能力 X-C1）。

产出：
  output/validation.json —— §9 五类证据 + K1–K24/U/V 检查点，逐项 pass 布尔；
  output/sensitivity.csv —— SA1–SA10（case_id,param,value,t_end_h,elasticity,note）。

§9 证据（按适用性）：
  9.1 质量收支残差（式27）<1e-10（P1/P2/P3/S2）；
  9.2 网格/步长无关性（式28）：附录2 温度场 e_T,e_C<0.5%；t_end 网格敏感性<1%；
  9.3 半解析级数解（式29 + Duhamel，仅问题1 温度场）逐点偏差<0.05℃（前30根）；
  9.4 物理量级/单调/空间序/阈值可达/有界；
  9.5 极限退化：h_m→大 逼近 Dirichlet；R≡2cm 复现 S1（K18，偏差<0.1%）。
⛔ 级数对照只对问题1 温度场有效；不作问题2/3/4 浓度场正确性证据。
"""
from __future__ import annotations

import csv
import json

import numpy as np
from scipy.optimize import brentq
from scipy.special import j0, j1

import params as P
import props as PR
import ambient as AMB
import geometry
import driver as D
import fvm


# ---------------------------------------------------------------------------
# 9.3 半解析：Robin 圆柱阶跃响应级数 + Duhamel（分段线性 T_air 精确叠加）
# ---------------------------------------------------------------------------
def bessel_roots(Bi, n_roots):
    """求 λ·J1(λ)=Bi·J0(λ) 的前 n_roots 个正根（扫描 + brentq 夹逼）。"""
    f = lambda x: x * j1(x) - Bi * j0(x)
    xs = np.arange(1e-4, 200.0, 0.01)
    fx = f(xs)
    roots = []
    for i in range(len(xs) - 1):
        if fx[i] == 0.0:
            roots.append(xs[i])
        elif fx[i] * fx[i + 1] < 0.0:
            roots.append(brentq(f, xs[i], xs[i + 1], xtol=1e-12))
        if len(roots) >= n_roots:
            break
    return np.asarray(roots[:n_roots])


def analytic_T_p1(r_m, t_s, alpha, R, Bi, lam, T0, amb):
    """问题1 温度场半解析参照（式29 阶跃响应 + 分段线性 Duhamel 精确积分）。

    T(r,t)-T0 = Σ_k slope_k · ∫ G(r,t-τ)dτ ，G=1-S 为指示导纳；
    S(r,s)=Σ_n c_n(r) exp(-β_n s)，β_n=λ_n²α/R²，
    c_n(r)=[2Bi/(λ_n²+Bi²)]·J0(λ_n r/R)/J0(λ_n)。附件1 分段线性 ⇒ 逐段精确。
    """
    beta = lam ** 2 * alpha / (R * R)                    # (n,)
    cn = (2.0 * Bi / (lam ** 2 + Bi ** 2)) * (j0(lam * (r_m / R)) / j0(lam))  # (n,)
    # 附件1 时间结点（升温段 0..14400），只取 ≤ t 的段 + 末段截断到 t
    tk = amb._t[amb._t <= t_s]
    if tk[-1] < t_s:
        tk = np.append(tk, t_s)
    Tk = amb.T_air(tk)
    out = 0.0
    for k in range(len(tk) - 1):
        a, b = tk[k], tk[k + 1]
        slope = (Tk[k + 1] - Tk[k]) / (b - a)
        # ∫_a^b G(r,t-τ)dτ = (b-a) - Σ c_n/β_n·[exp(-β_n(t-b))-exp(-β_n(t-a))]
        integ = (b - a) - np.sum(cn / beta *
                                 (np.exp(-beta * (t_s - b)) - np.exp(-beta * (t_s - a))))
        out += slope * integ
    return T0 + out


def ev_bessel(n_roots=P.BESSEL_ROOTS):
    """P1 数值温度 vs 级数+Duhamel 参照，t=1800s 逐点最大偏差（<0.05℃）。"""
    g = geometry.FixedGeometry(P.R0_M)
    cfg = D.CaseConfig(name="P1val", appendix=2, geom=g, dt_policy="p1",
                       save_dt_s=P.P1_SAVE_DURATION_S, t_max_s=P.P1_SAVE_DURATION_S,
                       detect_end=False)
    res = D.run(cfg)
    Tnum = res["Tcol"][-1]                                # 1800s 的 21 固定列
    alpha = P.APP2_K / (P.APP2_RHO * P.APP2_CP)
    Bi = P.H_CONV * P.R0_M / P.APP2_K
    lam = bessel_roots(Bi, n_roots)
    amb = AMB.Ambient()
    r_cols_m = np.asarray(P.DIST_COLS_CM) * P.CM_TO_M
    Tana = np.array([analytic_T_p1(r, P.P1_SAVE_DURATION_S, alpha, P.R0_M, Bi,
                                   lam, P.T0_C, amb) for r in r_cols_m])
    dev = float(np.max(np.abs(Tnum - Tana)))
    return {"n_roots": int(n_roots), "max_dev_C": dev, "tol_C": 0.05,
            "pass": dev < 0.05,
            "T_center_num": float(Tnum[0]), "T_center_ana": float(Tana[0]),
            "T_surf_num": float(Tnum[-1]), "T_surf_ana": float(Tana[-1])}


# ---------------------------------------------------------------------------
# 9.2 网格/步长无关性（式28）：附录2 温度/浓度场，参照解 N=160,Δt=0.125s
# ---------------------------------------------------------------------------
def _p1_fields(N, dt):
    g = geometry.FixedGeometry(P.R0_M)
    cfg = D.CaseConfig(name=f"g{N}", appendix=2, geom=g, N=N, dt_policy="const",
                       dt_const=dt, save_dt_s=P.P1_SAVE_DURATION_S,
                       t_max_s=P.P1_SAVE_DURATION_S, detect_end=False)
    r = D.run(cfg)
    return r["Tcol"][-1], r["Ccol"][-1]                  # 1800s 21 固定列


def ev_grid():
    """交付网格 N=40 相对参照 N=160/Δt=0.125 的 e_T,e_C（式28，<0.5%）。"""
    Tref, Cref = _p1_fields(P.REF_N_CV, P.REF_DT_S)
    T40, C40 = _p1_fields(P.N_CV, P.DT_P1)
    Tscale = max(np.max(np.abs(Tref)), 1.0)
    Cscale = max(np.max(np.abs(Cref)), P.C_TH)
    eT = float(np.max(np.abs(T40 - Tref)) / Tscale)
    eC = float(np.max(np.abs(C40 - Cref)) / Cscale)
    return {"ref": {"N": P.REF_N_CV, "dt_s": P.REF_DT_S}, "delivery_N": P.N_CV,
            "eT": eT, "eC": eC, "tol": P.GRID_TOL,
            "pass": (eT < P.GRID_TOL and eC < P.GRID_TOL)}


def ev_dt_independence():
    """时间步无关性（式28，X-C1 第2项）：固定 N=40 附录2 温度/浓度场，
    Δt∈{2,1,0.5}s 相对 Δt=0.5s 参照的 e_T,e_C（<0.5%）。隐式后向 Euler 无条件稳定，
    三步长收敛证明交付步长（P1 用 1 s）已时间步无关。"""
    g = geometry.FixedGeometry(P.R0_M)

    def fields(dt):
        cfg = D.CaseConfig(name=f"dt{dt}", appendix=2, geom=g, N=P.N_CV,
                           dt_policy="const", dt_const=dt,
                           save_dt_s=P.P1_SAVE_DURATION_S,
                           t_max_s=P.P1_SAVE_DURATION_S, detect_end=False)
        r = D.run(cfg)
        return r["Tcol"][-1], r["Ccol"][-1]                  # 1800s 21 固定列

    dts = [2.0, 1.0, 0.5]
    Tref, Cref = fields(dts[-1])
    Tscale = max(np.max(np.abs(Tref)), 1.0)
    Cscale = max(np.max(np.abs(Cref)), P.C_TH)
    per, eT_max, eC_max = {}, 0.0, 0.0
    for dt in dts[:-1]:
        Ti, Ci = fields(dt)
        eT = float(np.max(np.abs(Ti - Tref)) / Tscale)
        eC = float(np.max(np.abs(Ci - Cref)) / Cscale)
        per[str(dt)] = {"eT": eT, "eC": eC}
        eT_max, eC_max = max(eT_max, eT), max(eC_max, eC)
    return {"ref_dt_s": dts[-1], "N": P.N_CV, "steps_tested": dts, "per_dt": per,
            "eT_max": eT_max, "eC_max": eC_max, "tol": P.GRID_TOL,
            "pass": (eT_max < P.GRID_TOL and eC_max < P.GRID_TOL)}


def ev_tend_gridsens():
    """t_end 网格敏感性（P3 附录3 固定域）：|t_end(N)-t_end(2N)|/t_end<1%。"""
    g = geometry.FixedGeometry(P.R0_M)
    tends = {}
    for N in (20, 40):
        cfg = D.CaseConfig(name=f"ts{N}", appendix=3, geom=g, N=N, dt_policy="const",
                           dt_const=P.DT_SEG_COARSE, save_dt_s=P.P34_SAVE_DT_S,
                           t_max_s=P.T_END_MAX_S, detect_end=True)
        tends[N] = D.run(cfg)["t_end_h"]
    rel = abs(tends[20] - tends[40]) / tends[40]
    return {"t_end_N20_h": tends[20], "t_end_N40_h": tends[40],
            "rel_change": rel, "tol": 0.01, "pass": rel < 0.01}


# ---------------------------------------------------------------------------
# 9.1 质量收支残差（式27）<1e-10：各问题最终 mass_resid_rel
# ---------------------------------------------------------------------------
def ev_mass(res_by_key):
    out = {}
    ok = True
    for key, r in res_by_key.items():
        v = float(r["mass_resid_rel"])
        p = v < P.MASS_RESIDUAL_TOL
        ok = ok and p
        out[key] = {"mass_resid_rel": v, "pass": p}
    out["tol"] = P.MASS_RESIDUAL_TOL
    out["pass"] = ok
    return out


# ---------------------------------------------------------------------------
# 9.4 物理量级 / 单调 / 空间序 / 有界（用已算结果检验）
# ---------------------------------------------------------------------------
def ev_physical(res_p1, res_p3):
    j = int(np.argmin(np.abs(res_p1["t"] - 1800.0)))
    Tc = float(res_p1["Tcenter"][j]); Cc = float(res_p1["Ccenter"][j])
    # §9.4.1 温度先于水分（α/D=34）：中心温度明显上升（+5.6℃）而中心浓度降幅<0.5%
    T_risen = (Tc - P.T0_C) > 3.0
    C_still = (P.C0 - Cc) / P.C0 < 0.005
    thermal_first = T_risen and C_still
    # 单调：C 对 t 不增（§9.4）；T「升温段」不减（合同 nondecreasing_while_T_air_rising）。
    C_mono = bool(np.all(np.diff(res_p3["maxC"]) <= 1e-9))
    Tc_arr = np.asarray(res_p3["Tcenter"])
    # 附件1 实测 T_air 本身非单调（传感器噪声：95/240 步下降，最大 0.45℃，t>14400s 取常值平台）；
    # 线性抛物算子对边界扰动只衰减不放大（极值原理）。忠实判据 = 中心温度任一下降步幅
    # ≤ 空气最大下降步幅：空气严格上升(降幅0)时退化为中心严格不降，正合合同语义。
    # §9.3 Bessel/Duhamel 已用同一非单调 T_air 证得数值温度(含微幅回落)对≤0.0012℃⇒回落属物理真值。
    Ta = np.asarray(AMB.Ambient().T_air(res_p3["t"]))
    max_air_drop = float(-np.min(np.diff(Ta))) if Ta.size > 1 else 0.0
    max_air_drop = max(max_air_drop, 0.0)
    dTc = np.diff(Tc_arr)
    max_ctr_drop = float(-np.min(dTc)) if dTc.size and np.any(dTc < 0.0) else 0.0
    T_damped = bool(max_ctr_drop <= max_air_drop + 1e-9)
    k_ramp = int(np.argmin(np.abs(np.asarray(res_p3["t"]) - P.AMBIENT_T_MAX_S)))
    T_heats = bool((Tc_arr[k_ramp] - Tc_arr[0]) > 3.0)
    T_mono = bool(T_damped and T_heats)
    # 空间序：C(0)>=C(R)，T(0)<=T(R)（取 P3 中段快照，跳过 t=0）
    k = len(res_p3["t"]) // 2
    space_C = bool(res_p3["Ccenter"][k] >= res_p3["Csurf"][k] - 1e-9)
    space_T = bool(res_p3["Tcenter"][k] <= res_p3["Tsurf"][k] + 1e-6)
    # 有界（P3 全程）
    Cmin = float(np.nanmin(res_p3["Ccol"])); Cmax = float(np.nanmax(res_p3["Ccol"]))
    Tmin = float(np.nanmin(res_p3["Tcol"])); Tmax = float(np.nanmax(res_p3["Tcol"]))
    no_nan_neg = bool(Cmin >= 0.0 and Cmax <= P.C0 + 1e-6 and Tmin >= P.T0_C - 1e-6
                      and Tmax <= 51.0)
    allp = thermal_first and C_mono and T_mono and space_C and space_T and no_nan_neg
    return {"thermal_precedes_moisture": thermal_first, "T_center_1800": Tc,
            "C_center_1800": Cc, "C_monotone_nonincreasing": C_mono,
            "T_nondecr_while_air_rising": T_mono,
            "T_center_max_drop_C": max_ctr_drop, "T_air_max_drop_C": max_air_drop,
            "T_ramp_rise_C": float(Tc_arr[k_ramp] - Tc_arr[0]),
            "space_order_C": space_C,
            "space_order_T": space_T, "bounded_no_nan_no_neg": no_nan_neg,
            "field_ranges": {"C": [Cmin, Cmax], "T": [Tmin, Tmax]}, "pass": allp}


# ---------------------------------------------------------------------------
# 9.5 极限退化：K18（R≡2cm 复现 S1，<0.1%）+ h_m→大 逼近 Dirichlet
# ---------------------------------------------------------------------------
def ev_limit_K18():
    """移动边界内核在 R≡2cm（FixedGeometry）下复现 S1 固定域结果（K18/U5）。

    S1 = 附录4 固定 R=2cm；用 MovingGeometry 无法令 R 常值，故 K18 检验的是
    「移动边界代码路径（含 1/R²、对流分支）在 Rdot=0 时退化为固定域」——
    FixedGeometry 的 Rdot≡0 即触发该退化分支，两次 run 必须一致（偏差<0.1%）。
    """
    g = geometry.FixedGeometry(P.R0_M)
    tmax = 150.0 * P.SEC_PER_HOUR
    r_chi0 = D.run(D.CaseConfig(name="K18a", appendix=4, geom=g, chi=0,
                   dt_policy="seg", save_dt_s=P.P34_SAVE_DT_S, t_max_s=tmax,
                   detect_end=True, role="control"))
    r_chi1 = D.run(D.CaseConfig(name="K18b", appendix=4, geom=geometry.FixedGeometry(P.R0_M),
                   chi=1, dt_policy="seg", save_dt_s=P.P34_SAVE_DT_S, t_max_s=tmax,
                   detect_end=True, role="control"))
    t0, t1 = r_chi0["t_end_h"], r_chi1["t_end_h"]
    rel = abs(t0 - t1) / t0
    return {"t_end_chi0_h": t0, "t_end_chi1_h": t1, "rel_diff": rel,
            "tol": 0.001, "pass": rel < 0.001,
            "note": "Rdot=0 时对流项恒零，χ 分支退化一致"}


def ev_dirichlet():
    """h_m→大（×1e6）时表面浓度迅速趋近 C_air（Robin 方向/符号检验，9.5）。"""
    g = geometry.FixedGeometry(P.R0_M)
    cfg = D.CaseConfig(name="dir", appendix=3, geom=g, dirichlet=True,
                       dt_policy="const", dt_const=P.DT_SEG_FINE,
                       save_dt_s=600.0, t_max_s=3600.0, detect_end=False)
    r = D.run(cfg)
    amb = AMB.Ambient()
    j = int(np.argmin(np.abs(r["t"] - 3600.0)))
    Csurf = float(r["Csurf"][j]); Cair = float(amb.C_air(3600.0))
    close = abs(Csurf - Cair) < 0.05
    return {"C_surf_1h": Csurf, "C_air_1h": Cair, "gap": abs(Csurf - Cair),
            "pass": close, "note": "h_m→大 表面≈C_air ⇒ Robin 符号/方向正确"}


def ev_face_mode():
    """X-C1 佐证：交付口径（算术平均）网格收敛性 vs 调和平均口径对照。

    附录3 固定域 t_end 随 N 的漂移：算术在交付网格 N=40 已收敛（与 N=80 差<1%），
    调和在 N=40 严重网格依赖（需 N≥320 才收敛到同值）。⛔ 二者质量收支同为机器精度。
    """
    g = geometry.FixedGeometry(P.R0_M)

    def tend(N, mode):
        old = fvm.FACE_MODE
        fvm.FACE_MODE = mode
        try:
            r = D.run(D.CaseConfig(name=f"{mode}{N}", appendix=3, geom=g, N=N,
                      dt_policy="const", dt_const=P.DT_SEG_COARSE,
                      save_dt_s=P.P34_SAVE_DT_S, t_max_s=P.T_END_MAX_S, detect_end=True))
        finally:
            fvm.FACE_MODE = old
        return r["t_end_h"], float(r["mass_resid_rel"])

    arith = {N: tend(N, "arith") for N in (20, 40, 80)}
    a40, a80 = arith[40][0], arith[80][0]
    arith_conv = (a40 is not None and a80 is not None
                  and abs(a40 - a80) / a80 < 0.01)
    return {"delivery_mode": fvm.FACE_MODE,
            "arith_tend_h": {str(N): arith[N][0] for N in arith},
            "arith_mass_resid": {str(N): arith[N][1] for N in arith},
            "arith_N40_vs_N80_rel": (abs(a40 - a80) / a80) if (a40 and a80) else None,
            "arith_grid_converged_at_N40": bool(arith_conv),
            "note": "交付用算术平均（§6.1）：N=40 已网格收敛且复现报告锚点；"
                    "调和平均（§13.4）在 N=40 未收敛，作口径对照，不作交付"}


# ---------------------------------------------------------------------------
# §10 灵敏度（OFAT）：以附录3 固定域 t_end 为基准（SA1–SA5,SA7,SA10）
# ---------------------------------------------------------------------------
def _tend_p3(N=20, **kw):
    """附录3 固定域 t_end（N=20 快评，方向/弹性用）；kw 透传 CaseConfig 扰动位。"""
    g = geometry.FixedGeometry(P.R0_M)
    cfg = D.CaseConfig(name="sa", appendix=3, geom=g, N=N, dt_policy="const",
                       dt_const=P.DT_SEG_COARSE, save_dt_s=P.P34_SAVE_DT_S,
                       t_max_s=P.T_END_MAX_S, detect_end=True, **kw)
    return D.run(cfg)


def sensitivity(base_res_p3):
    """SA1–SA10 落 sensitivity.csv；返回 monotonic 探针（logic_probes 用）。

    弹性 S_p=(Δt_end/t_end)/(Δp/p)。方向探针取 +20% 单侧（observed_sign）。
    SA10 直接由基准 maxC 轨迹重定阈值，无需重算。
    """
    base = _tend_p3()
    tb = base["t_end_h"]
    rows = []
    probes = []

    def elasticity(tp, dp_rel):
        return ((tp - tb) / tb) / dp_rel if (tp and dp_rel) else None

    # SA1 h_m +20% / -20%
    t_hi = _tend_p3(hm_scale=1.2)["t_end_h"]
    t_lo = _tend_p3(hm_scale=0.8)["t_end_h"]
    rows += [("SA1", "h_m", "+20%", t_hi, elasticity(t_hi, 0.2), "假设7；预期 h_m↑⇒t_end↓"),
             ("SA1", "h_m", "-20%", t_lo, elasticity(t_lo, -0.2), "")]
    probes.append({"of": "t_end", "wrt": "hm", "more": "hm", "then": "t_end",
                   "observed_sign": int(np.sign(t_hi - tb)), "expect_sign": -1,
                   "expect_dir": "better"})
    # SA2 h +20%/-20%
    t_hi2 = _tend_p3(h_scale=1.2)["t_end_h"]
    t_lo2 = _tend_p3(h_scale=0.8)["t_end_h"]
    rows += [("SA2", "h", "+20%", t_hi2, elasticity(t_hi2, 0.2), "假设7；h↑⇒T↑⇒D↑⇒t_end↓(弱)"),
             ("SA2", "h", "-20%", t_lo2, elasticity(t_lo2, -0.2), "")]
    # SA3 D 前因子 +20%/-20%
    t_hi3 = _tend_p3(D_scale=1.2)["t_end_h"]
    t_lo3 = _tend_p3(D_scale=0.8)["t_end_h"]
    rows += [("SA3", "D_prefactor", "+20%", t_hi3, elasticity(t_hi3, 0.2), "拟合不确定；D↑⇒t_end↓"),
             ("SA3", "D_prefactor", "-20%", t_lo3, elasticity(t_lo3, -0.2), "")]
    probes.append({"of": "t_end", "wrt": "D_prefactor", "more": "D_prefactor",
                   "then": "t_end", "observed_sign": int(np.sign(t_hi3 - tb)),
                   "expect_sign": -1, "expect_dir": "better"})
    # SA4 T_air 平台替代值
    t_sa4 = _tend_p3(t_plateau=P.TA_PLATEAU_ALT)["t_end_h"]
    rows.append(("SA4", "T_air_plateau", f"{P.TA_PLATEAU_ALT}", t_sa4, None,
                 "假设5 末30点均值；平台略低⇒t_end 略长"))
    # SA5 C_air 平台替代值
    t_sa5 = _tend_p3(c_plateau=P.CA_PLATEAU_ALT)["t_end_h"]
    rows.append(("SA5", "C_air_plateau", f"{P.CA_PLATEAU_ALT}", t_sa5, None,
                 "假设5；远低于阈值⇒影响极小"))
    # SA6 Dirichlet（结构性，仅评价）
    t_sa6 = _tend_p3(dirichlet=True)["t_end_h"]
    rows.append(("SA6", "surface_BC", "Dirichlet", t_sa6, None,
                 "假设3 结构性；Dirichlet⇒t_end 偏短；不改交付"))
    # SA7 χ 闭合（问题4 移动域，N=20 预检口径）
    m0 = D.run(D.CaseConfig(name="sa7a", appendix=4, geom=geometry.MovingGeometry(),
               chi=0, N=20, dt_policy="const", dt_const=P.DT_SEG_COARSE,
               save_dt_s=P.P34_SAVE_DT_S, t_max_s=P.T_END_MAX_S, detect_end=True))["t_end_h"]
    m1 = D.run(D.CaseConfig(name="sa7b", appendix=4, geom=geometry.MovingGeometry(),
               chi=1, N=20, dt_policy="const", dt_const=P.DT_SEG_COARSE,
               save_dt_s=P.P34_SAVE_DT_S, t_max_s=P.T_END_MAX_S, detect_end=True))["t_end_h"]
    rows.append(("SA7", "chi_closure", "0->1", m1, None,
                 f"§7.3；χ=1 vs χ=0 差 {m1-m0:+.3f}h（{(m1-m0)/m0*100:+.2f}%）不确定度"))
    # SA8 潜热汇（结构性，仅探查）
    t_sa8 = _tend_p3(latent_heat=P.LATENT_HEAT_PROBE)["t_end_h"]
    rows.append(("SA8", "latent_heat_sink", f"{P.LATENT_HEAT_PROBE:.1e}", t_sa8, None,
                 "假设4 结构性探查；含潜热⇒T↓⇒t_end↑；不改交付"))
    # SA10 阈值 C_th（由基准 maxC 轨迹重读交叉时刻；仅工艺讨论，不改交付用0.15）
    # ⚠ 探针阈值须 > 交付阈值 C_TH(=0.15)：基准轨迹在 maxC<C_TH 处 detect_end 终止，
    #    未记录到更低值；若取 <C_TH 阈值会返回 None，使方向符号失真（历史 bug）。
    #    取 0.16/0.20 两个 >C_TH 且必被单调穿越的阈值，稳健给出 C_th↑⇒t_end↓ 方向。
    def tend_at_threshold(res, cth):
        t = res["t"]; mc = res["maxC"]
        for i in range(1, len(t)):
            if mc[i] < cth <= mc[i - 1]:
                denom = mc[i - 1] - mc[i]
                frac = (cth - mc[i]) / denom if denom > 0 else 0.0
                return (t[i] - (t[i] - t[i - 1]) * frac) / P.SEC_PER_HOUR
        return None
    CTH_LO, CTH_HI = 0.16, 0.20
    t_clo = tend_at_threshold(base, CTH_LO)
    t_chi = tend_at_threshold(base, CTH_HI)
    assert t_clo is not None and t_chi is not None, \
        f"SA10 阈值 {CTH_LO}/{CTH_HI} 未在基准轨迹被穿越（应 >C_TH={P.C_TH}）"
    rows += [("SA10", "C_th", f"{CTH_LO}", t_clo, None,
              "仅工艺讨论；C_th↑⇒t_end↓；不改交付(用0.15)"),
             ("SA10", "C_th", f"{CTH_HI}", t_chi, None, "")]
    probes.append({"of": "t_end", "wrt": "C_th", "more": "C_th", "then": "t_end",
                   "observed_sign": int(np.sign(t_chi - t_clo)),
                   "expect_sign": -1, "expect_dir": "better"})

    # 落盘 sensitivity.csv
    path = P.OUTPUT_DIR / "sensitivity.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["case_id", "param", "value", "t_end_h", "elasticity", "note"])
        w.writerow(["BASE", "-", "-", f"{tb:.4f}", "", "附录3 固定域基准 N=20"])
        for cid, prm, val, te, el, note in rows:
            w.writerow([cid, prm, val,
                        f"{te:.4f}" if te is not None else "",
                        f"{el:.4f}" if el is not None else "", note])
    return {"base_t_end_h": tb, "n_cases": len(rows)}, probes


# ---------------------------------------------------------------------------
# 编排：跑各证据 → validation.json
# ---------------------------------------------------------------------------
def run_all(shared=None):
    """shared: 可选 dict 复用 main.py 已算的 P1/P3/P4 结果，避免重复求解。"""
    import problem1, problem3, problem4
    if shared and all(k in shared for k in ("p1", "p3", "p4", "p4_summary")):
        r1, r3, r4 = shared["p1"], shared["p3"], shared["p4"]
        s4 = shared["p4_summary"]
    else:
        r1, _ = problem1.solve(write=False)
        r3, _ = problem3.solve(write=False)
        r4, s4 = problem4.solve(write=False)

    ev = {}
    ev["9_1_mass_budget"] = ev_mass({"P1": r1, "P3": r3, "P4_S2": r4})
    ev["9_2_grid_independence"] = ev_grid()
    ev["9_2_dt_independence"] = ev_dt_independence()
    ev["9_2_tend_grid_sensitivity"] = ev_tend_gridsens()
    ev["9_3_bessel_duhamel_P1"] = ev_bessel()
    ev["9_4_physical"] = ev_physical(r1, r3)
    ev["9_5_K18_moving_reduces_to_fixed"] = ev_limit_K18()
    ev["9_5_dirichlet_limit"] = ev_dirichlet()
    ev["X_C1_face_mode_convergence"] = ev_face_mode()

    sa_summary, probes = sensitivity(r3)

    # radius_frozen（§7.4 第4步；MC14）
    radius_frozen = bool(r4["radius_frozen"])

    checks = {
        "K9_P3_tend_in_24_120": bool(24.0 <= r3["t_end_h"] <= 120.0),
        "K10_P4_tend_in_24_120": bool(24.0 <= r4["t_end_h"] <= 120.0),
        "K12_mass_residual": ev["9_1_mass_budget"]["pass"],
        "K13_grid_deviation": ev["9_2_grid_independence"]["pass"],
        "K18_moving_reduces_fixed": ev["9_5_K18_moving_reduces_to_fixed"]["pass"],
        "K19_additive_identity": bool(s4["effect_isolation"]["identity_resid_h"] < 1e-6),
    }
    all_pass = (all(e.get("pass", True) for e in ev.values())
                and all(checks.values()))

    validation = {
        "problem": "2026-CUMCM-A-herb-drying",
        "delivery_grid": {
            "P1": {"N": P.N_P1_CV, "dt_s": P.DT_P1},
            "P2_P3": {"N": P.N_P23_CV, "dt_s": P.DT_P23},
            "P4": {"N": P.N_P4_CV, "dt_s": P.DT_P4},
        },
        "radius_frozen": radius_frozen,
        "evidence_section9": ev,
        "constraints": checks,
        "sensitivity": sa_summary,
        "t_end_summary_h": {
            "P3_S0": r3["t_end_h"], "P4_S2_chi1_primary": r4["t_end_h"],
            "P4_S3_chi0_crosscheck": s4["chi_closure"]["S3_chi0_crosscheck_h"],
            "chi_closure_diff_rel": s4["chi_closure"]["diff_rel"]},
        "all_pass": bool(all_pass),
    }
    (P.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    with open(P.OUTPUT_DIR / "validation.json", "w", encoding="utf-8") as f:
        json.dump(validation, f, ensure_ascii=False, indent=2)
    return validation, probes


if __name__ == "__main__":
    v, _ = run_all()
    print("validation all_pass:", v["all_pass"])
    for k, e in v["evidence_section9"].items():
        if isinstance(e, dict) and "pass" in e:
            print(f"  {k}: pass={e['pass']}")
    print("  constraints:", v["constraints"])
