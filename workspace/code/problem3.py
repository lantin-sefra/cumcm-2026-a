"""问题3：附录3 + 达标判据（MODELING_REPORT §6.4）。

模型与问题2 完全相同，只加终止事件 t_end=min{t:max_r C<0.15}（式17，逐点最大值）。
表5 行 6,12,18,… h + 末行「烘干结束时间」× r∈{0,0.5,1,1.5,2} cm 浓度；
result3.xlsx 单表 A 列步长 60 s，从 60 s 到末个不超过 t_end 的整分点，
再追加精确达标时刻一行；21 距离列，工作表名 Sheet1。
"""
from __future__ import annotations

import numpy as np

import params as P
import io_out as IO
import driver as D
import master_p23

REPORT_RADII = P.P34_REPORT_RADII_CM
_COLIDX = [P.DIST_COLS_CM.index(round(r, 4)) for r in REPORT_RADII]


def _row_labels_6h(t_end_s):
    """6,12,… h（<t_end 的整数倍 6h）时刻列表（秒）。"""
    out = []
    k = 1
    while k * P.P34_REPORT_DT_H * P.SEC_PER_HOUR < t_end_s:
        out.append(k * P.P34_REPORT_DT_H * P.SEC_PER_HOUR)
        k += 1
    return out


def solve(res=None, write=True):
    if res is None:
        res = master_p23.run_master()
    if not res["reached"]:
        raise RuntimeError("问题3 未在 120 h 内达标（按 §13.3 自查 E1–E5）")
    t_end_s = res["t_end_s"]

    # 表5：6h 行 + 末行「烘干结束时间」
    times6 = _row_labels_6h(t_end_s)
    C_tab = []
    for tq in times6:
        j = int(np.argmin(np.abs(res["t"] - tq)))
        C_tab.append([res["Ccol"][j, ci] for ci in _COLIDX])
    C_tab = np.asarray(C_tab)
    C_end = D.field_at_time(res, t_end_s, "C")[_COLIDX]

    if write:
        radii_lbl = [f"{r:g}" for r in REPORT_RADII]
        row_lbls = [f"{int(round(t/P.SEC_PER_HOUR))}" for t in times6]
        IO.write_table_csv(
            P.OUTPUT_DIR / "table5_problem3.csv",
            row_lbls, radii_lbl, C_tab,
            corner="水分浓度(kg/kg)  时间(h)\\距离(cm)",
            extra_last_row=(f"烘干结束时间 {t_end_s/P.SEC_PER_HOUR:.3f}h", C_end))

        # result3.xlsx：60,120,… s（≤t_end）+ 精确达标时刻末行
        step = int(round(P.P34_SAVE_DT_S / P.P2_SAVE_DT_S))   # 60
        mask_idx = np.arange(0, res["t"].size, step)
        tt = res["t"][mask_idx]
        keep = (tt >= P.P34_SAVE_DT_S - 1e-9) & (tt <= t_end_s + 1e-6)
        times = tt[keep]
        cols = res["Ccol"][mask_idx][keep]
        if res.get("end_C") is not None:
            C_event = D._interp_cols(res["end_C"], P.R0_M, res["cols_m"])
        else:
            C_event = D.field_at_time(res, t_end_s, "C")
        if times.size == 0 or abs(float(times[-1]) - t_end_s) > 1e-6:
            times = np.append(times, t_end_s)
            cols = np.vstack([cols, C_event])
        IO.write_result_xlsx(P.OUTPUT_DIR / "result3.xlsx",
                             {"Sheet1": cols}, times)

    summary = {
        "problem": 3, "appendix": 3, "N": res["N"],
        "dt_s": P.DT_P23, "output_dt_s": P.P2_SAVE_DT_S, "chi": "n.a.(fixed)",
        "t_end_h": res["t_end_h"], "t_end_s": t_end_s,
        "maxC_at_end": float(res["maxC"][int(np.argmin(np.abs(res["t"] - t_end_s)))]),
        "mass_resid_rel": res["mass_resid_rel"],
        "picard_iters_max": res["picard_iters_max"],
        "picard_nonconv": res["picard_nonconv"],
        "floor_trunc_steps": res["floor_trunc_steps"],
        "table5_C": C_tab.round(4).tolist(),
        "table5_end_row_C": [round(float(v), 4) for v in C_end],
        "report_times_h": [t / P.SEC_PER_HOUR for t in times6],
        "report_radii_cm": list(REPORT_RADII),
    }
    return res, summary


if __name__ == "__main__":
    _, s = solve()
    print("P3 done:", {k: s[k] for k in
          ("t_end_h", "maxC_at_end", "mass_resid_rel", "picard_iters_max")})
