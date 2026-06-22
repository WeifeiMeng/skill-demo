#!/usr/bin/env python3
"""
数据解析核心模块 - 参考答案
"""

import pandas as pd


FINAL_COLUMNS = [
    'daily_incremental_imps_pool', 'rqvae_id', 'proxy_ctr', 'proxy_cvr_ab',
    'proxy_cvr_abpro', 'proxy_cvr_pay', 'proxy_p_ab', 'normalized_proxy_p_ab',
    'avg_time_to_first_ab', 'median_time_to_first_ab', 'prod_id', 'comp_id',
    'ipv_roi_自然', 'normalized_ipv_roi_自然', 'crt_time', 'prod_name',
    'real_imps', 'real_ab', 'base_time_to_first_ab', 'is_broken_zero',
    'imps_needed_to_break', 'imps_needed_to_break_xiuzheng',
    'normalized_imps_needed_to_break', 'priority_score', 'rn'
]

NUMERIC_COLUMNS = [
    'proxy_ctr', 'proxy_cvr_ab', 'proxy_cvr_abpro', 'proxy_cvr_pay',
    'proxy_p_ab', 'normalized_proxy_p_ab', 'avg_time_to_first_ab',
    'median_time_to_first_ab', 'ipv_roi_自然', 'normalized_ipv_roi_自然',
    'real_imps', 'real_ab', 'base_time_to_first_ab', 'is_broken_zero',
    'imps_needed_to_break', 'imps_needed_to_break_xiuzheng',
    'normalized_imps_needed_to_break', 'priority_score', 'rn'
]


def parse_raw_data(input_file, output_file):
    """解析原始数据为结构化 CSV。"""
    print(f"开始读取文件: {input_file}")

    df_raw = pd.read_csv(input_file, encoding='gbk')

    if 'group_id' in df_raw.columns and 'big_chunk_string' in df_raw.columns:
        chunk_col = 'big_chunk_string'
    elif len(df_raw.columns) == 2:
        chunk_col = df_raw.columns[1]
    else:
        raise ValueError("无法识别数据列结构，期望包含 group_id 和 big_chunk_string")

    print(f"读取完成，共 {len(df_raw)} 个数据包 (Groups)")

    all_records = []
    expected_field_count = len(FINAL_COLUMNS)

    skipped_records = 0
    field_mismatch = 0

    for _, row_data in df_raw.iterrows():
        chunk_str = str(row_data[chunk_col])

        if not chunk_str or chunk_str.lower() == 'nan':
            continue

        records_in_chunk = chunk_str.split('二')

        for record in records_in_chunk:
            record = record.strip()
            if not record:
                skipped_records += 1
                continue

            fields = record.split('一')

            # 处理字段数不一致的情况
            if len(fields) == expected_field_count:
                all_records.append(fields)
            elif len(fields) < expected_field_count:
                # 字段缺失，用空值补齐
                fields.extend([''] * (expected_field_count - len(fields)))
                all_records.append(fields)
                field_mismatch += 1
            else:
                # 字段过多，截断
                all_records.append(fields[:expected_field_count])
                field_mismatch += 1

    print(f"解析完成，共提取 {len(all_records)} 条原始记录")
    if skipped_records > 0:
        print(f"[WARN] 跳过了 {skipped_records} 条空记录")
    if field_mismatch > 0:
        print(f"[WARN] 处理了 {field_mismatch} 条字段数不一致的记录")

    if not all_records:
        print("没有提取到有效数据，请检查分隔符是否正确。")
        return

    df_final = pd.DataFrame(all_records, columns=FINAL_COLUMNS)

    for col in NUMERIC_COLUMNS:
        if col in df_final.columns:
            df_final[col] = pd.to_numeric(df_final[col], errors='coerce')

    df_final.to_csv(output_file, index=False, encoding='gbk')
    print(f"数据已保存至: {output_file}")
