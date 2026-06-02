# Admin Dashboard Design Spec

## Overview

为 Coding Coach 平台添加管理后台功能。独立前端项目 `frontend-admin/`，共用后端 API。管理员可以管理题目、查看考生答题数据。

## Visual Style

深色侧边栏 + 浅灰内容区，专业数据面板风格。
- 侧边栏：深色背景 `#0f172a`，白色文字，选中项蓝色高亮
- 内容区：浅灰背景 `#f1f5f9`，白色卡片
- 强调色：蓝色系 `#4a6cf7`

## Database Changes

### users 表加 role 字段
```sql
ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user';
-- 值: 'user' | 'admin'
-- 手动将管理员账号设为 'admin'（首次通过 SQL 直接插入或更新）
```

### 新建 exam_results 表
```sql
CREATE TABLE exam_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    article_name VARCHAR(255) NOT NULL,
    score INT DEFAULT 0,
    max_score INT DEFAULT 100,
    passed BOOLEAN DEFAULT FALSE,
    cases_json TEXT,
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## Article Directory Structure

每个题目文件夹扩展为：
```
articles/<name>/
  readme.md           # 题目描述（markdown）
  test_config.json    # 测试用例配置
  attachments/        # 附件文件
    ...
```

### test_config.json 结构
```json
{
  "test_command": "python test.py",
  "max_score": 100,
  "cases": [
    { "name": "基础功能", "score": 30 },
    { "name": "边界条件", "score": 30 },
    { "name": "性能测试", "score": 40 }
  ]
}
```

## API Design

所有管理 API 在 `/admin` 前缀下，需要 admin 角色认证（通过 JWT 中 role=admin 校验）。

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/admin/login` | 管理员登录，校验 role=admin |
| GET | `/admin/dashboard` | 总览：总考生数、总通过率、题目数、每题通过率 |
| GET | `/admin/articles` | 题目列表（含 test_config） |
| POST | `/admin/articles` | 新建题目（创建文件夹 + readme.md + test_config.json） |
| PUT | `/admin/articles/{name}` | 更新 readme.md 和 test_config.json |
| DELETE | `/admin/articles/{name}` | 删除题目文件夹 |
| POST | `/admin/articles/{name}/attachments` | 上传附件到 attachments/ |
| DELETE | `/admin/articles/{name}/attachments/{filename}` | 删除附件 |
| GET | `/admin/students` | 考生列表，每人包含完成题数、通过率 |
| GET | `/admin/students/{user_id}` | 考生详情：各题目答题次数、最高分、最近提交详情 |

### Admin JWT 认证

在现有 JWT payload 中加入 `role` 字段。新建 `dependencies.py` 中的 `get_admin_user` 依赖，校验 `role == 'admin'`。

### 题目提交时写入 exam_results

修改 `route/exam.py` 的 `submit_exam` 端点，提交成功后同时写入 `exam_results` 表，保存本次得分、通过状态和测试用例详细结果（cases_json）。

## Frontend Structure

独立 Vite + Vue 3 项目 `frontend-admin/`，运行在 `localhost:3001`。

```
frontend-admin/
  index.html
  package.json
  vite.config.js
  src/
    main.js
    App.vue              # 深色侧边栏 + router-view
    router.js
    style.css
    views/
      Login.vue          # 管理员登录
      Dashboard.vue      # 仪表盘（统计卡片 + 通过率条形图）
      ArticleList.vue    # 题目列表（表格 + 操作按钮）
      ArticleEdit.vue    # 新建/编辑题目（Tab 切换）
      StudentList.vue    # 考生列表（统计数据 + 表格）
      StudentDetail.vue  # 考生详情（汇总 + 答题记录 + 下钻用例结果）
    components/
      Sidebar.vue        # 侧边栏导航
      StatCard.vue       # 统计数字卡片
      TestCaseEditor.vue # 测试用例编辑器（在 ArticleEdit Tab 内）
      AttachmentList.vue # 附件列表（在 ArticleEdit Tab 内）
```

## Routes

| 路径 | 组件 | 说明 |
|------|------|------|
| `/login` | Login | 管理员登录页 |
| `/dashboard` | Dashboard | 仪表盘首页 |
| `/articles` | ArticleList | 题目管理列表 |
| `/articles/new` | ArticleEdit | 新建题目 |
| `/articles/:name/edit` | ArticleEdit | 编辑题目 |
| `/students` | StudentList | 考生列表 |
| `/students/:id` | StudentDetail | 考生详情 |

所有路由（除 `/login`）需要登录守卫，检查 token 存在。

## Key Interactions

### ArticleEdit（题目编辑器）
- Tab 1 "Markdown"：textarea 编辑 markdown 内容，保存时写入 readme.md
- Tab 2 "测试用例"：TestCaseEditor 组件，动态添加/删除/编辑测试用例（name + score），保存时写入 test_config.json
- Tab 3 "附件"：AttachmentList 组件，显示已有附件，支持上传新文件和删除已有文件

### Dashboard（仪表盘）
- 3 张 StatCard：总考生数、总通过率、题目数
- 每题通过率条形图：纯 CSS 实现，不引入图表库

### StudentList（考生列表）
- 顶部统计行：总考生、已通过、未通过
- 表格列：姓名、邮箱、完成题数、通过率、详情链接

### StudentDetail（考生详情）
- 汇总卡片：完成题目数、总通过率、平均得分
- 答题记录表：每题展示提交次数、最高分、通过状态，可展开最近一次提交的测试用例得分明细

## CORS Update

`backend/main.py` 中添加 `http://localhost:3001` 到 CORS allow_origins。

## Out of Scope

- 管理员注册页面（首次管理员通过数据库手动创建）
- 富文本 markdown 编辑器（先用 textarea）
- 图表库（先用纯 CSS 条形图）
- 分页（数据量小时全量返回）
