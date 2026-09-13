"""fig_input_chamber — 附件1 烘房环境时序（241 行全量）双轴图。"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _figcommon import (C, M, load, newfig, finish, auto_legend, C_TH,
                        SEC_PER_HOUR)

d = load('inputs')
t_h = d['t_air'] / SEC_PER_HOUR
T = d['T_air']
Ca = d['C_air']

fig = newfig(6.4, 3.5, width_fraction=0.9)
ax = fig.add_subplot(1, 1, 1)
ax2 = ax.twinx()

ln1, = ax.plot(t_h, T, color=C['red_strong'], lw=1.6, label='空气温度 $T_{air}$')
ln2, = ax2.plot(t_h, Ca, color=C['blue_main'], lw=1.6, ls='--',
                label='空气含湿量 $C_{air}$')

# 升温段 / 平台段分界（附件1 数据本身的转折时刻，非人为设定）
i_pl = int(np.argmax(T >= T.max() - 1e-9))
t_pl = t_h[i_pl]
ax.axvline(t_pl, color=C['neutral_mid'], lw=0.8, ls=':')
ax.annotate('%.2f h' % t_pl, xy=(t_pl, 44.0),
            xytext=(t_pl + 0.10, 43.4), color=C['neutral_dark'])
ax.annotate('%.3f ℃' % T[-1], xy=(t_h[-1], T[-1]), xytext=(1.35, 51.2),
            color=C['red_strong'])
ax2.annotate('%.5f kg/kg' % Ca[-1], xy=(t_h[-1], Ca[-1]),
             xytext=(1.30, 0.0165), color=C['blue_main'])

ax.set_xlabel('时间 $t$ (h)')
ax.set_ylabel('空气温度 $T_{air}$ (℃)', color=C['red_strong'])
ax2.set_ylabel('空气含湿量 $C_{air}$ (kg/kg)', color=C['blue_main'])
ax.tick_params(axis='y', colors=C['red_strong'])
ax2.tick_params(axis='y', colors=C['blue_main'])
ax.set_xlim(0, t_h[-1])
ax.set_ylim(26, 54)
# 右轴量程下压，使 C_air 占据画面下半，与升至顶部的 T_air 曲线分带不叠
ax2.set_ylim(0.010, 0.080)
ax.set_xticks(np.arange(0, 4.5, 0.5))
auto_legend(ax, handles=[ln1, ln2], loc='center right')

finish(fig, 'fig_input_chamber')
