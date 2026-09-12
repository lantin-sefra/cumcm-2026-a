"""fig_q3_ridgeline — 问题3 每 6 h 径向含水率剖面山脊图（表5 报表口径）。"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _figcommon import (C, load, newfig, finish, seq_colors,  # noqa: E402
                        nearest_idx, SEC_PER_HOUR, C0)

d = load('p3')
t = d['t']
r = d['cols_cm']
t_end = float(d['t_end_h'])
hours = list(np.arange(0.0, np.floor(t_end / 6.0) * 6.0 + 0.1, 6.0)) + [t_end]
idx = [nearest_idx(t, h * SEC_PER_HOUR) for h in hours]
cols = seq_colors(len(hours), 'blue')

# result3.xlsx 第一行是 t=60s。0.0 h 必须用精确均匀初值，不能把 60s 薄边界层标成 t=0。
prof = []
for h, i in zip(hours, idx):
    if abs(float(h)) < 1e-12:
        prof.append(np.full(r.shape, C0))
    else:
        prof.append(d['Ccol'][i])

# 基线间距取 2.60，略大于 C0=2.55，0 h 平带不再盖住 6 h。
step = 2.60
fig = newfig(6.4, 6.6, width_fraction=0.90)
ax = fig.add_subplot(1, 1, 1)

for j in range(len(hours) - 1, -1, -1):
    base = j * step
    y = base + prof[j]
    ax.fill_between(r, y, base, color=cols[j], alpha=0.42, lw=0)
    ax.plot(r, y, color=cols[j], lw=1.25)
    ax.plot(r, np.full_like(r, base), color=C['neutral_light'], lw=0.5)

ax.set_yticks([j * step for j in range(len(hours))])
ax.set_yticklabels(['%.1f' % h for h in hours])
ax.set_ylabel('时间 $t$ (h) — 各脊线基线')
ax.set_xlabel('径向位置 $r$ (cm)')
ax.set_xlim(0.0, 2.42)
ax.set_ylim(-0.25, (len(hours) - 1) * step + 1.55)
ax.set_xticks(np.arange(0.0, 2.1, 0.5))
ax.yaxis.set_tick_params(which='minor', left=False)

# 幅值短尺挂在 0 h 基线右侧：只表示高度对应的 C，不与左轴时刻对齐。
x_bar = 2.10
c_ticks = (0.0, 1.0, 2.0, C0)
ax.plot([x_bar, x_bar], [0.0, C0], color=C['neutral_black'], lw=0.9,
        clip_on=False)
for cv, lab in zip(c_ticks, ('0', '1', '2', '2.55')):
    ax.plot([x_bar, x_bar + 0.04], [cv, cv], color=C['neutral_black'],
            lw=0.8, clip_on=False)
    ax.text(x_bar + 0.06, cv, lab, va='center', ha='left',
            color=C['neutral_black'])
ax.text(x_bar + 0.02, C0 + 0.18, '$C$ (kg/kg)', ha='left', va='bottom',
        color=C['neutral_black'])

# 末条脊线（t_end）峰值即达标判据值，标出其数值供读数
i_last = len(hours) - 1
ax.plot([0.0], [i_last * step + prof[i_last][0]], marker='o', ms=4.0,
        mfc='none', mew=1.1, color=C['red_strong'])
ax.text(0.08, i_last * step + 0.70,
        '%.3f h / %.4f kg/kg' % (t_end, prof[i_last][0]),
        color=C['red_strong'], va='bottom', ha='left')

finish(fig, 'fig_q3_ridgeline')
