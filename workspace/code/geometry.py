"""求解域半径 R(t) 与收缩速率 Rdot(t)（MODELING_REPORT §7.4）。

固定域：返回常值 R 与 Rdot=0。
移动边界（问题4）：附件2 → 累积最小值单调化 → PCHIP 保形插值；
Rdot 取 PCHIP 解析导数；数据用尽后冻结半径（radius_frozen）。
⛔ 单调化只用累积最小值，不用平滑滤波（端点不变）。
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.interpolate import PchipInterpolator

import params as P

_CACHE = {}


class FixedGeometry:
    """固定求解域，R≡R_const（问题1/2/3 与情景 S0/S1/S4）。"""

    def __init__(self, R_const_m):
        self.R_const = float(R_const_m)
        self.radius_frozen = False
        self.moving = False

    def R(self, t):
        t = np.asarray(t, dtype=float)
        return np.full(t.shape, self.R_const) if t.ndim else self.R_const

    def Rdot(self, t):
        t = np.asarray(t, dtype=float)
        return np.zeros(t.shape) if t.ndim else 0.0


class MovingGeometry:
    """附件2 移动边界（问题4，情景 S2/S3）。半径单位 cm→m。"""

    def __init__(self):
        t_arr, R_mono_m = _load_attach2_mono()
        self._t = t_arr
        self._R = R_mono_m
        self._t_max = float(t_arr[-1])
        self._R_end = float(R_mono_m[-1])
        self._pchip = PchipInterpolator(t_arr, R_mono_m, extrapolate=False)
        self._pchip_d = self._pchip.derivative()
        self.radius_frozen = False
        self.moving = True

    def R(self, t):
        t = np.asarray(t, dtype=float)
        inside = np.clip(t, self._t[0], self._t_max)
        val = self._pchip(inside)
        if np.any(t > self._t_max):
            self.radius_frozen = True
        return np.where(t > self._t_max, self._R_end, val)

    def Rdot(self, t):
        t = np.asarray(t, dtype=float)
        inside = np.clip(t, self._t[0], self._t_max)
        val = self._pchip_d(inside)
        # 冻结段 Rdot=0；数据端点导数按 PCHIP 端点值
        return np.where((t > self._t_max) | (t < self._t[0]), 0.0, val)

    @property
    def t_data_max(self):
        return self._t_max

    @property
    def R_data(self):
        """返回 (t, R_mono_m) 供诊断/绘图。"""
        return self._t.copy(), self._R.copy()


def _load_attach2_mono():
    if "attach2" not in _CACHE:
        df = pd.read_excel(P.ATTACH2, sheet_name=0)
        n = int(df.shape[0])
        if n != P.N_ROWS_ATTACH2:
            raise ValueError(f"附件2 应为 {P.N_ROWS_ATTACH2} 行，实际 {n} 行（数据未读全）")
        t = pd.to_numeric(df.iloc[:, 0], errors="coerce").to_numpy(dtype=float)
        R_cm = pd.to_numeric(df.iloc[:, 1], errors="coerce").to_numpy(dtype=float)
        if not (np.all(np.isfinite(t)) and np.all(np.isfinite(R_cm))):
            raise ValueError("附件2 含非有限值")
        # 累积最小值单调化（收缩不可逆），端点保持不变
        R_mono_cm = np.minimum.accumulate(R_cm)
        R_mono_m = R_mono_cm * P.CM_TO_M
        _CACHE["attach2"] = (t, R_mono_m)
    return _CACHE["attach2"]
