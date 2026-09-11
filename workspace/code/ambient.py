"""烘房环境驱动函数（附件1 线性插值 + 平台外推，MODELING_REPORT §3.2 式(7)(8)）。

T_air(t), C_air(t)：t∈[0,14400] 线性插值附件1 全部 241 行；t>14400 取平台值（假设5）。
⛔ 附件1 第3列是烘房空气含湿量（量级 1e-2），不是药材水分浓度。
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import params as P

_CACHE = {}


class Ambient:
    """时变环境边界。可注入平台替代值做灵敏度（SA4/SA5）。"""

    def __init__(self, t_plateau=None, c_plateau=None):
        t_arr, T_arr, C_arr = _load_attach1()
        self._t = t_arr
        self._T = T_arr
        self._C = C_arr
        self.T_plateau = P.TA_PLATEAU if t_plateau is None else float(t_plateau)
        self.C_plateau = P.CA_PLATEAU if c_plateau is None else float(c_plateau)
        self.t_max = P.AMBIENT_T_MAX_S

    def T_air(self, t):
        """烘房空气温度 ℃。t 可为标量或数组。"""
        t = np.asarray(t, dtype=float)
        val = np.interp(t, self._t, self._T)
        return np.where(t <= self.t_max, val, self.T_plateau)

    def C_air(self, t):
        """烘房空气含湿量 kg/kg。t 可为标量或数组。"""
        t = np.asarray(t, dtype=float)
        val = np.interp(t, self._t, self._C)
        return np.where(t <= self.t_max, val, self.C_plateau)


def _load_attach1():
    if "attach1" not in _CACHE:
        df = pd.read_excel(P.ATTACH1, sheet_name=0)
        n = int(df.shape[0])
        if n != P.N_ROWS_ATTACH1:
            raise ValueError(f"附件1 应为 {P.N_ROWS_ATTACH1} 行，实际 {n} 行（数据未读全）")
        t = pd.to_numeric(df.iloc[:, 0], errors="coerce").to_numpy(dtype=float)
        T = pd.to_numeric(df.iloc[:, 1], errors="coerce").to_numpy(dtype=float)
        C = pd.to_numeric(df.iloc[:, 2], errors="coerce").to_numpy(dtype=float)
        if not (np.all(np.isfinite(t)) and np.all(np.isfinite(T)) and np.all(np.isfinite(C))):
            raise ValueError("附件1 含非有限值")
        _CACHE["attach1"] = (t, T, C)
    return _CACHE["attach1"]
