"""fig_q1_profiles — 问题1 预热段径向剖面（温度/含水率）2 面板。"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _figcommon import (C, M, load, newfig, panel, finish, shared_legend,  # noqa: E402
                        seq_colors, nearest_idx)

d = load('p1')
t = d['t']
r = d['cols_cm']
times = [100.0, 300.0, 600.0, 900.0, 1200.0, 1500.0, 1800.0]   # 表1/表2 报表时刻
idx = [nearest_idx(t, tt) for tt in times]
cs = seq_colors(len(times), 'blue')

fig = newfig(6.4, 3.2, width_fraction=0.98)
gs = fig.add_gridspec(1, 2, wspace=0.30)
axT = fig.add_subplot(gs[0, 0])
axC = fig.add_subplot(gs[0, 1])

for j, (i, tt) in enumerate(zip(idx, times)):
    axT.plot(r, d['Tcol'][i], color=cs[j], lw=1.3, marker=M[j % len(M)],
             ms=2.8, markevery=(j, 5), label='%d s' % int(tt))
    axC.plot(r, d['Ccol'][i], color=cs[j], lw=1.3, marker=M[j % len(M)],
             ms=2.8, markevery=(j, 5))

axT.set_xlabel('径向位置 $r$ (cm)')
axT.set_ylabel('温度 $T$ (℃)')
axC.set_xlabel('径向位置 $r$ (cm)')
axC.set_ylabel('干基含水率 $C$ (kg/kg)')
for ax in (axT, axC):
    ax.set_xlim(0, 2.0)
    ax.set_xticks(np.arange(0, 2.1, 0.5))
panel(axT, '(a)')
panel(axC, '(b)')
axT.set_ylim(27.4, 38.6)
axC.set_ylim(1.32, 2.78)

axT.annotate('%.3f ℃' % d['Tcol'][idx[-1]][0], xy=(0.0, d['Tcol'][idx[-1]][0]),
             xytext=(0.10, 37.7), color=C['neutral_black'])
axC.annotate('%.3f kg/kg' % d['Ccol'][idx[-1]][-1],
             xy=(2.0, d['Ccol'][idx[-1]][-1]), xytext=(0.10, 1.38),
             color=C['neutral_black'])
shared_legend(fig, axes=[axT], where='top', ncol=7)

finish(fig, 'fig_q1_profiles')
