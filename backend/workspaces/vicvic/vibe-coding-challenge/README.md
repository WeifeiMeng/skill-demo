# Vibe Coding Challenge: 新品冷启动流量配额分配系统

> **考察目标**: 数据 pipeline 设计、最优化建模、异常处理、工程化能力
> **考核方式**: 笔试，无面试官答疑，所有信息已在本文档中给出
> **防作弊说明**: 本题设计有开放性问题、边界异常、代码 review 环节，直接丢给 agent 无法获得高分

---

## 一、项目背景

在电商平台中，新品上架后面临 **冷启动（cold start）** 问题：新品缺乏历史曝光和交互数据，导致搜索排序难以获得自然流量，形成恶性循环。为打破这一循环，平台需要为新品分配 **曝光配额（quota）**，帮助其快速"破零"（获得首次有效曝光）。

你的任务是：构建一个完整的 **新品冷启动流量配额分配系统**，实现从上游数据采集 → 数据解析 → 最优化配额求解 → 结果回写的全流程自动化 pipeline。

---

## 二、系统架构

```
┌────────────────────────────────────────────────────────────────────────┐
│                      Mock ODPS（本地文件系统模拟）                      │
│  ┌────────────────────────┐        ┌────────────────────────┐         │
│  │  上游输入表            │        │  下游输出表            │         │
│  │  dws_new_prod_         │        │  dws_new_prod_         │         │
│  │  info_data             │        │  quota_result          │         │
│  │  (ds=YYYYMMDD)         │        │  (ds=YYYYMMDD)         │         │
│  │                        │        │                        │         │
│  │  group_id              │        │  prod_id               │         │
│  │  big_chunk_string      │        │  comp_id               │         │
│  │  ds                    │        │  x_曝光配额            │         │
│  └──────────┬─────────────┘        └──────────▲─────────────┘         │
│             │  SELECT (读权限)               │  INSERT/Tunnel         │
│             │                                │  (写权限→默认拒绝)      │
└─────────────┼────────────────────────────────┼────────────────────────┘
              │                                │
              ▼                                │
┌────────────────────────────────────────────────────────────────────────┐
│                      你的 Pipeline（代码结构自行设计）                   │
│                                                                        │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐    │
│   │ 数据获取 │────▶│ 数据解析 │────▶│ 配额求解 │────▶│ 结果入库 │    │
│   └──────────┘     └──────────┘     └──────────┘     └─────┬─────┘   │
│                                                            │          │
│                                                            ▼          │
│                                                  ┌────────────────┐   │
│                                                  │  降级方案      │   │
│                                                  │  本地CSV+清单  │   │
│                                                  └────────────────┘   │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 三、数据链路设计

### 3.1 上游输入表

**表名**: `icbu_ensa.dws_new_prod_info_data`

**结构**:
| 字段名 | 类型 | 说明 |
|--------|------|------|
| group_id | STRING | 数据包分组 ID |
| big_chunk_string | STRING | 聚合压缩后的商品数据字符串 |
| ds | STRING | 分区日期 (YYYYMMDD) |

> 注意：ODPS 对下载结果有 **行数限制**。为了绕过这个限制，上游表将多条商品记录 **聚合压缩** 为一个 `big_chunk_string` 字段。你需要在本地进行解压解析。

### 3.2 压缩格式

`big_chunk_string` 中，**多条商品记录用 `二` 分隔**，**单条记录内部字段用 `一` 分隔**。

示例：
```
prod_id=1001一comp_id=C001一ctr=0.05二prod_id=1002一comp_id=C001一ctr=0.03
```

解压后还原为结构化 CSV，字段顺序如下：

```python
FINAL_COLUMNS = [
    'daily_incremental_imps_pool', 'rqvae_id', 'proxy_ctr', 'proxy_cvr_ab',
    'proxy_cvr_abpro', 'proxy_cvr_pay', 'proxy_p_ab', 'normalized_proxy_p_ab',
    'avg_time_to_first_ab', 'median_time_to_first_ab', 'prod_id', 'comp_id',
    'ipv_roi_自然', 'normalized_ipv_roi_自然', 'crt_time', 'prod_name',
    'real_imps', 'real_ab', 'base_time_to_first_ab', 'is_broken_zero',
    'imps_needed_to_break', 'imps_needed_to_break_xiuzheng',
    'normalized_imps_needed_to_break', 'priority_score', 'rn'
]
```

### 3.3 下游输出表

**表名**: `icbu_ensa.dws_new_prod_quota_result`

需要写入的字段包括但不限于：
| 字段名 | 类型 | 说明 |
|--------|------|------|
| prod_id | STRING | 商品ID |
| comp_id | STRING | 商家ID |
| rqvae_id | STRING | 类目/属性分组ID |
| x_曝光配额 | DOUBLE | 分配的曝光配额 |
| y_冷启成功 | INT | 是否冷启成功 (0/1) |
| sim_time_to_first_ab | DOUBLE | 预计破零时间（天） |
| ... | ... | 其他业务字段 |

---

## 四、题目要求

### 4.1 前置任务：代码 Review（20分）

以下是项目中一段 **参考实现代码**，你能发现其中存在哪些问题？

> **要求**：阅读 `review_reference.py`（位于本题根目录），找出其中至少 **3 处设计缺陷或潜在 bug**，并说明你的改进思路。
>
> 请将你的 review 结果写入 `review_report.md`，包括但不限于：问题描述、影响分析、改进建议。

这段代码是真实生产环境中可能出现的写法，请从 **正确性、鲁棒性、工程化** 三个维度进行 review。

---

### 4.2 核心任务：实现 Pipeline（80分）

你需要实现一个完整的新品冷启动配额分配 pipeline，覆盖以下 **4 个核心环节**：

**环节一：数据获取**

- 使用 Mock ODPS SDK 从上游表获取指定分区的新品数据
- 正确识别和处理日期分区参数

**环节二：数据解析**

- 将 `big_chunk_string` 按压缩格式还原为结构化数据
- 数值字段需要正确类型转换

> **注意**：测试数据中存在异常情况，你的解析逻辑需要能够处理。异常情况包括但不限于：字段缺失、字段数不一致、空值等。

**环节三：配额求解**

你需要设计 **一种** 基于最优化的配额分配策略。

**业务目标**（按优先级排序）：
1. 尽量让更多的商品获得配额（扶持覆盖面）
2. 在预算内优先扶持转化效率高的商品（效率导向）
3. 给尾部商家（`ipv_roi_自然 < 1`）适当倾斜（公平性）
4. 避免头部商家（`ipv_roi_自然 > 20`）过度占用资源（防止垄断）

**业务规则**（你需要转化为数学约束）：
- 平台每日总曝光配额有上限
- 单个商家不能占用过多资源
- 单个商品的分配量有上限
- 每个商家扶持的商品数有限制
- 每个类目（rqvae_id）下的扶持商品数有限制

> 具体权重和阈值请根据测试数据中的分布合理设定，并在 `design_notes.md` 中说明你的设计决策。

**破零时间计算**：

对于已破零商品（`is_broken_zero = 1`），破零时间保持不变。

对于未破零商品：
$$
\text{sim\_time} = \text{base\_time} \times \frac{\text{real\_imps}}{\text{real\_imps} + \text{allocated\_imps}}
$$

如果分配量大于等于破零所需曝光量，则认为已破零，破零时间取最小值。

> 💡 **求解器选择**：你不需要 Gurobi。可以使用 `pulp`（开源）、`scipy.optimize.milp` 或任何你熟悉的开源求解器。

**环节四：结果入库**

- 将求解结果写入 ODPS 分区表
- 支持 `tunnel` 或 `sql` 写入方式
- **重要**：你的 ODPS 账号只有读权限，写入会失败。请设计降级方案。
- 降级方案应包括：本地文件保存、交付清单生成、清晰的交付提示

> Mock ODPS 默认模拟只读权限。如需在本地测试写入逻辑，可设置环境变量 `MOCK_ODPS_WRITE_ENABLED=1`。

**主入口**

串联上述环节，形成完整可运行的 pipeline，输出运行报告。

> **代码结构由你自行设计**。如何划分模块、组织文件、命名函数，是本题工程化能力的考核内容之一。

---

### 4.3 设计文档要求

请提交一份 `design_notes.md`，说明以下内容：

1. **目标函数设计**：你为什么选择这样的目标函数？权重是如何确定的？
2. **约束条件设计**：各项阈值的设定依据是什么？
3. **异常处理策略**：你发现了哪些数据异常？是如何处理的？
4. **降级方案设计**：如果 ODPS 写入失败，你的交付流程是什么？

---

### 4.4 评分标准

| 考核维度 | 权重 | 评分要点 |
|----------|------|----------|
| **代码 Review** | 20% | 能否发现 reference 代码中的缺陷，分析是否到位 |
| **功能完整性** | 25% | 4个核心环节+主入口是否全部实现，pipeline是否可跑通 |
| **异常处理** | 15% | 是否发现并处理测试数据中的边界异常 |
| **最优化建模** | 20% | MIP模型是否合理，约束是否完整，设计决策是否有依据 |
| **工程化能力** | 10% | 代码结构设计是否合理、模块划分是否清晰、错误处理、日志输出 |
| **降级设计** | 10% | 是否处理ODPS写入权限受限，是否有合理的降级交付方案 |

---

## 五、模拟 ODPS 环境

由于你没有公司系统权限，**真实的 ODPS 无法直接连接**。但在本地开发环境中，我们提供了一个 **Mock ODPS SDK**（见 `mock_odps/` 目录）。

### 5.1 模拟规则

- Mock ODPS 在本地文件系统中模拟 ODPS 行为
- **默认只读权限**，写入操作会抛出 `PermissionError`
- 如需测试写入逻辑，可设置环境变量：`export MOCK_ODPS_WRITE_ENABLED=1`

```python
from mock_odps.odps_client import ODPS

# 创建客户端（无需真实凭据）
client = ODPS('mock_id', 'mock_key', 'icbu_ensa')

# 执行 SQL
result = client.execute_sql(
    "SELECT group_id, big_chunk_string FROM icbu_ensa.dws_new_prod_info_data WHERE ds='20260501'"
)
with result.open_reader() as reader:
    for record in reader:
        print(record[0], record[1])

# 获取最新分区
result = client.execute_sql("SELECT MAX_PT('icbu_ensa.dws_new_prod_info_data')")
```

### 5.2 数据准备

```bash
# 生成测试数据
python mock_odps/generate_test_data.py --ds 20260501 --products 200 --seed 42
```

> **提示**：测试数据中存在多种边界异常情况。请运行 pipeline 后观察日志和输出，发现并处理这些问题。

---

## 六、项目目录结构

```
vibe-coding-challenge/
├── README.md                          # 本题文档
├── review_reference.py                # 前置 review 任务（有问题的参考代码）
├── requirements.txt                   # 基础依赖
├── mock_odps/
│   ├── odps_client.py                 # Mock ODPS SDK（已提供）
│   └── generate_test_data.py          # 测试数据生成器（已提供）
├── data/                              # 模拟数据存储目录（运行时生成）
└── output/                            # 输出目录（你的代码生成）
    ├── raw/                           #   原始数据 CSV
    ├── parsed/                        #   解析后结构化 CSV
    ├── quota/                         #   配额结果 CSV
    └── fallback/                      #   降级交付文件
```

> **说明**：`mock_odps/` 和 `data/` 已预先提供，请勿修改。`output/` 由你的代码生成。

---

## 七、运行方式

### 7.1 本地运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 生成测试数据
python mock_odps/generate_test_data.py --ds 20260501 --products 200 --seed 42

# 3. 运行你的 pipeline
python run_pipeline.py --ds 20260501
```

### 7.2 在线提交测试

在考试页面中，点击顶部 **"提交测试"** 按钮。系统会在你的容器中执行自动化测试脚本，验证以下内容：

| 检查项 | 说明 |
|--------|------|
| Pipeline 可运行 | `run_pipeline.py --ds 20260501` 正常退出 |
| 输出文件完整性 | `output/raw/`, `output/parsed/`, `output/quota/`, `output/fallback/` 均有文件产出 |
| 解析正确性 | CSV 列数 >= 20，数值字段类型转换正确 |
| 求解器约束 | 总预算、单商品/单商家/商品数/类目数上限 |
| 文档完整性 | `review_report.md` 和 `design_notes.md` 存在 |

点击后会弹出评测结果面板，展示每项得分和通过/失败详情。

---

## 八、提交产物清单

你需要确保以下 **5 项产物** 全部就绪后再点击"提交测试"：

### 8.1 入口文件（必须）

```
run_pipeline.py          # 主入口，必须放在 workspace 根目录
```

**命令行接口约定**：
```bash
python run_pipeline.py --ds YYYYMMDD
```
- `--ds`：指定分区日期，格式 `YYYYMMDD`（如 `20260501`）
- 入口文件名**必须**是 `run_pipeline.py`，不能是其他名称
- 启动后应依次执行 数据获取 → 数据解析 → 配额求解 → 结果入库，完成全流程

### 8.2 输出文件（必须）

你的 pipeline 运行后必须在以下路径产生文件：

```
output/
├── raw/          # 从 ODPS 获取的原始数据 CSV（如 20260501_新品数据(未解析).csv）
├── parsed/       # 解析后的结构化 CSV（如 20260501_新品数据(已解析).csv）
├── quota/        # 配额分配结果 CSV（如 20260501_新品配额.csv）
└── fallback/     # 降级交付清单 + 本地保存的配额 CSV
```

> 输出目录名和文件名可自行命名，但**四个目录必须存在且包含对应文件**。

### 8.3 文档（必须）

```
review_report.md         # 代码 review 报告（前置任务，阅读 review_reference.py 后撰写）
design_notes.md          # 设计决策文档
```

**review_report.md 内容**：阅读 `review_reference.py`，找出至少 3 处设计缺陷或潜在 bug，说明问题、影响、改进建议。

**design_notes.md 内容**：
1. 目标函数设计：为什么选择这个目标函数？权重如何确定？
2. 约束条件设计：各项阈值的设定依据
3. 异常处理策略：发现了哪些数据异常？如何处理？
4. 降级方案设计：ODPS 写入失败时的交付流程

### 8.4 代码模块（你自行设计）

除入口文件外，其他代码模块可自由组织。建议拆分为：

- 数据获取模块（调用 Mock ODPS）
- 数据解析模块（解压 big_chunk_string）
- 配额求解模块（MIP 建模）
- 结果入库模块（ODPS 写入 + 降级）

模块名、文件名、函数名自定，不影响测试结果。

### 8.5 产物清单速查

| # | 产物 | 必须？ | 约定 |
|---|------|--------|------|
| 1 | `run_pipeline.py` | 是 | 入口文件，接受 `--ds` 参数 |
| 2 | `output/` 目录 | 是 | 含 raw/parsed/quota/fallback 四个子目录 |
| 3 | `review_report.md` | 是 | 代码 review 报告 |
| 4 | `design_notes.md` | 是 | 设计决策文档 |
| 5 | 其他代码模块 | 自由 | 自行组织结构

---

## 九、参考答案提示

### 9.1 表结构速查

| 问题 | 答案 |
|------|------|
| 上游表有哪些字段？ | group_id, big_chunk_string, ds |
| big_chunk_string 的格式？ | 多条记录用 `二` 分隔，字段用 `一` 分隔 |
| 下游表需要哪些核心字段？ | prod_id, comp_id, rqvae_id, x_曝光配额, y_冷启成功, sim_time_to_first_ab 等 |
| 分区格式是什么？ | ds=YYYYMMDD |
| 如何检查最新分区？ | `SELECT MAX_PT('icbu_ensa.dws_new_prod_info_data')` |

### 9.2 评价维度参考

| 等级 | 标准 |
|------|------|
| 优秀 | Review 发现 3+ 问题，pipeline 完整，发现并处理异常，MIP 建模合理且有设计依据，有降级方案 |
| 良好 | Review 发现 2+ 问题，核心功能实现，MIP 有少量遗漏，有基本的异常处理 |
| 合格 | Review 发现 1+ 问题，基础功能实现，MIP 建模基本完整，pipeline 可跑通 |
| 不合格 | Review 未发现问题或分析肤浅，核心模块缺失，pipeline 无法跑通 |

---

## 十、FAQ

**Q: 我没有 Gurobi license，怎么实现最优化分配？**

A: 可以使用开源替代方案：`pulp` 库、`scipy.optimize.milp` 等。

**Q: Mock ODPS 和真实 ODPS 有什么区别？**

A: Mock ODPS 是本地文件系统模拟器，数据存储在本地 CSV 中，仅支持简化版 SQL。

**Q: 测试数据中有异常，但我没发现，会扣多少分？**

A: 异常处理占 15%。未发现异常但 pipeline 能跑通，会部分扣分；发现并优雅处理则满分。

**Q: 目标函数和约束的权重可以怎么定？**

A: 没有标准答案。请在 `design_notes.md` 中说明你的设计依据。评分看重的是决策的合理性，而非数值的"正确性"。
