# 代码 Review 报告

> 审查对象: `review_reference.py` — 新品冷启动流量配额分配系统参考实现

---

## 问题 1：`parse_big_chunk` — 数组越界导致 IndexError

**文件**: `review_reference.py:44`  
**严重程度**: 高（正确性）

```python
for i, col in enumerate(FINAL_COLUMNS):
    row[col] = fields[i]  # 直接用索引，不做边界检查
```

**问题描述**: 当 `big_chunk_string` 中某条记录的字段数少于 `FINAL_COLUMNS` 的长度时，`fields[i]` 会抛出 `IndexError`，导致整个 pipeline 崩溃。测试数据生成器明确埋入了字段缺失异常（约 5% chunk 中缺最后一个字段，约 2% chunk 末尾有空记录）。

**影响**: 一条异常记录即可导致全量数据解析失败，无法继续执行。

**改进建议**: 
- 对每条记录的字段数做边界检查，字段不足时用 `None` 填充
- 空记录直接跳过，不参与后续处理
- 字段数超出预期时截断并记录警告

---

## 问题 2：`allocate_quota` — 嵌套循环逻辑错误 + 约束缺失

**文件**: `review_reference.py:57-66`  
**严重程度**: 高（正确性）

```python
for row in rows:
    sorted_rows = sorted(rows, key=lambda x: x['priority_score'], reverse=True)
    for row in sorted_rows:
        if total_used >= TOTAL_BUDGET:
            break
        ...
```

**问题描述**:
1. **逻辑冗余**: 外层 `for row in rows` 遍历 N 条记录，每轮内部又排序并完整遍历所有记录。排序执行了 N 次，实际只执行第一次就完成了所有分配。这导致 O(N² log N) 的无效计算。
2. **约束完全缺失**: 只检查了总预算上限，未实现题目要求的任何业务约束——每商家配额上限、每商品上限、每商家扶持商品数限制、每类目扶持商品数限制。
3. 贪心算法无法保证全局最优，在有复杂约束的场景下可能严重偏离最优解。

**影响**: 配额分配结果不满足业务约束，实际不可用；算法复杂度虚高。

**改进建议**:
- 使用 MIP（混合整数规划）建模，将业务目标量化为目标函数，业务规则形式化为约束条件
- 使用 `pulp` 或 `scipy.optimize.milp` 开源求解器

---

## 问题 3：`write_to_odps` — SQL 注入风险

**文件**: `review_reference.py:71-75`  
**严重程度**: 中（安全性）

```python
sql = (
    "INSERT OVERWRITE TABLE icbu_ensa.dws_new_prod_quota_result "
    f"PARTITION (ds='{ds}') "
    "SELECT * FROM tmp_result"
)
```

**问题描述**: 直接使用 f-string 拼接 SQL，`ds` 参数未做任何校验。虽然本题中 `ds` 来自命令行参数，风险相对可控，但在生产环境中如果 `ds` 来自用户输入或上游系统，可能构成 SQL 注入攻击面。

**影响**: 潜在的 SQL 注入风险。

**改进建议**:
- 对 `ds` 做格式校验：`re.match(r'^\d{8}$', ds)` 确保为 8 位数字
- 使用参数化查询（如果 ODPS SDK 支持）
- 至少对特殊字符做转义处理

---

## 问题 4：异常处理静默吞噬

**文件**: `review_reference.py:81-84`  
**严重程度**: 中（鲁棒性）

```python
try:
    from odps import ODPS as RealODPS
    client = RealODPS('xxx', 'yyy', 'icbu_ensa')
except ImportError:
    from mock_odps.odps_client import ODPS
    client = ODPS('mock_id', 'mock_key', 'icbu_ensa')
```

**问题描述**: 
1. 只 catch 了 `ImportError`，如果真实 ODPS 导入成功但连接失败（网络、认证等问题），异常会被抛出且无处理。
2. 硬编码了真实 ODPS 的凭据 `'xxx', 'yyy'`，这是不应出现在代码中的占位符。
3. 没有日志记录当前使用的是真实 ODPS 还是 Mock ODPS，排查问题时缺乏上下文。

**改进建议**:
- 统一使用 Mock ODPS（本地开发/测试）
- 环境变量控制 ODPS 模式：`ODPS_MODE=mock|real`
- 连接失败时记录详细错误日志并降级到 Mock ODPS

---

## 问题 5：`convert_types` — 无类型转换异常保护

**文件**: `review_reference.py:48-55`  
**严重程度**: 中（鲁棒性）

```python
row['proxy_ctr'] = float(row['proxy_ctr'])
row['real_imps'] = int(row['real_imps'])
```

**问题描述**: 当字段值为空字符串 `""` 或非数值字符串时，`float()` 和 `int()` 会抛出 `ValueError`。测试数据中有约 3% 的记录存在空字段。函数没有 try/except 保护，也未检查空值。

**影响**: 空字段或脏数据导致 pipeline 崩溃。

**改进建议**:
- 转换前检查空值：`if v is None or v == '': return 0.0`
- 使用 try/except 包裹转换逻辑，异常时使用默认值并记录警告
- 不要对所有字段做硬编码转换，应根据字段类型表进行批量安全转换

---

## 问题 6：缺少日志系统

**文件**: 全局  
**严重程度**: 低（工程化）

**问题描述**: 代码仅使用 `print()` 输出 2 行信息，无结构化日志。在生产环境中排查数据异常、配额分配结果、写入失败原因时，无法追溯 pipeline 执行过程。

**改进建议**:
- 使用 `logging` 模块，按 INFO/WARNING/ERROR 分级记录
- 关键节点记录：读取行数、解析成功/失败数、配额求解耗时、写入结果
- 异常记录附带上下文（记录索引、字段名、原始值）

---

## 问题 7：缺少降级方案

**文件**: `write_to_odps`、`run_pipeline`  
**严重程度**: 中（工程化）

**问题描述**: 题目明确说明"ODPS 账号只有读权限，写入会失败"，但参考代码中 `write_to_odps` 直接尝试 INSERT 后无任何异常处理，也无降级方案。Mock ODPS 默认会拒绝写入并抛出 `PermissionError`。

**改进建议**:
- 捕获写入异常，降级为本地 CSV 文件保存
- 生成交付清单（包含输出文件路径、记录数、时间戳）
- 提示用户手动上传或切换有写权限的账号

---

## 总结

| 维度 | 问题数 | 关键问题 |
|------|--------|----------|
| 正确性 | 3 | 数组越界、嵌套循环逻辑错误、约束缺失 |
| 鲁棒性 | 2 | 异常静默吞噬、类型转换无保护 |
| 工程化 | 2 | 缺少日志、缺少降级方案 |
