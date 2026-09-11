"""fig_q3_sensitivity — OFAT 灵敏度龙卷风图（output/sensitivity.csv 真算结果）。"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _figcommon import C, load_csv, newfig, finish  # noqa: E402

df = load_csv('sensitivity.csv')
df.columns = [c.strip().lstrip('﻿') for c in df.columns]
base = float(df.loc[df['case_id'] == 'BASE', 't_end_h'].iloc[0])

rows = df[df['case_id'] != 'BASE'].copy()
rows['dev'] = rows['t_end_h'].astype(float) - base

# 同一参数的多个扰动值合并为一条（取偏离基准最远的低/高两侧）
labels = {
    'h_m': '对流传质系数 $h_m$ ±20%',
    'h': '对流换热系数 $h$ ±20%',
    'D_prefactor': '扩散前因子 $D_0$ ±20%',
    'T_air_plateau': '空气温度平台值',
    'C_air_plateau': '空气含湿平台值',
    'surface_BC': '表面边界条件改 Dirichlet',
    'chi_closure': '移动边界闭合 $\\chi$: 0→1',
    'latent_heat_sink': '蒸发潜热汇（结构性）',
    'C_th': '达标阈值 $C_{th}$: 0.15→0.2',
}
items = []
for p, lab in labels.items():
    sub = rows[rows['param'] == p]
    if not len(sub):
        continue
    lo = float(sub['dev'].min())
    hi = float(sub['dev'].max())
    items.append((lab, lo, hi, max(abs(lo), abs(hi))))
items.sort(key=lambda x: x[3])

y = np.arange(len(items))
neg = [min(it[1], 0.0) for it in items]
pos = [max(it[2], 0.0) for it in items]

fig = newfig(6.4, 3.8, width_fraction=0.94)
ax = fig.add_subplot(1, 1, 1)
ax.barh(y, neg, height=0.60, color=C['blue_main'],
        edgecolor=C['neutral_black'], lw=0.5, label='使 $t_{end}$ 缩短')
ax.barh(y, pos, height=0.60, color=C['red_strong'],
        edgecolor=C['neutral_black'], lw=0.5, label='使 $t_{end}$ 延长')
# 零基准线只画到柱行范围：axvline 会贯穿整个轴高，顶部共享图例在最终字号下会
# 向下涨约 1 pt 探进轴内，落在这条线上被判为"图例遮挡数据"。
ax.vlines(0.0, -0.45, len(items) - 0.55, color=C['neutral_black'], lw=0.9)

ax.set_yticks(y)
ax.set_yticklabels([it[0] for it in items])
ax.set_xlabel('$t_{end}$ 相对基准 %.2f h 的变化 (h)' % base)
ax.set_ylabel('单因子扰动项')
ax.set_xlim(-31.0, 14.0)
ax.set_xticks(np.arange(-30, 14.1, 10))
ax.set_ylim(-0.7, len(items) - 0.3)

top = items[-1]
# 数值贴在柱体之外的白底区（柱内是深色填充，文字对比度不足 4.5:1）。
# 放柱尖一侧（左）会伸进 y 轴刻度文字，实测与"达标阈值 Cth: 0.15→0.2"横向重叠
# 7.6 pt；该行零轴右侧无柱体，读数改挂在那一侧的空白区。
ax.text(0.8, y[-1], '%+.1f h' % top[1], ha='left', va='center',
        color=C['neutral_black'])
# 基准读数并入 x 轴标签：作为图内标注它落在第 0 行的行带里，顶部图例让位后
# 行距变窄，实测已越过行边界。
# 图例原本 loc='lower left' 落在数据区内，压着末几行近零小柱所在的留白。
# 这里不能用 shared_legend：它提交车道时会 set_layout_engine('none') 冻结轴位，
# 而落盘阶段的最终字号会把本图很长的中文 y 刻度标签（"表面边界条件改 Dirichlet"
# 等）撑宽，冻结后无法重排，左侧标签栈直接溢出画布（实测 y 轴标签跑到 −4.4 pt）。
# 用 constrained layout 自己的外置图例槽位，版面引擎保持在线、可随字号重排。
fig.legend(*ax.get_legend_handles_labels(), loc='outside upper center',
           ncol=2, frameon=False)

finish(fig, 'fig_q3_sensitivity')
