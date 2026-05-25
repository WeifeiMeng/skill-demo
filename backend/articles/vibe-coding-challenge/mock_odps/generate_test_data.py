"""
测试数据生成器

为 vibe coding 题目生成模拟的 ODPS 上游数据。
生成逻辑：
1. 生成 N 个商家，每个商家有若干商品
2. 每个商品有随机属性（CTR、CVR、ROI、破零时间等）
3. 将商品按商家分组，聚合成 big_chunk_string 格式
4. 写入 mock ODPS 的本地文件系统

使用方法:
    python generate_test_data.py --ds 20260501 --products 200 --seed 42
"""

import argparse
import csv
import random
import os
from pathlib import Path
from datetime import datetime, timedelta


FINAL_COLUMNS = [
    'daily_incremental_imps_pool', 'rqvae_id', 'proxy_ctr', 'proxy_cvr_ab',
    'proxy_cvr_abpro', 'proxy_cvr_pay', 'proxy_p_ab', 'normalized_proxy_p_ab',
    'avg_time_to_first_ab', 'median_time_to_first_ab', 'prod_id', 'comp_id',
    'ipv_roi_自然', 'normalized_ipv_roi_自然', 'crt_time', 'prod_name',
    'real_imps', 'real_ab', 'base_time_to_first_ab', 'is_broken_zero',
    'imps_needed_to_break', 'imps_needed_to_break_xiuzheng',
    'normalized_imps_needed_to_break', 'priority_score', 'rn'
]


def generate_products(num_products: int, seed: int = 42) -> list:
    """生成模拟商品数据。"""
    random.seed(seed)

    # 商家池
    num_merchants = max(3, num_products // 5)
    merchant_ids = [f"COMP_{i:04d}" for i in range(num_merchants)]

    # rqvae 池（类目/属性分组）
    num_rqvae = max(2, num_products // 10)
    rqvae_ids = [f"RQ_{i:03d}" for i in range(num_rqvae)]

    products = []
    daily_pool = random.randint(50000, 100000)

    for i in range(num_products):
        comp_id = random.choice(merchant_ids)
        rqvae_id = random.choice(rqvae_ids)
        prod_id = f"PROD_{i:06d}"

        # 随机属性
        ctr = round(random.uniform(0.01, 0.15), 4)
        cvr_ab = round(random.uniform(0.001, 0.05), 4)
        cvr_abpro = round(random.uniform(0.0005, 0.03), 4)
        cvr_pay = round(random.uniform(0.0001, 0.01), 4)

        # p_ab = ctr * cvr_ab * 某个系数
        p_ab = round(ctr * cvr_ab * 100, 6)
        norm_p_ab = round(p_ab * random.uniform(0.8, 1.2), 6)

        # ROI
        roi = round(random.uniform(0.5, 30.0), 2)
        norm_roi = round(roi * random.uniform(0.9, 1.1), 2)

        # 破零相关
        base_time = round(random.uniform(30, 180), 2)
        avg_time = round(base_time * random.uniform(0.8, 1.5), 2)
        median_time = round(base_time * random.uniform(0.7, 1.3), 2)

        # 是否已破零
        is_broken = random.choice([0, 1])
        real_imps = random.randint(0, 500) if is_broken == 0 else random.randint(500, 5000)
        real_ab = int(real_imps * cvr_ab * random.uniform(0.5, 2.0))

        # 破零所需曝光（控制在合理范围，使最优化约束有意义）
        imps_needed = max(10, int(base_time * random.uniform(0.5, 3)))
        imps_needed_xiuzheng = max(10, int(imps_needed * random.uniform(0.8, 1.5)))
        norm_imps_needed = round(imps_needed * random.uniform(0.9, 1.1), 2)

        # === 埋入异常边界情况 ===
        # 约 3% 的商品破零所需曝光为 0（测试除零处理）
        if random.random() < 0.03:
            imps_needed_xiuzheng = 0

        # 约 2% 的商品 real_imps 为 0（测试除零处理）
        if random.random() < 0.02:
            real_imps = 0

        # 约 2% 的商品 base_time 为 0
        if random.random() < 0.02:
            base_time = 0

        # 优先级分数
        priority = round(
            (norm_p_ab * 100) +
            (norm_roi * 10) +
            random.uniform(-5, 5),
            2
        )

        # 约 2% 的商品 priority_score 为负数
        if random.random() < 0.02:
            priority = round(random.uniform(-50, -1), 2)

        # 约 1% 的商品 ROI 为 0
        if random.random() < 0.01:
            roi = 0

        # 创建时间
        crt_delta = random.randint(-90, -1)
        crt_time = (datetime.now() + timedelta(days=crt_delta)).strftime("%Y-%m-%d %H:%M:%S")
        prod_name = f"商品_{i}_{random.randint(1000, 9999)}"

        row = [
            daily_pool,           # daily_incremental_imps_pool
            rqvae_id,             # rqvae_id
            ctr,                  # proxy_ctr
            cvr_ab,               # proxy_cvr_ab
            cvr_abpro,            # proxy_cvr_abpro
            cvr_pay,              # proxy_cvr_pay
            p_ab,                 # proxy_p_ab
            norm_p_ab,            # normalized_proxy_p_ab
            avg_time,             # avg_time_to_first_ab
            median_time,          # median_time_to_first_ab
            prod_id,              # prod_id
            comp_id,              # comp_id
            roi,                  # ipv_roi_自然
            norm_roi,             # normalized_ipv_roi_自然
            crt_time,             # crt_time
            prod_name,            # prod_name
            real_imps,            # real_imps
            real_ab,              # real_ab
            base_time,            # base_time_to_first_ab
            is_broken,            # is_broken_zero
            imps_needed,          # imps_needed_to_break
            imps_needed_xiuzheng, # imps_needed_to_break_xiuzheng
            norm_imps_needed,     # normalized_imps_needed_to_break
            priority,             # priority_score
            i + 1,                # rn
        ]
        products.append(row)

    return products


def aggregate_to_chunks(products: list, chunk_size: int = 10) -> list:
    """将商品列表聚合成 big_chunk_string 格式。"""
    chunks = []

    for i in range(0, len(products), chunk_size):
        chunk_prods = products[i:i + chunk_size]
        records = []

        for idx, prod in enumerate(chunk_prods):
            fields = [str(v) if v is not None else "" for v in prod]

            # === 埋入异常：约 5% 的 chunk 中有一条记录缺少最后一个字段 ===
            if random.random() < 0.005 and len(fields) > 1:
                fields = fields[:-1]

            # === 埋入异常：约 3% 的 chunk 中有一条记录有一个空字段 ===
            if random.random() < 0.003 and len(fields) > 5:
                fields[5] = ""

            record = '一'.join(fields)
            records.append(record)

        # === 埋入异常：约 2% 的 chunk 末尾有一条空记录 ===
        if random.random() < 0.02:
            records.append("")

        # 多条记录用 '二' 连接
        big_chunk_string = '二'.join(records)
        group_id = f"GROUP_{i // chunk_size:04d}"
        chunks.append([group_id, big_chunk_string])

    return chunks


def write_to_mock_odps(ds: str, chunks: list, data_root: Path):
    """写入 mock ODPS 的本地文件系统。"""
    table_path = data_root / "icbu_ensa" / "dws_new_prod_info_data" / f"ds={ds}"
    table_path.mkdir(parents=True, exist_ok=True)

    data_file = table_path / "data.csv"
    with open(data_file, 'w', encoding='gbk', newline='', errors='replace') as f:
        writer = csv.writer(f)
        writer.writerow(["group_id", "big_chunk_string"])
        for chunk in chunks:
            writer.writerow(chunk)

    print(f"[OK] 已生成测试数据: {data_file}")
    print(f"     分区: ds={ds}")
    print(f"     数据包数: {len(chunks)}")
    print(f"     商品总数: {len(chunks) * 10}")


def main():
    parser = argparse.ArgumentParser(description="生成冷启动测试数据")
    parser.add_argument("--ds", type=str, default="20260501",
                        help="分区日期，格式 YYYYMMDD")
    parser.add_argument("--products", type=int, default=200,
                        help="商品总数（默认 200）")
    parser.add_argument("--seed", type=int, default=42,
                        help="随机种子")
    parser.add_argument("--data-root", type=str,
                        default=str(Path(__file__).parent.parent / "data"),
                        help="数据根目录")
    args = parser.parse_args()

    data_root = Path(args.data_root)

    print(f"正在生成测试数据...")
    print(f"  分区: {args.ds}")
    print(f"  商品数: {args.products}")
    print(f"  种子: {args.seed}")

    products = generate_products(args.products, args.seed)
    chunks = aggregate_to_chunks(products, chunk_size=10)
    write_to_mock_odps(args.ds, chunks, data_root)

    print("\n[OK] 测试数据生成完成！")
    print(f"你可以运行: python check_odps.py --ds {args.ds}")


if __name__ == "__main__":
    main()
