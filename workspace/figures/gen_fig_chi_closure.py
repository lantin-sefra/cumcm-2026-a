"""fig_chi_closure — 物质坐标 vs Eulerian Landau 的 C_max(t) 交叉验证。"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _figcommon import (C, M, load, newfig, finish, auto_legend,  # noqa: E402
                        C_TH, SEC_PER_HOUR)

s2 = load('p4s2')   # Lagrangian 主用
s3 = load('p4s3')   # Eulerian χ=0 交叉验证

t2 = s2['t'] / SEC_PER_HOUR
t3 = s3['t'] / SEC_PER_HOUR
m2 = s2['maxC']
m3 = s3['maxC']
e2 = float(s2['t_end_h'])
e3 = float(s3['t_end_h'])

fig = newfig(6.4, 3.5, width_fraction=0.92)
ax = fig.add_subplot(1, 1, 1)

l2, = ax.plot(t2, m2, color=C['blue_main'], lw=1.6, marker=M[0], ms=3.0,
              markevery=260, label=r'物质坐标 $\eta=(r/R)^2$（交付）')
l3, = ax.plot(t3, m3, color=C['red_strong'], lw=1.6, ls='--', marker=M[1],
              ms=3.0, markevery=(130, 260),
              label=r'Eulerian Landau（交叉验证）')
ax.axhline(C_TH, color=C['neutral_dark'], lw=0.9, ls=':')
ax.axvline(e2, color=C['blue_main'], lw=0.8, ls='--')
ax.axvline(e3, color=C['red_strong'], lw=0.8, ls='--')
ax.plot([e2], [C_TH], marker='o', ms=5.0, color=C['blue_main'], zorder=4)
ax.plot([e3], [C_TH], marker='s', ms=5.0, color=C['red_strong'], zorder=4)

ax.set_xlabel(r'时间 $t$ (h)  |  $t_{end}$: %.3f h / %.3f h'
              % (e2, e3))
ax.set_ylabel(r'全域最大干基含水率 $C_{max}$ (kg/kg)')
ax.set_xlim(0, 56.0)
ax.set_ylim(0, 2.72)
ax.set_xticks(np.arange(0, 56.1, 8))
ax.set_yticks(np.arange(0, 2.71, 0.5))
ax.text(2.0, C_TH + 0.09, r'$C_{th}$=0.15 kg/kg', color=C['neutral_dark'])
ax.text(22.0, 1.62, r'相对差 %+.2f%%' % ((e3 - e2) / e2 * 100.0),
        color=C['neutral_black'])
auto_legend(ax, handles=[l2, l3], loc='upper right')

finish(fig, 'fig_chi_closure')
