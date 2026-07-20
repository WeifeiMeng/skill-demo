## 同城末端配送路径规划

### 业务背景

某同城物流公司每天需要从配送站派出快递员为客户送包裹。公司有一批电动车，每辆车能承载的包裹重量有限。现在需要为当天的配送任务规划方案，目标是让车辆行驶的总距离尽可能短。

### 代码入口

```python
from typing import List, Dict

def plan_routes(depot: List[float],
                customers: List[Dict],
                vehicle_capacity: float,
                max_vehicles: int) -> Dict:
    """
    规划同城配送路径。

    Parameters:
        depot: 配送站坐标，例如 [0.0, 0.0]
        customers: 客户列表，每个客户为字典：
            {
                "id": str,             # 客户唯一标识
                "coord": List[float],  # 客户坐标 [x, y]
                "weight": float        # 包裹重量
            }
        vehicle_capacity: 车辆载重上限
        max_vehicles: 可用车辆数

    Returns:
        dict，包含：
        {
            "routes": List[List[str]],  # 每条路径按访问顺序排列客户，格式为 "id(x,y)"
            "total_distance": float,    # 所有车辆总行驶距离
            "num_vehicles": int,        # 实际使用车辆数
            "message": str              # 求解情况说明，例如求解成功、无解原因、异常情况等
        }

    如果任务无法完成，返回：
        {"routes": [], "total_distance": -1.0, "num_vehicles": -1, "message": "无解原因说明"}
    """
```

### 输出格式说明

- `routes` 中每个子列表代表一辆车的配送顺序。
- 每个客户以 `"id(x,y)"` 格式输出，例如 `"c1(3.0,4.0)"`，便于按坐标验证完整性。
- 两点之间距离按欧几里得距离计算。
- `total_distance` 为所有车辆实际行驶距离之和。
- 距离计算中，车辆默认从 `depot` 出发，按 `routes` 中的顺序访问客户，最后返回 `depot`。
- 在没有异常情况时，可行方案必须服务所有客户；若无法服务全部客户，应返回无解标识。
- `message` 字段用于阐述求解情况，例如求解成功时的方案摘要、无解时的具体原因、遇到异常情况时的说明等。

### 数据规模

- 单次配送任务的客户数量不超过 **100** 个。
