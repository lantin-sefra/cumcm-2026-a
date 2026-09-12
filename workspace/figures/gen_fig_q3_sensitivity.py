"""fig_q3_sensitivity — 问题3 达标时长单因子灵敏度（正式诊断）。

数据源只允许 output/final_diagnostics/q3_sensitivity_final.csv。
正式口径：基准为正式 Q3（N=2560, 57.4716 h），χ 扰动为 1→0。
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _figcommon import C, load_formal_csv, newfig, finish  # noqa: E402

df = load_formal_csv('final_diagnostics/q3_sensitivity_final.csv')
df.columns = [c.strip().lstrip('\ufeff') for c in df.columns]
base = float(df.loc[df['case_id'] == 'BASE', 't_end_h'].iloc[0])
if abs(base - 57.4716) > 5e-4:
    raise RuntimeError('灵敏度基准偏离正式 Q3：%.6f h' % base)
print('[source] N=2560  dt=0.25s  BASE=%.4f h  χ: 1→0' % base, flush=True)

rows = df[df['case_id'] != 'BASE'].copy()
rows['dev'] = rows['delta_h_vs_BASE'].astype(float)

labels = {
    'h_m': '对流传质系数 $h_m$ ±20%',
    'h': '对流换热系数 $h$ ±20%',
    'D_prefactor': '扩散前因子 $D_0$ ±20%',
    'T_air_plateau_after_4h': '空气温度平台值',
    'C_air_plateau_after_4h': '空气含湿平台值',
    'surface_boundary_type': '表面边界条件改 Dirichlet',
    'chi_closure_Q4': '移动边界闭合 $\\chi$: 1→0',
    'latent_heat_sink': '蒸发潜热汇（结构性）',
    'C_th': '达标阈值 $C_{th}$: 0.15→0.2',
}
items = []
for p, lab in labels.items():
    sub = rows[rows['parameter'] == p]
    if not len(sub):
        continue
    lo = float(sub['dev'].min())
    hi = float(sub['dev'].max())
    items.append((lab, lo, hi, max(abs(lo), abs(hi))))
    print('[source] %s  %.4f .. %.4f h' % (p, lo, hi), flush=True)
items.sort(key=lambda x: x[3])

y = np.arange(len(items))
neg = [min(it[1], 0.0) for it in items]
pos = [max(it[2], 0.0) for it in items]

fig = newfig(6.4, 3.8, width_fraction=0.94)
ax = fig.add_subplot(1, 1, 1)
ax.barh(y, neg, height=0.60, color=C['blue_main'],
        edgecolor=C['neutral_black'], lw=0.5, label='使 $t_{end}$ 缩短')
ax.barh(y, pos, height=0.60, color=C['red_strong'],
        edgecolor=C['neutral_black'], lw=0.5, label='使 $t_{end}$ 延长')
ax.vlines(0.0, -0.45, len(items) - 0.55, color=C['neutral_black'], lw=0.9)

ax.set_yticks(y)
ax.set_yticklabels([it[0] for it in items])
ax.set_xlabel('$t_{end}$ 相对基准 %.2f h 的变化 (h)' % base)
ax.set_ylabel('单因子扰动项')
ax.set_xlim(-32.0, 16.0)
ax.set_xticks(np.arange(-30, 16.1, 10))
ax.set_ylim(-0.7, len(items) - 0.3)

top = items[-1]
ax.text(0.8, y[-1], '%+.1f h' % top[1], ha='left', va='center',
        color=C['neutral_black'])
fig.legend(*ax.get_legend_handles_labels(), loc='outside upper center',
           ncol=2, frameon=False)

finish(fig, 'fig_q3_sensitivity')
