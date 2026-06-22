"""
配额求解模块：基于 MIP（混合整数规划）的新品流量配额分配。

使用 pulp 开源求解器，建模业务目标与约束。
"""

import logging
import time
from pathlib import Path
import pulp
import csv

logger = logging.getLogger(__name__)


# --- 可配置参数 ---

# 总预算：平台每日总曝光配额
TOTAL_BUDGET = 200000

# 单商品分配上限
MAX_PER_PRODUCT = 5000

# 单个商家分配总量上限
MAX_PER_MERCHANT = 40000

# 每个商家最多扶持的商品数
MAX_PRODUCTS_PER_MERCHANT = 30

# 每个类目 (rqvae_id) 最多扶持的商品数
MAX_PRODUCTS_PER_RQVAE = 60

# 最低分配阈值（低于此值不分配，避免碎片化）
MIN_ALLOCATION = 50

# 目标函数权重
WEIGHT_PRIORITY = 1.0       # 优先级分数权重
WEIGHT_EFFICIENCY = 0.5     # 效率导向权重（ROI 归一化）
WEIGHT_TAIL_FAIRNESS = 0.3  # 尾部商家公平性权重
WEIGHT_ANTI_MONOPOLY = 0.1  # 反垄断惩罚权重


def compute_efficiency_score(row: dict) -> float:
    """计算商品转化效率得分，综合 CTR、CVR 和 ROI。"""
    ctr = row.get('proxy_ctr', 0) or 0
    cvr_pay = row.get('proxy_cvr_pay', 0) or 0
    p_ab = row.get('proxy_p_ab', 0) or 0
    return 0.3 * (ctr * 100) + 0.3 * (cvr_pay * 1000) + 0.4 * p_ab


def compute_tail_indicator(row: dict) -> int:
    """判断是否为尾部商家 (ipv_roi_自然 < 1)。"""
    roi = row.get('ipv_roi_自然', 0) or 0
    return 1 if roi < 1 else 0


def compute_monopoly_indicator(row: dict) -> int:
    """判断是否为头部商家 (ipv_roi_自然 > 20)。"""
    roi = row.get('ipv_roi_自然', 0) or 0
    return 1 if roi > 20 else 0


def compute_breaking_time(row: dict, allocated_imps: float) -> float:
    """计算预计破零时间。

    已破零商品 (is_broken_zero=1): 保持 base_time_to_first_ab
    未破零商品: sim_time = base_time * real_imps / (real_imps + allocated_imps)
    如果 allocated >= imps_needed_to_break_xiuzheng，认为已破零，取当前时间
    """
    is_broken = row.get('is_broken_zero', 0) or 0
    base_time = row.get('base_time_to_first_ab', 0) or 0
    real_imps = row.get('real_imps', 0) or 0
    imps_needed = row.get('imps_needed_to_break_xiuzheng', 0) or 0

    if is_broken == 1:
        return base_time

    # 如果分配量 >= 所需曝光量，视为已破零
    if imps_needed > 0 and allocated_imps >= imps_needed:
        return 1.0  # 破零成功，时间取最小值

    # 安全保护：除零
    denominator = real_imps + allocated_imps
    if denominator <= 0:
        return base_time

    return base_time * real_imps / denominator


def build_and_solve(rows: list[dict]) -> list[dict]:
    """构建 MIP 模型并求解配额分配。

    Returns:
        list[dict]: 包含分配的配额和破零状态的结果行
    """
    if not rows:
        logger.warning("无输入数据，跳过求解")
        return []

    start_time = time.time()
    products = []

    # 预处理：构建商品列表
    for idx, row in enumerate(rows):
        priority = row.get('priority_score', 0) or 0
        efficiency = compute_efficiency_score(row)
        is_tail = compute_tail_indicator(row)
        is_monopoly = compute_monopoly_indicator(row)

        comp_id = row.get('comp_id', 'UNKNOWN')
        rqvae_id = row.get('rqvae_id', 'UNKNOWN')
        imps_needed = row.get('imps_needed_to_break_xiuzheng', 0) or 0

        # 综合得分：用于目标函数
        score = (
            WEIGHT_PRIORITY * max(priority, 0) +
            WEIGHT_EFFICIENCY * efficiency +
            WEIGHT_TAIL_FAIRNESS * is_tail * efficiency -
            WEIGHT_ANTI_MONOPOLY * is_monopoly * efficiency
        )

        products.append({
            'index': idx,
            'original': row,
            'comp_id': comp_id,
            'rqvae_id': rqvae_id,
            'score': score,
            'imps_needed': imps_needed,
        })

    n = len(products)
    logger.info("构建 MIP 模型: %d 个商品, 总预算=%d", n, TOTAL_BUDGET)

    # --- 构建 MIP ---
    prob = pulp.LpProblem("ColdStart_Quota_Allocation", pulp.LpMaximize)

    # 决策变量：每条记录分配多少曝光
    x_vars = []
    y_vars = []  # 二进制：是否分配（>= MIN_ALLOCATION）

    for i in range(n):
        x = pulp.LpVariable(f"x_{i}", lowBound=0, upBound=MAX_PER_PRODUCT, cat='Continuous')
        y = pulp.LpVariable(f"y_{i}", cat='Binary')
        x_vars.append(x)
        y_vars.append(y)

    # --- 目标函数：最大化综合得分加权配额 ---
    objective = pulp.lpSum([products[i]['score'] * x_vars[i] for i in range(n)])
    prob += objective

    # --- 约束 ---

    # C1: 总预算约束
    prob += pulp.lpSum([x_vars[i] for i in range(n)]) <= TOTAL_BUDGET, "TotalBudget"

    # C2: 最低分配阈值（分配量 >= MIN_ALLOCATION 或 0）
    for i in range(n):
        prob += x_vars[i] >= MIN_ALLOCATION * y_vars[i], f"MinAlloc_{i}"
        prob += x_vars[i] <= MAX_PER_PRODUCT * y_vars[i], f"MaxPerProduct_{i}"

    # C3: 单个商家配额上限
    merchant_groups: dict[str, list[int]] = {}
    for i, p in enumerate(products):
        merchant_groups.setdefault(p['comp_id'], []).append(i)

    for comp_id, indices in merchant_groups.items():
        prob += pulp.lpSum([x_vars[i] for i in indices]) <= MAX_PER_MERCHANT, f"MerchantCap_{comp_id}"

    # C4: 每个商家扶持商品数上限
    for comp_id, indices in merchant_groups.items():
        prob += pulp.lpSum([y_vars[i] for i in indices]) <= MAX_PRODUCTS_PER_MERCHANT, f"MerchantProdCount_{comp_id}"

    # C5: 每个类目扶持商品数上限
    rqvae_groups: dict[str, list[int]] = {}
    for i, p in enumerate(products):
        rqvae_groups.setdefault(p['rqvae_id'], []).append(i)

    for rqvae_id, indices in rqvae_groups.items():
        prob += pulp.lpSum([y_vars[i] for i in indices]) <= MAX_PRODUCTS_PER_RQVAE, f"RqvaeProdCount_{rqvae_id}"

    # C6: 破零所需曝光约束（如果分配，至少达到 needed 的 50%）
    for i, p in enumerate(products):
        if p['imps_needed'] > 0:
            min_needed = min(p['imps_needed'] * 0.5, MAX_PER_PRODUCT)
            prob += x_vars[i] >= min_needed * y_vars[i], f"BreakNeeded_{i}"

    # --- 求解 ---
    logger.info("开始求解... (变量数: %d, 约束数: %d)", len(x_vars) * 2, len(prob.constraints))
    solver = pulp.PULP_CBC_CMD(msg=False)  # msg=False 抑制 CBC 输出
    prob.solve(solver)

    status = pulp.LpStatus[prob.status]
    elapsed = time.time() - start_time
    logger.info("求解完成: status=%s, 耗时=%.2fs", status, elapsed)

    if prob.status not in (pulp.LpStatusOptimal, pulp.LpStatusOptimal):
        logger.warning("未找到最优解，状态: %s，使用可行解", status)

    # --- 后处理：构建结果 ---
    results = []
    total_allocated = 0
    supported_count = 0

    for i in range(n):
        allocated = x_vars[i].varValue or 0.0
        # 四舍五入到整数
        allocated = round(allocated, 0)
        if allocated < 1:
            allocated = 0.0

        row = dict(products[i]['original'])

        # 计算破零时间
        sim_time = compute_breaking_time(row, allocated)
        is_broken = row.get('is_broken_zero', 0) or 0
        imps_needed = row.get('imps_needed_to_break_xiuzheng', 0) or 0

        # y_冷启成功: 已破零 或 分配量 >= 所需曝光量
        cold_start_success = 1 if (is_broken == 1 or (imps_needed > 0 and allocated >= imps_needed)) else 0

        row['x_曝光配额'] = allocated
        row['y_冷启成功'] = cold_start_success
        row['sim_time_to_first_ab'] = round(sim_time, 2)

        total_allocated += allocated
        if allocated > 0:
            supported_count += 1

        results.append(row)

    logger.info("分配结果: 总配额=%.0f/%.0f, 扶持商品数=%d/%d",
                total_allocated, TOTAL_BUDGET, supported_count, n)

    return results


def save_quota_csv(results: list[dict], filepath: Path):
    """保存配额结果为 CSV。"""
    filepath.parent.mkdir(parents=True, exist_ok=True)

    output_cols = [
        'prod_id', 'comp_id', 'rqvae_id', 'x_曝光配额', 'y_冷启成功',
        'sim_time_to_first_ab', 'priority_score', 'ipv_roi_自然',
        'proxy_ctr', 'proxy_cvr_pay', 'is_broken_zero',
        'base_time_to_first_ab', 'imps_needed_to_break_xiuzheng',
        'real_imps', 'prod_name'
    ]

    with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=output_cols, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(results)

    logger.info("配额结果已保存: %s (%d 条)", filepath, len(results))
