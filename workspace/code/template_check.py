"""核对 result 模板的行列规模、时间列取值范围；附件1尾部平台值。"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "user_data" / "附件" / "附件"
RES = DATA / "附件3"


def main() -> int:
    out = {}
    for i in (1, 2, 3, 4):
        f = RES / f"result{i}.xlsx"
        xl = pd.ExcelFile(f)
        sh = xl.sheet_names[0]
        df = pd.read_excel(f, sheet_name=sh, header=0)
        # 首列为时间标签
        tcol = df.iloc[:, 0]
        tvals = pd.to_numeric(tcol, errors="coerce").to_numpy()
        tvals = tvals[np.isfinite(tvals)]
        out[f"result{i}"] = {
            "sheet0": sh,
            "shape": [int(df.shape[0]), int(df.shape[1])],
            "col_headers": list(map(str, df.columns)),
            "n_time_rows": int(tvals.size),
            "t_first3": [float(x) for x in tvals[:3]],
            "t_last3": [float(x) for x in tvals[-3:]],
            "t_step": float(tvals[1] - tvals[0]) if tvals.size > 1 else None,
        }

    # 附件1 尾部平台
    df1 = pd.read_excel(DATA / "附件1.xlsx", sheet_name=0)
    t1 = pd.to_numeric(df1.iloc[:, 0], errors="coerce").to_numpy()
    T1 = pd.to_numeric(df1.iloc[:, 1], errors="coerce").to_numpy()
    C1 = pd.to_numeric(df1.iloc[:, 2], errors="coerce").to_numpy()
    out["附件1_tail"] = {
        "t_last5": [float(x) for x in t1[-5:]],
        "T_last5": [float(x) for x in T1[-5:]],
        "C_last5": [float(x) for x in C1[-5:]],
        "T_at_7200": float(T1[np.argmin(np.abs(t1 - 7200))]),
        "C_at_9000": float(C1[np.argmin(np.abs(t1 - 9000))]),
        "T_plateau_mean_last30": float(np.mean(T1[-30:])),
        "C_plateau_mean_last30": float(np.mean(C1[-30:])),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
