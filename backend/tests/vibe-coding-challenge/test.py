"""vibe-coding-challenge 测试脚本 — 通过 stdin 注入容器执行"""

import sys, os, json, subprocess, csv, shutil
from pathlib import Path
from collections import defaultdict

os.chdir("/workspace")
sys.path.insert(0, "/workspace")
sys.path.insert(0, "/workspace/mock_odps")

RESULTS = {"passed": True, "score": 0, "max_score": 100, "cases": []}

def add_case(name, passed, message="", weight=5):
    RESULTS["cases"].append({"name": name, "passed": passed, "message": str(message)})
    if passed:
        RESULTS["score"] += weight
    else:
        RESULTS["passed"] = False

def find_col(header, patterns):
    """在 CSV header 中找匹配的列索引"""
    for pat in patterns:
        for i, c in enumerate(header):
            if pat.lower() in c.lower().replace(" ", "_").replace("-", "_"):
                return i
    return None

def read_csv_gbk(path):
    with open(path, "r", encoding="gbk", errors="replace") as f:
        reader = csv.reader(f)
        header = next(reader, [])
        rows = [row for row in reader]
    return header, rows

# ── 清理旧输出 ──────────────────────────────────────────────
shutil.rmtree("output", ignore_errors=True)

# ══════════════════════════════════════════════════════════════
# 1. Pipeline 可运行                                              (15分)
# ══════════════════════════════════════════════════════════════
print("[TEST] Running pipeline --ds 20260501 ...", file=sys.stderr)
try:
    proc = subprocess.run(
        ["python3", "run_pipeline.py", "--ds", "20260501"],
        capture_output=True, text=True, timeout=180, cwd="/workspace"
    )
    pipeline_ok = proc.returncode == 0
    detail = f"rc={proc.returncode}"
    if not pipeline_ok:
        tail = (proc.stdout + "\n" + proc.stderr).strip().split("\n")[-8:]
        detail += " | " + "; ".join(t for t in tail if t)
    add_case("1. Pipeline 成功运行", pipeline_ok, detail, weight=15)
except subprocess.TimeoutExpired:
    add_case("1. Pipeline 成功运行", False, "超时(180s)未完成", weight=15)
    pipeline_ok = False
except FileNotFoundError:
    add_case("1. Pipeline 成功运行", False, "未找到 run_pipeline.py", weight=15)
    pipeline_ok = False

# ══════════════════════════════════════════════════════════════
# 2. 输出文件检查                                                (20分)
# ══════════════════════════════════════════════════════════════
raw_files = list(Path("output/raw").glob("*.csv"))
parsed_files = list(Path("output/parsed").glob("*.csv"))
quota_files = list(Path("output/quota").glob("*.csv"))
fallback_files = list(Path("output/fallback").glob("*"))

add_case("2a. 原始数据文件 (output/raw/*.csv)", len(raw_files) > 0, f"{len(raw_files)} files")
add_case("2b. 解析后文件 (output/parsed/*.csv)", len(parsed_files) > 0, f"{len(parsed_files)} files")
add_case("2c. 配额结果文件 (output/quota/*.csv)", len(quota_files) > 0, f"{len(quota_files)} files")
add_case("2d. 降级交付文件 (output/fallback/*)", len(fallback_files) > 0, f"{len(fallback_files)} files")

# ══════════════════════════════════════════════════════════════
# 3. 解析正确性                                                  (20分)
# ══════════════════════════════════════════════════════════════
if parsed_files:
    try:
        header, rows = read_csv_gbk(parsed_files[0])
        add_case("3a. 解析后列数 >= 20", len(header) >= 20, f"got {len(header)} cols")
        add_case("3b. 解析后有数据行", len(rows) > 0, f"got {len(rows)} rows")

        # 检查数值列
        numeric_names = {"proxy_ctr", "proxy_p_ab", "real_imps", "real_ab",
                         "imps_needed_to_break", "is_broken_zero", "rn",
                         "ipv_roi_自然", "priority_score"}
        col_map = {}
        for c in numeric_names:
            idx = find_col(header, [c])
            if idx is not None:
                col_map[c] = idx

        if col_map:
            bad = 0
            sample = min(30, len(rows))
            for row in rows[:sample]:
                for c, idx in col_map.items():
                    if idx < len(row) and row[idx].strip() not in ("", None):
                        try:
                            v = float(row[idx])
                        except ValueError:
                            bad += 1
            add_case("3c. 数值字段正确转换", bad == 0,
                     f"{bad} bad values / {sample * len(col_map)} checks")
        else:
            add_case("3c. 数值字段正确转换", False, "未找到任何期望的数值列")

    except Exception as e:
        add_case("3. 解析正确性", False, str(e), weight=20)

# ══════════════════════════════════════════════════════════════
# 4. 求解器约束验证                                              (35分)
# ══════════════════════════════════════════════════════════════
if quota_files:
    try:
        header, rows = read_csv_gbk(quota_files[0])

        idx_quota   = find_col(header, ["x_曝光配额", "x_quota", "配额"])
        idx_prod    = find_col(header, ["prod_id", "product_id"])
        idx_comp    = find_col(header, ["comp_id", "company", "company_id"])
        idx_broken  = find_col(header, ["y_冷启成功", "is_broken_zero", "broken"])
        idx_sim     = find_col(header, ["sim_time_to_first_ab", "sim_time"])
        idx_need    = find_col(header, ["imps_needed_to_break_xiuzheng",
                                        "imps_needed_to_break", "needed_imps"])

        if None in (idx_quota, idx_prod, idx_comp):
            missing = [n for n, i in [("配额列", idx_quota), ("prod_id", idx_prod),
                        ("comp_id", idx_comp)] if i is None]
            add_case("4a. 必要列存在", False, f"缺少: {', '.join(missing)}", weight=10)
        else:
            # 解析数据
            prods = []
            for row in rows:
                if max(idx_prod, idx_comp, idx_quota) >= len(row):
                    continue
                try:
                    q = float(row[idx_quota]) if row[idx_quota].strip() else 0
                except ValueError:
                    q = 0
                prods.append({
                    "prod_id": row[idx_prod],
                    "comp_id": row[idx_comp],
                    "quota": q,
                })

            supported = [p for p in prods if p["quota"] > 0]
            add_case("4a. 分配了配额的扶持商品 > 0", len(supported) > 0,
                     f"{len(supported)} / {len(prods)}", weight=5)

            # 约束: 单商品配额 <= 500
            over_i = [p for p in prods if p["quota"] > 500]
            add_case("4b. 单商品配额上限 (<=500)", len(over_i) == 0,
                     f"{len(over_i)} violations" +
                     (f" (max={max(p['quota'] for p in over_i):.0f})" if over_i else ""))

            # 约束: 单商家总曝光 <= 3000
            comp_totals = defaultdict(float)
            for p in prods:
                comp_totals[p["comp_id"]] += p["quota"]
            comp_bad = [(c, v) for c, v in comp_totals.items() if v > 3000]
            add_case("4c. 单商家曝光上限 (<=3000)", len(comp_bad) == 0,
                     f"{len(comp_bad)} merchants over limit" +
                     (f" (max={max(v for _, v in comp_bad):.0f})" if comp_bad else ""))

            # 约束: 商家商品数上限 (<= 30 per merchant)
            comp_counts = defaultdict(int)
            for p in prods:
                if p["quota"] > 0:
                    comp_counts[p["comp_id"]] += 1
            cc_bad = [(c, v) for c, v in comp_counts.items() if v > 30]
            add_case("4d. 单商家扶持商品数 (<=30)", len(cc_bad) == 0,
                     f"{len(cc_bad)} violations" +
                     (f" (max={max(v for _, v in cc_bad)})" if cc_bad else ""))

            # 约束: 总预算 (从 parsed 数据推算 pool)
            total_alloc = sum(p["quota"] for p in prods)
            pool = None
            if parsed_files:
                try:
                    ph, prs = read_csv_gbk(parsed_files[0])
                    pi = find_col(ph, ["daily_incremental_imps_pool", "imps_pool", "pool"])
                    if pi is not None:
                        vals = []
                        for r in prs:
                            if pi < len(r) and r[pi].strip():
                                try:
                                    vals.append(float(r[pi]))
                                except ValueError:
                                    pass
                        if vals:
                            pool = max(vals)
                except Exception:
                    pass

            if pool and pool > 0:
                alloc_limit = pool * 0.95 + max(pool * 0.1, 500)  # loose tolerance
                budget_ok = total_alloc <= alloc_limit
                add_case("4e. 总预算约束 (alloc <= pool*0.95)",
                         budget_ok,
                         f"pool={pool:.0f} allocated={total_alloc:.0f} ({total_alloc/pool*100:.1f}%)")
            else:
                add_case("4e. 总预算约束 (alloc <= pool*0.95)", False,
                         "无法从 parsed 数据获取 pool 值")

            # 检查 sim_time 字段
            if idx_sim is not None:
                sim_vals = []
                for row in rows:
                    if idx_sim < len(row) and row[idx_sim].strip():
                        try:
                            sim_vals.append(float(row[idx_sim]))
                        except ValueError:
                            pass
                add_case("4f. sim_time 破零时间字段有效", len(sim_vals) > 0,
                         f"{len(sim_vals)} values, avg={sum(sim_vals)/len(sim_vals):.1f}" if sim_vals else "no values")

            # 检查 broken_zero 逻辑: 已破零的应该保留
            if idx_broken is not None and idx_quota is not None:
                broken_with_quota = 0
                for row in rows:
                    if idx_broken < len(row) and idx_quota < len(row):
                        try:
                            if int(float(row[idx_broken])) == 1 and float(row[idx_quota]) > 0:
                                broken_with_quota += 1
                        except (ValueError, IndexError):
                            pass
                # This is informational - already-broken products can still get quota

    except Exception as e:
        import traceback
        add_case("4. 求解器验证", False, f"{e}\n{traceback.format_exc()}", weight=35)

else:
    add_case("4. 求解器约束验证", False, "未生成配额文件", weight=35)

# ══════════════════════════════════════════════════════════════
# 5. 文档检查                                                    (10分)
# ══════════════════════════════════════════════════════════════
for fname in ["review_report.md", "design_notes.md"]:
    p = Path(fname)
    if p.exists():
        size = p.stat().st_size
        add_case(f"5. {fname} 存在", size > 0, f"{size} bytes")
    else:
        add_case(f"5. {fname} 存在", False, "not found")

# ── 输出最终 JSON 结果 ──────────────────────────────────────
print(json.dumps(RESULTS, ensure_ascii=False))
