"""fig_q3_rate_curve — 问题3 干燥速率面积图：-dC̄/dt 时程 + 速率对含水率的关系。"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _figcommon import (C, load, newfig, panel, finish,  # noqa: E402
                        shared_legend, SEC_PER_HOUR)

d = load('p3')
t_h = d['t'] / SEC_PER_HOUR
Cbar = d['Cbar']
maxC = d['maxC']
# 干燥速率（体平均含水率对时间的下降率，中心差分；单位 kg/(kg·h)）
rate = -np.gradient(Cbar, t_h)
rate_max = -np.gradient(maxC, t_h)
t_end = float(d['t_end_h'])

fig = newfig(6.4, 3.2, width_fraction=0.98)
gs = fig.add_gridspec(1, 2, wspace=0.30)
ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])

ax1.fill_between(t_h, rate, 0.0, color=C['blue_secondary'], alpha=0.35, lw=0)
ax1.plot(t_h, rate, color=C['blue_main'], lw=1.5, label='体平均 $-d\\bar{C}/dt$')
ax1.plot(t_h, rate_max, color=C['red_strong'], lw=1.2, ls='--',
         label='逐点最大 $-dC_{max}/dt$')
i_pk = int(np.argmax(rate))
ax1.plot([t_h[i_pk]], [rate[i_pk]], marker='o', ms=4.2, mfc='none', mew=1.2,
         color=C['neutral_black'])
ax1.set_xlabel('时间 $t$ (h)｜峰值 %.4f kg/(kg·h)' % rate[i_pk])
ax1.set_ylabel('干燥速率 (kg/(kg·h))')
ax1.set_xlim(0, t_h[-1])
ax1.set_ylim(0, float(rate.max()) * 1.55)
ax1.set_xticks(np.arange(0, 61, 12))
panel(ax1, '(a)')

# (b) 速率-含水率关系（Krischer 曲线口径：速率对当前含水率作图）
ax2.fill_between(Cbar, rate, 0.0, color=C['green_1'], alpha=0.35, lw=0)
ax2.plot(Cbar, rate, color=C['green_3'], lw=1.5)
ax2.axvline(float(Cbar[-1]), color=C['red_strong'], lw=0.9, ls=':')
ax2.annotate('%.4f h' % t_end, xy=(float(Cbar[-1]), float(rate.max()) * 0.5),
             xytext=(0.22, float(rate.max()) * 0.66), color=C['red_strong'])
ax2.set_xlabel('体平均含水率 $\\bar{C}$ (kg/kg)')
ax2.set_ylabel('干燥速率 (kg/(kg·h))')
ax2.set_xlim(0, 2.65)
ax2.set_ylim(0, float(rate.max()) * 1.28)
ax2.invert_xaxis()
ax2.set_xticks(np.arange(0, 2.6, 0.5))
panel(ax2, '(b)')

# (b) 只有一条曲线，靠轴标签即可辨识；(a) 的两条走共享车道，避免图例压面板标签
shared_legend(fig, axes=[ax1], where='top', ncol=2)

finish(fig, 'fig_q3_rate_curve')
