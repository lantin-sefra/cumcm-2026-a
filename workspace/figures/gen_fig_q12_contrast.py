"""fig_q12_contrast — 问题1（附录2 常物性）vs 问题2（附录3 变物性）背靠背柱状图。

同一时刻 1800 s、同 5 个报表位置，左半为温升 ΔT，右半为失水量 ΔC，
两问共用离散与环境驱动，差异只来自物性口径。
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _figcommon import (C, load, newfig, finish, auto_legend,  # noqa: E402
                        nearest_idx)

p1 = load('p1')
p2 = load('p2')
r_want = [0.0, 0.5, 1.0, 1.5, 2.0]
ci = [nearest_idx(p1['cols_cm'], rr) for rr in r_want]
i1 = nearest_idx(p1['t'], 1800.0)
i2 = nearest_idx(p2['t'], 1800.0)

dT1 = p1['Tcol'][i1][ci] - 28.0
dT2 = p2['Tcol'][i2][ci] - 28.0
dC1 = 2.55 - p1['Ccol'][i1][ci]
dC2 = 2.55 - p2['Ccol'][i2][ci]

y = np.arange(len(r_want))
h = 0.36

fig = newfig(6.4, 3.4, width_fraction=0.98)
gs = fig.add_gridspec(1, 2, wspace=0.06)
axL = fig.add_subplot(gs[0, 0])
axR = fig.add_subplot(gs[0, 1])

axL.barh(y - h / 2, -dT1, height=h, color=C['blue_secondary'],
         edgecolor=C['neutral_black'], lw=0.5, label='问题1（附录2 常物性）')
axL.barh(y + h / 2, -dT2, height=h, color=C['blue_main'],
         edgecolor=C['neutral_black'], lw=0.5, label='问题2（附录3 变物性）')
axR.barh(y - h / 2, dC1, height=h, color=C['red_1'],
         edgecolor=C['neutral_black'], lw=0.5, label='问题1（附录2 常物性）')
axR.barh(y + h / 2, dC2, height=h, color=C['red_strong'],
         edgecolor=C['neutral_black'], lw=0.5, label='问题2（附录3 变物性）')

axL.set_xlim(-9.5, 0)
axL.set_xticks([-8, -6, -4, -2, 0])
axL.set_xticklabels(['8', '6', '4', '2', '0'])
axL.set_xlabel('温升 $\\Delta T$ @1800 s (K)')
axR.set_xlim(0, 1.30)
axR.set_xticks(np.arange(0, 1.31, 0.25))
axR.set_xlabel('失水量 $\\Delta C$ @1800 s (kg/kg)')

for ax in (axL, axR):
    ax.set_yticks(y)
    ax.set_ylim(-0.62, len(y) - 0.38)
axL.set_yticklabels(['%.1f' % v for v in r_want])
axL.set_ylabel('径向位置 $r$ (cm)')
axR.set_yticklabels(['%.1f' % v for v in r_want])
axR.set_ylabel('径向位置 $r$ (cm)')
axR.yaxis.tick_right()
axR.yaxis.set_label_position('right')
axR.spines['left'].set_visible(False)
axR.spines['right'].set_visible(True)

axL.annotate('%.2f K' % dT2[-1], xy=(-dT2[-1], y[-1] + h / 2),
             xytext=(-9.2, y[-1] + 0.24), color=C['blue_main'])
axR.annotate('%.3f kg/kg' % dC1[-1], xy=(dC1[-1], y[-1] - h / 2),
             xytext=(0.60, y[-1] - 0.60), color=C['red_1'])
auto_legend(axL, outside=True, where='top')
auto_legend(axR, outside=True, where='top')

finish(fig, 'fig_q12_contrast')
