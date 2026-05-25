# 面试题：基于工具函数的人脸 Deep Search Skill 设计

---

## 一、背景

### 1.1 任务目标

给定一张模糊的人脸图片，通过**多轮搜索 + 用户反馈确认**，最终定位到具体的人员档案（entity_id）。

### 1.2 可用函数 API


| 函数                           | 功能         |
| ---------------------------- | ---------- |
| `search_person_face`         | 基于人脸检索人员档案 |
| `search_person_trajectory`   | 查询人员轨迹     |
| `search_cameras_by_location` | 查询区域摄像头    |


### 1.3 关键约束

> **必须使用提供的 function API，不能假设新能力**


| 约束项     | 说明                                 |
| ------- | ---------------------------------- |
| Top1 限制 | `search_person_face` 默认只返回 Top1 结果 |
| 多轮调用    | 系统必须支持 iterative 搜索                |
| 用户反馈    | 支持确认（confirmed）和排除（rejected）反馈     |
| 误识别     | 需要考虑模糊图像带来的识别困难                    |
| 搜索扩展    | 通过轨迹 / 摄像头实现搜索空间扩展                 |


### 1.4 场景上下文

面试官会给定一个具体场景，候选人应基于此设计输入输出。

**场景示例**：

```
目标图片：/surveillance/footage/cam07/frame_00432.jpg
目标时间：2026-03-30 14:26:00
目标摄像头：cam07（东走廊）
已知信息：
  - 图片模糊，光线较暗
  - 目标身高约 180cm
  - 目标穿着深色外套
```

**候选人应主动询问/假设的上下文**：


| 上下文项  | 重要性 | 说明               |
| ----- | --- | ---------------- |
| 目标时间  | 高   | 用于轨迹验证的关键时间点     |
| 目标摄像头 | 高   | 用于判断候选人的轨迹是否经过   |
| 图片质量  | 高   | 影响搜索策略（是否需要多帧融合） |
| 目标区域  | 中   | 用于摄像头扩展          |
| 搜索范围  | 中   | 确定时间窗口大小         |


---

## 二、任务要求

### Task 1：设计 Deep Search Skill

设计一个单一 Skill：`deep_face_search`，完成整个搜索过程。

#### 1️⃣ 输入设计

- `query_face`：查询用的人脸图片
- 用户反馈：`confirmed` / `rejected`
- 状态：`state`

#### 2️⃣ 输出设计

- 当前候选人列表（candidates）
- 收敛状态（status）
- 更新后的 state

#### 3️⃣ 状态设计（重点）

```
state = {
    candidates: [...],      # 当前目标（嫌疑人）集合
    rejected_ids: [...],   # 已排除人员
    confirmed_id: str?,    # 已确认人员
    iteration: int,
    history: [...]          # 搜索历史
}
```

---

### Task 2：函数调用策略设计

#### `search_person_face`

- **什么时候用？** 初始检索 + 迭代中的搜索扩展
- **如何弥补 Top1 限制？** （见 Task 5）

#### `search_person_trajectory`

- **如何验证候选人？** 通过轨迹与目标时间/地点交叉验证
- **如何提升置信度？** 轨迹匹配度高的候选人排名上升

#### `search_cameras_by_location`

- **什么时候扩展？** 候选人不明确时，扩展到目标区域附近的摄像头
- **如何结合轨迹？** 找到附近摄像头后，检查候选人的轨迹是否经过

---

### Task 3：搜索流程设计

```
输入模糊人脸
    ↓
初始搜索（search_person_face）
    ↓
用户反馈（确认 / 排除）
    ↓
搜索优化（轨迹验证 / 摄像头扩展）
    ↓
收敛（确认 / 达到阈值 / 达最大轮次）
```

**每轮迭代策略不同**（不是简单重复）：


| 轮次  | 策略    | 调用的函数                        |
| --- | ----- | ---------------------------- |
| 第1轮 | 初始检索  | `search_person_face`         |
| 第2轮 | 轨迹验证  | `search_person_trajectory`   |
| 第3轮 | 摄像头扩展 | `search_cameras_by_location` |
| ... | 动态调整  | 组合调用                         |


---

### Task 4：用户反馈机制

#### 用户如何参与？

- 确认：`E-1234 是这个人`
- 排除：`E-1234 不像，继续找`
- 描述：`这个人更高，大概180cm`
- 指令：`扩大搜索范围`

#### 系统如何利用反馈？

```
confirmed  → 终止搜索，返回结果
rejected   → 从候选集中移除，更新 state
refine     → 根据描述调整搜索策略
expand     → 扩大搜索范围（时间/空间）
```

---

### Task 5（进阶）：如何解决 Top1 限制

> 这是本题最关键的一点：`search_person_face` 只能返回一个结果

**如何实现类似 TopK 搜索的效果？**

可能的思路：

1. **多次查询**：调整参数多次调用
2. **轨迹反向验证**：先用其他方式获得候选人，再用轨迹筛选
3. **搜索空间扩展**：通过摄像头和轨迹扩大候选人池

---

## 三、评分维度


| 维度          | 权重  | 考察点            |
| ----------- | --- | -------------- |
| Skill 设计完整性 | 25% | 输入/输出/状态是否完整   |
| 函数调用策略      | 30% | 能否正确使用 3 个 API |
| 搜索流程设计      | 25% | 多轮迭代逻辑是否合理     |
| Top1 限制解决方案 | 20% | 能否突破 Top1 限制   |


---

## 四、可用函数 API 详解

---

### 1. search_person_face

**Description**：基于输入的人脸图片，在人脸库中检索最相似的一个人（Top1）。

**Request**：

```json
{
  "image_url": "string"
}
```

**Response**：

```json
{
  "person_face": {
    "entity_id": "string",
    "person_name": "string",
    "person_face_img": "string"
  }
}
```

**⚠️ Constraints（重点）**


| 约束       | 说明              |
| -------- | --------------- |
| 只返回 Top1 | 每次调用只返回一个最相似的人  |
| 模糊图像     | 对模糊图像可能误匹配      |
| 不支持 TopK | 无法直接获取 TopK 结果  |
| 单人脸建议    | 输入建议为单人脸，否则可能报错 |


**💡 面试考点提示**

👉 候选人需要解决：

- Top1 → TopK 的"伪扩展问题"
- 如何避免 early wrong decision

---

### 2. search_person_trajectory

**Description**：查询某个人在监控系统中的跨摄像头轨迹。

**Request**：

```json
{
  "entity_id": "string",
  "start_time": "string (optional, ISO8601)",
  "end_time": "string (optional, ISO8601)",
  "camera_ids": ["string"]  // optional
}
```

**Response**：

```json
{
  "entity_id": "string",
  "person_name": "string",
  "trajectory": [
    {
      "camera_id": "string",
      "camera_location": "string",
      "timestamp": "string",
      "face_image_url": "string",
      "body_image_url": "string",
      "confidence": 0.92,
      "position_estimate": { "x": 0.45, "y": 0.62 }
    }
  ],
  "total_frames": 15,
  "first_seen": "2026-03-29T10:00:00Z",
  "last_seen": "2026-03-29T10:05:00Z"
}
```

**⚠️ Constraints**


| 约束                 | 说明                          |
| ------------------ | --------------------------- |
| 数据不连续              | 轨迹数据可能不连续（摄像头盲区）            |
| confidence ≠ 身份置信度 | confidence 表示检测置信度，不等于身份置信度 |
| 查询成本高              | rate limit 低（50/min）        |


**💡 可用能力**

候选人可以利用：

- ✔ 多帧数据增强判断
- ✔ 判断是否经过某区域
- ✔ 判断时间连续性

**🧠 典型用途（应被候选人提到）**

👉 验证候选人是否合理：

- 如果一个候选人**从未出现在目标区域** → 降低置信度
- 如果轨迹**经过目标摄像头** → 提高置信度

---

### 3. search_cameras_by_location

**Description**：根据区域查找摄像头，用于扩展搜索空间。

**Request**：

```json
{
  "location": "string",
  "radius": 50.0
}
```

**Response**：

```json
{
  "cameras": [
    {
      "camera_id": "cam_001",
      "camera_name": "Lobby Entrance Cam",
      "location": "lobby",
      "position": {
        "latitude": 35.123,
        "longitude": 139.123,
        "altitude": 5.0
      },
      "direction": "north",
      "coverage_area": "entrance gate",
      "status": "online",
      "last_active": "2026-03-30T10:00:00Z"
    }
  ]
}
```

**⚠️ Constraints**


| 约束          | 说明                              |
| ----------- | ------------------------------- |
| location 模糊 | location 可能是模糊描述（如 "east_wing"） |
| 区域重叠        | 摄像头覆盖区域可能重叠                     |
| 只返回设备       | 不能直接返回人，只能返回设备                  |


**💡 可用能力**

候选人可以利用：

- ✔ 扩展搜索范围
- ✔ 推断人可能出现的位置
- ✔ 结合 trajectory 做交叉验证

---

### ⚠️ 全局约束（非常重要）

#### ⏱ Rate Limit


| Function                     | Limit   |
| ---------------------------- | ------- |
| `search_person_face`         | 100/min |
| `search_person_trajectory`   | 50/min  |
| `search_cameras_by_location` | 200/min |


👉 要求候选人：

- 避免无效调用
- 有策略地使用 API

---

### ❌ Error Handling

所有函数可能返回：

```json
{
  "error": {
    "code": "NO_FACE_DETECTED",
    "message": "No face found in image"
  }
}
```


| Code                      | 说明      |
| ------------------------- | ------- |
| `NO_FACE_DETECTED`        | 没有检测到人脸 |
| `MULTIPLE_FACES_DETECTED` | 多人脸     |
| `ENTITY_NOT_FOUND`        | 人不存在    |
| `TIMEOUT`                 | 超时      |


---

## 五、交付物说明

候选人需要交付以下内容：

### 5.1 Skill 设计文档

以 Markdown 格式输出完整的 `deep_face_search` Skill 设计，包含：


| 部分         | 必须包含                                                  |
| ---------- | ----------------------------------------------------- |
| **输入设计**   | `query_face`、`feedback`、`state` 的定义                   |
| **输出设计**   | `candidates`、`status`、`state` 的定义                     |
| **状态设计**   | 完整的 state schema（含 candidates、rejected_ids、history 等） |
| **函数调用策略** | 每个迭代阶段调用什么函数、如何组合                                     |
| **收敛策略**   | 何种条件下停止（确认 / 阈值 / 最大轮次）                               |


### 5.2 搜索流程图

用文字描述或 ASCII 图表示完整的多轮搜索流程，示例：

```
Round 1: search_person_face → candidates = [Top1]
    ↓ 用户反馈（不对）
Round 2: search_person_trajectory(Top1) → 验证轨迹
    ↓ 轨迹不在目标区域
Round 3: search_cameras_by_location → 扩展摄像头
    ↓
Round 4: 对扩展摄像头覆盖区域重新 search_person_face
```

### 5.3 Top1 限制的解决方案

必须明确说明：

- **策略是什么**（不是简单重复 search_person_face）
- **为什么这个策略有效**
- **如何避免 early wrong decision**

---

## 六、答案质量分级标准

### 6.1 及格答案（60-70分）

- 能正确调用 `search_person_face` 进行初始检索
- 有 state 概念，能维护 candidates 和 rejected_ids
- 能根据用户反馈排除候选人
- 能收敛（确认或达到最大轮次）

**典型缺陷**：

- 每轮只是机械重复 `search_person_face`，不理解 Top1 限制的问题
- 没有轨迹验证逻辑
- 状态设计不完整

---

### 6.2 良好答案（70-85分）

- 满足及格答案的所有要求
- 理解 Top1 限制，能通过**轨迹反向验证**扩展候选人
- 有清晰的函数调用策略（不是随机调用）
- 能利用 `search_cameras_by_location` 扩展搜索范围
- 有置信度概念，会结合多维度评分

**典型缺陷**：

- 策略单一，没有针对不同反馈调整策略
- 缺少多帧一致性概念
- 错误处理不完善

---

### 6.3 优秀答案（85-100分）

- 满足良好答案的所有要求
- 能主动构建**候选人生成 → 轨迹筛选 → 置信度排序**的闭环
- 有清晰的**多轮策略变化**：每轮策略不同，而非简单重复
- 能合理利用 Rate Limit，不浪费调用次数
- 考虑了边界情况：错误处理、轨迹盲区、模糊图像
- 能主动发现并提出**潜在问题**（如 Top1 误识别风险）

**加分项**：

- 能说明如何利用多帧数据做一致性判断
- 能设计置信度衰减机制
- 考虑到 early wrong decision 的问题并给出解决方案

---

## 七、Top1 限制的直观示例

### 问题场景

```
输入图片：模糊人脸（low-quality.jpg）
预期目标：entity_id = E-9901（Zhao Gang）

Round 1:
  search_person_face(low-quality.jpg)
  → 返回 E-8834（相似度 0.91）❌ 误识别！
  → 返回 E-9901（相似度 0.73）❗ 被遗漏！

问题：E-9901 才是正确目标，但因为 Top1 限制，永远不会被返回
```

### 错误策略（扣分项）

```
Round 1: 返回 Top1 = E-8834 → 用户说"不对" → 陷入僵局
```

### 正确策略（加分项）

```
Round 1: 返回 Top1 = E-8834 → 用户说"不对"
    ↓
Round 2: 尝试获取更多候选人
    方案A: search_person_face(E-8834 的相似图) → 可能返回 E-9901
    方案B: 查 E-8834 的轨迹 → 发现他不在目标区域 → 排除
    方案C: search_cameras_by_location(目标区域) → 找到附近摄像头
           → 对这些摄像头的历史记录搜索 → 找到 E-9901
```

### 核心问题


| 问题                       | 说明                         |
| ------------------------ | -------------------------- |
| **Early Wrong Decision** | Top1 返回后，如果用户接受就结束了（错）     |
| **搜索空间封闭**               | 只在一个候选人的范围内搜索，无法发现新候选人     |
| **需要"破圈"**               | 必须通过轨迹/摄像头扩展，打破 Top1 的封闭空间 |


---

## 八、多帧一致性概念

### 为什么重要

```
目标：在时间 T 被 cam07 拍摄到的人 → entity_id = ?

单一帧的问题：
  - 低质量图片 → search_person_face 误匹配
  - 角度/光照 → embedding 偏差

多帧验证：
  - 如果 E-9901 在 T-5min 到 T+5min 都被检测到
  - 且所有帧的 entity_id 都是 E-9901
  - → 置信度大幅提升
```

### 如何利用轨迹

```
候选人的 trajectory 字段包含多个检测点：

E-9901 的轨迹：
  T-5min: cam05 (北走廊)
  T-3min: cam05 (北走廊)   ← 同一个人，连续检测
  T:      cam07 (东走廊)   ← 目标摄像头
  T+3min: cam09 (东翼出口)

一致性判断：
  - 如果多个检测点的 entity_id 一致 → 高置信度
  - 如果某帧的 entity_id 不同 → 可能不是同一人（误检测）
```

### 一致性在验证中的作用


| 情况                            | 置信度变化 |
| ----------------------------- | ----- |
| 轨迹中只有 1 帧在目标区域                | +10%  |
| 轨迹中有多帧在目标区域，且 entity_id 一致    | +30%  |
| 轨迹中 entity_id 不一致（如中间混入其他 ID） | -20%  |


---

## 九、用户反馈格式定义

### 9.1 反馈类型


| 类型       | 格式示例                       | 作用          |
| -------- | -------------------------- | ----------- |
| **确认**   | `confirmed: E-1234`        | 终止搜索，返回该候选人 |
| **排除**   | `rejected: E-1234`         | 从候选集移除，继续搜索 |
| **描述**   | `description: 更高，180cm左右`  | 调整搜索特征      |
| **扩展**   | `expand: 扩大到东走廊`           | 扩大搜索范围      |
| **多选排除** | `rejected: E-1234, E-4567` | 一次排除多人      |


### 9.2 系统解析逻辑

```python
def parse_feedback(raw_feedback: str) -> Feedback:
    if "confirmed" in raw_feedback:
        return Feedback(type="confirmed", entity_id=extract_id(raw_feedback))
    elif "rejected" in raw_feedback:
        return Feedback(type="rejected", entity_ids=extract_ids(raw_feedback))
    elif "expand" in raw_feedback:
        return Feedback(type="expand", direction=extract_direction(raw_feedback))
    elif "更高" or "更矮" or "胖" or "瘦" in raw_feedback:
        return Feedback(type="description", attributes=extract_attributes(raw_feedback))
    else:
        return Feedback(type="unknown")  # 需要用户澄清
```

### 9.3 反馈驱动的策略调整


| 反馈                         | 系统行为                                   |
| -------------------------- | -------------------------------------- |
| `confirmed: E-1234`        | 终止搜索，输出结果                              |
| `rejected: E-1234`         | 从 candidates 移除，查 E-1234 轨迹来排除相似人      |
| `rejected: E-1234, E-4567` | 批量排除，可能触发扩展策略                          |
| `expand: 东走廊`              | search_cameras_by_location("东走廊")，扩大搜索 |
| `description: 更高`          | 调整相似度权重，或用轨迹中身高信息辅助                    |


