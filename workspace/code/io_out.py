"""交付文件落盘（CSV 报表 + result*.xlsx）。

数值以 Excel 数值类型写入（round 到 4 位小数 + 单元格格式 0.0000），
禁止把温度/含水率写成字符串。问题4 域外单元留空（None），不是 0、也不是 'NaN'。
result*.xlsx 表头与附件3 模板一致：首格「时间\\到药材中心的距离」+ 距离列（cm）。
result3/result4 工作表名保持模板的 Sheet1。
"""
from __future__ import annotations

import csv
import math

import numpy as np
from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell

import params as P

HEADER0 = "时间\\到药材中心的距离"


def fmt4(x):
    """4 位小数字符串；NaN/None → 空串。仅用于 CSV 报表，不用于 xlsx。"""
    if x is None:
        return ""
    xf = float(x)
    if not math.isfinite(xf):
        return ""
    return f"{xf:.4f}"


def as_num4(x):
    """xlsx 用：有限值 → round(..., 4) 的 float；否则 None（空白单元格）。"""
    if x is None:
        return None
    xf = float(x)
    if not math.isfinite(xf):
        return None
    return round(xf, 4)


def _num_cell(ws, value, number_format="0.0000"):
    cell = WriteOnlyCell(ws, value=value)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        cell.number_format = number_format
    return cell


def _dist_header(last_label=None):
    """距离表头：0.0..2.0（21 列），可选末列标签（问题4「药材表面」）。"""
    cols = [round(c, 4) for c in P.DIST_COLS_CM]
    head = [HEADER0] + cols
    if last_label is not None:
        head.append(last_label)
    return head


def write_result_xlsx(path, sheets, times_s, last_label=None):
    """写 result*.xlsx。

    sheets : dict 工作表名 -> 2D 数组 (nt, ncol)，ncol=21 或 22（含末列表面）。
    times_s: 长度 nt 的时间列（秒，整数写出）。
    温度/含水率为数值单元格（四位小数），域外为空白。
    """
    wb = Workbook(write_only=True)
    header = _dist_header(last_label)
    for name, arr in sheets.items():
        ws = wb.create_sheet(title=name)
        ws.append(header)
        arr = np.asarray(arr)
        for i in range(arr.shape[0]):
            row = [_num_cell(ws, int(round(times_s[i])), "0")]
            for v in arr[i]:
                nv = as_num4(v)
                row.append(None if nv is None else _num_cell(ws, nv))
            ws.append(row)
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(str(path))


def write_table_csv(path, row_labels, col_labels, matrix, corner=HEADER0,
                    extra_last_row=None):
    """写报表 CSV（表1–6）。matrix 经 fmt4（含置空）。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow([corner] + list(col_labels))
        for lbl, vals in zip(row_labels, matrix):
            w.writerow([lbl] + [fmt4(v) for v in vals])
        if extra_last_row is not None:
            lbl, vals = extra_last_row
            w.writerow([lbl] + [fmt4(v) for v in vals])
