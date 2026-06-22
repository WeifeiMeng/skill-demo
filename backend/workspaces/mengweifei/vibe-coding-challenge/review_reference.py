"""
参考实现：新品冷启动流量配额分配系统
=========================================
注意：这段代码包含多处设计缺陷和潜在 bug，请仔细 review。

这是生产环境中可能出现的典型写法——看起来"能跑通"，但存在
正确性、鲁棒性和工程化方面的问题。
"""

import csv
import os
import sys

# 全局常量
TOTAL_BUDGET = 100000
MAX_PER_MERCHANT = 30000
MAX_PER_PRODUCT = 5000
MAX_PRODUCTS_PER_MERCHANT = 50
MAX_PRODUCTS_PER_RQVAE = 100

FINAL_COLUMNS = [
    'daily_incremental_imps_pool', 'rqvae_id', 'proxy_ctr', 'proxy_cvr_ab',
    'proxy_cvr_abpro', 'proxy_cvr_pay', 'proxy_p_ab', 'normalized_proxy_p_ab',
    'avg_time_to_first_ab', 'median_time_to_first_ab', 'prod_id', 'comp_id',
    'ipv_roi_自然', 'normalized_ipv_roi_自然', 'crt_time', 'prod_name',
    'real_imps', 'real_ab', 'base_time_to_first_ab', 'is_broken_zero',
    'imps_needed_to_break', 'imps_needed_to_break_xiuzheng',
    'normalized_imps_needed_to_break', 'priority_score', 'rn'
]


def parse_big_chunk(big_chunk_string):
    """解析 big_chunk_string 为结构化数据。"""
    records = big_chunk_string.split('二')
    result = []

    for record in records:
        fields = record.split('一')
        row = {}
        for i, col in enumerate(FINAL_COLUMNS):
            row[col] = fields[i]  # 直接用索引，不做边界检查
        result.append(row)

    return result


def convert_types(rows):
    """将字符串转换为正确的类型。"""
    for row in rows:
        row['proxy_ctr'] = float(row['proxy_ctr'])
        row['proxy_cvr_ab'] = float(row['proxy_cvr_ab'])
        row['ipv_roi_自然'] = float(row['ipv_roi_自然'])
        row['real_imps'] = int(row['real_imps'])
        row['is_broken_zero'] = int(row['is_broken_zero'])
        row['base_time_to_first_ab'] = float(row['base_time_to_first_ab'])
        row['imps_needed_to_break_xiuzheng'] = float(row['imps_needed_to_break_xiuzheng'])
    return rows


def allocate_quota(rows):
    """配额分配——简化版贪心算法。"""
    total_used = 0
    for row in rows:
        # 按 priority_score 降序分配
        sorted_rows = sorted(rows, key=lambda x: x['priority_score'], reverse=True)

        for row in sorted_rows:
            if total_used >= TOTAL_BUDGET:
                break
            quota = min(MAX_PER_PRODUCT, TOTAL_BUDGET - total_used)
            row['x_曝光配额'] = quota
            total_used += quota

    return rows


def write_to_odps(client, rows, ds):
    """写入 ODPS 结果表。"""
    sql = (
        "INSERT OVERWRITE TABLE icbu_ensa.dws_new_prod_quota_result "
        f"PARTITION (ds='{ds}') "
        "SELECT * FROM tmp_result"
    )
    client.execute_sql(sql)
    print(f"写入完成: {len(rows)} 条记录")


def run_pipeline(ds):
    """主 pipeline。"""
    # 先尝试真实 ODPS，失败不处理
    try:
        from odps import ODPS as RealODPS
        client = RealODPS('xxx', 'yyy', 'icbu_ensa')
    except ImportError:
        from mock_odps.odps_client import ODPS
        client = ODPS('mock_id', 'mock_key', 'icbu_ensa')

    # 数据获取
    sql = f"SELECT group_id, big_chunk_string FROM icbu_ensa.dws_new_prod_info_data WHERE ds='{ds}'"
    result = client.execute_sql(sql)

    all_rows = []
    with result.open_reader() as reader:
        for record in reader:
            rows = parse_big_chunk(record[1])
            all_rows.extend(rows)

    # 类型转换
    all_rows = convert_types(all_rows)

    # 配额分配
    all_rows = allocate_quota(all_rows)

    # 写入结果
    write_to_odps(client, all_rows, ds)

    # 输出简单统计
    print(f"总商品数: {len(all_rows)}")


if __name__ == '__main__':
    ds = sys.argv[1] if len(sys.argv) > 1 else '20260501'
    run_pipeline(ds)
