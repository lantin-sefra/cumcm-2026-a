"""交付文件落盘（CSV 报表 + result*.xlsx，MODELING_REPORT §11 落盘清单）。

表1–6 的 CSV 仍按 4 位小数写出。result*.xlsx 保存求解器高精度浮点：
时间列为实际秒（整数秒写 int，达标时刻写非整数 float），域外为空白。
表头与附件3 模板一致：首格「时间\\到药材中心的距离」+ 距离列（cm）。
大表用 openpyxl write_only 流式写出，避免峰值内存。
"""
from __future__ import annotations

import csv
import math

import numpy as np
from openpyxl import Workbook

import params as P

HEADER0 = "时间\\到药材中心的距离"


def fmt4(x):
    """4 位小数字符串；NaN/None → 空串（域外置空，K17）。"""
    if x is None:
        return ""
    xf = float(x)
    if not math.isfinite(xf):
        return ""
    return f"{xf:.4f}"


def _dist_header(last_label=None):
    """距离表头：0.0..2.0（21 列），可选末列标签（问题4「药材表面」）。"""
    cols = [round(c, 4) for c in P.DIST_COLS_CM]
    head = [HEADER0] + cols
    if last_label is not None:
        head.append(last_label)
    return head


def time_cell(t):
    """整数秒写成 int，亚步达标时刻保留 float，与已交付工作簿一致。"""
    tf = float(t)
    if abs(tf - round(tf)) < 1e-9:
        return int(round(tf))
    return tf


def value_cell(x):
    """result*.xlsx 单元格：有限浮点原样写入，非有限值置空。"""
    if x is None:
        return None
    xf = float(x)
    if not math.isfinite(xf):
        return None
    return xf


def write_result_xlsx(path, sheets, times_s, last_label=None):
    """写 result*.xlsx。

    sheets : dict 工作表名 -> 2D 数组 (nt, ncol)，ncol=21 或 22（含末列表面）。
    times_s: 长度 nt 的时间列（秒；整数秒与非整数达标时刻均可）。
    数值保留求解器精度；域外空白。表头由 _dist_header 生成。
    """
    wb = Workbook(write_only=True)
    header = _dist_header(last_label)
    times_s = np.asarray(times_s, dtype=float)
    for name, arr in sheets.items():
        ws = wb.create_sheet(title=name)
        ws.append(header)
        arr = np.asarray(arr, dtype=float)
        for i in range(arr.shape[0]):
            row = [time_cell(times_s[i])]
            row.extend(value_cell(v) for v in arr[i])
            ws.append(row)
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(str(path))


def write_table_csv(path, row_labels, col_labels, matrix, corner=HEADER0,
                    extra_last_row=None):
    """写报表 CSV（表1–6）。

    row_labels : 行标签（时间）；col_labels：列标签（距离/「药材表面」）。
    matrix     : (nrow, ncol)；经 fmt4（含置空）。
    extra_last_row : (label, values) 末行（如「烘干结束时间」），可选。
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow([corner] + list(col_labels))
        for lbl, vals in zip(row_labels, matrix):
            w.writerow([lbl] + [fmt4(v) for v in vals])
        if extra_last_row is not None:
            lbl, vals = extra_last_row
            w.writerow([lbl] + [fmt4(v) for v in vals])
