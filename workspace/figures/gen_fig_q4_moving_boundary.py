"""fig_q4_moving_boundary — 问题4 收缩域内含水率等高线（物理坐标 r–t）+ 移动边界 R(t)。"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _figcommon import (C, load, newfig, finish, mono_cmap, auto_legend,  # noqa: E402
                        C_TH, SEC_PER_HOUR)

d = load('p4s2')
t_h = d['t'] / SEC_PER_HOUR
R_cm = d['R_m'] / 1e-2
nodesC = d['nodesC']
N = int(d['N'])
t_end = float(d['t_end_h'])

# 物质坐标 η=(r/R)² 均匀，物理半径 r=R√η
eta = np.linspace(0.0, 1.0, N + 1)

# 物理网格上插值到固定 r 栅格（域外留 NaN，不外推）
r_grid = np.linspace(0.0, 2.0, 121)
Z = np.full((r_grid.size, t_h.size), np.nan)
for j in range(t_h.size):
    rr = np.sqrt(eta) * R_cm[j]
    Z[:, j] = np.where(r_grid <= R_cm[j],
                       np.interp(r_grid, rr, nodesC[j], left=np.nan,
                                 right=np.nan),
                       np.nan)

fig = newfig(6.4, 3.7, width_fraction=0.92)
ax = fig.add_subplot(1, 1, 1)

# 分层填充在 PDF 里是逐层独立路径，相邻层之间留发丝缝；栅格化底图消除接缝，
# 等值线/移动边界线/文字仍是矢量。dark_end 让黑等值线在高含水率区可见。
cf = ax.contourf(t_h, r_grid, Z, levels=14,
                 cmap=mono_cmap('blue', dark_end=0.72))
cf.set_rasterized(True)
cb = fig.colorbar(cf, ax=ax, pad=0.02)
cb.set_label('干基含水率 $C$ (kg/kg)')
ax.contour(t_h, r_grid, Z, levels=[C_TH, 0.5, 1.0, 1.5, 2.0],
           colors=[C['neutral_black']], linewidths=0.6)

lb, = ax.plot(t_h, R_cm, color=C['red_strong'], lw=1.8, label='移动边界 $R(t)$')
ax.axvline(t_end, color=C['red_strong'], lw=0.9, ls='--')
ax.annotate('%.3f h' % t_end, xy=(t_end, 0.20), xytext=(t_end - 15.0, 0.16),
            color=C['red_strong'])
ax.annotate('%.3f cm' % R_cm[-1], xy=(t_h[-1], R_cm[-1]), xytext=(30.0, 1.34),
            color=C['red_strong'])

ax.set_xlabel('时间 $t$ (h)')
ax.set_ylabel('径向位置 $r$ (cm)')
ax.set_xlim(0, t_h[-1])
ax.set_ylim(0, 2.10)
ax.set_xticks(np.arange(0, 61, 12))
ax.set_yticks(np.arange(0, 2.1, 0.5))
auto_legend(ax, handles=[lb], loc='upper right')

finish(fig, 'fig_q4_moving_boundary')
