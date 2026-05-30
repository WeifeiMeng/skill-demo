"""
Mock ODPS Client - 模拟阿里云 ODPS/MaxCompute 的本地 SDK

这个模块模拟了 pyodps 的核心接口，让候选人可以在本地环境中
开发和测试冷启动 pipeline，无需真实的 ODPS 连接。

数据存储在本地 CSV 文件中，按 "项目/表/分区" 的目录结构组织：
    data/
    └── icbu_ensa/
        └── dws_new_prod_info_data/
            └── ds=20260501/
                └── data.csv
        └── dws_new_prod_quota_result/
            └── ds=20260501/
                └── data.csv

使用方法:
    from mock_odps.odps_client import ODPS
    client = ODPS('mock_access_id', 'mock_secret', 'icbu_ensa')
    # 执行 SQL 查询
    result = client.execute_sql("SELECT * FROM icbu_ensa.dws_new_prod_info_data WHERE ds='20260501'")
    # 读取结果
    with result.open_reader() as reader:
        for record in reader:
            print(record[0], record[1])
"""

import csv
import os
import re
import shutil
from pathlib import Path
from typing import List, Optional, Tuple


# 数据根目录，相对于当前工作目录
DATA_ROOT = Path(__file__).parent.parent / "data"

# 模拟权限控制：是否允许写入 ODPS
# 默认 False（模拟候选人只有读权限）
# 可通过环境变量 MOCK_ODPS_WRITE_ENABLED=1 开启（用于本地测试验证）
MOCK_WRITE_ENABLED = os.environ.get("MOCK_ODPS_WRITE_ENABLED", "0").strip() == "1"


class Record:
    """模拟 ODPS Record 对象。"""
    def __init__(self, values: List):
        self._values = values

    def __getitem__(self, index):
        return self._values[index]

    def __len__(self):
        return len(self._values)

    def __repr__(self):
        return f"Record({self._values})"


class Reader:
    """模拟 ODPS SQL 结果读取器。"""
    def __init__(self, records: List[Record]):
        self._records = records
        self._index = 0

    def __iter__(self):
        return iter(self._records)

    def __len__(self):
        return len(self._records)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class SQLResult:
    """模拟 ODPS SQL 执行结果。"""
    def __init__(self, records: List[Record]):
        self._records = records

    def open_reader(self):
        return Reader(self._records)


class Table:
    """模拟 ODPS Table 对象。"""
    def __init__(self, project: str, table_name: str, client):
        self.project = project
        self.name = table_name
        self._client = client

    def exist_partition(self, partition_spec: str) -> bool:
        """检查分区是否存在。"""
        return self._client._partition_exists(self.project, self.name, partition_spec)

    def get_partition(self, partition_spec: str):
        """获取分区对象（简化版，仅返回是否存在）。"""
        if not self.exist_partition(partition_spec):
            raise ValueError(f"Partition {partition_spec} not found in {self.project}.{self.name}")
        return Partition(self.project, self.name, partition_spec, self._client)

    def open_writer(self, partition: Optional[str] = None):
        """打开写入器。"""
        return TableWriter(self.project, self.name, partition, self._client)


class Partition:
    """模拟 ODPS Partition 对象。"""
    def __init__(self, project: str, table_name: str, spec: str, client):
        self.project = project
        self.table_name = table_name
        self.spec = spec
        self._client = client

    def drop(self):
        """删除分区。"""
        self._client._drop_partition(self.project, self.table_name, self.spec)


class TableWriter:
    """模拟 ODPS Table Writer（Tunnel 批量写入）。"""
    def __init__(self, project: str, table_name: str, partition: Optional[str], client):
        self.project = project
        self.name = table_name
        self.partition = partition
        self._client = client
        self._records = []

    def write(self, record: List):
        """写入一条记录。"""
        self._records.append(record)

    def close(self):
        """关闭写入器，将数据写入文件。"""
        self._client._write_partition(self.project, self.name, self.partition, self._records)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class ODPS:
    """
    模拟 pyodps.ODPS 客户端。

    实现了核心的 execute_sql、get_table、exist_partition 等接口。
    数据存储在本地文件系统中，按 项目/表/分区 的层级组织。
    """

    def __init__(self, access_id: str, secret_access_key: str, project: str,
                 endpoint: str = "http://mock-odps.aliyun-inc.com/api"):
        self.access_id = access_id
        self.secret_access_key = secret_access_key
        self.project = project
        self.endpoint = endpoint
        self._data_root = DATA_ROOT

    def execute_sql(self, sql: str, hints: Optional[dict] = None) -> SQLResult:
        """
        执行 SQL 查询（仅支持简化版的 SELECT、INSERT OVERWRITE/INTO）。

        支持的 SQL 模式：
        - SELECT *|列名 FROM 表名 [WHERE 条件] [LIMIT n]
        - SELECT MAX_PT('表名')  -- 获取最新分区
        - INSERT OVERWRITE TABLE 表名 PARTITION (...) SELECT ...
        - INSERT INTO TABLE 表名 PARTITION (...) SELECT ...
        """
        sql = sql.strip()

        if sql.upper().startswith("SELECT MAX_PT"):
            return self._handle_max_pt(sql)

        if sql.upper().startswith("SELECT"):
            return self._handle_select(sql)

        if sql.upper().startswith("INSERT"):
            return self._handle_insert(sql)

        raise NotImplementedError(f"不支持的 SQL 类型: {sql[:50]}...")

    def get_table(self, table_name: str) -> Table:
        """获取表对象。"""
        return Table(self.project, table_name, self)

    def get_project(self, project_name: Optional[str] = None):
        """获取项目对象（简化版）。"""
        return MockProject(project_name or self.project, self)

    def _table_path(self, project: str, table_name: str) -> Path:
        """获取表的本地存储路径。"""
        return self._data_root / project / table_name

    def _partition_path(self, project: str, table_name: str, partition_spec: str) -> Path:
        """获取分区的本地存储路径。"""
        return self._table_path(project, table_name) / partition_spec.replace("'", "").replace(" ", "")

    def _partition_exists(self, project: str, table_name: str, partition_spec: str) -> bool:
        """检查分区是否存在。"""
        pp = self._partition_path(project, table_name, partition_spec)
        return pp.exists() and (pp / "data.csv").exists()

    def _drop_partition(self, project: str, table_name: str, partition_spec: str):
        """删除分区。"""
        pp = self._partition_path(project, table_name, partition_spec)
        if pp.exists():
            shutil.rmtree(pp)

    def _write_partition(self, project: str, table_name: str, partition_spec: Optional[str],
                         records: List[List]):
        """向分区写入数据。"""
        if not MOCK_WRITE_ENABLED:
            raise PermissionError(
                "[模拟 ODPS] 写入被拒绝：当前账号仅有读权限，无法写入生产表。"
                "如需在本地测试写入逻辑，请设置环境变量 MOCK_ODPS_WRITE_ENABLED=1"
            )

        table_path = self._table_path(project, table_name)
        table_path.mkdir(parents=True, exist_ok=True)

        if partition_spec:
            pp = self._partition_path(project, table_name, partition_spec)
        else:
            pp = table_path / "default"

        pp.mkdir(parents=True, exist_ok=True)
        data_file = pp / "data.csv"

        # 如果文件已存在，追加写入；否则新建
        mode = 'a' if data_file.exists() else 'w'
        with open(data_file, mode, encoding='gbk', newline='', errors='replace') as f:
            writer = csv.writer(f)
            for record in records:
                writer.writerow([str(v) if v is not None else "" for v in record])

    def _read_partition(self, project: str, table_name: str, partition_spec: Optional[str]) -> Tuple[List[str], List[Record]]:
        """读取分区的列名和记录。"""
        if partition_spec:
            pp = self._partition_path(project, table_name, partition_spec)
        else:
            pp = self._table_path(project, table_name) / "default"

        data_file = pp / "data.csv"
        if not data_file.exists():
            return [], []

        with open(data_file, 'r', encoding='gbk', errors='replace') as f:
            reader = csv.reader(f)
            rows = list(reader)
            if not rows:
                return [], []
            columns = rows[0]
            records = [Record(row) for row in rows[1:] if row]
            return columns, records

    def _handle_max_pt(self, sql: str) -> SQLResult:
        """处理 SELECT MAX_PT('表名') 查询。"""
        match = re.search(r"MAX_PT\s*\(\s*['\"]([^'\"]+)['\"]\s*\)", sql, re.IGNORECASE)
        if not match:
            raise ValueError(f"无法解析 MAX_PT SQL: {sql}")

        table_full_name = match.group(1)
        parts = table_full_name.split('.')
        if len(parts) == 2:
            project, table_name = parts
        else:
            project, table_name = self.project, table_full_name

        table_path = self._table_path(project, table_name)
        if not table_path.exists():
            return SQLResult([Record([None])])

        partitions = []
        for p in table_path.iterdir():
            if p.is_dir() and p.name.startswith("ds="):
                ds_value = p.name.replace("ds=", "")
                partitions.append(ds_value)

        if not partitions:
            return SQLResult([Record([None])])

        max_ds = max(partitions)
        return SQLResult([Record([max_ds])])

    def _handle_select(self, sql: str) -> SQLResult:
        """处理 SELECT 查询。"""
        # 解析 FROM 子句
        from_match = re.search(r"FROM\s+(\S+)", sql, re.IGNORECASE)
        if not from_match:
            raise ValueError(f"无法解析 FROM 子句: {sql}")

        table_full_name = from_match.group(1)
        parts = table_full_name.split('.')
        if len(parts) == 2:
            project, table_name = parts
        else:
            project, table_name = self.project, table_full_name

        # 解析 WHERE 条件中的 ds 分区过滤
        ds_value = None
        where_match = re.search(r"WHERE\s+.*?ds\s*=\s*['\"]([^'\"]+)['\"]", sql, re.IGNORECASE)
        if where_match:
            ds_value = where_match.group(1)

        # 读取数据
        columns, records = self._read_partition(project, table_name, f"ds={ds_value}" if ds_value else None)

        if not records:
            return SQLResult([])

        # 解析 SELECT 列
        select_match = re.search(r"SELECT\s+(.*?)\s+FROM", sql, re.IGNORECASE | re.DOTALL)
        selected_cols = []
        if select_match:
            select_part = select_match.group(1).strip()
            if select_part == '*':
                selected_cols = columns
            else:
                # 简单解析逗号分隔的列名
                selected_cols = [c.strip().split()[-1] for c in select_part.split(',')]

        # 过滤列
        if selected_cols and selected_cols != columns:
            col_indices = {c: i for i, c in enumerate(columns)}
            filtered_records = []
            for record in records:
                new_values = []
                for col in selected_cols:
                    idx = col_indices.get(col)
                    if idx is not None:
                        new_values.append(record[idx])
                filtered_records.append(Record(new_values))
            records = filtered_records

        # 解析 LIMIT
        limit_match = re.search(r"LIMIT\s+(\d+)", sql, re.IGNORECASE)
        if limit_match:
            limit = int(limit_match.group(1))
            records = records[:limit]

        return SQLResult(records)

    def _handle_insert(self, sql: str) -> SQLResult:
        """处理 INSERT OVERWRITE/INTO 语句（简化版，支持 INSERT INTO ... VALUES ...）。"""
        # 解析目标表和分区
        match = re.search(
            r"INSERT\s+(OVERWRITE|INTO)\s+TABLE\s+(\S+)\s*(?:PARTITION\s*\(([^)]+)\))?",
            sql, re.IGNORECASE
        )
        if not match:
            raise ValueError(f"无法解析 INSERT SQL: {sql}")

        mode = match.group(1).upper()
        table_full_name = match.group(2)
        partition_spec = match.group(3)

        parts = table_full_name.split('.')
        if len(parts) == 2:
            project, table_name = parts
        else:
            project, table_name = self.project, table_full_name

        # 解析 VALUES 子句
        values_match = re.search(r"VALUES\s*\((.*)\)", sql, re.IGNORECASE | re.DOTALL)
        if values_match:
            # 解析单条或多条 VALUES
            values_str = values_match.group(1)
            records = []
            for row_str in values_str.split('),('):
                row_str = row_str.strip().strip('()')
                vals = []
                for v in row_str.split(','):
                    v = v.strip()
                    if (v.startswith("'") and v.endswith("'")) or (v.startswith('"') and v.endswith('"')):
                        vals.append(v[1:-1])
                    elif v.upper() == 'NULL':
                        vals.append(None)
                    else:
                        try:
                            vals.append(float(v) if '.' in v else int(v))
                        except ValueError:
                            vals.append(v)
                records.append(vals)
            self._write_partition(project, table_name, partition_spec, records)
            return SQLResult([])

        # INSERT SELECT 暂不支持完整解析
        raise NotImplementedError(
            "INSERT SELECT 在 mock ODPS 中暂不支持完整解析。"
            "请直接使用 TableWriter 进行数据写入，或使用 INSERT INTO ... VALUES (...)。"
        )


class MockProject:
    """模拟 ODPS Project 对象。"""
    def __init__(self, name: str, client: ODPS):
        self.name = name
        self._client = client


class MockOptions:
    """模拟 pyodps.options 配置对象。"""
    def __init__(self):
        self.connect_timeout = 120
        self.read_timeout = 120


# 兼容 pyodps 的 options 全局对象
options = MockOptions()
