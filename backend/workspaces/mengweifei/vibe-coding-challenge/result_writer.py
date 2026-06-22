"""
结果入库模块：将配额结果写入 ODPS + 降级方案。
"""

import csv
import logging
import os
from datetime import datetime
from pathlib import Path

from mock_odps.odps_client import ODPS

logger = logging.getLogger(__name__)

OUTPUT_TABLE = "icbu_ensa.dws_new_prod_quota_result"

FALLBACK_COLS = [
    'prod_id', 'comp_id', 'rqvae_id', 'x_曝光配额', 'y_冷启成功',
    'sim_time_to_first_ab', 'priority_score', 'ipv_roi_自然',
    'proxy_ctr', 'proxy_cvr_pay', 'is_broken_zero',
    'base_time_to_first_ab', 'imps_needed_to_break_xiuzheng',
    'real_imps', 'prod_name'
]


def write_to_odps(client: ODPS, results: list[dict], ds: str) -> bool:
    """尝试通过 SQL INSERT 写入 ODPS 结果表。

    Returns:
        bool: 写入成功返回 True，失败返回 False
    """
    logger.info("尝试写入 ODPS: %s, partition ds=%s", OUTPUT_TABLE, ds)
    try:
        # 使用 INSERT INTO ... VALUES 方式写入
        records = []
        for row in results:
            records.append([
                str(row.get('prod_id', '')),
                str(row.get('comp_id', '')),
                str(row.get('rqvae_id', '')),
                f"{row.get('x_曝光配额', 0)}",
                f"{row.get('y_冷启成功', 0)}",
                f"{row.get('sim_time_to_first_ab', 0)}",
            ])

        table = client.get_table("dws_new_prod_quota_result")
        partition_spec = f"ds='{ds}'"

        with table.open_writer(partition=partition_spec) as writer:
            for record in records:
                writer.write(record)

        logger.info("ODPS 写入成功: %d 条记录", len(records))
        return True

    except PermissionError as e:
        logger.warning("ODPS 写入被拒绝 (权限不足): %s", e)
        return False
    except Exception as e:
        logger.error("ODPS 写入异常: %s", e)
        return False


def generate_fallback(results: list[dict], ds: str, output_base: Path) -> dict:
    """降级方案：保存本地 CSV 并生成交付清单。

    Returns:
        dict: 降级交付信息
    """
    fallback_dir = output_base / "fallback"
    fallback_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 1. 保存配额 CSV 到 fallback 目录
    quota_file = fallback_dir / f"{ds}_quota_fallback.csv"
    with open(quota_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FALLBACK_COLS, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(results)
    logger.info("降级 CSV 已保存: %s", quota_file)

    # 2. 生成交付清单
    total_allocated = sum(r.get('x_曝光配额', 0) or 0 for r in results)
    supported = sum(1 for r in results if (r.get('x_曝光配额', 0) or 0) > 0)
    cold_start_success = sum(1 for r in results if r.get('y_冷启成功', 0) == 1)

    manifest_lines = [
        "=" * 60,
        "新品冷启动配额分配 - 降级交付清单",
        "=" * 60,
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"分区日期: {ds}",
        f"商品总数: {len(results)}",
        f"扶持商品数: {supported}",
        f"总分配配额: {total_allocated:.0f}",
        f"冷启成功数: {cold_start_success}",
        "",
        "--- 交付文件 ---",
        f"配额数据: {quota_file.absolute()}",
        "",
        "--- 交付说明 ---",
        "1. ODPS 写入因权限不足失败，已降级为本地 CSV 交付",
        "2. 配额结果包含以下核心字段:",
        "   - prod_id: 商品ID",
        "   - comp_id: 商家ID",
        "   - rqvae_id: 类目分组ID",
        "   - x_曝光配额: 分配的曝光配额",
        "   - y_冷启成功: 是否冷启成功 (0/1)",
        "   - sim_time_to_first_ab: 预计破零时间（天）",
        "3. 请使用有写入权限的账号执行以下命令完成入库:",
        f"   python run_pipeline.py --ds {ds} --upload-only",
        f"   或手动将配额文件导入 ODPS: {OUTPUT_TABLE}",
        f"4. 已设置环境变量 MOCK_ODPS_WRITE_ENABLED=1 可启用本地写入测试",
        "",
        "--- 校验信息 ---",
        f"MD5: 请手动计算: md5sum {quota_file.name}",
        "=" * 60,
    ]

    manifest_file = fallback_dir / f"{ds}_delivery_manifest.txt"
    with open(manifest_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(manifest_lines))

    logger.info("降级清单已生成: %s", manifest_file)

    return {
        'quota_file': str(quota_file),
        'manifest_file': str(manifest_file),
        'total_products': len(results),
        'supported_products': supported,
        'total_allocated': total_allocated,
        'cold_start_success': cold_start_success,
    }


def save_results(results: list[dict], ds: str, client: ODPS, output_base: Path) -> dict:
    """保存结果：先尝试 ODPS 写入，失败则降级。

    Returns:
        dict: 写入结果摘要
    """
    # 尝试 ODPS 写入
    odps_success = write_to_odps(client, results, ds)

    # 降级方案
    fallback_info = generate_fallback(results, ds, output_base)

    # 同时保存到 output/quota/ 目录
    quota_dir = output_base / "quota"
    quota_dir.mkdir(parents=True, exist_ok=True)
    quota_file = quota_dir / f"{ds}_新品配额.csv"
    with open(quota_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FALLBACK_COLS, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(results)
    logger.info("配额结果已保存到: %s", quota_file)

    return {
        'odps_success': odps_success,
        'fallback': fallback_info,
        'quota_csv': str(quota_file),
        'total_records': len(results),
    }
