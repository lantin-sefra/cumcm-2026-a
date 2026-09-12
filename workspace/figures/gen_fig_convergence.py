"""fig_convergence — Q3/Q4 现成空间与时间步收敛数据。"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _figcommon import C, M, newfig, panel, finish  # noqa: E402

# 已锁定的现成收敛数据；本脚本只负责绘图，不调用任何求解程序。
Ns = np.array([40.0, 80.0, 160.0, 320.0, 640.0, 1280.0, 2560.0])
q3_N = np.array([57.00755707, 57.26943191, 57.39012359, 57.44199872,
                 57.46254873, 57.46991302, 57.47226331])
q4_N = np.array([50.95825804, 51.03687180, 51.07041568, 51.08254851,
                 51.08632349, 51.08736888, 51.08764000])

q3_dt = np.array([1.00, 0.50, 0.25])
q3_tend = np.array([57.47226331, 57.47182726, 57.47160923])
q4_dt = np.array([1.000, 0.500, 0.250, 0.125])
q4_tend = np.array([51.08736888, 51.08703959, 51.08687495, 51.08679262])

fig = newfig(6.4, 3.3, width_fraction=0.96)
gs = fig.add_gridspec(1, 2, wspace=0.30)
ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])

# (a) 空间收敛：Q3 正式 N=2560，Q4 正式 N=1280
ax1.plot(Ns, q3_N, color=C['blue_main'], lw=1.6, marker=M[0], ms=5.0,
               )
ax1.plot(Ns, q4_N, color=C['green_3'], lw=1.6, marker=M[1], ms=5.0,
               )
ax1.axhline(57.4716, color=C['neutral_mid'], lw=0.9, ls=':')
ax1.plot([2560.0], [q3_N[-1]], marker='D', ms=6.5,
         color=C['red_strong'], zorder=4)
ax1.plot([1280.0], [q4_N[-2]], marker='D', ms=6.5,
         color=C['red_strong'], zorder=4)
ax1.set_xscale('log', base=2)
ax1.set_xlabel('径向控制体数 $N$')
# 轴标签只留量名与单位：并上"附录3 / 固定半径"后旋转标签高 217 pt、逼到画布顶缘
# 3.9 pt，几乎贯穿整个轴高。求解口径写进 caption。
ax1.set_ylabel('达标时间 $t_{end}$ (h)')
ax1.set_xlim(32.0, 3200.0)
ax1.set_ylim(50.7, 57.7)
ax1.set_xticks(Ns)
ax1.set_xticklabels(['40', '80', '160', '320', '640', '1280', '2560'])
ax1.set_yticks(np.arange(51.0, 57.1, 2.0))
ax1.text(45.0, 57.18, 'Q3｜正式 $N$=2560',
         color=C['neutral_black'])
ax1.text(45.0, 51.28, 'Q4｜正式 $N$=1280', color=C['neutral_dark'])
panel(ax1, '(a)')

# (b) 时间步收敛：两问正式均取 Δt=0.25 s
ax2.plot(q3_dt, q3_tend, color=C['blue_main'], lw=1.6, marker=M[0], ms=5.0,
               )
ax2.plot(q4_dt, q4_tend, color=C['green_3'], lw=1.6, marker=M[1], ms=5.0,
               )
ax2.plot([0.25], [q3_tend[-1]], marker='D', ms=6.5,
         color=C['red_strong'], zorder=4)
ax2.plot([0.25], [q4_tend[-2]], marker='D', ms=6.5,
         color=C['red_strong'], zorder=4)
ax2.set_xscale('log', base=2)
ax2.set_xlabel('时间步 $\\Delta t$ (s)')
ax2.set_ylabel('达标时间 $t_{end}$ (h)')
ax2.set_xlim(1.2, 0.10)
ax2.set_ylim(50.7, 57.7)
ax2.set_xticks([1.0, 0.5, 0.25, 0.125])
ax2.set_xticklabels(['1', '0.5', '0.25', '0.125'])
ax2.set_yticks(np.arange(51.0, 57.1, 2.0))
ax2.text(0.92, 57.18, 'Q3｜57.4716 h｜$\\Delta t$=0.25 s', color=C['neutral_black'])
ax2.text(0.92, 51.28, 'Q4｜51.0869 h｜$\\Delta t$=0.25 s', color=C['neutral_dark'])
panel(ax2, '(b)')

finish(fig, 'fig_convergence')
