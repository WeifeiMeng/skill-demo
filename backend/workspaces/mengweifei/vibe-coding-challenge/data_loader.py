"""
数据获取模块：从 Mock ODPS 获取上游新品数据。
"""

import re
import logging
from mock_odps.odps_client import ODPS

logger = logging.getLogger(__name__)

UPSTREAM_TABLE = "icbu_ensa.dws_new_prod_info_data"


def create_client(access_id: str = "mock_id", secret: str = "mock_key",
                  project: str = "icbu_ensa") -> ODPS:
    """创建 ODPS 客户端。"""
    return ODPS(access_id, secret, project)


def get_latest_ds(client: ODPS) -> str | None:
    """获取上游表的最新分区日期。"""
    sql = f"SELECT MAX_PT('{UPSTREAM_TABLE}')"
    result = client.execute_sql(sql)
    with result.open_reader() as reader:
        for record in reader:
            val = record[0]
            if val:
                logger.info("最新分区: ds=%s", val)
                return val
    return None


def validate_ds(ds: str) -> str:
    """校验 ds 格式。"""
    if not re.match(r'^\d{8}$', ds):
        raise ValueError(f"ds 格式错误，需要 YYYYMMDD 格式，实际: {ds}")
    return ds


def fetch_raw_data(client: ODPS, ds: str) -> list[tuple[str, str]]:
    """从上游表获取指定分区的原始数据。

    Returns:
        list of (group_id, big_chunk_string)
    """
    validate_ds(ds)
    sql = (
        f"SELECT group_id, big_chunk_string "
        f"FROM {UPSTREAM_TABLE} "
        f"WHERE ds='{ds}'"
    )
    logger.info("执行查询: %s", sql)
    result = client.execute_sql(sql)

    records = []
    with result.open_reader() as reader:
        for record in reader:
            group_id = str(record[0]) if record[0] is not None else ""
            chunk = str(record[1]) if record[1] is not None else ""
            records.append((group_id, chunk))

    logger.info("获取 %d 个数据包 (group)", len(records))
    return records
