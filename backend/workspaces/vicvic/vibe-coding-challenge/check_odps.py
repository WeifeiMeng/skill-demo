#!/usr/bin/env python3
"""
检查 Mock ODPS 中指定分区的状态。

用法：
    python check_odps.py --ds 20260501
    python check_odps.py --check-latest
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "mock_odps"))
from odps_client import ODPS


def check_partition(ds: str):
    """检查指定分区是否存在且有数据。"""
    client = ODPS('mock_id', 'mock_key', 'icbu_ensa')

    print(f"检查分区: ds={ds}")
    print("-" * 50)

    # 检查上游表
    try:
        table = client.get_table('dws_new_prod_info_data')
        if table.exist_partition(f"ds='{ds}'"):
            print("[OK] 上游表 dws_new_prod_info_data 分区存在")

            # 读取数据量
            result = client.execute_sql(
                f"SELECT group_id, big_chunk_string FROM icbu_ensa.dws_new_prod_info_data WHERE ds='{ds}'"
            )
            with result.open_reader() as reader:
                records = list(reader)
                print(f"[OK] 上游数据包数: {len(records)}")
        else:
            print(f"[FAIL] 上游表 dws_new_prod_info_data 分区 ds={ds} 不存在")
    except Exception as e:
        print(f"[FAIL] 上游表检查失败: {e}")

    # 检查下游表
    try:
        table = client.get_table('dws_new_prod_quota_result')
        if table.exist_partition(f"ds='{ds}'"):
            print("[OK] 下游表 dws_new_prod_quota_result 分区存在")

            result = client.execute_sql(
                f"SELECT 1 FROM icbu_ensa.dws_new_prod_quota_result WHERE ds='{ds}' LIMIT 1"
            )
            with result.open_reader() as reader:
                records = list(reader)
                if len(records) > 0:
                    print("[OK] 下游分区有数据")
                else:
                    print("[WARN] 下游分区存在但无数据")
        else:
            print(f"[INFO] 下游表 dws_new_prod_quota_result 分区 ds={ds} 不存在（尚未写入）")
    except Exception as e:
        print(f"[FAIL] 下游表检查失败: {e}")


def check_latest():
    """检查最新分区日期。"""
    client = ODPS('mock_id', 'mock_key', 'icbu_ensa')
    result = client.execute_sql("SELECT MAX_PT('icbu_ensa.dws_new_prod_info_data')")
    with result.open_reader() as reader:
        for record in reader:
            latest_ds = record[0]
            if latest_ds:
                print(f"[OK] 最新分区: ds={latest_ds}")
            else:
                print("[INFO] 暂无分区数据")
            return


def main():
    parser = argparse.ArgumentParser(description="检查 Mock ODPS 分区状态")
    parser.add_argument("--ds", type=str, help="指定分区日期 (YYYYMMDD)")
    parser.add_argument("--check-latest", action="store_true", help="检查最新分区")
    args = parser.parse_args()

    if args.check_latest:
        check_latest()
    elif args.ds:
        check_partition(args.ds)
    else:
        print("用法: python check_odps.py --ds 20260501")
        print("       python check_odps.py --check-latest")


if __name__ == "__main__":
    main()
