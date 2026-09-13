"""fig_q1_spacetime — 问题1 温度/含水率 Hovmöller 时空图（2 面板）。"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _figcommon import (C, load, newfig, panel, finish,  # noqa: E402
                        mono_cmap, label_levels_on_cbar)

d = load('p1')
t = d['t']
r = d['cols_cm']
T = d['Tcol'].T          # (21, nt)
Cc = d['Ccol'].T

fig = newfig(6.4, 2.9, width_fraction=0.98)
gs = fig.add_gridspec(1, 2, wspace=0.28)
ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])

# rasterized=True：181×21 网格在 PDF 里是 3801 个独立填充路径（整图 7742 个），
# 相邻格元之间留下发丝缝，渲染出来是一片竖向"梳齿"条纹，把等值线压得认不出。
# 底图栅格化成 300 dpi 图像层，等值线与文字仍是矢量。
# dark_end：色标暗端截掉一截，黑色等值线在高值区才看得见。
im1 = ax1.pcolormesh(t, r, T, cmap=mono_cmap('red', dark_end=0.80),
                     shading='auto', vmin=28.0, vmax=37.0, rasterized=True)
cb1 = fig.colorbar(im1, ax=ax1, pad=0.02)
cb1.set_label('温度 $T$ (℃)')
cs1 = ax1.contour(t, r, T, levels=[30, 32, 34, 36], colors=[C['neutral_black']],
                  linewidths=0.55)
label_levels_on_cbar(cb1, cs1, '%d')

im2 = ax2.pcolormesh(t, r, Cc, cmap=mono_cmap('blue', dark_end=0.72),
                     shading='auto', vmin=1.5, vmax=2.55, rasterized=True)
cb2 = fig.colorbar(im2, ax=ax2, pad=0.02)
cb2.set_label('干基含水率 $C$ (kg/kg)')
cs2 = ax2.contour(t, r, Cc, levels=[1.8, 2.1, 2.4, 2.5],
                  colors=[C['neutral_black']], linewidths=0.55)
label_levels_on_cbar(cb2, cs2, '%.1f')

for ax in (ax1, ax2):
    ax.set_xlabel('时间 $t$ (s)')
    ax.set_ylabel('径向位置 $r$ (cm)')
    ax.set_xlim(0, t[-1])
    ax.set_ylim(0, 2.0)
    ax.set_xticks(np.arange(0, 1801, 600))
    ax.set_yticks(np.arange(0, 2.1, 0.5))
panel(ax1, '(a)')
panel(ax2, '(b)')

finish(fig, 'fig_q1_spacetime')
