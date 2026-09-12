"""fig_q4_shrink_effect — 历史效应隔离图脚本（legacy / historical diagnostic）。

读取 output/legacy/effect_isolation.csv，其中 S2=χ0 / S3=χ1 为旧口径。
正式诊断见 output/final_diagnostics/q4_effect_isolation_final.csv
（正式：S2 χ=1 主模型，S3 χ=0 交叉验证）。
⛔ 不要用本脚本覆盖正式 fig_*.pdf。
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _figcommon import C, load_csv, newfig, panel, finish  # noqa: E402

df = load_csv('legacy/effect_isolation.csv')
df.columns = [c.strip().lstrip('﻿') for c in df.columns]
df = df[df['scenario'].astype(str).str.startswith('S')].copy()
df['t_end_h'] = df['t_end_h'].astype(float)

names = {'S0': 'S0 附录3 / 固定 2 cm',
         'S1': 'S1 附录4 / 固定 2 cm',
         'S2': 'S2 附录4 / 收缩, χ=0',
         'S3': 'S3 附录4 / 收缩, χ=1',
         'S4': 'S4 附录4 / 固定 1.198 cm'}
sc = list(df['scenario'])
tv = np.array(df['t_end_h'])
t_s0 = float(tv[sc.index('S0')])
t_s1 = float(tv[sc.index('S1')])
t_s2 = float(tv[sc.index('S2')])
dev = tv - t_s0

fig = newfig(6.4, 3.9, width_fraction=0.98)
gs = fig.add_gridspec(1, 2, wspace=0.32, width_ratios=[1.25, 1.0])
ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])

# (a) 各情景相对 S0 基线的发散柱
y = np.arange(len(sc))
colors = [C['neutral_light'] if abs(v) < 1e-9 else
          (C['red_strong'] if v > 0 else C['blue_main']) for v in dev]
ax1.barh(y, dev, height=0.62, color=colors, edgecolor=C['neutral_black'], lw=0.5)
ax1.axvline(0.0, color=C['neutral_black'], lw=0.9)
ax1.set_yticks(y)
# t_end 读数并入刻度标签（坐标轴标签不占图内标注预算，也不会与柱体相撞）
ax1.set_yticklabels(['%s\n%.2f h' % (names[s], tv[j])
                     for j, s in enumerate(sc)])
ax1.set_xlabel('$t_{end}$ 相对 S0 的偏差 (h)')
ax1.set_ylabel('效应隔离情景')
ax1.set_xlim(-16.0, 80.0)
ax1.set_xticks(np.arange(-10, 71, 20))
ax1.set_ylim(-0.65, len(sc) - 0.35)
ax1.invert_yaxis()
# 数值贴在柱尖之外，用 ha 对齐避免按字宽估偏移
panel(ax1, '(a)')

# (b) 加性分解（式24）：净差 = 换物性 + 加收缩
steps = [('换物性', t_s1 - t_s0, C['red_strong']),
         ('加收缩', t_s2 - t_s1, C['blue_main']),
         ('净差', t_s2 - t_s0, C['green_3'])]
xb = np.arange(3)
bottoms = [0.0, t_s1 - t_s0, 0.0]
for j, (lab, val, col) in enumerate(steps):
    ax2.bar(xb[j], val, bottom=bottoms[j], width=0.56, color=col,
            edgecolor=C['neutral_black'], lw=0.5)
ax2.axhline(0.0, color=C['neutral_black'], lw=0.9)
ax2.set_xticks(xb)
# (b) 面板窄，3 个 3 字标签相邻字形会相撞（在 PDF 里并成一个文本行，
# 文字相撞体检查不到），压到 2 字
ax2.set_xticklabels(['物性', '收缩', '净差'])
ax2.set_ylabel('$t_{end}$ 变化量 (h)｜S1−S0 / S2−S1 / S2−S0')
ax2.set_xlim(-0.62, 2.62)
ax2.set_ylim(-30.0, 96.0)
ax2.set_yticks(np.arange(-20, 91, 20))
# 标注放在各柱几何端点之外（柱1 0→71.9、柱2 71.9→−4.5、柱3 −4.5→0）
label_y = [t_s1 - t_s0 + 5.0, -13.0, -22.0]
for j, (lab, val, col) in enumerate(steps):
    ax2.annotate('%+.2f h' % val, xy=(xb[j], val),
                 xytext=(xb[j] - 0.40, label_y[j]), color=col)
panel(ax2, '(b)')

finish(fig, 'fig_q4_shrink_effect')
