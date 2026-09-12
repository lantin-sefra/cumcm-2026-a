"""fig_q4_triptych — 问题4 三联图：收缩域内含水率/温度剖面分三阶段 + 半径同步收缩。"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _figcommon import (C, M, load, newfig, panel, finish, shared_legend,  # noqa: E402
                        seq_colors, nearest_idx, C_TH, SEC_PER_HOUR)

d = load('p4s2')
t_h = d['t'] / SEC_PER_HOUR
R_cm = d['R_m'] / 1e-2
N = int(d['N'])
xi = np.linspace(0.0, 1.0, N + 1)
t_end = float(d['t_end_h'])

stages = [(0.0, 12.0, '(a)'), (12.0, 36.0, '(b)'), (36.0, t_end, '(c)')]
fig = newfig(6.4, 2.9, width_fraction=0.98)
gs = fig.add_gridspec(1, 3, wspace=0.34)
axes = [fig.add_subplot(gs[0, j]) for j in range(3)]

for j, (h0, h1, tag) in enumerate(stages):
    ax = axes[j]
    hs = np.linspace(h0, h1, 5)
    cols = seq_colors(len(hs), 'blue')
    for m, hh in enumerate(hs):
        i = nearest_idx(t_h, hh)
        ax.plot(xi * R_cm[i], d['nodesC'][i], color=cols[m], lw=1.3,
                marker=M[m % len(M)], ms=2.6, markevery=(m, 8),
                label='%.1f h' % hh if j == 0 else None)
        ax.plot([R_cm[i]], [d['nodesC'][i][-1]], marker='|', ms=5.0,
                color=C['red_strong'])
    # 阈值线的身份走图例，不在图内加文字标注：'0.15 kg/kg' 宽约 1.17 个数据单位，
    # 放在 xlim=2.05 内的空白带里必然右溢出到 (b)，save_fig 的解重叠会把它甩到
    # 左下角，正好压在这条点线上。
    ax.axhline(C_TH, color=C['red_strong'], lw=0.9, ls=':',
               label='达标阈值 0.15 kg/kg' if j == 0 else None)
    ax.set_xlabel('径向位置 $r$ (cm)')
    ax.set_xlim(0, 2.05)
    ax.set_ylim(0, 2.70)
    ax.set_xticks(np.arange(0, 2.1, 0.5))
    panel(ax, tag)
axes[0].set_ylabel('干基含水率 $C$ (kg/kg)')
for ax in axes[1:]:
    ax.set_yticklabels([])

axes[2].annotate('%.4f cm' % R_cm[-1], xy=(R_cm[-1], 0.35),
                 xytext=(0.14, 0.52), color=C['red_strong'])
shared_legend(fig, axes=[axes[0]], where='top', ncol=6)

finish(fig, 'fig_q4_triptych')
