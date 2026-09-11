# 能力清单验收总账（逐项）

- ✅ **P1-C1** [semantic] PASS — 结论 PASS —— code/driver.py:172-190 每步同时解 T^{n+1} 与 C^{n+1} 两场（形状同为 N+1）；code/fvm.py:90-102 离散算子含柱坐标面积权重 2π·ξ_{i±1/2}（等价 1/r 的有限体积形式）；code/props.py:31 附录2 D=7e-9·exp(-0.89/C) 随逐点 C 计算为数组；中心零通量为自然边界（fvm.py:9 注释，无显式 Dirichlet）。
- ✅ **P1-C2** [machine] PASS — 结论 PASS —— code/ambient.py:41-53 读附件1 全部 241 行（params.py:26 N_ROWS_ATTACH1=241 断言，行数不符即 raise）；ambient.py:28-38 np.interp 线性插值 T_air(t)/C_air(t)，t>14400s 取平台值。code/data_check.py 断言附件1 行数==241。
- ✅ **P1-C3** [machine] PASS — 产物 output/table1_2_problem1.csv 已产出（722 bytes；仅验证交付存在，不代表内容正确）
- ✅ **P1-C4** [machine] PASS — 产物 output/result1.xlsx 已产出（395781 bytes；仅验证交付存在，不代表内容正确）
- ✅ **P2-C1** [semantic] PASS — 结论 PASS —— code/props.py:43-48 附录3 四式全变：ρ=650+128C、cp=1450+2736w、k=0.21+0.38w、D=2.4e-3·exp(-0.45/C)·exp(-3850/T_K)；props.py:37-40 T_K=T_℃+273.15 且 K15 断言 T_K>273（误用℃即 raise）；driver.py:172-186 每步 Picard 重算物性并双向耦合（C→ρ/cp/k→传热，T→D→传质）。未出现附录2 常数 820/2600/0.36。
- ✅ **P2-C2** [machine] PASS — 结论 PASS —— code/ambient.py:32,38 分段：t<=14400s 插值附件1 升温段，t>14400s 返回平台值 TA_PLATEAU=50.165℃/CA_PLATEAU=0.04986（params.py:95-96）；driver.py 主推进至 t_end≈56.7h≫14400s(=4h)，跨越升温段与恒温平台段。
- ✅ **P2-C3** [machine] PASS — 产物 output/table3_4_problem2.csv 已产出（619 bytes；仅验证交付存在，不代表内容正确）
- ✅ **P2-C4** [machine] PASS — 产物 output/result2.xlsx 已产出（27990679 bytes；仅验证交付存在，不代表内容正确）
- ✅ **P3-C1** [machine] PASS — 结论 PASS —— code/driver.py:215-221 终止判据用逐点最大值 maxC=np.max(C)（driver.py:130 record 存 np.max(Cf)），首次 maxC<C_TH(=0.15) 时式(19)亚步线性插值定位 t_end；非 mean/体平均。problem_3_results.json：t_end=56.706h，maxC_at_end=0.14999987（<0.15），落在 24–120h 内。
- ✅ **P3-C2** [machine] PASS — 产物 output/table5_problem3.csv 已产出（473 bytes；仅验证交付存在，不代表内容正确）
- ✅ **P3-C3** [machine] PASS — 产物 output/result3.xlsx 已产出（363673 bytes；仅验证交付存在，不代表内容正确）
- ✅ **P4-C1** [semantic] PASS — 结论 PASS —— code/geometry.py:36-63 MovingGeometry 读附件2 全部 145 行（params.py:27 N_ROWS_ATTACH2=145 断言），PCHIP 保形插值 R(t) 与解析导数 Rdot(t)，累积最小值单调化；code/fvm.py:116-125 χ=0 时含 Landau 对流项 (1-χ)·κ·ξ·Rdot/R 一阶迎风；code/props.py:50-55 物性用附录4 系数 760/90/1850/2150/0.12/0.20/4.2e-4/0.30，未用附录3 系数。
- ✅ **P4-C2** [machine] PASS — 结论 PASS —— code/problem4.py:55-73 同一离散/环境/判据下运行 S2（附录4+收缩，t=52.190h）与 S1（附录4+固定R=2cm，t=128.594h）隔离收缩效应；driver.py:215-221 收缩域内 maxC<0.15 判定。problem_4_results.json effect_isolation：prop_swap=+71.885h、shrink=-76.404h、net=-4.519h，加性恒等残差 7.1e-15。
- ✅ **P4-C3** [machine] PASS — 产物 output/table6_problem4.csv 已产出（402 bytes；仅验证交付存在，不代表内容正确）
- ✅ **P4-C4** [machine] PASS — 产物 output/result4.xlsx 已产出（316083 bytes；仅验证交付存在，不代表内容正确）
- ✅ **X-C1** [semantic] PASS — 结论 PASS —— 四项证据齐备（output/validation.json evidence_section9）：(1) 网格无关性 9_2_grid_independence N=40 vs N=160 eT=2.76e-5/eC=3.04e-4<0.5%，另 ev_face_mode N∈{20,40,80}、tend_gridsens N∈{20,40}，共 4 套网格；(2) 时间步无关性 9_2_dt_independence Δt∈{2,1,0.5}s eT/eC≈5e-5<0.5%（3 个步长）；(3) 半解析级数+Duhamel 9_3_bessel_duhamel_P1 逐点最大偏差 0.0012℃（≈0.0036%<1%），code/validate.py:51-95；(4) 水分总量守恒残差 9_1_mass_budget ~1e-14<1e-10，driver.py:203-209 逐步累加 resid_step_max/mass_bal_abs。