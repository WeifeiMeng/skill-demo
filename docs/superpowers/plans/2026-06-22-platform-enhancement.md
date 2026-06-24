# AI Done 平台功能增强实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 AI Done 平台新增 B端管理页面和 C端功能页面，增强现有页面，共 20+ 文件。

**Architecture:** Vue 3 Composition API + scoped CSS。页面组件放 `src/`，可复用组件放 `src/components/`，数据层 `src/data/`（mock + API 混合模式）。B端页面共用 AdminLayout。

**Tech Stack:** Vue 3, Vue Router, scoped CSS

---

### Task 1: 数据层 — mockData.js

**Files:** Create: `frontend/src/data/mockData.js`

All mock data factory functions. See design doc for full data structures. Key exports:
`getChallenges`, `getUserProfile`, `getUserActivities`, `getScoreReport`, `getSolutions`, `getContestData`, `getLeaderboard`, `getRatingTrend`, `getExamSessions`, `getExamStats`, `getMonitorData`, `getGradingData`

### Task 2: 数据层 — api.js

**Files:** Create: `frontend/src/data/api.js`

Unified API wrapper with mock fallback. Exports: `fetchChallenges`, `fetchProfile`, `fetchActivities`, `fetchScoreReport`, `fetchSolutions`, `fetchContestData`, `fetchLeaderboard`, `fetchRatingTrend`, `fetchExamSessions`, `fetchExamStats`, `fetchMonitorData`, `fetchGradingData`

Pattern: `async function fetchX() { try { res = await fetch(url); if (res.ok) return res.json() } catch {} return mockFallback() }`

### Task 3: StatCard 组件

**Files:** Create: `frontend/src/components/StatCard.vue`

Props: `label` (String), `value` (String|Number), `color` (String: blue/green/amber/red). White card with border, colored value text.

### Task 4: StatusBadge 组件

**Files:** Create: `frontend/src/components/StatusBadge.vue`

Props: `label` (String), `variant` (String). Variants: default/active/upcoming/ended/draft/pass/fail/pending/easy/medium/hard/solved/attempted/new. Colored pill badge.

### Task 5: ScoreBar 组件

**Files:** Create: `frontend/src/components/ScoreBar.vue`

Props: `score` (Number), `max` (Number, default 100). Horizontal bar with score number. Auto color: >=80 green, >=50 amber, <50 red.

### Task 6: FilterChip 组件

**Files:** Create: `frontend/src/components/FilterChip.vue`

Props: `label` (String), `modelValue` (Boolean). Emits: `update:modelValue`. Pill-shaped toggle chip with active state.

### Task 7: CircleProgress 组件

**Files:** Create: `frontend/src/components/CircleProgress.vue`

Props: `value` (Number), `max` (Number, default 100), `size` (Number, default 120). SVG circular progress. Color: >=80% green, >=50% amber, <50% red.

### Task 8: ProcessBar 组件

**Files:** Create: `frontend/src/components/ProcessBar.vue`

Props: `icon` (String), `label` (String), `score` (Number), `max` (Number, default 20). Label + score + gradient fill bar.

### Task 9: CodeBlock 组件

**Files:** Create: `frontend/src/components/CodeBlock.vue`

Props: `code` (String), `highlights` (Array of line numbers). Dark themed code display with line numbers. Highlighted lines get blue background.

### Task 10: RatingCard 组件

**Files:** Create: `frontend/src/components/RatingCard.vue`

Props: `rating` (Number), `rank` (Number), `total` (Number), `tierName` (String). Dark gradient card with large rating number. Has slot for right-side stats.

### Task 11: AdminLayout 组件

**Files:** Create: `frontend/src/components/AdminLayout.vue`

220px sidebar with nav links (考试场次/实时监控/成绩报告) + main content slot. White sidebar, light gray main area. Active nav state with blue right border.

### Task 12: Solutions.vue — 题解广场

**Files:** Create: `frontend/src/Solutions.vue`

Uses FilterChip, CodeBlock. Two-column solution card grid. Featured cards have gold border. Each card: problem name + difficulty, title, summary, code preview (dark bg with gradient fade), tags, author + stats. Detail modal: approach text, full CodeBlock, complexity analysis cards, pitfalls list, action buttons (like/star/comment).

### Task 13: Contest.vue — 周度竞赛

**Files:** Create: `frontend/src/Contest.vue`

Uses StatusBadge. Dark gradient hero banner with countdown timer (updates every second). Stats row (registered/problems/points/completion). Problems list with status left-border colors. Live ranking table top 5. History cards grid (3 columns).

### Task 14: Leaderboard.vue — 排行榜

**Files:** Create: `frontend/src/Leaderboard.vue`

Uses RatingCard. Rating card at top, tier legend (7 colors), rating trend bar chart (20 bars with hover), tab row (总排名/周榜/月榜/做题数/胜率), ranking table with: rank number (gold/silver/bronze for top 3), avatar + name + tier title, rating with change (+green/-red), contests count, win rate %, peak rating, recent result. Current user row highlighted. Pagination at bottom.

### Task 15: AdminExamSessions.vue — B端考试管理

**Files:** Create: `frontend/src/AdminExamSessions.vue`

Wraps in AdminLayout. Uses StatCard, StatusBadge. Stat row (total/active/upcoming/participants). Exam list table: name + ID, time window, question count, participants, status badge, pass rate, action buttons. Create exam modal with form: name, datetime range, duration, pass score, question tags (removable), whitelist input + CSV upload button, anti-cheat checkboxes. Cancel/save draft/publish buttons.

### Task 16: AdminMonitor.vue — B端实时监控

**Files:** Create: `frontend/src/AdminMonitor.vue`

Top info bar: exam name, active badge with pulse dot, online count, countdown timer. Three-column grid layout:
- Left (280px): mini stats (online/offline/submitted/alerts), question progress bars, container resource status dots.
- Center: candidate card grid with status indicator dots (online/idle/alert colors), current question, progress bar, time/submission meta. Alert cards have red border + pulse animation.
- Right (300px): real-time alert stream with time + text + action link. Quick action buttons (broadcast/extend time/export/audit log).

### Task 17: AdminGrading.vue — B端成绩阅卷

**Files:** Create: `frontend/src/AdminGrading.vue`

Wraps in AdminLayout. Uses StatCard, ScoreBar, StatusBadge, CodeBlock. Stat row, tab bar (成绩总览/分数分布/人工阅卷/题目分析). Score distribution bar chart. Student scores table: rank, name, per-question ScoreBar, total score, status badge, action button. Pending review rows highlighted. Grading panel: auto-score breakdown (3 sub-scores), manual score input, comment textarea, student CodeBlock with submission metadata (time/attempt count). Save draft/submit buttons.

### Task 18: Home.vue — 增强挑战列表

**Files:** Modify: `frontend/src/Home.vue`

Add above existing challenge grid: 4 StatCards row, FilterChip row (by difficulty + tag), search input. Enhance ArticleCard usage with difficulty badge component display. Add right sidebar or bottom section for recent activity list (pass/fail/start icons with time and result).

### Task 19: Completed.vue — 改造为评分报告

**Files:** Modify: `frontend/src/Completed.vue`

Replace simple "done" UI with full score report. Uses CircleProgress, ProcessBar, CodeBlock. Layout: large score number + grade badge, two-column detail grid (result score circle + process scores list), test case results list (pass/fail with name and message), CodeBlock showing submitted code, bottom stats bar (time/AI rounds/tokens/model/tab switches).

### Task 20: 路由与导航更新

**Files:** Modify: `frontend/src/router.js`, `frontend/src/NavBar.vue`, `frontend/src/App.vue`

**router.js**: Add routes: `/solutions` → Solutions, `/contest` → Contest, `/leaderboard` → Leaderboard, `/admin/exams` → AdminExamSessions, `/admin/monitor/:examId` → AdminMonitor, `/admin/grading/:examId` → AdminGrading.

**NavBar.vue**: Add C端 nav links between brand and actions: 首页, 题库, 我的考试, 题解广场, 竞赛, 排行榜. Active state for current route.

**App.vue**: Hide NavBar for B端 routes (`/admin/*`). Add B端 routes to `isLanding`-style check or create separate `isAdminRoute` computed.

### Task 21: 验证所有页面

- [ ] Run `cd frontend && npm run dev` and verify all routes load without errors
- [ ] Check C端 pages: /challenges, /solutions, /contest, /leaderboard
- [ ] Check B端 pages: /admin/exams, /admin/monitor/test, /admin/grading/test
- [ ] Check enhanced pages: /completed/advanced-short-url
- [ ] Verify NavBar links work and active state shows correctly
- [ ] Verify B端 pages hide NavBar and show AdminLayout sidebar
