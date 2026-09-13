"""fig_q1_center_surface — 问题1 中心/表面温度与含水率时程（双轴图）。"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _figcommon import C, load, newfig, finish, auto_legend  # noqa: E402

d = load('p1')
t = d['t']

fig = newfig(6.4, 3.5, width_fraction=0.9)
ax = fig.add_subplot(1, 1, 1)
ax2 = ax.twinx()

l1, = ax.plot(t, d['T_air'], color=C['neutral_mid'], lw=1.1, ls=':',
              label='空气温度 $T_{air}$')
l2, = ax.plot(t, d['Tsurf'], color=C['red_strong'], lw=1.6,
              label='表面温度 $T(R,t)$')
l3, = ax.plot(t, d['Tcenter'], color=C['red_1'], lw=1.6, ls='--',
              label='中心温度 $T(0,t)$')
l4, = ax2.plot(t, d['Csurf'], color=C['blue_main'], lw=1.6,
               label='表面含水率 $C(R,t)$')
l5, = ax2.plot(t, d['Ccenter'], color=C['blue_secondary'], lw=1.6, ls='--',
               label='中心含水率 $C(0,t)$')

ax.annotate('%.3f ℃' % d['Tsurf'][-1], xy=(t[-1], d['Tsurf'][-1]),
            xytext=(1130, 39.6), color=C['red_strong'])
ax.annotate('%.3f ℃' % d['Tcenter'][-1], xy=(t[-1], d['Tcenter'][-1]),
            xytext=(1130, 31.4), color=C['red_1'])
ax2.annotate('%.3f kg/kg' % d['Csurf'][-1], xy=(t[-1], d['Csurf'][-1]),
             xytext=(690, 1.435), color=C['blue_main'])

ax.set_xlabel('时间 $t$ (s)')
ax.set_ylabel('温度 $T$ (℃)')
ax2.set_ylabel('干基含水率 $C$ (kg/kg)')
ax.set_xlim(0, t[-1])
# 两轴量程错开分带：温度族占画面上部，含水率族占下部，避免五条曲线互相压叠
ax.set_ylim(26.5, 43.0)
ax2.set_ylim(1.40, 4.10)
ax.set_xticks(np.arange(0, 1801, 300))
ax2.set_yticks([1.5, 2.0, 2.5])
auto_legend(ax, handles=[l1, l2, l3, l4, l5], loc='upper left', ncol=2)

finish(fig, 'fig_q1_center_surface')
