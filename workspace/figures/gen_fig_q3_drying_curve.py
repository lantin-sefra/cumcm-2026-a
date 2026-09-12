"""fig_q3_drying_curve — 问题3 干燥曲线：逐点最大/体平均/中心/表面含水率 + 达标定位。"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _figcommon import (C, load, newfig, finish, auto_legend, C_TH,  # noqa: E402
                        SEC_PER_HOUR)

d = load('p3')
t_h = d['t'] / SEC_PER_HOUR
t_end = float(d['t_end_h'])

fig = newfig(6.4, 3.6, width_fraction=0.92)
ax = fig.add_subplot(1, 1, 1)

# 渐变填充：max 与 min（表面）之间按 18 层薄带表示药材内部含水率分布带
lo = d['Csurf']
hi = d['maxC']
n_band = 18
for i in range(n_band):
    f0 = i / n_band
    f1 = (i + 1) / n_band
    ax.fill_between(t_h, lo + (hi - lo) * f0, lo + (hi - lo) * f1,
                    color=C['blue_secondary'], alpha=0.055, lw=0)

l1, = ax.plot(t_h, hi, color=C['blue_main'], lw=1.7,
              label='逐点最大 $C_{max}$（判据量）')
l2, = ax.plot(t_h, d['Cbar'], color=C['green_3'], lw=1.4, ls='--',
              label='体平均 $\\bar{C}$')
l3, = ax.plot(t_h, lo, color=C['neutral_dark'], lw=1.3, ls='-.',
              label='表面 $C(R,t)$')
l4 = ax.axhline(C_TH, color=C['red_strong'], lw=1.1, ls=':')
l4.set_label('达标阈值 0.15 kg/kg')
ax.axvline(t_end, color=C['red_strong'], lw=0.9, ls='--')
ax.plot([t_end], [C_TH], marker='o', ms=4.5, mfc='none', mew=1.2,
        color=C['red_strong'])

ax.annotate('%.4f h' % t_end, xy=(t_end, C_TH), xytext=(t_end - 15.5, 0.42),
            color=C['red_strong'])
ax.annotate('%.4f kg/kg' % float(d['Cbar'][-1]), xy=(t_h[-1], d['Cbar'][-1]),
            xytext=(28.0, 0.86), color=C['green_3'])

ax.set_xlabel('时间 $t$ (h)')
ax.set_ylabel('干基含水率 $C$ (kg/kg)')
ax.set_xlim(0, t_h[-1])
ax.set_ylim(0, 2.72)
ax.set_xticks(np.arange(0, 61, 12))
auto_legend(ax, handles=[l1, l2, l3, l4], loc='upper right')

finish(fig, 'fig_q3_drying_curve')
