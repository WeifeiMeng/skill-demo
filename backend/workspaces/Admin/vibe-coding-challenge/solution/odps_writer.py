#!/usr/bin/env python3
"""
ODPS 结果写入模块 - 参考答案

考核点：候选人在没有 ODPS 写权限的情况下，如何设计数据入库方案。
"""

import csv
import shutil
from pathlib import Path


def write_quota_to_odps(odps_client, csv_path, ds, method="tunnel",
                        fallback_dir=None, notify_callback=None):
    """
    将配额结果写入 ODPS 分区表。

    面试场景说明：
      候选人的 ODPS 账号只有读取权限，没有写入生产表的权限。
      候选人需要：
      1. 捕获写入异常（PermissionError）
      2. 将结果保存为本地 CSV（降级方案）
      3. 输出交付信息，便于 DBA / 管理员代为入库

    参数:
        odps_client: Mock ODPS 客户端
        csv_path: 配额结果 CSV 路径
        ds: 分区日期 (YYYYMMDD)
        method: 写入方式 ("tunnel" 或 "sql")
        fallback_dir: 写入失败时的本地降级保存目录
        notify_callback: 通知回调函数，传入 (status, message, filepath)

    返回:
        (success: bool, record_count: int, info: dict)
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"配额结果文件不存在: {csv_path}")

    # 读取 CSV 数据
    with open(csv_path, 'r', encoding='gbk', errors='replace') as f:
        reader = csv.reader(f)
        rows = list(reader)
        if not rows:
            print("[WARN] 配额结果 CSV 为空")
            return False, 0, {"reason": "empty_csv"}

    columns = rows[0]
    data_rows = rows[1:]
    total_rows = len(data_rows)

    # 尝试写入 ODPS
    try:
        table = odps_client.get_table('dws_new_prod_quota_result')
        partition_spec = f"ds='{ds}'"

        # 检查并清理旧分区
        if table.exist_partition(partition_spec):
            print(f"[INFO] 分区 {partition_spec} 已存在，准备覆盖")
            table.get_partition(partition_spec).drop()

        if method == "tunnel":
            with table.open_writer(partition=partition_spec) as writer:
                for row in data_rows:
                    if row:
                        writer.write(row)
            msg = f"[OK] 通过 Tunnel 写入 {total_rows} 条记录到 {partition_spec}"
            print(msg)
            if notify_callback:
                notify_callback("success", msg, str(csv_path))
            return True, total_rows, {"method": "tunnel", "partition": partition_spec}

        elif method == "sql":
            record_count = 0
            for row in data_rows:
                if not row:
                    continue
                values = ", ".join([f"'{v}'" if v is not None else "NULL" for v in row])
                sql = f"INSERT INTO TABLE icbu_ensa.dws_new_prod_quota_result PARTITION (ds='{ds}') VALUES ({values})"
                try:
                    odps_client.execute_sql(sql)
                    record_count += 1
                except Exception as e:
                    print(f"[WARN] INSERT 失败: {e}")
            msg = f"[OK] 通过 SQL 写入 {record_count} 条记录到 {partition_spec}"
            print(msg)
            if notify_callback:
                notify_callback("success", msg, str(csv_path))
            return True, record_count, {"method": "sql", "partition": partition_spec}

        else:
            raise ValueError(f"不支持的写入方式: {method}")

    except PermissionError as e:
        # --- 核心考核点：无写权限时的降级处理 ---
        print(f"[WARN] ODPS 写入被拒绝: {e}")
        print("[INFO] 触发降级方案：将结果保存到本地，等待 DBA 代为入库")

        # 1. 保存到本地降级目录
        if fallback_dir is None:
            fallback_dir = Path(csv_path).parent.parent / "fallback"
        fallback_dir = Path(fallback_dir)
        fallback_dir.mkdir(parents=True, exist_ok=True)

        fallback_file = fallback_dir / f"{ds}_quota_ready_for_odps.csv"
        shutil.copy2(csv_path, fallback_file)

        # 2. 生成交付清单
        manifest_file = fallback_dir / f"{ds}_delivery_manifest.txt"
        with open(manifest_file, 'w', encoding='utf-8') as f:
            f.write(f"ODPS 数据交付清单\n")
            f.write(f"{'='*50}\n")
            f.write(f"日期分区: ds={ds}\n")
            f.write(f"目标表: icbu_ensa.dws_new_prod_quota_result\n")
            f.write(f"记录数: {total_rows}\n")
            f.write(f"数据文件: {fallback_file.name}\n")
            f.write(f"文件大小: {fallback_file.stat().st_size} 字节\n")
            f.write(f"\n请 DBA 使用以下命令入库:\n")
            f.write(f"  tunnel upload {fallback_file.name} "
                    f"icbu_ensa.dws_new_prod_quota_result/ds={ds}/\n")

        msg = (
            f"[FALLBACK] 因无 ODPS 写权限，已保存到本地: {fallback_file}\n"
            f"  交付清单: {manifest_file}\n"
            f"  请将此文件提交给 DBA 代为写入 ODPS"
        )
        print(msg)

        if notify_callback:
            notify_callback("fallback", msg, str(fallback_file))

        return False, total_rows, {
            "reason": "no_write_permission",
            "fallback_file": str(fallback_file),
            "manifest_file": str(manifest_file),
            "records": total_rows,
        }

    except Exception as e:
        print(f"[ERROR] ODPS 写入失败: {e}")
        if notify_callback:
            notify_callback("error", str(e), str(csv_path))
        return False, 0, {"reason": "write_error", "error": str(e)}
