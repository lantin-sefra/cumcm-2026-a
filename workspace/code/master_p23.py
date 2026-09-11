"""问题2/3 共享主推进（附录3 固定域 R=R0，Δt=1 s 全程至达标）。

⛔ 问题2/3 模型完全相同（§6.3/§6.4），仅报表窗口与终止判据不同：
一次 1 s 主运行同时供 result2（全程 1 s）、result3（60 s 子采样）、表3/4/5 与 P3 的 t_end。
result2 要求「每隔 1 s」故主步长取 1 s（严于分段 2s→4s，更精确，不做事后插值，§13.3）。
"""
from __future__ import annotations

import params as P
import geometry
import driver as D

_MASTER = {}


def run_master(force=False):
    """运行（或复用）附录3 固定域主解，返回 driver.run 结果字典。"""
    if "res" in _MASTER and not force:
        return _MASTER["res"]
    g = geometry.FixedGeometry(P.R0_M)
    cfg = D.CaseConfig(name="P2P3_master", appendix=3, geom=g,
                       dt_policy="const", dt_const=P.DT_P1,      # 1 s
                       save_dt_s=P.P2_SAVE_DT_S,                 # 1 s 输出
                       t_max_s=P.T_END_MAX_S, detect_end=True,
                       store_nodes=False)
    res = D.run(cfg)
    _MASTER["res"] = res
    return res
