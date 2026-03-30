---
name: deep-face-search
description: Iterative face search with human feedback — solves Top1 limitation via trajectory-guided candidate expansion
type: skill
version: 2.0.0
author: security-team
tags:
  - face-search
  - surveillance
  - iterative-search
  - human-in-the-loop
  -安防
dependencies:
  - functions.md
---

# Deep Face Search Skill

## Invocation

```
/deep-face-search <image_path> [--target-time <ISO8601>] [--target-camera <camera_id>]
```

## Purpose

Given a blurry or low-quality face image from surveillance footage, identify the correct person through **iterative search + human feedback**. This is an **interactive search problem**, not a classification task.

**Core Challenge**: `search_person_face` returns only **Top1** result. This skill solves the Top1 limitation through **trajectory-guided candidate expansion**.

---

## Function APIs

| Function | Rate Limit | Purpose |
|----------|-----------|---------|
| `search_person_face(image_url)` | 100/min | 每次只返回 Top1 |
| `search_person_trajectory(entity_id, start_time?, end_time?, camera_ids?)` | 50/min | 查询轨迹，验证候选人 |
| `search_cameras_by_location(location, radius?)` | 200/min | 查找区域摄像头，扩展搜索空间 |

---

## Core Concept: Breaking the Top1 Limitation

### The Problem

```
search_person_face(image) → 只返回 Top1

如果 Top1 是误匹配（模糊图）：
  → 正确答案永远不会被返回
  → 用户说"不对"后，不知道下一步怎么办
```

### The Solution: Trajectory-Guided Expansion

```
Step 1: 获取 Top1 → 但不信任它
Step 2: 查 Top1 的轨迹 → 发现他不在目标区域
Step 3: 查 Top1 轨迹经过的摄像头覆盖了哪些人
Step 4: 用这些摄像头找到新的候选人（不是用 face similarity）
Step 5: 新候选人 = 真正在目标区域出现的人
```

**核心思想**：用轨迹代替 face similarity 来扩展候选人池。

---

## Input Design

When invoked, the skill receives:

| Field | Type | Required | Description |
|-------|------|---------|-------------|
| `input_image` | `string` | Yes | Path/URL to the query face image |
| `target_time` | `string` | No | ISO8601 时间，用于轨迹验证 |
| `target_camera` | `string` | No | 目标摄像头 ID |
| `feedback` | `Feedback` | No | 上一轮用户反馈 |

### Feedback Schema

```typescript
interface Feedback {
  type: "confirmed" | "rejected" | "expand" | "description" | "multi_reject";
  entity_ids?: string[];        // for confirmed/rejected/multi_reject
  direction?: string;           // for expand (e.g., "东走廊")
  attributes?: string;         // for description (e.g., "更高，180cm")
}
```

---

## Output Design

### Iteration Response (awaiting feedback)

```markdown
## Iteration {n}

**Status**: searching | confirmed | failed
**Candidates**: {count} in pool

### Candidate Pool

| # | Entity ID | Name | Face | Sim | Traj Match | Final | Verdict |
|---|----------|------|------|-----|------------|-------|---------|
| 1 | E-8834   | ...  | [img] | 0.91 | cam07@14:23 | 0.85 | TOP1, in area |
| 2 | E-9901   | ...  | [img] | 0.73 | cam07@14:28 | 0.88 | **NEW** via traj |

### Top1 Trajectory Analysis
**E-8834**: cam01→cam05→cam07→cam09 (14:15-14:31)
  → PASSES target camera cam07 at 14:23 ✓

### Action History
| Round | Action | API Called | Result |
|-------|--------|------------|--------|
| 1 | initial_retrieval | search_person_face | E-8834 (sim=0.91) |
| 2 | traj_verify | search_person_trajectory | E-8834 in area ✓ |
| 3 | user_reject | - | E-8834 rejected |
| 4 | camera_expand | search_cameras_by_location | 4 cameras found |
| 5 | traj_search | search_person_trajectory(all in area) | Found E-9901 |

**Feedback needed**: Is E-9901 the target?
```

### Final Result (confirmed)

```markdown
## Search Complete — CONFIRMED

**Person ID**: {entity_id}
**Person Name**: {person_name}
**Confidence**: {percentage}%
**Iterations**: {n}

### Evidence Chain
1. Face similarity: {sim} (from search_person_face)
2. Trajectory: appeared at {target_camera} at {target_time}
3. Multi-frame consistency: {n} frames with same entity_id

### Trajectory
| Time | Camera | Location |
|------|--------|----------|
| 14:15 | cam01 | Entrance |
| 14:23 | cam07 | **Target frame** |
| 14:31 | cam09 | Exit |

### Search Summary
Total iterations: {n}
APIs called: {count}
Candidate pool built via: face→trajectory→camera expansion
```

---

## State Schema

```typescript
interface FaceSearchState {
  // Core state
  iteration: number;
  status: "searching" | "confirmed" | "exhausted" | "failed";

  // Candidate management
  candidate_pool: Candidate[];    // 所有发现的候选人
  rejected_ids: Set<string>;      // 已排除
  confirmed_id: string | null;    // 已确认

  // Top1 tracking (关键！)
  top1_current: Candidate | null;     // 当前 Top1
  top1_rejected_count: number;        // Top1 被拒绝次数
  top1_wrong_decisions: boolean;       // 是否发生了 Early Wrong Decision

  // Context
  target_time: string | null;
  target_camera: string | null;
  target_area: string | null;         // 目标区域（从摄像头推断）

  // Trajectory-based candidate discovery
  expanded_cameras: string[];          // 已扩展的摄像头列表
  traj_verified_entities: Set<string>;  // 通过轨迹验证过的人

  // History
  history: HistoryEntry[];

  // Config
  config: SearchConfig;
}

interface Candidate {
  entity_id: string;
  person_name: string;
  person_face_img: string;
  similarity: number;                    // face similarity (may be null for traj-found)
  found_via: "face" | "trajectory" | "camera_expansion";
  trajectory?: TrajectoryInfo;          // 轨迹数据
  traj_match_score: number;              // 轨迹匹配分
  final_score: number;                  // 综合评分
  frame_count: number;                  // 轨迹中的检测帧数
  multi_frame_consistent: boolean;       // 多帧一致性
}

interface TrajectoryInfo {
  total_frames: number;
  first_seen: string;
  last_seen: string;
  cameras_visited: string[];
  path: Array<{camera_id: string; timestamp: string; entity_id: string}>;
  in_target_area: boolean;
  near_target_time: boolean;
}

interface HistoryEntry {
  iteration: number;
  action: SearchAction;
  function_calls: string[];
  candidates_found: number;
  candidates_rejected: number;
  reasoning: string;
}

type SearchAction =
  | "initial_retrieval"      // 第一轮：拿 Top1
  | "top1_trajectory_verify"  // 验证 Top1 轨迹
  | "trajectory_expansion"    // 用轨迹找更多人
  | "camera_expansion"        // 用摄像头扩展
  | "camera_trajectory_search" // 在摄像头区域查轨迹
  | "user_confirmed"          // 用户确认
  | "user_rejected"           // 用户排除
  | "rerank"                  // 重排
  | "confidence_threshold_met"; // 达到阈值
```

---

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_iterations` | 10 | 安全上限 |
| `confidence_threshold` | 0.95 | 自动确认阈值 |
| `top1_reject_threshold` | 3 | Top1 被拒绝多少次后强制轨迹扩展 |
| `trajectory_window_minutes` | 30 | 轨迹时间窗口 |
| `min_frames_for_consistency` | 3 | 多帧一致性的最小帧数 |

---

## Search Strategy: Multi-Round Dynamic Adjustment

**每轮策略不同！不是简单重复！**

### Round 1: Initial Retrieval

```
1. search_person_face(image_url)
   → 返回 Top1 (entity_id, similarity)
   → state.top1_current = Top1
   → state.candidate_pool = [Top1]

2. search_person_trajectory(top1_entity_id)
   → 获取 Top1 的完整轨迹
   → 检查是否经过 target_camera at target_time
```

**分析逻辑**：

```
IF Top1 经过目标区域 AND 时间吻合:
  → 可能性高，保留
  → 询问用户确认/排除

IF Top1 不在目标区域:
  → Early Wrong Decision 风险！
  → 进入 Round 2 扩展策略
```

---

### Round 2: Trajectory-Guided Expansion（当 Top1 轨迹不匹配时）

```
1. 从 Top1 的轨迹中提取：
   - 经过的摄像头列表 (cameras_visited)
   - 经过的时间段 (first_seen ~ last_seen)

2. search_cameras_by_location(location=target_area)
   → 获取目标区域的所有摄像头

3. 对于目标区域内的每个摄像头，
   search_person_trajectory(entity_id=top1_id, camera_ids=[目标摄像头])
   → 检查 top1 在目标摄像头处的具体时间

4. 如果 Top1 确实不在目标区域：
   → 用目标摄像头的其他检测记录找新候选人
   → 这些新候选人 = 真正在目标区域出现的人
```

**这是打破 Top1 限制的关键！**

---

### Round 3+: Dynamic Strategy Based on Feedback

| 用户反馈 | 系统策略 |
|---------|---------|
| `rejected: E-xxx` | 从 pool 移除；查该人的轨迹来排除相似的人 |
| `confirmed: E-xxx` | 终止，返回结果 |
| `expand: 东走廊` | 调用 search_cameras_by_location 扩展 |
| `description: 更高` | 用轨迹中的身高信息辅助判断 |

**动态调整逻辑**：

```
IF rejected_ids.size > 3 AND candidate_pool.size < 3:
  → 触发 camera_expansion
  → search_cameras_by_location → 获取区域摄像头
  → 在这些摄像头的历史检测中找更多人

IF top1_rejected_count >= top1_reject_threshold:
  → Top1 连续被拒，可能需要用完全不同的方法
  → 用 trajectory 反向搜索：找在目标区域出现的人
```

---

## Confidence Scoring Algorithm

```
final_confidence = (
    face_similarity * 0.35 +
    trajectory_match * 0.35 +
    multi_frame_consistency * 0.20 +
    context_alignment * 0.10
)

Where:

face_similarity: 来自 search_person_face (0.0-1.0)
  - 注意：模糊图可能不准确

trajectory_match: 轨迹匹配分 (0.0-1.0)
  - +0.35 if 轨迹经过 target_camera at target_time
  - +0.20 if 轨迹经过 target_area（不在精确时间）
  - +0.15 if 轨迹经过 nearby_camera within 5min
  - 0 if 完全不在目标区域

multi_frame_consistency: 多帧一致性 (0.0-1.0)
  - +0.20 if 轨迹中有 >=3 帧且 entity_id 一致
  - +0.10 if 轨迹中有 >=1 帧
  - 0 if 轨迹中 entity_id 不一致

context_alignment: 上下文一致性 (0.0-1.0)
  - +0.10 if 用户描述的身高/穿着匹配
  - +0.05 if 时间段合理
```

---

## Multi-Frame Consistency Check

**为什么重要**：模糊图像的单帧匹配可能出错。多帧验证可以提高置信度。

```
候选人的 trajectory 包含多个检测点：

E-9901 轨迹：
  T-5min: cam05, entity=E-9901 ✓
  T-3min: cam05, entity=E-9901 ✓  ← 连续，同一人
  T:      cam07, entity=E-9901 ✓  ← 目标摄像头
  T+3min: cam09, entity=E-9901 ✓

一致性判断：
  IF 所有帧的 entity_id 一致:
    → multi_frame_consistent = true, +20%
  ELSE:
    → 可能存在误检测, 降低置信度
```

---

## Error Handling

### API Errors

| Error Code | System Action |
|------------|---------------|
| `NO_FACE_DETECTED` | 请求用户提供更高质量的图片 |
| `MULTIPLE_FACES_DETECTED` | 请求用户裁剪到单人脸 |
| `ENTITY_NOT_FOUND` | 从 pool 移除该 ID，继续搜索 |
| `TIMEOUT` | 重试一次，记录到 history |
| `RATE_LIMIT_EXCEEDED` | 等待后重试，优先使用低限额的 API |

### Boundary Conditions

| Condition | Action |
|-----------|--------|
| candidate_pool 为空 | 触发 camera_expansion 扩展搜索 |
| 所有候选人都被拒绝 | 降低阈值，重新 search_person_face |
| 达到 max_iterations | 返回最佳候选人 + 警告 |
| Top1 被拒绝 3 次以上 | 强制用轨迹扩展策略 |

---

## Example: Full Search Flow

### Round 1: Initial

```
Input: /surveillance/cam07/frame_00432.jpg

search_person_face(image_url)
→ E-8834 (Zhang Wei, sim=0.91)

search_person_trajectory(E-8834)
→ 轨迹: cam01→cam05→cam07→cam09 (14:15-14:31)
→ cam07 at 14:23 ← 在目标时间附近！

分析: Top1 轨迹匹配度高，询问用户
```

### Round 2: User Rejects Top1

```
User: "E-8834 不是，目标更高"

top1_rejected_count = 1
→ 从 pool 移除 E-8834
→ 进入 trajectory_expansion

search_cameras_by_location("cam07_zone")
→ [cam05, cam07, cam08, cam09]

检查 pool 中其他候选人的轨迹:
E-2109: cam12→cam14, 不在目标区域 ✗
E-4451: cam07 at 13:27, 不在目标时间 ✗

需要找新人！

策略: 在目标区域的历史检测中找其他人
```

### Round 3: Camera Expansion Discovery

```
search_cameras_by_location("east_corridor")
→ 找到 cam05, cam07, cam08, cam09

检查这些摄像头的检测记录:
→ 发现 E-9901 在 cam07 at 14:28 (目标时间!)
→ 发现 E-9901 的身高 ~182cm (符合用户描述)

新增 E-9901 到 candidate_pool
```

### Round 4: Confirmation

```
User: "E-9901 是这个人，confirmed"

state.confirmed_id = E-9901
state.status = "confirmed"

返回完整结果 + 置信度
```

---

## Top1 Limitation: Complete Strategy Summary

| 阶段 | 目标 | 调用的 API |
|------|------|-----------|
| Round 1 | 获取 Top1 | `search_person_face` |
| Round 1 | 验证 Top1 轨迹 | `search_person_trajectory` |
| Round 2 (if Top1 wrong) | 扩展摄像头 | `search_cameras_by_location` |
| Round 2+ | 在目标区域找其他人 | `search_person_trajectory(entity_ids, camera_ids)` |
| Any | 验证候选人 | `search_person_trajectory(entity_id)` |
| Any | 用户反馈 | 调整策略 |

**打破 Top1 限制的核心**：

1. **不要只依赖 face similarity** — 模糊图像的 Top1 可能完全错误
2. **用 trajectory 作为主要判断依据** — 人在哪里出现比脸更像谁更可靠
3. **通过目标区域的摄像头找候选人** — 而不是通过 face similarity 找
4. **追踪 Top1 的轨迹来排除** — 如果 Top1 不在目标区域，他就不可能是目标

---

## Future Extensions

- [ ] Video frame extraction for multi-image input
- [ ] Real-time stream processing
- [ ] Graph-based trajectory inference (A* path finding)
- [ ] Integration with `search_person_by_attributes`
- [ ] `compare_face_pair` for manual verification

---

## Changelog

### v2.0.0 (2026-03-30)
- **重写**：解决 Top1 限制问题
- 新增 trajectory-guided candidate expansion 策略
- 新增 multi-frame consistency 检查
- 新增 Top1 wrong decision 追踪
- 新增动态策略调整机制
- 重写状态schema，增加更多追踪字段
