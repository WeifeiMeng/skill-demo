"""
同城末端配送路径规划 — 自动评测脚本

在 Docker 容器中运行，导入考生的 plan_routes 函数，
用 11 个测试用例验证正确性和鲁棒性。
"""
import sys
import json
import math
import traceback

# ─── Test case data (embedded, self-contained) ─────────────────────

CASES = []

# Case 1: 基础可行场景 (10分)
CASES.append({
    "name": "基础可行场景",
    "score": 10,
    "input": {
        "depot": [0.0, 0.0],
        "customers": [
            {"id": "c1", "coord": [1.0, 0.0], "weight": 1.0},
            {"id": "c2", "coord": [0.0, 1.0], "weight": 1.0},
            {"id": "c3", "coord": [-1.0, 0.0], "weight": 1.0},
        ],
        "vehicle_capacity": 5.0,
        "max_vehicles": 2,
    },
    "check": "expect_success",
    "expect_coords": [(1.0, 0.0), (0.0, 1.0), (-1.0, 0.0)],
    "expect_distance": 4.828,
    "distance_tol": 0.1,
})

# Case 2: 容量边界 (10分)
CASES.append({
    "name": "容量边界",
    "score": 10,
    "input": {
        "depot": [0.0, 0.0],
        "customers": [
            {"id": "c1", "coord": [1.0, 0.0], "weight": 3.0},
            {"id": "c2", "coord": [0.0, 1.0], "weight": 3.0},
            {"id": "c3", "coord": [-1.0, 0.0], "weight": 3.0},
        ],
        "vehicle_capacity": 5.0,
        "max_vehicles": 3,
    },
    "check": "expect_success",
    "expect_coords": [(1.0, 0.0), (0.0, 1.0), (-1.0, 0.0)],
    "expect_distance": 6.0,
    "distance_tol": 0.1,
    "expect_num_vehicles": 3,
})

# Case 3: 负重量异常数据 (5分)
CASES.append({
    "name": "负重量异常数据",
    "score": 5,
    "input": {
        "depot": [0.0, 0.0],
        "customers": [
            {"id": "c1", "coord": [1.0, 0.0], "weight": -0.2},
            {"id": "c2", "coord": [0.0, 1.0], "weight": 0.2},
        ],
        "vehicle_capacity": 5.0,
        "max_vehicles": 2,
    },
    "check": "expect_anomaly_handling",
    # 方案A: 拒绝求解 (total_distance==-1)
    # 方案B: 跳过c1，只服务c2，total_distance≈2.0
    "must_not_include_coord": (1.0, 0.0),  # c1的坐标不能出现
})

# Case 4: 车辆不足 (10分)
CASES.append({
    "name": "车辆不足",
    "score": 10,
    "input": {
        "depot": [0.0, 0.0],
        "customers": [
            {"id": "c1", "coord": [1.0, 0.0], "weight": 4.0},
            {"id": "c2", "coord": [0.0, 1.0], "weight": 4.0},
            {"id": "c3", "coord": [-1.0, 0.0], "weight": 4.0},
        ],
        "vehicle_capacity": 5.0,
        "max_vehicles": 2,
    },
    "check": "expect_no_solution",
})

# Case 5: 往返距离完整性 (10分)
CASES.append({
    "name": "往返距离完整性",
    "score": 10,
    "input": {
        "depot": [0.0, 0.0],
        "customers": [
            {"id": "c1", "coord": [3.0, 0.0], "weight": 1.0},
            {"id": "c2", "coord": [0.0, 4.0], "weight": 1.0},
        ],
        "vehicle_capacity": 5.0,
        "max_vehicles": 1,
    },
    "check": "expect_success",
    "expect_coords": [(3.0, 0.0), (0.0, 4.0)],
    "expect_distance": 12.0,
    "distance_tol": 0.2,
})

# Case 6: 单点超载 (10分)
CASES.append({
    "name": "单点超载",
    "score": 10,
    "input": {
        "depot": [0.0, 0.0],
        "customers": [
            {"id": "c1", "coord": [1.0, 0.0], "weight": 2.0},
            {"id": "c2", "coord": [0.0, 1.0], "weight": 7.0},
        ],
        "vehicle_capacity": 5.0,
        "max_vehicles": 3,
    },
    "check": "expect_no_solution",
})

# Case 7: 同位置客户分组 (10分)
CASES.append({
    "name": "同位置客户分组",
    "score": 10,
    "input": {
        "depot": [0.0, 0.0],
        "customers": [
            {"id": "c1", "coord": [0.0, 0.0], "weight": 1.0},
            {"id": "c2", "coord": [0.0, 0.0], "weight": 1.0},
            {"id": "c3", "coord": [3.0, 4.0], "weight": 2.0},
            {"id": "c4", "coord": [3.0, 4.0], "weight": 3.0},
            {"id": "c5", "coord": [0.0, 1.0], "weight": 1.0},
        ],
        "vehicle_capacity": 5.0,
        "max_vehicles": 3,
    },
    "check": "expect_success",
    "expect_coords": [(0.0, 0.0), (0.0, 0.0), (3.0, 4.0), (3.0, 4.0), (0.0, 1.0)],
    # c3+c4 must be in the same vehicle (weight 2+3=5 = capacity)
    "must_same_vehicle": [(3.0, 4.0), (3.0, 4.0)],
})

# Case 8: 空客户列表 (5分)
CASES.append({
    "name": "空客户列表",
    "score": 5,
    "input": {
        "depot": [0.0, 0.0],
        "customers": [],
        "vehicle_capacity": 5.0,
        "max_vehicles": 2,
    },
    "check": "expect_empty",
})

# Case 9: 客户ID重复 (5分)
CASES.append({
    "name": "客户ID重复",
    "score": 5,
    "input": {
        "depot": [0.0, 0.0],
        "customers": [
            {"id": "c1", "coord": [1.0, 0.0], "weight": 1.0},
            {"id": "c2", "coord": [0.0, 1.0], "weight": 1.0},
            {"id": "c1", "coord": [-1.0, 0.0], "weight": 1.0},
        ],
        "vehicle_capacity": 5.0,
        "max_vehicles": 2,
    },
    "check": "expect_duplicate_id_handling",
    # 方案A: 服务所有3个位置
    # 方案B: 拒绝求解
    "all_coords": [(1.0, 0.0), (0.0, 1.0), (-1.0, 0.0)],
})

# Case 10: 坐标轴缺失 (5分)
CASES.append({
    "name": "坐标轴缺失",
    "score": 5,
    "input": {
        "depot": [0.0, 0.0],
        "customers": [
            {"id": "c1", "coord": [3.0, 0.0], "weight": 5.0},
            {"id": "c2", "coord": [3.0], "weight": 2.0},
            {"id": "c3", "coord": [0.0, 4.0], "weight": 10.0},
        ],
        "vehicle_capacity": 20.0,
        "max_vehicles": 2,
    },
    "check": "expect_anomaly_handling",
    "must_not_include_coord": (3.0,),  # 不完整坐标不能出现
})

# Case 11: Solomon R101 (20分)
_solomon_customers = [
    {"id": "1",  "coord": [41.0, 49.0], "weight": 10.0},
    {"id": "2",  "coord": [35.0, 17.0], "weight": 7.0},
    {"id": "3",  "coord": [55.0, 45.0], "weight": 13.0},
    {"id": "4",  "coord": [55.0, 20.0], "weight": 19.0},
    {"id": "5",  "coord": [15.0, 30.0], "weight": 26.0},
    {"id": "6",  "coord": [25.0, 30.0], "weight": 3.0},
    {"id": "7",  "coord": [20.0, 50.0], "weight": 5.0},
    {"id": "8",  "coord": [10.0, 43.0], "weight": 9.0},
    {"id": "9",  "coord": [55.0, 60.0], "weight": 16.0},
    {"id": "10", "coord": [30.0, 60.0], "weight": 16.0},
    {"id": "11", "coord": [20.0, 65.0], "weight": 12.0},
    {"id": "12", "coord": [50.0, 35.0], "weight": 19.0},
    {"id": "13", "coord": [30.0, 25.0], "weight": 23.0},
    {"id": "14", "coord": [15.0, 10.0], "weight": 20.0},
    {"id": "15", "coord": [30.0, 5.0],  "weight": 8.0},
    {"id": "16", "coord": [10.0, 20.0], "weight": 19.0},
    {"id": "17", "coord": [5.0, 30.0],  "weight": 2.0},
    {"id": "18", "coord": [20.0, 40.0], "weight": 12.0},
    {"id": "19", "coord": [15.0, 60.0], "weight": 17.0},
    {"id": "20", "coord": [45.0, 65.0], "weight": 9.0},
    {"id": "21", "coord": [45.0, 20.0], "weight": 11.0},
    {"id": "22", "coord": [45.0, 10.0], "weight": 18.0},
    {"id": "23", "coord": [55.0, 5.0],  "weight": 29.0},
    {"id": "24", "coord": [65.0, 35.0], "weight": 3.0},
    {"id": "25", "coord": [65.0, 20.0], "weight": 6.0},
    {"id": "26", "coord": [45.0, 30.0], "weight": 17.0},
    {"id": "27", "coord": [35.0, 40.0], "weight": 16.0},
    {"id": "28", "coord": [41.0, 37.0], "weight": 16.0},
    {"id": "29", "coord": [64.0, 42.0], "weight": 12.0},
    {"id": "30", "coord": [40.0, 60.0], "weight": 15.0},
    {"id": "31", "coord": [31.0, 52.0], "weight": 12.0},
    {"id": "32", "coord": [35.0, 69.0], "weight": 11.0},
    {"id": "33", "coord": [53.0, 52.0], "weight": 12.0},
    {"id": "34", "coord": [65.0, 55.0], "weight": 10.0},
    {"id": "35", "coord": [63.0, 65.0], "weight": 6.0},
    {"id": "36", "coord": [2.0, 60.0],  "weight": 9.0},
    {"id": "37", "coord": [20.0, 20.0], "weight": 10.0},
    {"id": "38", "coord": [5.0, 5.0],   "weight": 12.0},
    {"id": "39", "coord": [60.0, 12.0], "weight": 10.0},
    {"id": "40", "coord": [40.0, 25.0], "weight": 12.0},
    {"id": "41", "coord": [42.0, 7.0],  "weight": 14.0},
    {"id": "42", "coord": [24.0, 12.0], "weight": 15.0},
    {"id": "43", "coord": [23.0, 3.0],  "weight": 13.0},
    {"id": "44", "coord": [11.0, 14.0], "weight": 13.0},
    {"id": "45", "coord": [6.0, 38.0],  "weight": 13.0},
    {"id": "46", "coord": [2.0, 50.0],  "weight": 12.0},
    {"id": "47", "coord": [8.0, 45.0],  "weight": 12.0},
    {"id": "48", "coord": [13.0, 32.0], "weight": 13.0},
    {"id": "49", "coord": [6.0, 43.0],  "weight": 10.0},
    {"id": "50", "coord": [47.0, 37.0], "weight": 10.0},
    {"id": "51", "coord": [49.0, 38.0], "weight": 10.0},
    {"id": "52", "coord": [27.0, 68.0], "weight": 11.0},
    {"id": "53", "coord": [37.0, 52.0], "weight": 11.0},
    {"id": "54", "coord": [57.0, 15.0], "weight": 14.0},
    {"id": "55", "coord": [63.0, 32.0], "weight": 10.0},
    {"id": "56", "coord": [21.0, 47.0], "weight": 10.0},
    {"id": "57", "coord": [12.0, 43.0], "weight": 12.0},
    {"id": "58", "coord": [24.0, 54.0], "weight": 12.0},
    {"id": "59", "coord": [67.0, 41.0], "weight": 10.0},
    {"id": "60", "coord": [37.0, 31.0], "weight": 10.0},
    {"id": "61", "coord": [49.0, 31.0], "weight": 12.0},
    {"id": "62", "coord": [53.0, 38.0], "weight": 10.0},
    {"id": "63", "coord": [61.0, 33.0], "weight": 10.0},
    {"id": "64", "coord": [57.0, 58.0], "weight": 10.0},
    {"id": "65", "coord": [56.0, 37.0], "weight": 10.0},
    {"id": "66", "coord": [55.0, 54.0], "weight": 10.0},
    {"id": "67", "coord": [15.0, 47.0], "weight": 10.0},
    {"id": "68", "coord": [14.0, 37.0], "weight": 10.0},
    {"id": "69", "coord": [11.0, 31.0], "weight": 10.0},
    {"id": "70", "coord": [16.0, 22.0], "weight": 12.0},
    {"id": "71", "coord": [4.0, 18.0],  "weight": 12.0},
    {"id": "72", "coord": [28.0, 33.0], "weight": 12.0},
    {"id": "73", "coord": [26.0, 43.0], "weight": 12.0},
    {"id": "74", "coord": [26.0, 34.0], "weight": 12.0},
    {"id": "75", "coord": [31.0, 62.0], "weight": 12.0},
    {"id": "76", "coord": [15.0, 42.0], "weight": 12.0},
    {"id": "77", "coord": [22.0, 53.0], "weight": 12.0},
    {"id": "78", "coord": [18.0, 63.0], "weight": 12.0},
    {"id": "79", "coord": [26.0, 29.0], "weight": 12.0},
    {"id": "80", "coord": [25.0, 65.0], "weight": 12.0},
    {"id": "81", "coord": [22.0, 42.0], "weight": 12.0},
    {"id": "82", "coord": [25.0, 38.0], "weight": 12.0},
    {"id": "83", "coord": [19.0, 67.0], "weight": 12.0},
    {"id": "84", "coord": [20.0, 26.0], "weight": 12.0},
    {"id": "85", "coord": [18.0, 38.0], "weight": 12.0},
    {"id": "86", "coord": [35.0, 46.0], "weight": 12.0},
    {"id": "87", "coord": [35.0, 32.0], "weight": 12.0},
    {"id": "88", "coord": [44.0, 40.0], "weight": 12.0},
    {"id": "89", "coord": [42.0, 41.0], "weight": 12.0},
    {"id": "90", "coord": [40.0, 55.0], "weight": 12.0},
    {"id": "91", "coord": [40.0, 45.0], "weight": 12.0},
    {"id": "92", "coord": [38.0, 55.0], "weight": 12.0},
    {"id": "93", "coord": [35.0, 44.0], "weight": 12.0},
    {"id": "94", "coord": [50.0, 45.0], "weight": 12.0},
    {"id": "95", "coord": [55.0, 45.0], "weight": 12.0},
    {"id": "96", "coord": [35.0, 60.0], "weight": 12.0},
    {"id": "97", "coord": [62.0, 35.0], "weight": 12.0},
    {"id": "98", "coord": [62.0, 57.0], "weight": 12.0},
    {"id": "99", "coord": [62.0, 24.0], "weight": 12.0},
    {"id": "100", "coord": [21.0, 36.0], "weight": 12.0},
]
CASES.append({
    "name": "Solomon R101 (100客户)",
    "score": 20,
    "input": {
        "depot": [35.0, 35.0],
        "customers": _solomon_customers,
        "vehicle_capacity": 200.0,
        "max_vehicles": 25,
    },
    "check": "expect_success",
    "expect_coords": [tuple(c["coord"]) for c in _solomon_customers],
    "expect_distance_max": 900.0,
})


# ─── Helper functions ────────────────────────────────────────────

def extract_coords_from_routes(routes):
    """从 routes 中提取所有坐标元组"""
    coords = []
    for route in routes:
        for s in route:
            # 格式: "id(x,y)" 或 "id(x, y)"
            try:
                paren = s.index("(")
                end = s.rindex(")")
                inside = s[paren + 1:end]
                x, y = inside.split(",")
                coords.append((float(x.strip()), float(y.strip())))
            except (ValueError, IndexError):
                coords.append(None)
    return coords


def coords_in_same_vehicle(routes, c1, c2):
    """检查 c1 和 c2 是否在同一辆车的路径中"""
    s1 = f"({c1[0]},{c1[1]})" if c1[0] == int(c1[0]) and c1[1] == int(c1[1]) else f"({c1[0]:.1f},{c1[1]:.1f})"
    s2 = f"({c2[0]},{c2[1]})" if c2[0] == int(c2[0]) and c2[1] == int(c2[1]) else f"({c2[0]:.1f},{c2[1]:.1f})"
    for route in routes:
        found1 = any(c1 == coord or s1 in str(item) for item in route for coord in [c1])
        found2 = any(c2 == coord or s2 in str(item) for item in route for coord in [c2])
        # Simpler: just check that both coordinates appear in the same route string list
        route_str = "|".join(route)
        has_c1 = str(c1[0]) in route_str and str(c1[1]) in route_str
        has_c2 = str(c2[0]) in route_str and str(c2[1]) in route_str
        if has_c1 and has_c2:
            return True
    return False


def coords_in_same_vehicle_exact(routes, c1, c2):
    """更精确地检查两个坐标是否在同一辆车中"""
    s1 = f"({c1[0]},{c1[1]})"
    s2 = f"({c2[0]},{c2[1]})"
    for route in routes:
        items = " ".join(route)
        if s1 in items and s2 in items:
            return True
    return False


def check_capacity(routes, customers, depot, capacity):
    """检查是否违反容量约束，返回违规信息或 None"""
    # Build coord→weight map
    coord_weight = {}
    for c in customers:
        key = tuple(c["coord"])
        coord_weight[key] = coord_weight.get(key, [])
        coord_weight[key].append(c["weight"])

    for route in routes:
        total_w = 0.0
        for s in route:
            try:
                paren = s.index("(")
                end = s.rindex(")")
                inside = s[paren + 1:end]
                x_str, y_str = inside.split(",")
                x, y = float(x_str.strip()), float(y_str.strip())
            except (ValueError, IndexError):
                return f"无法解析坐标: {s}"
            key = (x, y)
            if key in coord_weight and coord_weight[key]:
                total_w += coord_weight[key].pop(0)
            else:
                return f"坐标 {key} 不在客户列表中"
        if total_w > capacity + 0.001:
            return f"车辆超载: {total_w} > {capacity}"
    return None


# ─── Main test runner ────────────────────────────────────────────

def run_tests():
    """运行所有测试用例，输出 JSON 结果"""
    results = []
    total_score = 0
    max_possible = sum(c["score"] for c in CASES)

    # Import student's solution
    try:
        sys.path.insert(0, "/workspace")
        from solution import plan_routes
    except ImportError as e:
        print(json.dumps({
            "score": 0,
            "max_score": max_possible,
            "passed": False,
            "cases": [{
                "name": "导入模块",
                "passed": False,
                "score": 0,
                "message": f"无法导入 solution.py: {e}"
            }]
        }))
        return

    if not callable(plan_routes):
        print(json.dumps({
            "score": 0,
            "max_score": max_possible,
            "passed": False,
            "cases": [{
                "name": "函数检查",
                "passed": False,
                "score": 0,
                "message": "plan_routes 不是可调用函数"
            }]
        }))
        return

    # Run each test case
    for case in CASES:
        name = case["name"]
        score_val = case["score"]
        check_type = case["check"]
        inp = case["input"]

        try:
            result = plan_routes(
                depot=inp["depot"],
                customers=inp["customers"],
                vehicle_capacity=inp["vehicle_capacity"],
                max_vehicles=inp["max_vehicles"],
            )
        except Exception as e:
            results.append({
                "name": name,
                "passed": False,
                "score": 0,
                "message": f"函数抛出异常: {str(e)}"
            })
            continue

        # Ensure result is a dict
        if not isinstance(result, dict):
            results.append({
                "name": name,
                "passed": False,
                "score": 0,
                "message": f"返回值类型错误: 期望 dict，实际 {type(result).__name__}"
            })
            continue

        # Check required keys
        if not all(k in result for k in ("routes", "total_distance", "num_vehicles", "message")):
            missing = [k for k in ("routes", "total_distance", "num_vehicles", "message") if k not in result]
            results.append({
                "name": name,
                "passed": False,
                "score": 0,
                "message": f"返回值缺少字段: {missing}"
            })
            continue

        routes = result["routes"]
        total_dist = result["total_distance"]
        num_vehicles = result["num_vehicles"]
        msg = result.get("message", "")

        if check_type == "expect_no_solution":
            # 必须返回无解标识
            if total_dist == -1.0 and num_vehicles == -1:
                results.append({
                    "name": name,
                    "passed": True,
                    "score": score_val,
                    "message": f"正确识别无解: {msg}"
                })
                total_score += score_val
            else:
                results.append({
                    "name": name,
                    "passed": False,
                    "score": 0,
                    "message": f"应返回无解标识 (total_distance=-1, num_vehicles=-1)，实际 total_distance={total_dist}, num_vehicles={num_vehicles}"
                })
            continue

        if check_type == "expect_empty":
            # 空客户列表
            if total_dist == 0.0 and num_vehicles == 0 and routes == []:
                results.append({
                    "name": name,
                    "passed": True,
                    "score": score_val,
                    "message": f"正确处理空列表: {msg}"
                })
                total_score += score_val
            elif total_dist == -1.0:
                results.append({
                    "name": name,
                    "passed": False,
                    "score": 0,
                    "message": f"空列表不应返回无解标识: {msg}"
                })
            else:
                results.append({
                    "name": name,
                    "passed": True,
                    "score": score_val,
                    "message": f"处理空列表（非标准结果但可接受）: {msg}"
                })
                total_score += score_val
            continue

        if check_type == "expect_anomaly_handling":
            must_not = case.get("must_not_include_coord")
            passed = False

            if total_dist == -1.0:
                # 方案A: 拒绝求解
                passed = True
                msg_detail = "方案A: 检测异常并拒绝求解"
            elif must_not:
                # 方案B: 跳过异常客户
                coords_found = extract_coords_from_routes(routes)
                has_bad_coord = any(
                    c == must_not or (c and abs(c[0] - must_not[0]) < 0.01 and len(c) > 1 and (len(must_not) < 2 or abs(c[1] - must_not[1]) < 0.01))
                    for c in coords_found if c and len(c) == len(must_not)
                )
                # Simpler check for the forbidden coord
                forbidden_str = f"({must_not[0]}"
                if len(must_not) > 1:
                    forbidden_str += f",{must_not[1]}"
                has_forbidden = any(forbidden_str in s for route in routes for s in route)

                if not has_forbidden and total_dist >= 0:
                    passed = True
                    msg_detail = f"方案B: 跳过异常客户，服务其余客户，total_distance={total_dist:.2f}"
                elif not has_forbidden and total_dist == -1.0:
                    passed = True
                    msg_detail = "方案A: 检测异常并拒绝求解"

            if passed:
                results.append({
                    "name": name,
                    "passed": True,
                    "score": score_val,
                    "message": msg_detail
                })
                total_score += score_val
            else:
                results.append({
                    "name": name,
                    "passed": False,
                    "score": 0,
                    "message": f"未正确处理异常数据: {msg}"
                })
            continue

        if check_type == "expect_duplicate_id_handling":
            all_coords_expected = case["all_coords"]
            coords_found = extract_coords_from_routes(routes)

            if total_dist == -1.0:
                # 拒绝求解也是合理的
                results.append({
                    "name": name,
                    "passed": True,
                    "score": score_val,
                    "message": f"检测到重复ID并拒绝求解: {msg}"
                })
                total_score += score_val
            else:
                # 检查是否所有3个坐标都出现
                all_found = True
                missing = []
                for expected in all_coords_expected:
                    found = False
                    for c in coords_found:
                        if c and abs(c[0] - expected[0]) < 0.01 and abs(c[1] - expected[1]) < 0.01:
                            found = True
                            break
                    if not found:
                        all_found = False
                        missing.append(expected)

                if all_found:
                    results.append({
                        "name": name,
                        "passed": True,
                        "score": score_val,
                        "message": f"服务所有3个位置（按坐标验证），total_distance={total_dist:.2f}"
                    })
                    total_score += score_val
                else:
                    results.append({
                        "name": name,
                        "passed": False,
                        "score": 0,
                        "message": f"缺少坐标: {missing}（可能因重复ID导致覆盖）"
                    })
            continue

        if check_type == "expect_success":
            # Validate coordinates
            if "expect_coords" in case:
                coords_found = extract_coords_from_routes(routes)
                missing_coords = []
                for expected in case["expect_coords"]:
                    found = False
                    for c in coords_found:
                        if c and abs(c[0] - expected[0]) < 0.01 and abs(c[1] - expected[1]) < 0.01:
                            found = True
                            break
                    if not found:
                        missing_coords.append(expected)

                if missing_coords:
                    results.append({
                        "name": name,
                        "passed": False,
                        "score": 0,
                        "message": f"缺少客户坐标: {missing_coords}"
                    })
                    continue

            # Validate distance
            if "expect_distance" in case:
                tol = case.get("distance_tol", 0.1)
                if abs(total_dist - case["expect_distance"]) > tol:
                    results.append({
                        "name": name,
                        "passed": False,
                        "score": 0,
                        "message": f"total_distance 不符: 期望 {case['expect_distance']}±{tol}, 实际 {total_dist:.3f}"
                    })
                    continue

            # Validate max distance (for large cases)
            if "expect_distance_max" in case:
                if total_dist > case["expect_distance_max"]:
                    results.append({
                        "name": name,
                        "passed": False,
                        "score": 0,
                        "message": f"total_distance 超标: 上限 {case['expect_distance_max']}, 实际 {total_dist:.2f}"
                    })
                    continue

            # Validate num_vehicles
            if "expect_num_vehicles" in case:
                if num_vehicles != case["expect_num_vehicles"]:
                    results.append({
                        "name": name,
                        "passed": False,
                        "score": 0,
                        "message": f"num_vehicles 不符: 期望 {case['expect_num_vehicles']}, 实际 {num_vehicles}"
                    })
                    continue

            # Validate same-vehicle constraint
            if "must_same_vehicle" in case:
                c1, c2 = case["must_same_vehicle"]
                if not coords_in_same_vehicle_exact(routes, c1, c2):
                    results.append({
                        "name": name,
                        "passed": False,
                        "score": 0,
                        "message": f"坐标 {c1} 和 {c2} 应在同一辆车中但被拆分"
                    })
                    continue

            # Validate capacity constraints
            capacity_err = check_capacity(routes, inp["customers"], inp["depot"], inp["vehicle_capacity"])
            if capacity_err:
                results.append({
                    "name": name,
                    "passed": False,
                    "score": 0,
                    "message": f"容量约束违反: {capacity_err}"
                })
                continue

            # All checks passed
            results.append({
                "name": name,
                "passed": True,
                "score": score_val,
                "message": f"通过。total_distance={total_dist:.2f}, num_vehicles={num_vehicles}"
            })
            total_score += score_val

    passed = total_score >= max_possible * 0.6
    print(json.dumps({
        "score": total_score,
        "max_score": max_possible,
        "passed": passed,
        "cases": results
    }))


if __name__ == "__main__":
    run_tests()
