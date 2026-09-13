"""fig_q4_shrink_effect — 问题4 共同网格效应隔离（正式诊断）。

数据源只允许 output/final_diagnostics/q4_effect_isolation_final.csv。
正式口径：S2 χ=1 材料随动 ALE（主模型），S3 χ=0 Eulerian/Landau（交叉验证）。
S0 是共同网格诊断基准，不是正式问题三。
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _figcommon import C, load_formal_csv, newfig, panel, finish  # noqa: E402

FORMAL_CSV = 'final_diagnostics/q4_effect_isolation_final.csv'
df = load_formal_csv(FORMAL_CSV)
df.columns = [c.strip().lstrip('\ufeff') for c in df.columns]

# 最终诊断把共同网格 S0 记为 S0_bridge；作图与正文统一写成 S0。
id_map = {'S0_bridge': 'S0'}
df['scenario'] = df['case_id'].astype(str).map(lambda s: id_map.get(s, s))
df = df[df['scenario'].isin(['S0', 'S1', 'S2', 'S3', 'S4'])].copy()
df['t_end_h'] = df['t_end_h'].astype(float)
order = ['S0', 'S1', 'S2', 'S3', 'S4']
df = df.set_index('scenario').loc[order].reset_index()

chi = {row.scenario: str(row.chi) for row in df.itertuples(index=False)}
if chi.get('S2') not in ('1', '1.0') or chi.get('S3') not in ('0', '0.0'):
    raise RuntimeError('正式诊断 χ 关系异常：S2=%s S3=%s（应为 S2=1, S3=0）'
                       % (chi.get('S2'), chi.get('S3')))

names = {
    'S0': 'S0 共同网格诊断基准',
    'S1': 'S1 附录4 / 固定 2 cm',
    'S2': 'S2 附录4 / 收缩, χ=1',
    'S3': 'S3 附录4 / 收缩, χ=0',
    'S4': 'S4 附录4 / 固定 1.198 cm',
}
sc = list(df['scenario'])
tv = np.array(df['t_end_h'], dtype=float)
t_s0 = float(tv[sc.index('S0')])
t_s1 = float(tv[sc.index('S1')])
t_s2 = float(tv[sc.index('S2')])
t_s3 = float(tv[sc.index('S3')])
d_prop = t_s1 - t_s0
d_shrink = t_s2 - t_s1
d_net = t_s2 - t_s0
if abs((d_prop + d_shrink) - d_net) > 1e-9:
    raise RuntimeError('加总关系不成立: %.10f + %.10f != %.10f'
                       % (d_prop, d_shrink, d_net))
print('[source] N=1280  dt=0.25s  S0=%.4f  S1=%.4f  S2=%.4f  S3=%.4f  S4=%.4f'
      % (t_s0, t_s1, t_s2, t_s3, float(tv[sc.index('S4')])), flush=True)
print('[source] 换物性=%+.4f  加收缩=%+.4f  净差=%+.4f  Δχ=%+.4f'
      % (d_prop, d_shrink, d_net, t_s3 - t_s2), flush=True)

dev = tv - t_s0

fig = newfig(6.4, 3.9, width_fraction=0.98)
gs = fig.add_gridspec(1, 2, wspace=0.32, width_ratios=[1.25, 1.0])
ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])

# (a) 各情景相对 S0 共同网格诊断基准的发散柱
y = np.arange(len(sc))
colors = [C['neutral_light'] if abs(v) < 1e-9 else
          (C['red_strong'] if v > 0 else C['blue_main']) for v in dev]
ax1.barh(y, dev, height=0.62, color=colors, edgecolor=C['neutral_black'], lw=0.5)
ax1.axvline(0.0, color=C['neutral_black'], lw=0.9)
ax1.set_yticks(y)
ax1.set_yticklabels(['%s\n%.4f h' % (names[s], tv[j])
                     for j, s in enumerate(sc)])
ax1.set_xlabel('$t_{end}$ 相对 S0 的偏差 (h)')
ax1.set_ylabel('效应隔离情景')
ax1.set_xlim(-16.0, 80.0)
ax1.set_xticks(np.arange(-10, 71, 20))
ax1.set_ylim(-0.65, len(sc) - 0.35)
ax1.invert_yaxis()
panel(ax1, '(a)')

# (b) 三项都从 0 起画，避免瀑布图把「加收缩 −78.76 h」看成另一根 +72 h 柱。
steps = [('换物性', d_prop, C['red_strong']),
         ('加收缩', d_shrink, C['blue_main']),
         ('净差', d_net, C['green_3'])]
xb = np.arange(3)
for j, (lab, val, col) in enumerate(steps):
    ax2.bar(xb[j], val, bottom=0.0, width=0.56, color=col,
            edgecolor=C['neutral_black'], lw=0.5)
ax2.axhline(0.0, color=C['neutral_black'], lw=0.9)
ax2.set_xticks(xb)
ax2.set_xticklabels(['物性', '收缩', '净差'])
ax2.set_ylabel('$t_{end}$ 变化量 (h)｜S1−S0 / S2−S1 / S2−S0')
ax2.set_xlim(-0.62, 2.62)
ax2.set_ylim(-98.0, 92.0)
ax2.set_yticks(np.arange(-80, 81, 20))
for j, (lab, val, col) in enumerate(steps):
    # 长柱：读数贴在柱尖外侧。短净差柱：改挂到零轴另一侧，避免字高吃进柱体。
    if abs(val) < 15.0:
        ytxt, va = (10.0, 'bottom') if val < 0 else (-10.0, 'top')
    elif val >= 0:
        ytxt, va = val + 5.0, 'bottom'
    else:
        ytxt, va = val - 5.0, 'top'
    ax2.text(xb[j], ytxt, '%+.4f h' % val, ha='center', va=va, color=col)
panel(ax2, '(b)')

finish(fig, 'fig_q4_shrink_effect')
