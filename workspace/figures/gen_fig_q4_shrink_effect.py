"""fig_q4_shrink_effect — 问题4 的 2×2 因子设计。"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _figcommon import C, load_csv, newfig, panel, finish  # noqa: E402

df = load_csv('effect_isolation.csv')
df.columns = [c.strip().lstrip('\ufeff') for c in df.columns]
df = df[df['scenario'].astype(str).str.match(r'^L\d{2}$')].copy()
df['t_end_h'] = df['t_end_h'].astype(float)

order = ['L00', 'L10', 'L01', 'L11']
names = {'L00': r'$t_{00}$ 附录3 / 固定',
         'L10': r'$t_{10}$ 附录4 / 固定',
         'L01': r'$t_{01}$ 附录3 / 收缩',
         'L11': r'$t_{11}$ 附录4 / 收缩'}
tv = np.array([float(df.loc[df['scenario'] == s, 't_end_h'].iloc[0]) for s in order])
t00, t10, t01, t11 = tv
I = t11 - t10 - t01 + t00
prop = 0.5 * ((t10 - t00) + (t11 - t01))
shrink = 0.5 * ((t01 - t00) + (t11 - t10))

fig = newfig(6.6, 3.7, width_fraction=0.98)
gs = fig.add_gridspec(1, 2, wspace=0.34, width_ratios=[1.15, 1.0])
ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])

x = np.arange(4)
cols = [C['neutral_light'], C['red_strong'], C['blue_main'], C['green_3']]
ax1.bar(x, tv, width=0.62, color=cols, edgecolor=C['neutral_black'], lw=0.5)
ax1.set_xticks(x)
ax1.set_xticklabels([names[s] for s in order], fontsize=7)
ax1.set_ylabel(r'$t_{\rm end}$ (h)')
ax1.set_ylim(0, 150)
for j, v in enumerate(tv):
    ax1.annotate('%.1f' % v, xy=(x[j], v), xytext=(x[j], v + 4),
                 ha='center', fontsize=7)
panel(ax1, '(a)')

steps = [('物性', prop, C['red_strong']),
         ('收缩', shrink, C['blue_main']),
         ('交互 $I$', I, C['neutral_dark']),
         ('净差', t11 - t00, C['green_3'])]
xb = np.arange(4)
for j, (lab, val, col) in enumerate(steps):
    ax2.bar(xb[j], val, width=0.58, color=col, edgecolor=C['neutral_black'], lw=0.5)
ax2.axhline(0.0, color=C['neutral_black'], lw=0.8)
ax2.set_xticks(xb)
ax2.set_xticklabels([s[0] for s in steps], fontsize=8)
ax2.set_ylabel(r'贡献 (h)')
for j, (lab, val, col) in enumerate(steps):
    yoff = 6 if val >= 0 else -12
    ax2.annotate('%+.1f' % val, xy=(xb[j], val),
                 xytext=(xb[j], val + yoff), ha='center', fontsize=7, color=col)
panel(ax2, '(b)')

finish(fig, 'fig_q4_shrink_effect')
