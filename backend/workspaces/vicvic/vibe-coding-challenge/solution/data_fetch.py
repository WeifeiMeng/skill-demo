#!/usr/bin/env python3
"""
ODPS 数据获取模块 - 参考答案
"""

import csv
from pathlib import Path


def fetch_odps_data(odps_client, ds):
    """从 ODPS 获取指定分区的原始数据。"""
    sql = f"""SELECT group_id, big_chunk_string
FROM icbu_ensa.dws_new_prod_info_data
WHERE ds = '{ds}'"""
    result = odps_client.execute_sql(sql, hints={"odps.sql.allow.fullscan": "true"})

    records = []
    with result.open_reader() as reader:
        for record in reader:
            records.append([record[0], record[1]])

    return ["group_id", "big_chunk_string"], records


def get_latest_ds(odps_client):
    """获取最新分区日期。"""
    sql = "SELECT MAX_PT('icbu_ensa.dws_new_prod_info_data')"
    result = odps_client.execute_sql(sql, hints={"odps.sql.allow.fullscan": "true"})
    with result.open_reader() as reader:
        for record in reader:
            return str(record[0])
    return None


def write_raw_csv(columns, records, ds, output_dir):
    """将原始数据写入 GBK 编码的 CSV 文件。"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{ds}_新品数据(未解析).csv"
    filepath = output_dir / filename

    with open(filepath, "w", encoding="gbk", errors="replace") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        for row in records:
            cleaned_row = [str(cell) if cell is not None else "" for cell in row]
            writer.writerow(cleaned_row)

    return filepath
