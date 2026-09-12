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

# 山脊图基线间距：按最大剖面幅度定，保证相邻脊线不互穿
step = 0.34
fig = newfig(6.4, 4.4, width_fraction=0.9)
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
ax.set_xlim(0, 2.0)
ax.set_xticks(np.arange(0, 2.1, 0.25))
ax.set_ylim(-0.12, (len(hours) - 1) * step + 2.85)
# y 轴刻度是脊线基线（时刻序），次刻度无意义；样式默认开次刻度后自动定位器按
# 0.34 的主刻度间距细分出 65 个次刻度，间距只有 5.4 pt、长 1.5 pt，在脊线上连成
# 一条实心黑带，认不出刻度位置。
ax.yaxis.set_tick_params(which='minor', left=False)

# 右侧副轴给出脊线自身的含水率标尺（每格 0.34 kg/kg 对应一个基线间距）
ax2 = ax.twinx()
ax2.set_ylim(ax.get_ylim())
ax2.set_yticks([0.0, 1.0, 2.0, 2.55])
ax2.set_yticklabels(['0', '1', '2', '2.55'])
ax2.set_ylabel('自基线起算的 $C$ (kg/kg)')
# 副轴同理：4 个不等距主刻度细分出 30 个次刻度，右脊线上半段成一排密点梳齿
ax2.yaxis.set_tick_params(which='minor', right=False)

# 末条脊线（t_end）峰值即达标判据值，标出其数值供读数
i_last = len(hours) - 1
ax.plot([0.0], [i_last * step + prof[i_last][0]], marker='o', ms=4.0,
        mfc='none', mew=1.1, color=C['red_strong'])
ax.annotate('%.3f h / %.4f kg/kg' % (t_end, prof[i_last][0]),
            xy=(0.0, i_last * step + prof[i_last][0]),
            xytext=(0.08, i_last * step + 1.60), color=C['red_strong'])

finish(fig, 'fig_q3_ridgeline')
