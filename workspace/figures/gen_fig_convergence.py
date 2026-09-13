"""fig_convergence — Q3/Q4 现成空间与时间步收敛数据。"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _figcommon import C, M, load_formal_csv, newfig, panel, finish  # noqa: E402

# 已锁定的现成收敛数据；本脚本只负责读正式 CSV 并绘图，不调用任何求解程序。
conv = load_formal_csv('final_diagnostics/convergence_final.csv')


def get_series(question, study, x_col):
    rows = conv[(conv['question'] == question) & (conv['study'] == study)]
    return (rows[x_col].to_numpy(dtype=float),
            rows['t_end_h'].to_numpy(dtype=float))


def get_selected(question, study):
    selected = conv['selected'].astype(str).str.lower().eq('true')
    rows = conv[(conv['question'] == question) &
                (conv['study'] == study) & selected]
    if len(rows) != 1:
        raise ValueError('%s %s 必须且只能有一个正式选用点' %
                         (question, study))
    return rows.iloc[0]


Ns, q3_N = get_series('Q3', 'grid', 'N')
q4_Ns, q4_N = get_series('Q4', 'grid', 'N')
if not np.array_equal(Ns, q4_Ns):
    raise ValueError('Q3/Q4 网格收敛的 N 序列不一致')
q3_dt, q3_tend = get_series('Q3', 'timestep', 'dt_s')
q4_dt, q4_tend = get_series('Q4', 'timestep', 'dt_s')

q3_grid_selected = get_selected('Q3', 'grid')
q4_grid_selected = get_selected('Q4', 'grid')
q3_dt_selected = get_selected('Q3', 'timestep')
q4_dt_selected = get_selected('Q4', 'timestep')

fig = newfig(6.4, 3.3, width_fraction=0.96)
gs = fig.add_gridspec(1, 2, wspace=0.30)
ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])

# (a) 空间收敛，整条曲线都是 Δt=1 s。菱形标的是正式选用的 N，
# 对应纵坐标仍是 Δt=1 s 的扫点，不是正式 Δt=0.25 s 的 57.4716 / 51.0869。
ax1.plot(Ns, q3_N, color=C['blue_main'], lw=1.6, marker=M[0], ms=5.0,
               )
ax1.plot(Ns, q4_N, color=C['green_3'], lw=1.6, marker=M[1], ms=5.0,
               )
ax1.axhline(round(q3_dt_selected['t_end_h'], 4),
            color=C['neutral_mid'], lw=0.9, ls=':')
ax1.plot([q3_grid_selected['N']], [q3_grid_selected['t_end_h']],
         marker='D', ms=6.5,
         color=C['red_strong'], zorder=4)
ax1.plot([q4_grid_selected['N']], [q4_grid_selected['t_end_h']],
         marker='D', ms=6.5,
         color=C['red_strong'], zorder=4)
ax1.set_xscale('log', base=2)
ax1.set_xlabel('径向控制体数 $N$')
# 轴标签只留量名与单位：并上"附录3 / 固定半径"后旋转标签高 217 pt、逼到画布顶缘
# 3.9 pt，几乎贯穿整个轴高。求解口径写进 caption。
ax1.set_ylabel('达标时间 $t_{end}$ (h)')
ax1.set_xlim(32.0, 3200.0)
ax1.set_ylim(50.7, 57.7)
ax1.set_xticks(Ns)
ax1.set_xticklabels(['%g' % value for value in Ns])
ax1.set_yticks(np.arange(51.0, 57.1, 2.0))
ax1.text(45.0, 57.18, 'Q3｜$N$=%g｜$\\Delta t$=%g s' %
         (q3_grid_selected['N'], q3_grid_selected['dt_s']),
         color=C['neutral_black'])
ax1.text(45.0, 51.28, 'Q4｜$N$=%g｜$\\Delta t$=%g s' %
         (q4_grid_selected['N'], q4_grid_selected['dt_s']),
         color=C['neutral_dark'])
panel(ax1, '(a)')

# (b) 时间步收敛：两问正式均取 Δt=0.25 s
ax2.plot(q3_dt, q3_tend, color=C['blue_main'], lw=1.6, marker=M[0], ms=5.0,
               )
ax2.plot(q4_dt, q4_tend, color=C['green_3'], lw=1.6, marker=M[1], ms=5.0,
               )
ax2.plot([q3_dt_selected['dt_s']], [q3_dt_selected['t_end_h']],
         marker='D', ms=6.5,
         color=C['red_strong'], zorder=4)
ax2.plot([q4_dt_selected['dt_s']], [q4_dt_selected['t_end_h']],
         marker='D', ms=6.5,
         color=C['red_strong'], zorder=4)
ax2.set_xscale('log', base=2)
ax2.set_xlabel('时间步 $\\Delta t$ (s)')
ax2.set_ylabel('达标时间 $t_{end}$ (h)')
ax2.set_xlim(1.2, 0.10)
ax2.set_ylim(50.7, 57.7)
dt_ticks = np.unique(np.concatenate((q3_dt, q4_dt)))[::-1]
ax2.set_xticks(dt_ticks)
ax2.set_xticklabels(['%g' % value for value in dt_ticks])
ax2.set_yticks(np.arange(51.0, 57.1, 2.0))
ax2.text(0.92, 57.18, 'Q3｜%.4f h｜$\\Delta t$=%g s' %
         (q3_dt_selected['t_end_h'], q3_dt_selected['dt_s']),
         color=C['neutral_black'])
ax2.text(0.92, 51.28, 'Q4｜%.4f h｜$\\Delta t$=%g s' %
         (q4_dt_selected['t_end_h'], q4_dt_selected['dt_s']),
         color=C['neutral_dark'])
panel(ax2, '(b)')

finish(fig, 'fig_convergence')
