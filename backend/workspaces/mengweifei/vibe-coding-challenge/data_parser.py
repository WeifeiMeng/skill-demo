"""
数据解析模块：将 big_chunk_string 解析为结构化数据。
"""

import csv
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

FINAL_COLUMNS = [
    'daily_incremental_imps_pool', 'rqvae_id', 'proxy_ctr', 'proxy_cvr_ab',
    'proxy_cvr_abpro', 'proxy_cvr_pay', 'proxy_p_ab', 'normalized_proxy_p_ab',
    'avg_time_to_first_ab', 'median_time_to_first_ab', 'prod_id', 'comp_id',
    'ipv_roi_自然', 'normalized_ipv_roi_自然', 'crt_time', 'prod_name',
    'real_imps', 'real_ab', 'base_time_to_first_ab', 'is_broken_zero',
    'imps_needed_to_break', 'imps_needed_to_break_xiuzheng',
    'normalized_imps_needed_to_break', 'priority_score', 'rn'
]

NUM_COLS = len(FINAL_COLUMNS)

FIELD_SEP = '一'   # \\u4e00
RECORD_SEP = '二'  # \\u4e8c

# 需要做数值类型转换的字段及其类型
NUMERIC_FIELDS: dict[str, type] = {
    'daily_incremental_imps_pool': int,
    'proxy_ctr': float,
    'proxy_cvr_ab': float,
    'proxy_cvr_abpro': float,
    'proxy_cvr_pay': float,
    'proxy_p_ab': float,
    'normalized_proxy_p_ab': float,
    'avg_time_to_first_ab': float,
    'median_time_to_first_ab': float,
    'ipv_roi_自然': float,
    'normalized_ipv_roi_自然': float,
    'real_imps': int,
    'real_ab': int,
    'base_time_to_first_ab': float,
    'is_broken_zero': int,
    'imps_needed_to_break': float,
    'imps_needed_to_break_xiuzheng': float,
    'normalized_imps_needed_to_break': float,
    'priority_score': float,
    'rn': int,
}


def safe_convert(value: str | None, target_type: type, default=None):
    """安全类型转换，转换失败返回默认值并记录警告。"""
    if value is None or value == '':
        if default is not None:
            return default
        return 0 if target_type is int else 0.0 if target_type is float else ''

    try:
        if target_type is int:
            return int(float(value))
        if target_type is float:
            return float(value)
        return target_type(value)
    except (ValueError, TypeError):
        if default is not None:
            return default
        return 0 if target_type is int else 0.0 if target_type is float else str(value)


def parse_one_record(field_string: str, record_index: int = 0) -> dict | None:
    """解析单条记录字符串为字典。
    异常处理：
    - 空记录返回 None
    - 字段数不足用 None 填充
    - 字段数超出截断
    """
    if not field_string or not field_string.strip():
        return None

    fields = field_string.split(FIELD_SEP)
    actual = len(fields)

    if actual < 5:  # 太少字段不太可能是有效数据
        logger.warning("记录#%d: 只有 %d 个字段，跳过", record_index, actual)
        return None

    if actual > NUM_COLS:
        logger.warning("记录#%d: 字段数 %d > 预期 %d，截断", record_index, actual, NUM_COLS)
        fields = fields[:NUM_COLS]
    elif actual < NUM_COLS:
        logger.debug("记录#%d: 字段数 %d < 预期 %d，用空值填充", record_index, actual, NUM_COLS)
        fields = fields + [''] * (NUM_COLS - actual)

    row = {}
    anomaly_flags = []

    for i, col in enumerate(FINAL_COLUMNS):
        raw = fields[i].strip() if fields[i] else ''

        if col in NUMERIC_FIELDS:
            target = NUMERIC_FIELDS[col]
            converted = safe_convert(raw, target)
            row[col] = converted

            # 检测潜在异常值
            if raw != '' and col == 'imps_needed_to_break_xiuzheng' and converted == 0:
                anomaly_flags.append(f'{col}=0 (破零所需曝光为0)')
            if raw != '' and col == 'base_time_to_first_ab' and converted == 0:
                anomaly_flags.append(f'{col}=0 (基准破零时间为0)')
            if raw != '' and col == 'real_imps' and converted == 0:
                anomaly_flags.append(f'{col}=0 (真实曝光为0)')
            if raw != '' and col == 'priority_score' and converted < 0:
                anomaly_flags.append(f'{col}<0 ({converted})')
        else:
            row[col] = raw

    if anomaly_flags:
        logger.debug("记录#%d (prod_id=%s): 异常值 - %s",
                     record_index, row.get('prod_id', '?'), ', '.join(anomaly_flags))

    return row


def parse_big_chunk(group_id: str, big_chunk_string: str) -> list[dict]:
    """解析整个 big_chunk_string 为结构化记录列表。"""
    if not big_chunk_string:
        logger.warning("group_id=%s: big_chunk_string 为空", group_id)
        return []

    records = []
    raw_records = big_chunk_string.split(RECORD_SEP)

    for i, raw in enumerate(raw_records):
        parsed = parse_one_record(raw, i)
        if parsed is not None:
            parsed['_group_id'] = group_id
            records.append(parsed)

    logger.info("group_id=%s: 解析 %d/%d 条有效记录", group_id, len(records), len(raw_records))
    return records


def parse_all(raw_records: list[tuple[str, str]]) -> list[dict]:
    """解析所有原始记录。"""
    all_rows = []
    empty_count = 0

    for group_id, chunk in raw_records:
        if not chunk:
            empty_count += 1
            continue
        rows = parse_big_chunk(group_id, chunk)
        all_rows.extend(rows)

    logger.info("总解析: %d 条有效记录, %d 个空数据包", len(all_rows), empty_count)
    return all_rows


def save_parsed_csv(rows: list[dict], filepath: Path):
    """保存解析后的数据为 CSV。"""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    export_cols = [c for c in FINAL_COLUMNS if c in next(iter(rows), {})]

    with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=export_cols, extrasaction='ignore')
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    logger.info("解析结果已保存: %s (%d 条)", filepath, len(rows))
