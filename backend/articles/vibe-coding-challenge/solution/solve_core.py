#!/usr/bin/env python3
"""
配额求解核心模块 - 参考答案（基于 pulp，无需 Gurobi）

设计说明：
  目标函数：
    max a1 * sum(y_i) + a2 * sum(p_i * v_i * y_i) + a3 * sum(y_i for tail) - a4 * sum(y_i for head)
    
    - a1=5000（扶持商品数权重）: 首要目标是让更多商品获得配额
    - a2=200（效率权重）: 优先扶持转化概率高的商品
    - a3=100（尾部扶持权重）: 给 ROI < 1 的尾部商家适当倾斜
    - a4=100（头部惩罚权重）: 避免 ROI > 20 的头部商家过度占用资源
    
    权重选择依据：
      - a1 远大于其他项，确保"扶持覆盖面"是第一优先级
      - a2*p_i*v_i 使效率导向在同等覆盖下发挥作用
      - a3 和 a4 用于平衡公平性和效率，避免头部垄断

  约束条件：
    1. 总预算 <= pool * 0.95（预留 5% 缓冲）
    2. 商家曝光上限 3000（防止单商家独占）
    3. 单商品曝光上限 500（控制单商品配额）
    4. 商家商品数上限 30（防止单商家商品过多）
    5. 类目商品数上限 100（保证类目多样性）

  阈值设定依据：
    - 测试数据中 daily_pool 约 80,000~100,000，预算约 80,000~90,000
    - 单商品破零所需曝光中位数约 200，500 是合理上限
    - 商家数约 40，每个商家最多扶持 30 个商品是合理的
    - 类目数约 20，每个类目最多扶持 100 个商品保证多样性
"""

import numpy as np
import pandas as pd
from collections import defaultdict


def read_data(input_file):
    """读取求解数据，处理缺失值和 0 值（避免后续除零）。"""
    data = pd.read_csv(input_file, encoding='gbk')
    data['imps_needed_to_break_xiuzheng'] = data['imps_needed_to_break_xiuzheng'].fillna(1)
    data['imps_needed_to_break_xiuzheng'] = data['imps_needed_to_break_xiuzheng'].replace(0, 1)
    data['base_time_to_first_ab'] = data['base_time_to_first_ab'].fillna(180)
    data['base_time_to_first_ab'] = data['base_time_to_first_ab'].replace(0, 1)
    data['real_imps'] = data['real_imps'].fillna(0)
    data['proxy_p_ab'] = data['proxy_p_ab'].fillna(0)
    return data


def get_param(data):
    """获取求解参数。"""
    params = {}
    params['I'] = set(data['prod_id'])
    params['M'] = set(data['comp_id'])
    params['R'] = set(data['rqvae_id'])
    params['H'] = set(data.loc[data['ipv_roi_自然'] > 20, 'comp_id'])
    params['L'] = set(data.loc[data['ipv_roi_自然'] < 1, 'comp_id'])

    params['I_H'] = (data['ipv_roi_自然'] > 20).astype(int).to_frame().set_index(data['prod_id']).iloc[:, 0].to_dict()
    params['I_L'] = (data['ipv_roi_自然'] < 1).astype(int).to_frame().set_index(data['prod_id']).iloc[:, 0].to_dict()
    m_i = {(data.loc[row, 'comp_id'], data.loc[row, 'prod_id']): 1 for row in range(data.shape[0])}
    r_m = {(data.loc[row, 'rqvae_id'], data.loc[row, 'comp_id']): 1 for row in range(data.shape[0])}
    r_i = {(data.loc[row, 'rqvae_id'], data.loc[row, 'prod_id']): 1 for row in range(data.shape[0])}

    params['pv_max'] = data['daily_incremental_imps_pool'].max() * 0.95
    params['m_pv_max'] = 3000
    params['i_pv_max'] = 500
    params['num1'] = 30
    params['num2'] = 12
    params['num3'] = 100

    params['pv_min_i'] = dict(zip(data['prod_id'], data['imps_needed_to_break_xiuzheng']))
    params['pab_i'] = dict(zip(data['prod_id'], data['proxy_p_ab'].fillna(0)))

    params.update({'m_i': m_i, 'r_m': r_m, 'r_i': r_i})
    return params


def _build_summary(data, params, opt_allocated, needed):
    """构建求解结果汇总字典。"""
    base_time = data['base_time_to_first_ab']

    head_mask = data['prod_id'].map(params['I_H']).astype(bool)
    tail_mask = data['prod_id'].map(params['I_L']).astype(bool)
    mid_mask = ~head_mask & ~tail_mask
    pab = data['prod_id'].map(params['pab_i'])
    pv_min = data['prod_id'].map(params['pv_min_i'])

    SEP = '=' * 60
    THIN_SEP = '-' * 60

    # 分配后破零时间
    sim_col = data['sim_time_to_first_ab']
    avg_sim = sim_col[sim_col < 180].mean()
    avg_base = base_time[base_time < 180].mean()

    print('\n' + SEP)
    print('  破零时间对比：优化前 | 基于最优化')
    print(SEP)

    print(f"\n  平均破零时间（过滤 >= 180 天）")
    print(THIN_SEP)
    print(f"    优化前: {avg_base:.2f} 天")
    print(f"    基于最优化: {avg_sim:.2f} 天 ({avg_sim-avg_base:+.2f})")
    print(THIN_SEP)

    opt_supported = (opt_allocated > 0).astype(int)
    print(f"\n  扶持商品数量: {opt_supported.sum()}")
    print(f"  扶持商家数量: {data.loc[opt_supported.astype(bool), 'comp_id'].nunique()}")

    broken = data['is_broken_zero']
    cond_a = broken == 1
    opt_success = np.where(cond_a, 1, (opt_allocated >= needed).astype(int))
    print(f"  冷启成功数量: {opt_success.sum():.0f}")

    opt_eff = (pab * pv_min * opt_success).sum()
    print(f"  总效率: {opt_eff:.2f}")

    print('\n' + SEP)
    return {
        "avg_base_time": round(float(avg_base), 2),
        "avg_opt_time": round(float(avg_sim), 2),
        "opt_supported": int(opt_supported.sum()),
        "opt_success": int(opt_success.sum()),
        "opt_efficiency": round(float(opt_eff), 2),
        "budget": int(params["pv_max"]),
    }


def solve(input_file, output_file):
    """执行配额求解（基于 pulp，无需 Gurobi）。"""
    try:
        import pulp
    except ImportError:
        print("[ERROR] 缺少 pulp 库，请运行: pip install pulp")
        return None

    data = read_data(input_file)
    print("==============读取数据成功===============")
    params = get_param(data)
    print("==============参数处理成功===============")

    prob = pulp.LpProblem("cold_start_quota", pulp.LpMaximize)

    I_list = list(params['I'])
    y = pulp.LpVariable.dicts("y", I_list, cat='Binary')
    print("==============创建变量成功===============")

    a1, a2, a3, a4 = 5000, 200, 100, 100
    prob += (
        a1 * pulp.lpSum([y[i] for i in I_list]) +
        a2 * pulp.lpSum([params['pab_i'][i] * params['pv_min_i'][i] * y[i] for i in I_list]) +
        a3 * pulp.lpSum([params['I_L'][i] * y[i] for i in I_list]) -
        a4 * pulp.lpSum([params['I_H'][i] * y[i] for i in I_list])
    )
    print("==============创建目标成功===============")

    # 约束1：总预算
    prob += pulp.lpSum([params['pv_min_i'][i] * y[i] for i in I_list]) <= params['pv_max']
    print("==============创建约束1成功==============")

    # 约束2：商家曝光上限
    m_to_items = defaultdict(list)
    for (m_id, i_id) in params['m_i']:
        m_to_items[m_id].append(i_id)
    for m in params['M']:
        if m in m_to_items:
            prob += pulp.lpSum([params['pv_min_i'][i] * y[i] for i in m_to_items[m]]) <= params['m_pv_max']
    print("==============创建约束2成功==============")

    # 约束3：单商品曝光上限
    for i in I_list:
        prob += params['pv_min_i'][i] * y[i] <= params['i_pv_max']
    print("==============创建约束3成功==============")

    # 约束4：商家商品数上限
    for m in params['M']:
        if m in m_to_items:
            prob += pulp.lpSum([y[i] for i in m_to_items[m]]) <= params['num1']
    print("==============创建约束4成功==============")

    # 约束5：类目商品数上限
    r_to_items = defaultdict(list)
    for (r_id, i_id) in params['r_i']:
        r_to_items[r_id].append(i_id)
    for r in params['R']:
        if r in r_to_items:
            prob += pulp.lpSum([y[i] for i in r_to_items[r]]) <= params['num3']
    print("==============创建约束5成功==============")

    solver = pulp.PULP_CBC_CMD(msg=1, timeLimit=300, threads=0)
    prob.solve(solver)

    status = pulp.LpStatus[prob.status]
    print(f'\n求解状态: {status}')
    print('目标函数值:', pulp.value(prob.objective))

    if prob.status != pulp.LpStatusOptimal and prob.status != pulp.LpStatusNotSolved:
        print(f'求解可能未收敛，状态: {status}')

    y_values = {i: int(y[i].varValue) if y[i].varValue is not None else 0 for i in I_list}
    data['y_冷启成功'] = data['prod_id'].map(lambda i: y_values.get(i, 0))
    data['x_曝光配额'] = data['prod_id'].map(lambda i: params['pv_min_i'].get(i, 0) * y_values.get(i, 0))

    # 计算破零时间
    sim_allocated = data['x_曝光配额']
    real = data['real_imps']
    base_time = data['base_time_to_first_ab']
    broken = data['is_broken_zero']
    needed = data['imps_needed_to_break_xiuzheng']
    cond_a = broken == 1

    def calc_sim_time(allocated):
        cond_b = (broken != 1) & (allocated >= needed)
        compressed = np.where(
            real == 0,
            np.where(cond_b, 1.0, base_time),
            np.round(base_time * (real / (real + allocated)), 2)
        )
        return np.where(cond_a, base_time, compressed)

    data['sim_time_to_first_ab'] = calc_sim_time(sim_allocated)

    summary = _build_summary(data, params, sim_allocated, needed)

    data.to_csv(output_file, index=False, encoding='gbk')
    print(f'求解结果已保存至: {output_file}')
    return summary
