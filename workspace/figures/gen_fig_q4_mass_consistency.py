"""fig_q4_mass_consistency — INC1 诊断配对点图：附录4 ρ(C) 与附件2 R(t) 的干物质自洽性。"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _figcommon import (C, load_csv, newfig, panel, finish,  # noqa: E402
                        shared_legend)

df = load_csv('mass_consistency.csv')
df.columns = [c.strip().lstrip('﻿') for c in df.columns]
df = df[~df['quantity'].astype(str).str.startswith('#')]
val = {str(q).strip(): float(v) for q, v in zip(df['quantity'], df['value'])}

# 密度比是无量纲量，单位位留空：写成末尾一个"—"时读起来像被截断的残字。
pairs = [
    ('干物质表观密度比\n$\\rho_s(C_{th})/\\rho_s(C_0)$',
     val['ratio_actual'], val['ratio_required'], ''),
    ('末态半径\n$R(t_{end})$',
     val['R_measured_end'], val['R_consistent'], 'cm'),
]

fig = newfig(6.4, 3.4, width_fraction=0.98)
gs = fig.add_gridspec(1, 2, wspace=0.34, width_ratios=[1.0, 1.0])
ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])

# (a) 配对点（哑铃）：实际值 vs 严格守恒要求值
y = np.arange(len(pairs))
for j, (lab, a, b, unit) in enumerate(pairs):
    ax1.hlines(y[j], min(a, b), max(a, b), color=C['neutral_mid'], lw=1.6)
ha = ax1.scatter([p[1] for p in pairs], y, s=42, color=C['blue_main'],
                 zorder=3, label='模型/实测实际值')
hb = ax1.scatter([p[2] for p in pairs], y, s=42, marker='D',
                 color=C['red_strong'], zorder=3, label='严格干物质守恒要求值')
ax1.set_yticks(y)
# 读数不再并进刻度标签：那样的长串会顶到画布左缘被裁。刻度只留量名，
# 具体数值贴在各自的配对点右侧。
# 8 字的"干物质表观密度比"会顶到画布左缘，压到 5 字；完整口径写在 caption 里
ax1.set_yticklabels(['干物质密度比', '末态半径'])
for j, (lab, a, b, unit) in enumerate(pairs):
    ax1.text(max(a, b) + 0.07, y[j] + 0.17,
             ('%.4f vs %.4f %s' % (a, b, unit)).strip(), va='center',
             color=C['neutral_black'])
ax1.set_xlabel('取值（两量纲分列，见刻度标签）')
ax1.set_xlim(0.9, 3.1)
# 刻度从 5 个减到 3 个：面板窄，5 个标签相邻字形会相撞
ax1.set_xticks([1.0, 2.0, 3.0])
ax1.set_ylim(-0.62, len(pairs) - 0.38)
panel(ax1, '(a)')

# (b) 不相容度：相对差 vs 收敛判据无关声明（诊断量，不参与求解）
rel = val['rel_diff']
r2 = abs(val['R_consistent'] - val['R_measured_end']) / val['R_measured_end'] * 100.0
ax2.bar([0], [rel], width=0.44, color=C['gold'],
        edgecolor=C['neutral_black'], lw=0.5)
ax2.bar([1], [r2], width=0.44,
        color=C['teal'], edgecolor=C['neutral_black'], lw=0.5)
ax2.set_xticks([0, 1])
# 两个标签原本重叠 13 pt（CJK 相邻标签在 PDF 里并成一行，相撞体检看不见）
ax2.set_xticklabels(['密度比', '半径'])
ax2.set_ylabel('相对差 (%)')
ax2.text(0.0, rel + 0.6, '%.2f%%' % rel, ha='center', color=C['neutral_black'])
ax2.text(1.0, r2 + 0.6, '%.2f%%' % r2, ha='center', color=C['neutral_black'])
# 柱顶读数比柱体宽，居中放会向左探进 y 轴刻度区；左端多留半格
ax2.set_xlim(-0.95, 1.62)
ax2.set_ylim(0, 18.0)
ax2.set_yticks(np.arange(0, 18.1, 3))
panel(ax2, '(b)')

shared_legend(fig, axes=[ax1], where='top', ncol=2)

finish(fig, 'fig_q4_mass_consistency')
