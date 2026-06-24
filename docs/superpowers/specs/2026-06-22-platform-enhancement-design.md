# AI Done 平台功能增强设计文档

## 概述

基于 refrence/ 中的 Coding Coach 参考设计，为 AI Done 平台增加 B端（管理员）和 C端（学生）功能页面。采用混合数据模式（前端 mock + API 接口预留），Layout + Page 分层架构。

## 技术方案

- **框架**: Vue 3 Composition API (`<script setup>`)
- **样式**: Scoped CSS，延续现有设计风格（#4a6cf7 主色、#f8fafc 背景）
- **数据**: `src/data/mockData.js` 提供静态 mock 数据，`src/data/api.js` 封装 API 调用（当前 fallback 到 mock）
- **路由**: Vue Router，B端路由挂载在 `/admin/*` 下

## 路由结构

### C端（6 个路由）
| Path | Component | 状态 |
|------|-----------|------|
| `/` | Landing.vue | 已有，保留 |
| `/challenges` | Home.vue | 增强：加统计、筛选、活动列表 |
| `/exam/:filename` | Exam.vue | 已有，保留 |
| `/completed/:filename` | Completed.vue | 增强：改为完整评分报告 |
| `/solutions` | Solutions.vue | **新增** |
| `/contest` | Contest.vue | **新增** |
| `/leaderboard` | Leaderboard.vue | **新增** |

### B端（3 个路由，共用 AdminLayout）
| Path | Component | 状态 |
|------|-----------|------|
| `/admin/exams` | AdminExamSessions.vue | **新增** |
| `/admin/monitor/:examId` | AdminMonitor.vue | **新增** |
| `/admin/grading/:examId` | AdminGrading.vue | **新增** |

## 共享组件

所有组件放在 `frontend/src/components/` 目录下，每个组件 scoped 样式，props 驱动。

| 组件 | Props | 使用场景 |
|------|-------|----------|
| `StatCard` | label, value, color | 统计卡片行，B端和C端复用 |
| `StatusBadge` | label, variant | 状态/难度/通过标记 |
| `ScoreBar` | score, max | 成绩明细中的水平进度条 |
| `FilterChip` | label, active | 筛选器 |
| `CircleProgress` | value, max, size | 环形得分图 |
| `ProcessBar` | icon, label, score, max | 过程分维度展示 |
| `CodeBlock` | code, highlights | 代码展示（阅卷、题解） |
| `RatingCard` | rating, rank, tier, change | 排行榜个人区 |

## 数据层

### `src/data/mockData.js`
纯数据工厂函数，导出静态 mock 数据。所有数据与最终 API 返回结构一致。

### `src/data/api.js`
```js
// 统一模式
export async function fetchChallenges() {
  // 后续替换为真实 API
  // const res = await fetch(`${API_BASE}/challenges`)
  // if (res.ok) return res.json()
  return getChallenges() // mock fallback
}
```

## 页面功能要点

### C端

**Home.vue（增强）**
- 上方统计区：4 个 StatCard（总挑战数、进行中、已完成、AI评分）
- FilterChip 筛选行（难度、类别、状态）
- 搜索框
- 题目卡片增强：difficulty badge、通过率、尝试人数
- 右侧最近活动列表

**Completed.vue（增强为评分报告）**
- 大号总分数 + 等级 Badge
- CircleProgress：结果得分环形图
- ProcessBar 列表：AI对话质量、Token效率、用时效率
- 测试用例结果列表
- CodeBlock：考生代码展示
- 底部统计条：用时、AI轮次、Token消耗、切屏次数

**Solutions.vue（新增）**
- 筛选栏：按题目、排序方式、搜索
- 双列卡片网格
- 精选题解标识（金色边框）
- 代码片段预览（深色背景）
- 作者信息、互动数据
- 详情 Modal：解题思路、完整代码、复杂度分析、踩坑记录
- 底部操作栏：点赞、收藏、评论

**Contest.vue（新增）**
- Hero Banner：深色渐变背景 + 标题 + 计时器
- 竞赛统计
- 题目列表：每行显示状态（已解决/尝试中/未开始）
- 实时排名 Top 10 表格
- 历史竞赛卡片网格

**Leaderboard.vue（新增）**
- 个人 Rating 深色卡片
- 段位图例（7 段位颜色）
- Rating 趋势柱状图
- Tab 切换（总排/周排/月排/做题数/胜率）
- 排名表格：头像、段位标题、积分、参赛次数、胜率
- 当前用户行高亮
- 分页组件

### B端

**AdminLayout**
- 左侧 220px 侧边栏（Logo + 导航链接）
- 右侧主内容区（max-width 1100px）

**AdminExamSessions.vue（新增）**
- 4 个 StatCard
- 考试列表 DataTable
- 行操作按钮（监控/编辑/详情/删除）
- 创建考试 Modal（表单含字段、时间、题目选择、白名单、防作弊设置）

**AdminMonitor.vue（新增）**
- 顶部信息栏（考试名、状态 Badge、在线人数、剩余时间）
- 三栏布局
- 左栏：实时统计 + 各题进度条 + 容器资源状态
- 中栏：考生卡片网格（状态指示灯、当前进度、异常标记）
- 右栏：实时告警流 + 快捷操作按钮

**AdminGrading.vue（新增）**
- 4 个 StatCard
- Tab 切换（成绩总览/分数分布/人工阅卷/题目分析）
- 分数分布柱状图
- 成绩明细表（各列 ScoreBar）
- 阅卷面板：自动评分子分数、人工评分、评语、CodeBlock、提交元数据

## 文件清单

遵循现有项目惯例：页面组件直接放 `src/`，可复用 UI 组件放 `src/components/`。

```
frontend/src/
├── data/
│   ├── mockData.js              # 新增
│   └── api.js                   # 新增
├── components/
│   ├── StatCard.vue             # 新增
│   ├── StatusBadge.vue          # 新增
│   ├── ScoreBar.vue             # 新增
│   ├── FilterChip.vue           # 新增
│   ├── CircleProgress.vue       # 新增
│   ├── ProcessBar.vue           # 新增
│   ├── CodeBlock.vue            # 新增
│   ├── RatingCard.vue           # 新增
│   └── AdminLayout.vue          # 新增（B端侧边栏布局）
├── Solutions.vue                # 新增（题解广场）
├── Contest.vue                  # 新增（周度竞赛）
├── Leaderboard.vue              # 新增（排行榜）
├── AdminExamSessions.vue        # 新增（B端-考试管理）
├── AdminMonitor.vue             # 新增（B端-实时监控）
├── AdminGrading.vue             # 新增（B端-成绩阅卷）
├── Home.vue                     # 修改（增强挑战列表）
├── Completed.vue                # 修改（改造为评分报告）
├── NavBar.vue                   # 修改（加C端导航链接）
├── router.js                    # 修改（加路由）
└── App.vue                      # 修改（B端路由不显示 NavBar）
```

## 设计约束

- 颜色体系：主色 #4a6cf7，深底 #0f172a/#1e293b，文字 #1e293b/#334155/#64748b/#94a3b8/#f1f5f9
- 成功/警告/危险：#22c55e / #f59e0b / #ef4444
- 间距：统计卡片间距 16px，页面 padding 32px
- 圆角：卡片 10-12px，按钮 8-10px，badge 20px
- 所有组件 scoped CSS，无全局污染
