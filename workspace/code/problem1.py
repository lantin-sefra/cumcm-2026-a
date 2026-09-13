"""问题1：附录2 常物性温度 + 非线性传质（MODELING_REPORT §5）。

内部 Δt=0.125 s 推进至 1800 s；表1/表2 报表 7×5；result1.xlsx 双表按 1 s 输出 21 列。
"""
from __future__ import annotations

import numpy as np

import params as P
import geometry
import driver as D
import io_out as IO

REPORT_TIMES = P.P1_REPORT_TIMES_S
REPORT_RADII = P.P1_REPORT_RADII_CM
_COLIDX = [P.DIST_COLS_CM.index(round(r, 4)) for r in REPORT_RADII]   # 0,5,10,15,20


def _report_block(res, times_s, field):
    """在快照时间轴上取 times_s × 报表半径的交叉矩阵。"""
    ts = res["t"]
    col = res["Tcol"] if field == "T" else res["Ccol"]
    rows = []
    for tq in times_s:
        j = int(np.argmin(np.abs(ts - tq)))
        rows.append([col[j, ci] for ci in _COLIDX])
    return np.asarray(rows)


def solve(write=True):
    g = geometry.FixedGeometry(P.R0_M)
    cfg = D.CaseConfig(name="P1", appendix=2, geom=g, N=P.N_P1_CV,
                       dt_policy="p1",
                       save_dt_s=P.P1_SAVE_DT_S, t_max_s=P.P1_SAVE_DURATION_S,
                       detect_end=False)
    res = D.run(cfg)

    T_tab = _report_block(res, REPORT_TIMES, "T")
    C_tab = _report_block(res, REPORT_TIMES, "C")

    if write:
        # 表1（温度）+ 表2（水分浓度）合并落盘，分区标注
        path = P.OUTPUT_DIR / "table1_2_problem1.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        import csv
        radii_lbl = [f"{r:g}" for r in REPORT_RADII]
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["表1 温度(℃)  时间(s)\\距离(cm)"] + radii_lbl)
            for t, row in zip(REPORT_TIMES, T_tab):
                w.writerow([int(t)] + [IO.fmt4(v) for v in row])
            w.writerow([])
            w.writerow(["表2 水分浓度(kg/kg)  时间(s)\\距离(cm)"] + radii_lbl)
            for t, row in zip(REPORT_TIMES, C_tab):
                w.writerow([int(t)] + [IO.fmt4(v) for v in row])

        # result1.xlsx：A 列 1 s 步长（1..1800），21 距离列，双表
        mask = res["t"] >= 1.0 - 1e-9
        times = res["t"][mask]
        IO.write_result_xlsx(P.OUTPUT_DIR / "result1.xlsx",
                             {"温度": res["Tcol"][mask], "水分浓度": res["Ccol"][mask]},
                             times)

    # JSON 摘要（无大数组）
    j = int(np.argmin(np.abs(res["t"] - 1800.0)))
    summary = {
        "problem": 1, "appendix": 2, "N": res["N"], "dt_s": P.DT_P1,
        "output_dt_s": P.P1_SAVE_DT_S, "chi": "n.a.(fixed)",
        "center_T_1800": float(res["Tcenter"][j]),
        "center_C_1800": float(res["Ccenter"][j]),
        "surface_T_1800": float(res["Tsurf"][j]),
        "surface_C_1800": float(res["Csurf"][j]),
        "mass_resid_rel": res["mass_resid_rel"],
        "resid_step_max": res["resid_step_max"],
        "picard_iters_max": res["picard_iters_max"],
        "picard_nonconv": res["picard_nonconv"],
        "floor_trunc_steps": res["floor_trunc_steps"],
        "table1_T": T_tab.round(4).tolist(),
        "table2_C": C_tab.round(4).tolist(),
        "report_times_s": list(REPORT_TIMES),
        "report_radii_cm": list(REPORT_RADII),
    }
    return res, summary


if __name__ == "__main__":
    _, s = solve()
    print("P1 done:", {k: s[k] for k in
          ("center_T_1800", "center_C_1800", "surface_C_1800",
           "mass_resid_rel", "picard_iters_max")})
