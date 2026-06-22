#!/usr/bin/env python3
"""
每日冷启新品数据全流程脚本 - 参考答案
"""

import sys
import time
import argparse
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "mock_odps"))
from odps_client import ODPS

from credentials import get_credentials
from data_fetch import fetch_odps_data, get_latest_ds, write_raw_csv
from parse_core import parse_raw_data
from solve_core import solve
from odps_writer import write_quota_to_odps
from utils import progress, format_duration, verify_csv

RAW_DIR = Path(__file__).parent.parent / "output" / "raw"
PARSED_DIR = Path(__file__).parent.parent / "output" / "parsed"
QUOTA_DIR = Path(__file__).parent.parent / "output" / "quota"


def main():
    parser = argparse.ArgumentParser(description="每日冷启新品数据全流程")
    parser.add_argument("--ds", type=str, default=None, help="指定分区日期 (YYYYMMDD)，默认使用最新分区")
    parser.add_argument("--write-method", type=str, default="tunnel", choices=["sql", "tunnel"],
                        help="ODPS 写入方式: tunnel(默认) 或 sql")
    args = parser.parse_args()

    print(f"{'='*60}")
    print("每日冷启新品数据全流程")
    print(f"{'='*60}")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    step_times = []
    total_steps = 6

    # ---------- Step 1: 凭据 ----------
    progress(1, total_steps, "读取 ODPS 凭据")
    t0 = time.time()
    access_id, secret_key, project, endpoint = get_credentials()
    print(f"[OK] Project: {project}")
    step_times.append(("读取 ODPS 凭据", time.time() - t0))

    # ---------- Step 2: 连接 ODPS & 获取数据 ----------
    progress(2, total_steps, "连接 ODPS 并获取分区数据")
    t0 = time.time()
    odps_client = ODPS(access_id, secret_key, project, endpoint)

    if args.ds:
        ds = args.ds
        print(f"[OK] 使用指定日期: {ds}")
    else:
        ds = get_latest_ds(odps_client)
        if not ds:
            print("[FAIL] 无法获取最新分区日期")
            return
        print(f"[OK] 最新分区: {ds}")

    columns, records = fetch_odps_data(odps_client, ds)
    print(f"[OK] 获取 {len(records)} 条原始记录")

    raw_file = write_raw_csv(columns, records, ds, RAW_DIR)
    print(f"[OK] 原始数据已写入: {raw_file}")
    step_times.append(("连接 ODPS 并获取分区数据", time.time() - t0))

    # ---------- Step 3: 验证原始文件 ----------
    progress(3, total_steps, "验证原始数据文件")
    t0 = time.time()
    verify_csv(raw_file, "原始数据")
    step_times.append(("验证原始数据文件", time.time() - t0))

    # ---------- Step 4: 解析数据 ----------
    progress(4, total_steps, "解析原始数据为结构化 CSV")
    t0 = time.time()
    parsed_file = PARSED_DIR / f"{ds}_新品数据(已解析).csv"
    parse_raw_data(str(raw_file), str(parsed_file))
    verify_csv(parsed_file, "解析后数据")
    step_times.append(("解析原始数据为结构化 CSV", time.time() - t0))

    # ---------- Step 5: 配额求解 ----------
    progress(5, total_steps, "运行配额求解")
    t0 = time.time()
    quota_file = QUOTA_DIR / f"{ds}_新品配额.csv"
    summary = solve(str(parsed_file), str(quota_file))
    verify_csv(quota_file, "配额结果")
    step_times.append(("运行配额求解", time.time() - t0))

    # ---------- Step 6: 写入 ODPS ----------
    progress(6, total_steps, "写入 ODPS 分区表并汇总")
    t0 = time.time()
    success, record_count, write_info = write_quota_to_odps(
        odps_client, str(quota_file), ds, method=args.write_method
    )
    step_times.append(("写入 ODPS 分区表", time.time() - t0))

    # 打印报告
    print("\n" + "="*60)
    print("  冷启全流程运行汇总报告")
    print("="*60)
    print(f"  日期分区: {ds}")
    print(f"  运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    print("\n  ▎各步骤耗时")
    for name, t in step_times:
        print(f"    {name}: {format_duration(t)}")

    if summary:
        print(f"\n  ▎求解核心指标")
        print(f"    预算上限: {summary.get('budget', 'N/A')}")
        print(f"    扶持商品数: {summary.get('opt_supported')}")
        print(f"    冷启成功数: {summary.get('opt_success')}")

    print(f"\n  ▎ODPS 入库")
    print(f"    目标表: dws_new_prod_quota_result")
    print(f"    写入方式: {args.write_method}")
    if success:
        print(f"    写入状态: 成功")
        print(f"    写入记录数: {record_count}")
    else:
        print(f"    写入状态: 降级（本地保存）")
        print(f"    记录数: {record_count}")
        if write_info.get("fallback_file"):
            print(f"    降级文件: {write_info['fallback_file']}")
        if write_info.get("manifest_file"):
            print(f"    交付清单: {write_info['manifest_file']}")

    print("\n" + "="*60)
    if success:
        print("  [SUCCESS] 全流程执行完成")
    else:
        print("  [COMPLETED WITH FALLBACK] 流程完成，但 ODPS 写入失败，结果已本地保存")
    print("="*60)


if __name__ == "__main__":
    main()
