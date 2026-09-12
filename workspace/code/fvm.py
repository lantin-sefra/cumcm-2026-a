"""有限体积内核（柱坐标控制体 + 全隐式后向 Euler，MODELING_REPORT §6.1、§7.5）。

统一在归一化坐标 ξ=r/R(t)∈[0,1] 上离散：
- 固定域（问题1/2/3）：R≡R0 常值、Rdot=0，退化为物理坐标（×R^2 后逐点等价，见 K18/U5）；
- 移动边界（问题4）：R(t)、Rdot(t) 由附件2 给出，含 (1-χ)·ξ·Rdot/R·∂ξφ 对流项。

界面输运系数取相邻节点平均（口径 FACE_MODE，交付用算术平均 §6.1；调和 §13.4 供对照）；
界面通量以 2π·ξ_{i±1/2}·Γ 面积权重体现 1/r 因子。
表面 Robin 以通量形式并入（§6.1）；中心零通量为自然边界（无需显式施加）。
对流项用一阶上风离散：Rdot≤0 ⇒ 平流速度 v=-ξ·Rdot/R≥0 ⇒ 迎风取后向差分，保证系数矩阵对角占优。
"""
from __future__ import annotations

import numpy as np
from scipy.linalg import solve_banded

import params as P


def make_grid(N=None):
    """返回 ξ 节点(N+1)、Δξ、单位长度控制体体积 Ṽ(N+1)（ξ 度量）。"""
    if N is None:
        N = P.N_CV
    dxi = 1.0 / N
    xi = np.linspace(0.0, 1.0, N + 1)
    Vt = np.empty(N + 1)
    Vt[0] = np.pi * (dxi / 2.0) ** 2
    Vt[1:N] = 2.0 * np.pi * xi[1:N] * dxi
    Vt[N] = np.pi * (1.0 - (1.0 - dxi / 2.0) ** 2)
    return xi, dxi, Vt


# 界面平均口径（正式结果用算术平均；调和平均仅作历史对照）：
# 'arith' —— §6.1 正文「相邻节点算术平均」。正式默认。
#            正式问题三配置：N=2560、dt=0.25 s、t_end=57.4716 h。
#            下方 N=20 / N=40 / 56.18 h 等数字是历史粗网格诊断，不作为正式结果。
# 'harm'  —— §13.4 指定的调和平均，仅作口径对照。
#            历史粗网格下收敛更慢（N=40 未收敛、需 N≥320），不作为正式交付口径。
# ⛔ 两种口径均给出左右唯一的界面值，质量收支同为机器精度；
#    分歧只是收敛速度与物理偏好，不改变本文件中的离散算法。
FACE_MODE = "arith"


def face_mean(G, mode=None):
    """相邻节点界面平均，返回长度 N 的界面值（i+1/2, i=0..N-1）。

    mode='arith' 算术平均（§6.1，交付默认）；'harm' 调和平均（§13.4，供对照）。
    G 可能为 0（D→0），调和口径此时取 0（无输运），避免 0/0。
    """
    mode = FACE_MODE if mode is None else mode
    Gi = G[:-1]
    Gi1 = G[1:]
    if mode == "arith":
        return 0.5 * (Gi + Gi1)
    denom = Gi + Gi1
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(denom > 0.0, 2.0 * Gi * Gi1 / denom, 0.0)


def harmonic_face(G):
    """向后兼容别名（调和口径）。新代码用 face_mean。"""
    return face_mean(G, mode="harm")


def step_implicit(phi_old, cap, G, beta, phi_air, R, Rdot, chi, dt, xi, dxi, Vt,
                  return_diag=False, src=None):
    """推进一个隐式时间步，返回 phi_new（长度 N+1）。

    参数：
      phi_old : 上一时刻场量 (N+1,)
      cap     : 容量系数 κ 逐点 (N+1,)  —— 温度取 ρc_p，浓度取 1
      G       : 输运系数 Γ 逐点 (N+1,)  —— 温度取 k，浓度取 D（已施 D_FLOOR）
      beta    : Robin 系数（h 或 h_m）
      phi_air : 环境侧驱动值（标量）
      R, Rdot : 当前半径与收缩速率
      chi     : 骨架闭合开关。
                χ=1：材料随动 ALE 正式主模型，相对对流项抵消；
                χ=0：Eulerian/Landau 交叉验证，保留相对对流项。
                本函数的数学实现不因上述口径说明而改变。
      dt      : 时间步长
      xi,dxi,Vt : make_grid 输出
      return_diag : True 时额外返回离散守恒残差（§9.1/K12 质量收支）
      src     : 逐控制体体积分源项 (N+1,)，rhs += src；默认 None（SA8 潜热汇 / U4 单测）

    返回：phi_new，或 (phi_new, resid_abs)。resid_abs 为独立核算的守恒残差
      |Δ储存率 − 表面净通量 + 对流净额|，扩散界面通量解析对消 ⇒ 应≈机器精度。
    """
    N = phi_old.size - 1
    R2 = R * R

    # 界面平均输运系数（i+1/2, i=0..N-1），口径由 FACE_MODE 决定（默认算术，§6.1）
    Gf = face_mean(G)
    xi_face = (np.arange(N) + 0.5) * dxi          # ξ_{i+1/2}
    aE = (2.0 * np.pi / R2) * xi_face * Gf / dxi  # 东面导纳，长度 N

    # 三对角：A[i,i-1]=lo[i], A[i,i]=di[i], A[i,i+1]=up[i]
    di = cap * Vt / dt                            # 时间项
    lo = np.zeros(N + 1)
    up = np.zeros(N + 1)

    # 扩散（每个界面同时进入两侧节点方程）
    di[0:N] += aE
    up[0:N] += -aE
    di[1:N + 1] += aE
    lo[1:N + 1] += -aE

    rhs = (cap * Vt / dt) * phi_old

    # 表面 Robin（节点 N）：sfc = 2π·β/R
    sfc = 2.0 * np.pi * beta / R
    di[N] += sfc
    rhs[N] += sfc * phi_air

    # 可选体积分源项（SA8 潜热汇 / U4 线性场源；默认无）
    if src is not None:
        rhs = rhs + src

    # 对流项（仅 χ=0）：g_i = (1-χ)·κ_i·ξ_i·Rdot/R·Ṽ_i，一阶迎风
    lo_adv = up_adv = di_adv = None
    if chi == 0 and Rdot != 0.0:
        g = cap * xi * (Rdot / R) * Vt            # ≤0（Rdot≤0）
        di_adv = np.abs(g) / dxi
        lo_adv = np.where(g <= 0.0, g / dxi, 0.0)  # 迎风：g≤0 → 后向差分进 lo
        up_adv = np.where(g > 0.0, -g / dxi, 0.0)  # g>0 → 前向差分进 up
        di += di_adv
        lo += lo_adv
        up += up_adv

    ab = np.zeros((3, N + 1))
    ab[0, 1:] = up[0:N]        # 超对角 A[i,i+1] 置于列 i+1
    ab[1, :] = di
    ab[2, :-1] = lo[1:N + 1]   # 次对角 A[i,i-1] 置于列 i-1
    phi_new = solve_banded((1, 1), ab, rhs)

    if not return_diag:
        return phi_new

    # 独立守恒核算：储存率 = 表面净通量 − 对流净额（扩散逐面对消）
    stored = float(np.sum(cap * Vt * (phi_new - phi_old)) / dt)
    qsurf = float(sfc * (phi_air - phi_new[N]))
    adv_net = 0.0
    if di_adv is not None:
        adv_net = float(np.sum(di_adv * phi_new)
                        + np.sum(lo_adv[1:] * phi_new[:-1])
                        + np.sum(up_adv[:-1] * phi_new[1:]))
    resid_abs = abs(stored - qsurf + adv_net)
    return phi_new, resid_abs


def discrete_operator(phi, G, R, xi, dxi, Vt):
    """对给定场返回柱坐标扩散算子的逐控制体积分值（诊断/单元测试用）。

    返回 (1/κV)·[界面通量净额]，用于 §6.1 的 φ=r^2 → 算子=4 校验。
    此处返回未除容量的净通量除以 Vt（即算子近似值）。
    """
    N = phi.size - 1
    R2 = R * R
    Gf = face_mean(G)
    xi_face = (np.arange(N) + 0.5) * dxi
    aE = (2.0 * np.pi / R2) * xi_face * Gf / dxi
    flux_E = aE * (phi[1:] - phi[:-1])            # 东面净通量，长度 N
    net = np.zeros(N + 1)
    net[0:N] += flux_E
    net[1:N + 1] -= flux_E
    return net / Vt
