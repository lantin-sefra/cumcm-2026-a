"""问题2：附录3 全程变物性强耦合（MODELING_REPORT §6.3）。

表3/表4 报表窗 t∈{0.5,1,1.5,2,2.5,3} h × r∈{0,0.5,1,1.5,2} cm；
result2.xlsx 双表覆盖整个烘干过程，A 列步长 1 s。⛔ 3 h 仅报表窗，非物理终止。
"""
from __future__ import annotations

import csv
import numpy as np

import params as P
import io_out as IO
import master_p23

REPORT_TIMES_H = P.P2_REPORT_TIMES_H
REPORT_RADII = P.P2_REPORT_RADII_CM
_COLIDX = [P.DIST_COLS_CM.index(round(r, 4)) for r in REPORT_RADII]


def _block(res, times_s, field):
    ts = res["t"]
    col = res["Tcol"] if field == "T" else res["Ccol"]
    rows = []
    for tq in times_s:
        j = int(np.argmin(np.abs(ts - tq)))
        rows.append([col[j, ci] for ci in _COLIDX])
    return np.asarray(rows)


def solve(res=None, write=True):
    if res is None:
        res = master_p23.run_master()
    times_s = [h * P.SEC_PER_HOUR for h in REPORT_TIMES_H]
    T_tab = _block(res, times_s, "T")
    C_tab = _block(res, times_s, "C")

    if write:
        path = P.OUTPUT_DIR / "table3_4_problem2.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        radii_lbl = [f"{r:g}" for r in REPORT_RADII]
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["表3 温度(℃)  时间(h)\\距离(cm)"] + radii_lbl)
            for h, row in zip(REPORT_TIMES_H, T_tab):
                w.writerow([f"{h:g}"] + [IO.fmt4(v) for v in row])
            w.writerow([])
            w.writerow(["表4 水分浓度(kg/kg)  时间(h)\\距离(cm)"] + radii_lbl)
            for h, row in zip(REPORT_TIMES_H, C_tab):
                w.writerow([f"{h:g}"] + [IO.fmt4(v) for v in row])

        # result2.xlsx：全程 1 s（大表，write_only 流式）。抽样声明见 RESULTS.md。
        mask = res["t"] >= 1.0 - 1e-9
        IO.write_result_xlsx(P.OUTPUT_DIR / "result2.xlsx",
                             {"温度": res["Tcol"][mask], "水分浓度": res["Ccol"][mask]},
                             res["t"][mask])

    summary = {
        "problem": 2, "appendix": 3, "N": res["N"], "dt_s": 1.0, "chi": "n.a.(fixed)",
        "report_window_h": 3.0,
        "process_end_h": res["t_end_h"],
        "mass_resid_rel": res["mass_resid_rel"],
        "picard_iters_max": res["picard_iters_max"],
        "picard_nonconv": res["picard_nonconv"],
        "floor_trunc_steps": res["floor_trunc_steps"],
        "table3_T": T_tab.round(4).tolist(),
        "table4_C": C_tab.round(4).tolist(),
        "report_times_h": list(REPORT_TIMES_H),
        "report_radii_cm": list(REPORT_RADII),
        "n_rows_result2": int(np.sum(res["t"] >= 1.0 - 1e-9)),
    }
    return res, summary


if __name__ == "__main__":
    _, s = solve()
    print("P2 done:", {k: s[k] for k in
          ("process_end_h", "mass_resid_rel", "picard_iters_max", "n_rows_result2")})
