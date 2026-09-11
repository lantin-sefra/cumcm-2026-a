"""三套附录物性模块（严格按问题隔离，MODELING_REPORT §4）。

props(appendix, C, T_celsius) -> (rho, cp, k, D)，全部返回与 C 同形状的 ndarray。
⛔ rho 用干基 C，cp/k 用湿基 w=C/(C+1)；D 中温度用绝对温度 K 且取药材局部温度。
附录2 的 D 不含温度项。附录之间禁止串用（K14）。
"""
from __future__ import annotations

import numpy as np

import params as P


def wet_basis(C):
    """湿基分率 w = C/(C+1)。"""
    C = np.asarray(C, dtype=float)
    return C / (C + 1.0)


def props(appendix: int, C, T_celsius=None):
    """返回 (rho, cp, k, D)，均为与 C 同形状的 ndarray。

    appendix ∈ {2,3,4}。附录3/4 需要 T_celsius（药材局部温度，℃）。
    """
    C = np.asarray(C, dtype=float)

    if appendix == 2:
        rho = np.full_like(C, P.APP2_RHO)
        cp = np.full_like(C, P.APP2_CP)
        k = np.full_like(C, P.APP2_K)
        D = P.APP2_D_PREF * np.exp(-P.APP2_D_EC / C)
        return rho, cp, k, D

    if T_celsius is None:
        raise ValueError(f"附录{appendix} 的 D 依赖温度，必须提供 T_celsius")
    T_celsius = np.asarray(T_celsius, dtype=float)
    T_K = T_celsius + P.T_KELVIN
    # ⛔ K15：绝对温度必须 > 273
    if np.any(T_K <= 273.0):
        raise ValueError(f"附录{appendix} D 计算温度非绝对温标：min(T_K)={float(np.min(T_K))}")
    w = C / (C + 1.0)

    if appendix == 3:
        rho = P.APP3_RHO_A + P.APP3_RHO_B * C
        cp = P.APP3_CP_A + P.APP3_CP_B * w
        k = P.APP3_K_A + P.APP3_K_B * w
        D = P.APP3_D_PREF * np.exp(-P.APP3_D_EC / C) * np.exp(-P.APP3_D_ET / T_K)
        return rho, cp, k, D

    if appendix == 4:
        rho = P.APP4_RHO_A + P.APP4_RHO_B * C
        cp = P.APP4_CP_A + P.APP4_CP_B * w
        k = P.APP4_K_A + P.APP4_K_B * w
        D = P.APP4_D_PREF * np.exp(-P.APP4_D_EC / C) * np.exp(-P.APP4_D_ET / T_K)
        return rho, cp, k, D

    raise ValueError(f"未知附录编号: {appendix}")


def rho_s_eff(appendix: int, C):
    """干物质表观密度 rho_s = rho/(1+C)（INC1 质量自洽诊断，问题4）。"""
    C = np.asarray(C, dtype=float)
    if appendix == 4:
        rho = P.APP4_RHO_A + P.APP4_RHO_B * C
    elif appendix == 3:
        rho = P.APP3_RHO_A + P.APP3_RHO_B * C
    elif appendix == 2:
        rho = np.full_like(C, P.APP2_RHO)
    else:
        raise ValueError(f"未知附录编号: {appendix}")
    return rho / (1.0 + C)
