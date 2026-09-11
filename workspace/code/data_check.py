"""数据核验：附件1(241行)/附件2(145行)、附件2时间轴、result模板表头。

只打印结论摘要，不把整表数组读进上下文。
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "user_data" / "附件" / "附件"

A1 = DATA / "附件1.xlsx"
A2 = DATA / "附件2.xlsx"
RES = DATA / "附件3"


def main() -> int:
    out = {}

    # 附件1：烘房温湿时程
    df1 = pd.read_excel(A1, sheet_name=0)
    out["附件1_rows"] = int(df1.shape[0])
    out["附件1_cols"] = list(map(str, df1.columns))
    t1 = pd.to_numeric(df1.iloc[:, 0], errors="coerce").to_numpy()
    T1 = pd.to_numeric(df1.iloc[:, 1], errors="coerce").to_numpy()
    C1 = pd.to_numeric(df1.iloc[:, 2], errors="coerce").to_numpy()
    out["附件1_t"] = [float(np.nanmin(t1)), float(np.nanmax(t1))]
    d1 = np.diff(t1)
    out["附件1_dt_unique"] = sorted({round(float(x), 6) for x in d1})[:5]
    out["附件1_T_range"] = [float(np.nanmin(T1)), float(np.nanmax(T1))]
    out["附件1_C_range"] = [float(np.nanmin(C1)), float(np.nanmax(C1))]

    # 附件2：半径时程
    df2 = pd.read_excel(A2, sheet_name=0)
    out["附件2_rows"] = int(df2.shape[0])
    out["附件2_cols"] = list(map(str, df2.columns))
    t2 = pd.to_numeric(df2.iloc[:, 0], errors="coerce").to_numpy()
    R2 = pd.to_numeric(df2.iloc[:, 1], errors="coerce").to_numpy()
    out["附件2_t"] = [float(np.nanmin(t2)), float(np.nanmax(t2))]
    d2 = np.diff(t2)
    out["附件2_dt_unique"] = sorted({round(float(x), 6) for x in d2})[:5]
    out["附件2_R_range"] = [float(np.nanmin(R2)), float(np.nanmax(R2))]
    out["附件2_R_first3"] = [round(float(x), 6) for x in R2[:3]]
    out["附件2_R_last3"] = [round(float(x), 6) for x in R2[-3:]]
    # 单调性检查（原始）
    out["附件2_R_monotone_nonincreasing"] = bool(np.all(d2 <= 1e-12) or np.all(np.diff(R2) <= 1e-12))
    out["附件2_R_diff_max"] = float(np.nanmax(np.diff(R2)))

    # 关键点核对
    def R_at(target_s):
        idx = int(np.nanargmin(np.abs(t2 - target_s)))
        return round(float(t2[idx]), 1), round(float(R2[idx]), 6)
    out["附件2_key_points"] = {
        "6h": R_at(6 * 3600), "12h": R_at(12 * 3600),
        "24h": R_at(24 * 3600), "36h": R_at(36 * 3600), "72h": R_at(72 * 3600),
    }

    # result 模板
    for i in (1, 2, 3, 4):
        f = RES / f"result{i}.xlsx"
        xl = pd.ExcelFile(f)
        out[f"result{i}_sheets"] = list(map(str, xl.sheet_names))
        first = pd.read_excel(f, sheet_name=xl.sheet_names[0], header=None, nrows=3)
        out[f"result{i}_head"] = first.astype(str).values.tolist()

    print(json.dumps(out, ensure_ascii=False, indent=2))

    # 断言（与 DATA_FACTS ingest_assertion 对齐）
    assert out["附件1_rows"] == 241, f"附件1 行数应=241, 实际={out['附件1_rows']}"
    assert out["附件2_rows"] == 145, f"附件2 行数应=145, 实际={out['附件2_rows']}"
    print("DATA_INGEST_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
