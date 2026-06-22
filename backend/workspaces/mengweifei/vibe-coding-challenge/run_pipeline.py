#!/usr/bin/env python3
"""
新品冷启动流量配额分配系统 - 主入口

用法:
    python run_pipeline.py --ds 20260501

流程:
    数据获取 → 数据解析 → 配额求解 → 结果入库（含降级方案）
"""

import argparse
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

from data_loader import create_client, fetch_raw_data, get_latest_ds
from data_parser import parse_all, save_parsed_csv
from quota_solver import build_and_solve, save_quota_csv
from result_writer import save_results

# --- 配置 ---
OUTPUT_BASE = Path(__file__).parent / "output"

# 输出目录结构
OUTPUT_RAW_DIR = OUTPUT_BASE / "raw"
OUTPUT_PARSED_DIR = OUTPUT_BASE / "parsed"
OUTPUT_QUOTA_DIR = OUTPUT_BASE / "quota"


def setup_logging(verbose: bool = False):
    """配置日志。"""
    level = logging.DEBUG if verbose else logging.INFO
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    logging.basicConfig(level=level, format=fmt, datefmt="%H:%M:%S")


def ensure_output_dirs():
    """确保输出目录存在。"""
    for d in [OUTPUT_RAW_DIR, OUTPUT_PARSED_DIR, OUTPUT_QUOTA_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def run(ds: str, upload_only: bool = False) -> dict:
    """执行完整 pipeline。

    Args:
        ds: 分区日期 YYYYMMDD
        upload_only: 如果为 True，仅尝试上传已有配额结果

    Returns:
        dict: 运行摘要
    """
    log = logging.getLogger("pipeline")
    stats = {'ds': ds, 'start_time': datetime.now()}
    ensure_output_dirs()

    client = create_client()

    # ============================================================
    # 环节一：数据获取
    # ============================================================
    log.info("=" * 50)
    log.info("环节一：数据获取")
    log.info("=" * 50)

    if not ds:
        ds = get_latest_ds(client) or "20260501"
        log.info("未指定 ds，使用最新分区: %s", ds)

    raw_records = fetch_raw_data(client, ds)
    stats['raw_groups'] = len(raw_records)

    if not raw_records:
        log.error("未获取到任何数据，终止 pipeline")
        return stats

    # 保存原始数据
    raw_csv = OUTPUT_RAW_DIR / f"{ds}_新品数据(未解析).csv"
    import csv
    raw_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(raw_csv, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['group_id', 'big_chunk_string'])
        for gid, chunk in raw_records:
            writer.writerow([gid, chunk])
    log.info("原始数据已保存: %s", raw_csv)

    # ============================================================
    # 环节二：数据解析
    # ============================================================
    log.info("=" * 50)
    log.info("环节二：数据解析")
    log.info("=" * 50)

    parsed_rows = parse_all(raw_records)
    stats['parsed_records'] = len(parsed_rows)

    if not parsed_rows:
        log.error("未解析到任何有效记录，终止 pipeline")
        return stats

    # 保存解析后的数据
    parsed_csv = OUTPUT_PARSED_DIR / f"{ds}_新品数据(已解析).csv"
    save_parsed_csv(parsed_rows, parsed_csv)

    # 异常统计
    broken_zero_count = sum(1 for r in parsed_rows if r.get('is_broken_zero', 0) == 1)
    zero_imps_needed = sum(1 for r in parsed_rows if (r.get('imps_needed_to_break_xiuzheng', 0) or 0) == 0)
    zero_real_imps = sum(1 for r in parsed_rows if (r.get('real_imps', 0) or 0) == 0)
    zero_base_time = sum(1 for r in parsed_rows if (r.get('base_time_to_first_ab', 0) or 0) == 0)
    null_rqvae = sum(1 for r in parsed_rows if not r.get('rqvae_id'))
    null_comp = sum(1 for r in parsed_rows if not r.get('comp_id'))

    log.info("异常统计: 已破零=%d, 所需曝光=0→%d, 真实曝光=0→%d, "
             "基准时间=0→%d, 缺失rqvae=%d, 缺失comp=%d",
             broken_zero_count, zero_imps_needed, zero_real_imps,
             zero_base_time, null_rqvae, null_comp)
    stats['anomalies'] = {
        'broken_zero': broken_zero_count,
        'zero_imps_needed': zero_imps_needed,
        'zero_real_imps': zero_real_imps,
        'zero_base_time': zero_base_time,
        'null_rqvae': null_rqvae,
        'null_comp': null_comp,
    }

    # ============================================================
    # 环节三：配额求解
    # ============================================================
    log.info("=" * 50)
    log.info("环节三：配额求解 (MIP)")
    log.info("=" * 50)

    solve_start = time.time()
    results = build_and_solve(parsed_rows)
    solve_elapsed = time.time() - solve_start

    stats['solve_time_seconds'] = round(solve_elapsed, 2)
    stats['total_products'] = len(results)

    if not results:
        log.error("配额求解无结果")
        return stats

    # 保存配额结果
    quota_csv = OUTPUT_QUOTA_DIR / f"{ds}_新品配额.csv"
    save_quota_csv(results, quota_csv)

    total_allocated = sum(r.get('x_曝光配额', 0) or 0 for r in results)
    supported = sum(1 for r in results if (r.get('x_曝光配额', 0) or 0) > 0)
    cold_start_success = sum(1 for r in results if r.get('y_冷启成功', 0) == 1)

    stats['total_allocated'] = total_allocated
    stats['supported_products'] = supported
    stats['cold_start_success'] = cold_start_success

    # ============================================================
    # 环节四：结果入库
    # ============================================================
    log.info("=" * 50)
    log.info("环节四：结果入库")
    log.info("=" * 50)

    write_result = save_results(results, ds, client, OUTPUT_BASE)
    stats['write_result'] = write_result

    # ============================================================
    # 运行报告
    # ============================================================
    elapsed_total = (datetime.now() - stats['start_time']).total_seconds()
    stats['total_time_seconds'] = round(elapsed_total, 2)

    log.info("=" * 60)
    log.info("Pipeline 运行完成")
    log.info("=" * 60)
    log.info("分区日期:     %s", ds)
    log.info("原始数据包:   %d", stats['raw_groups'])
    log.info("解析记录数:   %d", stats['parsed_records'])
    log.info("总商品数:     %d", stats['total_products'])
    log.info("扶持商品数:   %d", supported)
    log.info("冷启成功数:   %d", cold_start_success)
    log.info("总分配配额:   %.0f", total_allocated)
    log.info("求解耗时:     %.2fs", solve_elapsed)
    log.info("总耗时:       %.2fs", elapsed_total)
    log.info("ODPS写入:     %s", "成功" if write_result.get('odps_success') else "失败(已降级)")
    log.info("降级文件:     %s", write_result.get('fallback', {}).get('quota_file', 'N/A'))
    log.info("=" * 60)

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="新品冷启动流量配额分配系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python run_pipeline.py --ds 20260501
  python run_pipeline.py --ds 20260501 --verbose
        """
    )
    parser.add_argument("--ds", type=str, default="",
                        help="分区日期 YYYYMMDD (不指定则使用最新分区)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="输出详细日志")
    parser.add_argument("--upload-only", action="store_true",
                        help="仅上传已有配额结果 (降级恢复)")
    args = parser.parse_args()

    setup_logging(args.verbose)

    try:
        stats = run(args.ds, args.upload_only)
        return 0 if stats.get('total_products', 0) > 0 else 1
    except Exception as e:
        logging.getLogger("pipeline").exception("Pipeline 执行失败: %s", e)
        return 2


if __name__ == '__main__':
    sys.exit(main())
