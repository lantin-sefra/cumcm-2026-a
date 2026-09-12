"""问题2/3 共享主推进（附录3固定域 R=R0，从 t=0 连续推进至达标）。

问题2的3 h结果与问题3首达时间必须从同一次状态轨迹提取，禁止重新初始化或拼接。
正式生产离散统一为 N=2560、内部 Δt=0.25 s；快照仍每 1 s 保存。
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
                       N=P.N_P23_CV,
                       dt_policy="const", dt_const=P.DT_P23,
                       save_dt_s=P.P2_SAVE_DT_S,                 # 1 s 输出
                       t_max_s=P.T_END_MAX_S, detect_end=True,
                       store_nodes=False)
    res = D.run(cfg)
    _MASTER["res"] = res
    return res
