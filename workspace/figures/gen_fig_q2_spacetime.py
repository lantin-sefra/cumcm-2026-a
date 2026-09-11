"""fig_q2_spacetime — 问题2 温度/含水率 Hovmöller 时空图（0–3 h，2 面板）。"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _figcommon import (C, load, newfig, panel, finish, mono_cmap,  # noqa: E402
                        SEC_PER_HOUR, label_levels_on_cbar)

d = load('p2')
t_h = d['t'] / SEC_PER_HOUR
r = d['cols_cm']
T = d['Tcol'].T
Cc = d['Ccol'].T

fig = newfig(6.4, 2.9, width_fraction=0.98)
gs = fig.add_gridspec(1, 2, wspace=0.28)
ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])

# rasterized=True 与 dark_end 的理由同 fig_q1_spacetime：逐格元矢量填充在 PDF 里
# 留发丝缝（渲染成竖向梳齿条纹），且黑等值线在色标暗端看不见。
im1 = ax1.pcolormesh(t_h, r, T, cmap=mono_cmap('red', dark_end=0.80),
                     shading='auto', vmin=28.0, vmax=50.5, rasterized=True)
cb1 = fig.colorbar(im1, ax=ax1, pad=0.02)
cb1.set_label('温度 $T$ (℃)')
cs1 = ax1.contour(t_h, r, T, levels=[32, 38, 44, 48], colors=[C['neutral_black']],
                  linewidths=0.55)
label_levels_on_cbar(cb1, cs1, '%d')

im2 = ax2.pcolormesh(t_h, r, Cc, cmap=mono_cmap('blue', dark_end=0.72),
                     shading='auto', vmin=1.0, vmax=2.55, rasterized=True)
cb2 = fig.colorbar(im2, ax=ax2, pad=0.02)
cb2.set_label('干基含水率 $C$ (kg/kg)')
cs2 = ax2.contour(t_h, r, Cc, levels=[1.2, 1.6, 2.0, 2.4],
                  colors=[C['neutral_black']], linewidths=0.55)
label_levels_on_cbar(cb2, cs2, '%.1f')

for ax in (ax1, ax2):
    ax.set_xlabel('时间 $t$ (h)')
    ax.set_ylabel('径向位置 $r$ (cm)')
    ax.set_xlim(0, 3.0)
    ax.set_ylim(0, 2.0)
    ax.set_xticks(np.arange(0, 3.1, 1.0))
    ax.set_yticks(np.arange(0, 2.1, 0.5))
panel(ax1, '(a)')
panel(ax2, '(b)')

finish(fig, 'fig_q2_spacetime')
