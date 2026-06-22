#!/usr/bin/env python3
"""
参考实现：每日冷启新品配额分配（供 review 用）

以下代码实现了从 ODPS 获取数据、解析、求解、写入的全流程。
请从正确性、鲁棒性、工程化三个维度 review，找出其中的设计缺陷和潜在 bug。
"""

import pandas as pd
import numpy as np

# 配置
ACCESS_ID = "mock_access_id"
SECRET_KEY = "mock_secret_key"
PROJECT = "icbu_ensa"
ENDPOINT = "http://mock-odps.aliyun-inc.com/api"

# 预算系数
BUDGET_RATIO = 0.95


def run(ds):
    """运行每日冷启全流程。"""
    # 1. 连接 ODPS
    from mock_odps.odps_client import ODPS
    client = ODPS(ACCESS_ID, SECRET_KEY, PROJECT, ENDPOINT)

    # 2. 获取数据
    sql = f"SELECT group_id, big_chunk_string FROM icbu_ensa.dws_new_prod_info_data WHERE ds='{ds}'"
    result = client.execute_sql(sql, hints={"odps.sql.allow.fullscan": "true"})

    records = []
    with result.open_reader() as reader:
        for record in reader:
            records.append([record[0], record[1]])

    # 3. 写入原始 CSV
    import csv
    raw_file = f"/tmp/{ds}_raw.csv"
    with open(raw_file, "w", encoding="gbk") as f:
        writer = csv.writer(f)
        writer.writerow(["group_id", "big_chunk_string"])
        for row in records:
            writer.writerow(row)

    # 4. 解析数据
    df = pd.read_csv(raw_file, encoding="gbk")
    all_data = []
    for _, row in df.iterrows():
        chunk = row["big_chunk_string"]
        items = chunk.split("二")
        for item in items:
            fields = item.split("一")
            all_data.append(fields)

    parsed_df = pd.DataFrame(all_data)
    parsed_file = f"/tmp/{ds}_parsed.csv"
    parsed_df.to_csv(parsed_file, index=False, encoding="gbk")

    # 5. 配额求解
    data = pd.read_csv(parsed_file, encoding="gbk")

    # 预算
    budget = data["daily_incremental_imps_pool"].max() * BUDGET_RATIO

    # 贪心分配
    data_sorted = data.sort_values("priority_score", ascending=False)
    alloc = []
    remaining = budget
    for _, row in data_sorted.iterrows():
        need = row["imps_needed_to_break_xiuzheng"]
        if remaining >= need:
            alloc.append(need)
            remaining -= need
        else:
            alloc.append(0)
    data["quota"] = alloc

    # 破零时间计算
    sim_times = []
    for _, row in data.iterrows():
        if row["is_broken_zero"] == 1:
            sim_times.append(row["base_time_to_first_ab"])
        else:
            real = row["real_imps"]
            allocated = row["quota"]
            sim = row["base_time_to_first_ab"] * real / (real + allocated)
            sim_times.append(sim)
    data["sim_time"] = sim_times

    # 6. 写入 ODPS
    quota_file = f"/tmp/{ds}_quota.csv"
    data.to_csv(quota_file, index=False, encoding="gbk")

    table = client.get_table("dws_new_prod_quota_result")
    partition = f"ds='{ds}'"

    # 删除旧分区
    if table.exist_partition(partition):
        table.get_partition(partition).drop()

    # 写入
    with table.open_writer(partition=partition) as writer:
        for _, row in data.iterrows():
            writer.write(list(row))

    print(f"Done. Quota saved to {quota_file}")


if __name__ == "__main__":
    run("20260501")
