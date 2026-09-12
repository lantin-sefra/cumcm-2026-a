"""四问统一时间推进引擎（MODELING_REPORT §6.2、§7.5、§11）。

单一 run(cfg) 覆盖问题1/2/3/4 与兼容性诊断：
- 每步严格保序算子分裂（①ρ,cp,k → ②解 T^{n+1} → ③用 T^{n+1} 算 D → ④解 C^{n+1}
  → ⑤C 下限 → ⑥Picard 复核），顺序不可交换（§11、§13.4 MC4）；
- 正式调用显式传入步长：问题1为0.125s，问题2/3与问题4均为0.2500s；跨输出时刻截断步长精确命中；
- 终止事件按逐点最大值首次 <C_th，式(19) 亚步线性插值定位 t_end（§6.4、K11）；
- 移动边界经 ξ 网格统一处理；问题4正式配置χ=1，χ=0仅作Eulerian/Landau交叉验证；
- 快照按输出网格记录，节点场插值到固定 r 列，问题4 对 r>R(t) 置空、末列取 ξ=1（§7.7、式(26)）。
⛔ 不使用 solve_ivp（§11）；界面调和平均（MC2）；下限 1e-3≪0.15（§6.2）。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np

import params as P
import props as PR
import fvm


@dataclass
class CaseConfig:
    """一次推进的完整配置。几何对象须实现 R(t)/Rdot(t)（geometry.py）。"""
    name: str
    appendix: int                 # 物性附录 2/3/4
    geom: object                  # FixedGeometry 或 MovingGeometry
    chi: int = P.CHI_PRIMARY      # 兼容默认；问题4显式传入χ=1，χ=0仅作交叉验证
    N: int = P.N_CV               # 控制体数
    dt_policy: str = "seg"        # 'p1'(=1s) | 'seg'(2s→4s) | 'const'
    dt_const: float = P.DT_SEG_FINE
    save_dt_s: float = P.P34_SAVE_DT_S   # 输出网格步长
    t_max_s: float = P.T_END_MAX_S       # 仿真硬上限
    detect_end: bool = True       # 是否检测达标事件
    event_each_step: bool = False # 是否在每个内部步定位事件（默认保持原输出步检测）
    store_nodes: bool = False     # 是否保存全节点 ξ 场（问题4 表6 需要）
    dirichlet: bool = False       # SA6：h,h_m→大，退化 Dirichlet
    h_scale: float = 1.0          # SA2
    hm_scale: float = 1.0         # SA1
    D_scale: float = 1.0          # SA3
    t_plateau: Optional[float] = None   # SA4
    c_plateau: Optional[float] = None   # SA5
    latent_heat: float = 0.0      # SA8 潜热汇 J/kg（默认 0，假设4）
    ambient: object = None        # Ambient 实例（None 时内部构造）
    role: str = "deliverable"     # 'deliverable' | 'control'（S1 免 H18）

    def dt_at(self, t):
        """给定当前时刻返回策略步长。"""
        if self.dt_policy == "p1":
            return P.DT_P1
        if self.dt_policy == "const":
            return self.dt_const
        return P.DT_SEG_FINE if t < P.DT_SWITCH_S else P.DT_SEG_COARSE


def _interp_cols(phi_nodes, R, cols_m):
    """节点场（ξ 均布）插值到固定物理半径列 cols_m；r>R(t) 置 NaN（§7.7 式26）。"""
    n = phi_nodes.size - 1
    r_nodes = np.linspace(0.0, R, n + 1)
    out = np.interp(cols_m, r_nodes, phi_nodes)
    out = np.where(cols_m > R + 1e-12, np.nan, out)
    return out


def _adv_net_mass(C, xi, Rdot, R, dxi, Vt, chi):
    """迎风对流项对总量的净贡献（浓度方程 κ=1；用于全局质量收支复核）。

    与 fvm.step_implicit 内一致：g=ξ·Rdot/R·Ṽ≤0，进 di/lo/up。
    返回 Σ(di_adv·C + lo_adv[1:]·C[:-1] + up_adv[:-1]·C[1:])。
    """
    if chi != 0 or Rdot == 0.0:
        return 0.0
    g = xi * (Rdot / R) * Vt
    di_adv = np.abs(g) / dxi
    lo_adv = np.where(g <= 0.0, g / dxi, 0.0)
    up_adv = np.where(g > 0.0, -g / dxi, 0.0)
    return float(np.sum(di_adv * C)
                 + np.sum(lo_adv[1:] * C[:-1])
                 + np.sum(up_adv[:-1] * C[1:]))


def run(cfg: CaseConfig):
    """推进一个 CaseConfig，返回结果字典（见文件末尾字段说明）。"""
    import ambient as AMB
    amb = cfg.ambient if cfg.ambient is not None else AMB.Ambient(
        t_plateau=cfg.t_plateau, c_plateau=cfg.c_plateau)

    xi, dxi, Vt = fvm.make_grid(cfg.N)
    N = cfg.N
    cols_m = np.asarray(P.DIST_COLS_CM, dtype=float) * P.CM_TO_M   # 21 固定列 (m)

    # Robin 系数：SA6 Dirichlet 以大 β 实现（U2/§9.5）
    big = 1.0e9
    beta_T = big if cfg.dirichlet else P.H_CONV * cfg.h_scale
    beta_C = big if cfg.dirichlet else P.HM_CONV * cfg.hm_scale

    # 初值
    T = np.full(N + 1, P.T0_C)
    C = np.full(N + 1, P.C0)
    C0_tot = None                      # 初始总量（ξ 度量），用于式(27)相对残差

    # 累计诊断
    resid_step_max = 0.0
    mass_bal_abs = 0.0                 # Σ 储存变化 − Σ 表面通量 + Σ 对流净额（ξ 度量）
    picard_iters_max = 0
    picard_nonconv = 0
    floor_trunc_steps = 0
    dt_halving = 0

    # 快照容器（按输出网格）
    snap_t = []
    snap_Tcol = []
    snap_Ccol = []
    snap_Tsurf = []
    snap_Csurf = []
    snap_maxC = []
    snap_Tc = []                       # 中心温度
    snap_Cc = []                       # 中心浓度
    snap_R = []
    snap_nodesC = [] if cfg.store_nodes else None
    snap_nodesT = [] if cfg.store_nodes else None

    def record(t_now, Tf, Cf, Rn):
        snap_t.append(t_now)
        snap_Tcol.append(_interp_cols(Tf, Rn, cols_m))
        snap_Ccol.append(_interp_cols(Cf, Rn, cols_m))
        snap_Tsurf.append(float(Tf[N]))
        snap_Csurf.append(float(Cf[N]))
        snap_maxC.append(float(np.max(Cf)))
        snap_Tc.append(float(Tf[0]))
        snap_Cc.append(float(Cf[0]))
        snap_R.append(float(Rn))
        if cfg.store_nodes:
            snap_nodesC.append(Cf.copy())
            snap_nodesT.append(Tf.copy())

    R0 = float(cfg.geom.R(0.0))
    C0_tot = float(np.sum(Vt * C))
    record(0.0, T, C, R0)

    t = 0.0
    save_idx = 1
    next_save = save_idx * cfg.save_dt_s
    t_end = None
    end_T = None
    end_C = None
    end_R = None
    reached = False
    prev_maxC = float(np.max(C))
    prev_t = 0.0
    event_prev_maxC = prev_maxC
    event_prev_t = prev_t

    while t < cfg.t_max_s - 1e-9:
        dt = cfg.dt_at(t)
        # 跨越输出时刻：截断步长精确命中（§13.3）
        landed = False
        if t + dt >= next_save - 1e-9:
            dt = next_save - t
            landed = True
        if t + dt > cfg.t_max_s:
            dt = cfg.t_max_s - t
            landed = False
        t_new = t + dt

        Rn = float(cfg.geom.R(t_new))
        Rdot = float(cfg.geom.Rdot(t_new))
        Tair = float(amb.T_air(t_new))
        Cair = float(amb.C_air(t_new))

        # ---- 保序算子分裂 + Picard（§11 步 1–6）----
        T_it = T.copy()
        C_it = C.copy()
        dC_lag = np.zeros(N + 1)            # 潜热汇滞后项（SA8）
        n_it = 0
        for m in range(P.PICARD_MAX):
            n_it = m + 1
            rho, cp, k, _ = PR.props(cfg.appendix, C_it, T_it)
            capT = rho * cp
            srcT = None
            if cfg.latent_heat > 0.0:
                # 潜热汇：蒸发吸热 = λ·ρ_s·(−ΔC)/Δt·Ṽ，滞后一次迭代（探查用）
                srcT = -cfg.latent_heat * PR.rho_s_eff(cfg.appendix, C_it) * (-dC_lag) * Vt / dt
            T_new = fvm.step_implicit(T, capT, k, beta_T, Tair, Rn, Rdot, cfg.chi,
                                      dt, xi, dxi, Vt, src=srcT)
            _, _, _, D = PR.props(cfg.appendix, C_it, T_new)
            D = np.maximum(D * cfg.D_scale, P.D_FLOOR)
            capC = np.ones(N + 1)
            C_new = fvm.step_implicit(C, capC, D, beta_C, Cair, Rn, Rdot, cfg.chi,
                                      dt, xi, dxi, Vt)
            dT_it = float(np.max(np.abs(T_new - T_it)))
            dC_it = float(np.max(np.abs(C_new - C_it)))
            dC_lag = C_new - C
            T_it, C_it = T_new, C_new
            if m >= 1 and dT_it < P.PICARD_TOL_T and dC_it < P.PICARD_TOL_C:
                break
        else:
            picard_nonconv += 1
        picard_iters_max = max(picard_iters_max, n_it)

        # 步 5：浓度下限保护（§6.2；记录截断步数）
        below = C_it < P.C_FLOOR
        if np.any(below):
            floor_trunc_steps += 1
            C_it = np.maximum(C_it, P.C_FLOOR)

        # 全局质量收支（ξ 度量，式27 分子逐步累加）
        sfc = 2.0 * np.pi * beta_C / Rn
        flux = sfc * (Cair - C_it[N])                    # 表面净流入速率
        adv = _adv_net_mass(C_it, xi, Rdot, Rn, dxi, Vt, cfg.chi)
        stored_rate = float(np.sum(Vt * (C_it - C)) / dt)
        resid_step_max = max(resid_step_max, abs(stored_rate - flux + adv))
        mass_bal_abs += (float(np.sum(Vt * (C_it - C))) - flux * dt + adv * dt)

        T_prev_step, C_prev_step = T, C
        T, C = T_it, C_it
        t = t_new

        # 步 6/7：达标事件（逐点最大值，式19 亚步插值）+ 快照
        maxC = float(np.max(C))
        if (cfg.detect_end and cfg.event_each_step and not reached
                and maxC <= P.C_TH < event_prev_maxC):
            denom = event_prev_maxC - maxC
            frac = (event_prev_maxC - P.C_TH) / denom if denom > 0 else 1.0
            t_end = event_prev_t + (t - event_prev_t) * frac
            end_T = T_prev_step + frac * (T - T_prev_step)
            end_C = C_prev_step + frac * (C - C_prev_step)
            end_R = float(cfg.geom.R(t_end))
            reached = True
        event_prev_maxC = maxC
        event_prev_t = t

        if landed and abs(t - next_save) < 1e-6:
            record(t, T, C, Rn)
            if (cfg.detect_end and not cfg.event_each_step and not reached
                    and maxC < P.C_TH <= prev_maxC):
                denom = prev_maxC - maxC
                frac = (P.C_TH - maxC) / denom if denom > 0 else 0.0
                t_end = t - cfg.save_dt_s * frac
                end_T = None
                end_C = None
                end_R = float(cfg.geom.R(t_end))
                reached = True
            prev_maxC = maxC
            prev_t = t
            save_idx += 1
            next_save = save_idx * cfg.save_dt_s
            if reached and cfg.detect_end:
                break
        elif reached and cfg.detect_end:
            break

    # ---- 打包 ----
    out = {
        "name": cfg.name,
        "appendix": cfg.appendix,
        "chi": cfg.chi,
        "N": N,
        "dt_policy": cfg.dt_policy,
        "save_dt_s": cfg.save_dt_s,
        "role": cfg.role,
        "t": np.asarray(snap_t),
        "Tcol": np.asarray(snap_Tcol),          # (nt,21) 固定列温度
        "Ccol": np.asarray(snap_Ccol),          # (nt,21) 固定列浓度
        "Tsurf": np.asarray(snap_Tsurf),
        "Csurf": np.asarray(snap_Csurf),
        "maxC": np.asarray(snap_maxC),
        "Tcenter": np.asarray(snap_Tc),
        "Ccenter": np.asarray(snap_Cc),
        "R": np.asarray(snap_R),
        "cols_m": cols_m,
        "t_end_s": t_end,
        "t_end_h": (t_end / P.SEC_PER_HOUR) if t_end is not None else None,
        "end_T": end_T,
        "end_C": end_C,
        "end_R": end_R,
        "reached": reached,
        "resid_step_max": resid_step_max,
        "mass_resid_rel": abs(mass_bal_abs) / C0_tot if C0_tot else float("nan"),
        "picard_iters_max": picard_iters_max,
        "picard_nonconv": picard_nonconv,
        "floor_trunc_steps": floor_trunc_steps,
        "dt_halving": dt_halving,
        "radius_frozen": bool(getattr(cfg.geom, "radius_frozen", False)),
        "final_T": T.copy(),
        "final_C": C.copy(),
    }
    if cfg.store_nodes:
        out["nodesC"] = np.asarray(snap_nodesC)     # (nt,N+1)
        out["nodesT"] = np.asarray(snap_nodesT)
    return out


def field_at_time(res, t_query_s, which="C"):
    """在两快照间线性插值出 t_query 时刻的 21 列场（末行「烘干结束时间」用）。"""
    ts = res["t"]
    col = res["Ccol"] if which == "C" else res["Tcol"]
    if t_query_s <= ts[0]:
        return col[0].copy()
    if t_query_s >= ts[-1]:
        return col[-1].copy()
    j = int(np.searchsorted(ts, t_query_s))
    t0, t1 = ts[j - 1], ts[j]
    w = (t_query_s - t0) / (t1 - t0) if t1 > t0 else 0.0
    return (1.0 - w) * col[j - 1] + w * col[j]
