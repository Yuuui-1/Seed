# Spec: Seed — AI 人才优势测评与报告生成系统

> **版本**: v2.0（Grill 决策版）  
> **状态**: 已定稿，待冻结边界  
> **冻结范围**: 技术栈 · 接口格式 · 数据模型 · 目录结构 · 鉴权方案 · 题库方案 · 计分算法

---

## 一、产品概述

### 1.1 一句话定义

**Seed** — 基于科学量表 + Claude Agent SDK 自适应选题的人才优势测评工具。18-36 道选择题完成六维能力建模，生成含证据链的可分享报告。

### 1.2 与 Coze 原版的核心差异

| 维度 | Coze 原版 | Seed VibeCoding 版 |
|------|----------|-------------------|
| 题目来源 | AI 生成，不可控 | 改编 Big Five/RIASEC/Grit/SDT/NFC 经典量表，固定题库 60-80 题 |
| AI 职责 | 出题 + 分析（黑盒） | 自适应选题 + 加权计分 + 个性化解读（透明可审计） |
| 题型 | 开放题，回答负担重 | 5 级 Likert 选择题，作答快 |
| 计分 | 不可解释 | 维度加权 + 置信度区间，每题标注出处权重 |
| 报告 | 纯文本 | 雷达图 + 维度卡片 + 证据链引用 |
| 部署 | Coze 平台内 | 全栈自建，Vercel + Railway，移动优先 PWA |

### 1.3 核心流程（含注册漏斗）

```
进入首页 → 开始测评（无需注册）
    → 作答前 3 题 → 预览 1 个维度分数
    → 注册/登录 → 继续做完整套题（18-36题，自适应控制）
    → Claude Agent 分析引擎（六维建模 + 置信度计算）
    → 生成报告（雷达图 + 各维度卡片 + 证据链 + 职业建议）
    → 分享链接（底部裂变入口） / 历史记录
```

### 1.4 目标用户

| 用户类型 | 场景 | 痛点 |
|---------|------|------|
| 在校大学生（核心） | 职业规划迷茫，选专业/找实习 | 不了解自己优势，缺乏客观评估 |
| 职场新人（1-3年） | 考虑转行或跳槽 | 不确定长期方向是否适合自己 |
| 自我探索者 | 想系统认识自己的行为模式 | MBTI/星座缺乏科学深度 |

---

## 二、技术栈（冻结）

| 层 | 选型 | 版本 |
|----|------|------|
| 前端框架 | Vue 3 + Vite + PWA | Vue 3.4+, Vite 5+, vite-plugin-pwa |
| 前端语言 | TypeScript | 5.x |
| CSS 方案 | TailwindCSS | 3.x |
| 图表库 | ECharts | 5.x（雷达图） |
| 路由 | Vue Router | 4.x |
| 状态管理 | Pinia | 2.x |
| HTTP 客户端 | Axios | 1.x |
| 后端框架 | FastAPI | 0.111+ |
| 后端语言 | Python | 3.11+ |
| ORM | SQLAlchemy | 2.0+ |
| 数据校验 | Pydantic | v2 |
| 数据库迁移 | Alembic | 1.13+ |
| 数据库 | PostgreSQL | 16 |
| 缓存 | Redis | 7.x |
| AI SDK | OpenAI Python SDK | 1.x（兼容任意 OpenAI 格式 API） |
| AI 编排 | Claude Agent SDK (Anthropic) | latest（开源版） |
| 容器化 | Docker + docker-compose | - |
| 测试 | pytest + vitest | - |

---

## 三、目录结构（冻结）

```
/ai-talent-assessment
├── frontend/
│   ├── src/
│   │   ├── api/                  # API 调用层（统一封装 axios）
│   │   │   ├── client.ts         # axios 实例 + 拦截器
│   │   │   ├── auth.ts           # 认证接口
│   │   │   ├── assessment.ts     # 测评接口
│   │   │   └── report.ts         # 报告接口
│   │   ├── components/           # 通用组件
│   │   │   ├── layout/           # 布局组件
│   │   │   ├── common/           # 通用 UI 组件
│   │   │   └── chat/             # 对话组件
│   │   ├── composables/          # 组合式函数
│   │   ├── router/               # 路由配置
│   │   │   └── index.ts
│   │   ├── stores/               # Pinia 状态管理
│   │   │   ├── auth.ts
│   │   │   └── assessment.ts
│   │   ├── types/                # TypeScript 类型定义
│   │   ├── utils/                # 工具函数
│   │   ├── views/                # 页面视图
│   │   │   ├── HomeView.vue
│   │   │   ├── LoginView.vue
│   │   │   ├── RegisterView.vue
│   │   │   ├── AssessmentView.vue
│   │   │   ├── ReportView.vue
│   │   │   └── HistoryView.vue
│   │   ├── App.vue
│   │   └── main.ts
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   └── vitest.config.ts
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── endpoints/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── auth.py
│   │   │       │   ├── assessment.py
│   │   │       │   ├── report.py
│   │   │       │   └── user.py
│   │   │       └── router.py     # 注册所有路由
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py         # 环境变量配置
│   │   │   ├── security.py       # JWT 生成/校验
│   │   │   └── deps.py           # 依赖注入（get_db, get_current_user）
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── base.py           # SQLAlchemy Base
│   │   │   └── session.py        # 数据库会话
│   │   ├── models/               # SQLAlchemy 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── assessment.py
│   │   │   ├── report.py
│   │   │   └── share_link.py
│   │   ├── schemas/              # Pydantic 请求/响应模型
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── assessment.py
│   │   │   ├── report.py
│   │   │   └── common.py         # 统一响应格式
│   │   ├── services/             # 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── assessment_service.py
│   │   │   ├── report_service.py
│   │   │   └── user_service.py
│   │   ├── agents/               # Claude Agent SDK 编排层
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator.py    # AssessmentAgent 主编排器
│   │   │   ├── analysis_agent.py  # Analysis & Report Agent
│   │   │   ├── tools/             # Tool 定义（@tool 装饰器）
│   │   │   │   ├── __init__.py
│   │   │   │   ├── ask_question.py
│   │   │   │   ├── evaluate_question.py
│   │   │   │   ├── check_coverage.py
│   │   │   │   ├── score_dimension.py
│   │   │   │   ├── generate_report.py
│   │   │   │   └── career_suggestions.py
│   │   │   ├── prompts.py         # System Prompt 模板
│   │   │   └── sandbox.py         # 沙箱计算（归一化/异常检测）
│   │   ├── middlewares/
│   │   │   ├── __init__.py
│   │   │   ├── auth_middleware.py
│   │   │   └── error_handler.py
│   │   └── main.py               # FastAPI 入口
│   ├── alembic/
│   │   ├── versions/
│   │   └── env.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_assessment.py
│   │   ├── test_report.py
│   │   └── test_agents.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── data/
│   │   └── questions.json          # 题库（60-80 题）
│   └── .env.example
├── docs/
│   ├── PRD.md                    # 完整产品需求文档
│   ├── spec.md                   # 本文件（技术规格说明书）
│   └── contract.md               # 接口契约（待冻结边界阶段生成）
├── .cursorrules                  # AI 行为约束（工程基线阶段生成）
├── docker-compose.yml
├── .gitignore
├── README.md
└── LICENSE
```

---

## 四、接口统一格式（冻结）

### 4.1 响应结构

所有接口统一返回以下 JSON 结构：

```json
{
  "code": 0,
  "data": {},
  "msg": "success"
}
```

### 4.2 错误码定义

| code | 含义 | 场景 |
|------|------|------|
| 0 | 成功 | 正常返回 |
| 1001 | 参数校验失败 | Pydantic 校验不通过 |
| 1002 | 认证失败 | Token 无效/过期/未登录 |
| 1003 | 资源不存在 | 测评/报告 ID 找不到 |
| 1004 | 权限不足 | 访问他人私有数据 |
| 1005 | 重复操作 | 已完成的测评不可再答 |
| 2001 | AI 服务异常 | LLM API 超时/返回异常 |
| 2002 | AI 输出格式错误 | LLM 返回不符合预期 JSON |
| 5000 | 服务器内部错误 | 未预期的异常 |

### 4.3 分页响应格式

```json
{
  "code": 0,
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "page_size": 20
  },
  "msg": "success"
}
```

---

## 五、接口定义（冻结）

### 5.1 认证模块

#### POST /api/v1/auth/register

```yaml
请求:
  body:
    email: string       # 邮箱
    password: string    # 密码（8-32位）
    nickname: string    # 昵称（2-20字符）

响应:
  code: 0
  data:
    user:
      id: int
      email: string
      nickname: string
    access_token: string
    refresh_token: string
```

#### POST /api/v1/auth/login

```yaml
请求:
  body:
    email: string
    password: string

响应:
  code: 0
  data:
    user:
      id: int
      email: string
      nickname: string
    access_token: string
    refresh_token: string
```

#### POST /api/v1/auth/refresh

```yaml
请求:
  body:
    refresh_token: string

响应:
  code: 0
  data:
    access_token: string
    refresh_token: string
```

#### POST /api/v1/auth/logout

```yaml
请求:
  header: Authorization: Bearer {access_token}

响应:
  code: 0
  data: null
```

#### GET /api/v1/auth/me

```yaml
请求:
  header: Authorization: Bearer {access_token}

响应:
  code: 0
  data:
    id: int
    email: string
    nickname: string
    created_at: string
```

### 5.2 测评模块

#### POST /api/v1/assessment/start

```yaml
描述: 开始一次新测评，返回第一道题（SSE 流式输出）

请求:
  header: Authorization: Bearer {access_token}

响应（SSE 流）:
  event: start
  data: {"assessment_id": 1, "total_rounds": 10}

  event: question
  data: {"round": 1, "question": "当面对一个没有明确指南的复杂项目时，你通常会如何开展？", "question_id": 1}
```

#### POST /api/v1/assessment/{assessment_id}/answer

```yaml
描述: 提交当前轮答案，返回下一道题或完成提示（SSE 流式输出）

请求:
  header: Authorization: Bearer {access_token}
  path: assessment_id: int
  body:
    question_id: int
    answer: string

响应（SSE 流）:
  # 如果还有下一题:
  event: question
  data: {"round": 2, "question": "在团队合作中，你更倾向于扮演什么角色？为什么？", "question_id": 2}

  # 如果全部完成:
  event: complete
  data: {"assessment_id": 1, "message": "测评已完成，正在生成报告..."}
```

#### GET /api/v1/assessment/{assessment_id}/progress

```yaml
描述: 获取当前测评进度

请求:
  header: Authorization: Bearer {access_token}
  path: assessment_id: int

响应:
  code: 0
  data:
    assessment_id: int
    status: string            # "in_progress" | "completed"
    current_round: int
    total_rounds: int
    started_at: string
```

### 5.3 报告模块

#### GET /api/v1/reports

```yaml
描述: 获取当前用户的报告列表

请求:
  header: Authorization: Bearer {access_token}
  query:
    page: int (default: 1)
    page_size: int (default: 20)

响应:
  code: 0
  data:
    items:
      - id: int
        created_at: string
        dimensions:           # 六维摘要
          thinking: {score: 85, label: "思维力"}
          creativity: {score: 72, label: "创造力"}
          execution: {score: 68, label: "执行力"}
          social: {score: 90, label: "社交力"}
          emotional: {score: 75, label: "情绪力"}
          drive: {score: 80, label: "驱动力"}
    total: int
    page: int
    page_size: int
```

#### GET /api/v1/reports/{report_id}

```yaml
描述: 获取完整报告详情（含文字解读）

请求:
  header: Authorization: Bearer {access_token}
  path: report_id: int

响应:
  code: 0
  data:
    id: int
    assessment_id: int
    dimensions:
      thinking:
        score: int          # 0-100
        label: string
        strengths: string   # 优势描述
        areas_for_improvement: string  # 发展建议
        description: string # 详细解读
      creativity: {同上}
      execution: {同上}
      social: {同上}
      emotional: {同上}
      drive: {同上}
    summary: string         # 总体评价
    career_suggestions: string[]  # 职业方向建议
    created_at: string
```

#### POST /api/v1/reports/{report_id}/share

```yaml
描述: 生成分享链接

请求:
  header: Authorization: Bearer {access_token}
  path: report_id: int

响应:
  code: 0
  data:
    share_url: string      # 如 "/share/abc123"
    expires_at: string
```

#### GET /api/v1/reports/shared/{token}

```yaml
描述: 通过分享链接查看报告（无需登录）

请求:
  path: token: string

响应:
  code: 0
  data:
    # 同 GET /api/v1/reports/{report_id} 的 data
```

---

## 六、数据模型（冻结）

### User

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 用户 ID |
| email | VARCHAR(255) | UNIQUE, NOT NULL | 邮箱 |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt 哈希 |
| nickname | VARCHAR(50) | NOT NULL | 昵称 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 注册时间 |
| updated_at | TIMESTAMP | NOT NULL | 更新时间 |

### Assessment

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 测评 ID |
| user_id | BIGINT | FK → User.id, NOT NULL | 用户 ID |
| status | VARCHAR(20) | NOT NULL | in_progress / completed / abandoned |
| current_round | INT | NOT NULL, DEFAULT 0 | 当前轮次 |
| total_rounds | INT | NOT NULL | 总轮次（8-12） |
| started_at | TIMESTAMP | NOT NULL | 开始时间 |
| completed_at | TIMESTAMP | NULL | 完成时间 |

### AssessmentAnswer

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 回答 ID |
| assessment_id | BIGINT | FK → Assessment.id, NOT NULL | 测评 ID |
| round_number | INT | NOT NULL | 第几轮 |
| question | TEXT | NOT NULL | 题目内容 |
| answer | TEXT | NOT NULL | 用户回答 |
| created_at | TIMESTAMP | NOT NULL | 回答时间 |

### Report

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 报告 ID |
| user_id | BIGINT | FK → User.id, NOT NULL | 用户 ID |
| assessment_id | BIGINT | FK → Assessment.id, UNIQUE, NOT NULL | 关联测评 |
| dimensions | JSONB | NOT NULL | 六维数据（见下方结构） |
| summary | TEXT | NOT NULL | 总体评价 |
| career_suggestions | JSONB | NOT NULL | 职业建议列表 |
| created_at | TIMESTAMP | NOT NULL | 生成时间 |

**dimensions JSONB 结构:**

```json
{
  "thinking": {
    "score": 85,
    "label": "思维力",
    "strengths": "你善于系统性地分析复杂问题...",
    "areas_for_improvement": "可以尝试更多跨领域思考...",
    "description": "思维力反映了你的逻辑推理和问题解决能力..."
  },
  "creativity": { "同上" },
  "execution": { "同上" },
  "social": { "同上" },
  "emotional": { "同上" },
  "drive": { "同上" }
}
```

### ShareLink

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 分享 ID |
| report_id | BIGINT | FK → Report.id, NOT NULL | 报告 ID |
| token | VARCHAR(64) | UNIQUE, NOT NULL | 分享 token |
| expires_at | TIMESTAMP | NOT NULL | 过期时间 |
| created_at | TIMESTAMP | NOT NULL | 创建时间 |

---

## 七、鉴权方案（冻结）

| 项目 | 方案 |
|------|------|
| 认证方式 | JWT（JSON Web Token） |
| Token 类型 | Access Token + Refresh Token |
| Access Token 有效期 | 30 分钟 |
| Refresh Token 有效期 | 7 天 |
| Access Token 存储 | 前端 localStorage（或 httpOnly Cookie，待定） |
| Refresh Token 存储 | 前端 localStorage |
| 传输方式 | HTTP Header: `Authorization: Bearer {access_token}` |
| 刷新策略 | Access Token 过期后，前端用 Refresh Token 调 /auth/refresh 获取新 Token |
| 登出策略 | 前端清除 Token；后端将 Refresh Token 加入 Redis 黑名单（TTL = 剩余有效期） |
| 密码加密 | bcrypt |
| 鉴权中间件 | FastAPI Depends 注入，校验 Token 有效性 + 提取用户信息 |

---

## 八、AI Agent 架构 —— Claude Agent SDK（冻结）

### 8.0 为什么选 Claude Agent SDK

| 方案 | 问题 |
|------|------|
| Coze（原版） | 无代码编排，黑盒，不可控，面试官无感 |
| 裸调 LLM API | 无工具调用、无沙箱、无状态管理，工程深度不够 |
| LangGraph | 状态图概念重、调试困难、社区小 |
| **Claude Agent SDK** | Anthropic 官方出品，工具调用+沙箱+开源，2025 最热 AI 工程框架 |

### 8.1 系统架构

```
┌────────────────────────────────────────┐
│          Claude Agent SDK              │
│                                        │
│  ┌──────────────────────────────────┐  │
│  │     Assessment Orchestrator      │  │
│  │   (主 Agent，编排整个测评流)       │  │
│  │                                  │  │
│  │  System Prompt:                  │  │
│  │  "你是人才测评专家。通过对话挖掘   │  │
│  │   用户六维优势，每轮问1题，         │  │
│  │   动态调整追问策略..."             │  │
│  │                                  │  │
│  │  Tools:                          │  │
│  │  ┌────────────────────────────┐  │  │
│  │  │ ask_next_question()        │  │  │
│  │  │ 根据对话历史+已覆盖维度     │  │  │
│  │  │ 生成下一道测评题           │  │  │
│  │  ├────────────────────────────┤  │  │
│  │  │ evaluate_question(q)       │  │  │
│  │  │ 质检题目：重复度/清晰度     │  │  │
│  │  │ /诱导性 → 打分+修改建议    │  │  │
│  │  ├────────────────────────────┤  │  │
│  │  │ check_coverage()           │  │  │
│  │  │ 检查六维覆盖情况，返回      │  │  │
│  │  │ 缺失维度列表               │  │  │
│  │  ├────────────────────────────┤  │  │
│  │  │ record_answer(q, a, round) │  │  │
│  │  │ 持久化问答对到DB            │  │  │
│  │  └────────────────────────────┘  │  │
│  └──────────────────────────────────┘  │
│                                        │
│  ┌──────────────────────────────────┐  │
│  │     Analysis & Report Agent      │  │
│  │   (分析+报告，测评完成后触发)      │  │
│  │                                  │  │
│  │  Tools:                          │  │
│  │  ┌────────────────────────────┐  │  │
│  │  │ score_dimension(           │  │  │
│  │  │   name, qa_pairs)          │  │  │
│  │  │ 对单个维度评分+提取证据     │  │  │
│  │  ├────────────────────────────┤  │  │
│  │  │ generate_dimension_report( │  │  │
│  │  │   name, score, evidence)   │  │  │
│  │  │ 生成单维度文字解读          │  │  │
│  │  ├────────────────────────────┤  │  │
│  │  │ generate_career_suggestions│  │  │
│  │  │ (profile)                  │  │  │
│  │  │ 根据能力画像推荐职业方向    │  │  │
│  │  ├────────────────────────────┤  │  │
│  │  │ save_report(user_id, data) │  │  │
│  │  │ 写入 Report 表             │  │  │
│  │  └────────────────────────────┘  │  │
│  │                                  │  │
│  │  Sandbox:                        │  │
│  │  ┌────────────────────────────┐  │  │
│  │  │ 六维雷达图数据计算          │  │  │
│  │  │ 归一化/加权/异常检测        │  │  │
│  │  │ → Python 沙箱安全执行       │  │  │
│  │  └────────────────────────────┘  │  │
│  └──────────────────────────────────┘  │
│                                        │
│  ┌──────────────────────────────────┐  │
│  │  Context Window Management       │  │
│  │  会话上下文压缩 + 关键信息摘要     │  │
│  │  避免多轮对话爆 token             │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘
```

### 8.2 Tool 定义（核心）

```python
# Tool 1: 出题
@tool
async def ask_next_question(
    conversation_history: list[dict],
    covered_dimensions: list[str],
    current_round: int,
    max_rounds: int,
) -> dict:
    """
    根据对话历史和维度覆盖情况，生成下一道测评题。
    优先探测未覆盖维度，题目必须有情境感（避免抽象提问）。
    返回: {"question": str, "target_dimension": str, "question_type": str}
    """

# Tool 2: 题目质检
@tool
async def evaluate_question(question: str, existing_questions: list[str]) -> dict:
    """
    质检题目质量。检查：是否与历史题目重复？是否过于抽象？
    是否带有引导性（暗示"正确答案"）？
    返回: {"passed": bool, "score": float, "suggestions": str}
    """

# Tool 3: 维度覆盖检查
@tool
async def check_coverage(covered_dimensions: list[str]) -> dict:
    """
    检查六维覆盖情况，返回缺失维度 + 建议追问策略。
    返回: {"missing": list[str], "sufficient": bool, "strategy": str}
    """

# Tool 4: 单维度评分
@tool
async def score_dimension(dimension_name: str, qa_pairs: list[dict]) -> dict:
    """
    对单个维度评分(0-100)，必须引用用户原话作为证据。
    返回: {"score": int, "evidence": list[str], "reasoning": str}
    """

# Tool 5: 报告生成
@tool
async def generate_dimension_report(
    dimension_name: str, score: int, evidence: list[str]
) -> dict:
    """
    生成单维度文字解读：优势、发展建议、详细描述。
    返回: {"strengths": str, "areas_for_improvement": str, "description": str}
    """
```

### 8.3 Agent 编排流程

```
用户点击"开始测评"
    ↓
┌─ AssessmentAgent.start() ────────────────────────┐
│                                                   │
│  loop (until coverage sufficient or max_rounds):  │
│    ├─ ask_next_question()       # 出题            │
│    ├─ evaluate_question()       # 质检            │
│    ├─ [if failed] → 重出题 (max 3 retries)       │
│    ├─ [if passed] → 返回题目给用户               │
│    ├─ WAIT for user answer                        │
│    ├─ record_answer()           # 存储回答        │
│    └─ check_coverage()          # 检查覆盖度      │
│                                                   │
└───────────────────────────────────────────────────┘
    ↓ 测评完成
┌─ AnalysisAgent.start(assessment_id) ─────────────┐
│                                                   │
│  并行处理（6个维度同时评分）:                       │
│    ├─ score_dimension("thinking", qa_pairs)       │
│    ├─ score_dimension("creativity", qa_pairs)     │
│    ├─ score_dimension("execution", qa_pairs)      │
│    ├─ score_dimension("social", qa_pairs)         │
│    ├─ score_dimension("emotional", qa_pairs)      │
│    └─ score_dimension("drive", qa_pairs)          │
│                                                   │
│  沙箱计算:                                        │
│    ├─ 归一化处理                                   │
│    ├─ 异常值检测                                   │
│    └─ 六维雷达图数据生成                           │
│                                                   │
└───────────────────────────────────────────────────┘
    ↓
┌─ ReportAgent.start(scores) ──────────────────────┐
│                                                   │
│  并行生成（6个维度文字解读）:                       │
│    ├─ generate_dimension_report("thinking",...)   │
│    ├─ generate_dimension_report("creativity",...) │
│    └─ ...                                         │
│                                                   │
│  汇总:                                            │
│    ├─ generate_career_suggestions(profile)        │
│    └─ save_report(user_id, data)                  │
│                                                   │
└───────────────────────────────────────────────────┘
    ↓
返回报告给用户
```

### 8.4 LLM 配置

| 参数 | 值 |
|------|-----|
| 默认模型 | claude-sonnet-4-20250514 |
| 备选模型 | deepseek-chat（兼容 OpenAI API 格式切换） |
| Temperature | AssessmentAgent: 0.8, AnalysisAgent: 0.3, ReportAgent: 0.5 |
| Max Tokens | ask_question: 256, evaluate: 128, score: 1024, report: 2048 |
| Tool choice | auto（Agent 自主决定调用时机） |

### 8.5 沙箱使用场景

| 场景 | 沙箱内操作 | 安全收益 |
|------|-----------|---------|
| 六维评分归一化 | 6 个原始分数 → 0-100 标准化 | 避免 LLM 直接操作数值导致的计算错误 |
| 异常检测 | 识别用户全部回答为"I don't know"等无效输入 | 拒绝生成虚假报告 |
| 雷达图数据 | 计算 ECharts 所需的坐标点 | 精确数值计算 |

### 8.6 Prompt 管理

- 所有 Prompt 和 Tool Description 存放在 `backend/app/agents/tools/` 目录
- 每个 Tool 自描述（docstring 即 prompt，Agent SDK 自动读取）
- System Prompt 定义 Agent 角色+行为约束+输出规范
- 测评结束后上下文摘要压缩，避免 token 累积

---

## 九、模块拆分（迭代顺序）

| 模块 | 名称 | 产出 | 预估时间 |
|------|------|------|---------|
| M0 | 项目脚手架 + Docker 环境 | 项目启动、前后端可运行 | 0.5 天 |
| M1 | 数据库模型 + Alembic 迁移 | 建表脚本、初始迁移 | 0.5 天 |
| M2 | 认证系统（注册/登录/JWT） | 5 个认证接口 + 鉴权中间件 | 1 天 |
| M3 | 测评引擎（开始/答题/进度） | 3 个测评接口 + SSE 流式 | 1 天 |
| M4 | AI Agent 编排 | 3 个 Agent + Prompt 模板 | 1.5 天 |
| M5 | 报告生成 + 分享 | 4 个报告接口 | 1 天 |
| M6 | 前端 - 项目初始化 + 路由 + 布局 | 前端架子 + 路由守卫 | 0.5 天 |
| M7 | 前端 - 认证页面 | 登录/注册页 | 0.5 天 |
| M8 | 前端 - 测评对话 | 对话界面 + SSE 流式渲染 | 1 天 |
| M9 | 前端 - 报告展示 | 雷达图 + 文字报告页 | 1 天 |
| M10 | 前端 - 历史记录 + 分享页 | 列表页 + 分享查看页 | 0.5 天 |
| M11 | 联调 + 测试 + 部署 | 全流程测试 + docker-compose 部署 | 1 天 |

---

## 十、测试策略

| 类型 | 工具 | 覆盖要求 |
|------|------|---------|
| 后端单元测试 | pytest | 所有 Service 层函数 |
| 后端接口测试 | pytest + httpx | 所有 API 端点（含鉴权/异常分支） |
| 后端 Agent 测试 | pytest | Mock LLM 返回，验证 Agent 输出格式 |
| 前端单元测试 | vitest | 关键 composables 和工具函数 |
| 前端组件测试 | vitest + @vue/test-utils | 核心组件渲染验证 |

### 测试文件命名规范

- 后端: `test_{模块名}.py`（如 `test_auth.py`, `test_assessment.py`）
- 前端: `{组件名}.spec.ts`（如 `AssessmentChat.spec.ts`）

---

## 十一、分支策略

- `main` — 生产就绪代码，合并前通过全部测试
- `dev` — 开发分支
- `feature/m{编号}-{描述}` — 功能分支（如 `feature/m1-db-models`）
- 每个模块完成后打 tag: `v0.{模块号}`（如 `v0.1`, `v0.2`）
- 出问题时回滚到上一个 tag

---

## 十二、六维能力模型理论依据（冻结）

> 每个维度综合参考多项经典理论，不做单一体系对标。

| 维度 | 英文名 | 定义 | 理论参考 |
|------|--------|------|---------|
| **思维力** | Thinking | 逻辑推理、系统分析、问题拆解与抽象思维 | Raven 推理理论、认知需求量表(NFC) |
| **创造力** | Creativity | 发散思维、联想能力、对新事物的开放态度 | Guilford 发散思维、Torrance TTCT、Big Five-开放性 |
| **执行力** | Execution | 目标导向、自律、计划执行与复盘能力 | Grit 坚毅量表、大五人格-尽责性、自我调节理论 |
| **社交力** | Social | 沟通表达、共情理解、团队协作与影响力 | Goleman 情绪智力模型、社会认知理论 |
| **情绪力** | Emotional | 情绪觉察、压力管理、逆境反弹与稳定性 | MSCEIT 情绪智力、大五人格-神经质（反向）、心理韧性量表 |
| **驱动力** | Drive | 内在动机、成就渴望、自主性与目标感 | 自我决定理论(SDT)、McClelland 成就动机 |

> PRD 中需展开每个维度的详细定义、评分锚点、典型行为描述。

---

## 十三、题库设计（冻结）

### 13.1 题目来源

| 来源量表 | 改编题数 | 映射维度 |
|----------|---------|---------|
| 大五人格 IPIP-50 | 20-25 题 | 社交力、情绪力、执行力、创造力 |
| RIASEC 职业兴趣量表 | 10-12 题 | 驱动力、创造力 |
| Grit 坚毅量表(Short Grit Scale) | 8 题 | 执行力、驱动力 |
| SDT 自我决定量表 | 8-10 题 | 驱动力 |
| 认知需求量表(NFC) | 6-8 题 | 思维力 |
| 自编情境题 | 10-15 题 | 全部六维 |

**总题库**: 62-78 题

### 13.2 题目格式

```json
{
  "id": "q_001",
  "dimension": "thinking",
  "text": "面对一个复杂问题，我习惯先拆解成小部分再逐一解决",
  "options": [
    {"value": 1, "label": "非常不符合"},
    {"value": 2, "label": "不太符合"},
    {"value": 3, "label": "一般"},
    {"value": 4, "label": "比较符合"},
    {"value": 5, "label": "非常符合"}
  ],
  "reverse_scored": false,
  "source": "NFC #Q04 adapted",
  "weight": 0.9
}
```

- `reverse_scored: true` 表示反向计分（用于情绪力等负向题）
- `weight`: 改编自经典量表的题权重高（0.9-1.0），自编情境题权重低（0.7）

### 13.3 存储方案

- 题库以 JSON 文件存储在 `backend/app/data/questions.json`
- Git 版本化管理，每次修改可审计
- Agent 启动时读入内存，选题逻辑在 Python 层

---

## 十四、计分算法（冻结）

### 14.1 自适应选题策略

```
Phase 1 - 轮巡基线（前 6 题）:
  每个维度轮流各出 1 题，建立初始基线

Phase 2 - 加权追问（第 7 题起）:
  计算每个维度的:
    - 当前标准差（离散度）
    - 置信度 = 1 - 标准差/满分
  对置信度 < 0.85 的维度加权多出题

Phase 3 - 收束:
  任一维度满足以下条件之一即收束:
    - 置信度 >= 0.85（已答 4+ 题且结果高度一致）
    - 该维度已答 >= 8 题（防止过度追问）
  全部六维收束 → 测评完成

终止条件: 总题量 18-36 题（灵活区间）
```

### 14.2 维度评分公式

```
dimension_score = Σ(answer_value × question_weight) / Σ(question_weight)
                   × 20  (映射到 0-100)
```

- 反向题自动 6 - answer_value 转换
- 置信区间 = score ± (1 - 置信度) × 15

### 14.3 AI 职责边界

| 职责 | 谁来做 | 说明 |
|------|--------|------|
| 出题 | ❌ 不是 AI | 题库固定，AI 不生成题目 |
| 选题 | ✅ Claude Agent | 自适应从题库中选取下一题 |
| 计分 | ✅ 沙箱执行 | 确定性算法，不依赖 LLM |
| 置信度计算 | ✅ 沙箱执行 | 统计学计算 |
| 维度文字解读 | ✅ Claude Agent | AI 生成个性化解读 |
| 职业建议 | ✅ Claude Agent | AI 基于画像推荐 |

---

## 十五、UX 设计规范（冻结）

### 15.1 产品形态

- **移动优先 Web**：375px 基准设计宽度，PWA 支持添加到主屏幕
- PWA 配置：Service Worker 离线缓存、Web App Manifest、桌面图标

### 15.2 聊天式测评界面

```
┌─────────────────────┐
│  ← Seed             │  Header
│  思维力 2/6         │  维度进度
│  ████░░░░░░ 30%     │  总进度条
├─────────────────────┤
│                     │
│  ╭─ AI ──────────╮ │
│  │ 接下来我想了解  │ │  Agent 消息气泡
│  │ 你的思维方式... │ │
│  ╰───────────────╯ │
│                     │
│  ┌──────────────┐   │
│  │ 面对复杂问题，  │   │  选择题卡片
│  │ 我习惯先拆解   │   │  (选项按钮)
│  │ 成小部分再解决 │   │
│  │              │   │
│  │ ○ 非常不符合  │   │
│  │ ○ 不太符合    │   │
│  │ ○ 一般       │   │
│  │ ○ 比较符合    │   │
│  │ ○ 非常符合    │   │
│  └──────────────┘   │
│                     │
│  ╭─ AI ──────────╮ │
│  │ 好的，这反映出  │ │  即时反馈
│  │ 你的系统性思维  │ │
│  ╰───────────────╯ │
└─────────────────────┘
```

### 15.3 注册转化漏斗

| 阶段 | 用户可见 | 触发时机 |
|------|---------|---------|
| 1. 体验 | 完整作答前 3 题 | 首次进入，无需登录 |
| 2. 预览 | 展示 1 个维度（思维力）的简要分数 | 第 3 题完成后 |
| 3. 注册 | 注册/登录弹窗 | 用户点击"查看完整报告" |
| 4. 完整测评 | 继续作答剩余的 15-33 题 | 注册完成后自动继续 |
| 5. 完整报告 | 六维雷达图 + 全部维度卡片 | 全部题目完成后 |

### 15.4 分享机制

- 报告页生成公开分享链接（token，30 天有效）
- 分享页：六维雷达图 + 简化报告 + 底部"我也要测评"入口按钮
- 分享页无需登录即可查看

---

## 十六、部署架构（冻结）

| 层 | 平台 | 说明 |
|----|------|------|
| 前端 | Vercel | Vue 3 静态站点，自动部署，HTTPS 域名 |
| 后端 | Railway | FastAPI + Redis，自动扩展 |
| 数据库 | Railway PostgreSQL | 托管数据库，每日自动备份 |
| 域名 | vercel.app 默认域名 | MVP 不需要独立域名 |

### 环境变量

```env
# Backend
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
ANTHROPIC_API_KEY=sk-ant-...
JWT_SECRET=...
SHARE_LINK_BASE_URL=https://seed.vercel.app/share
```

---

## 十七、PRD 完成标志

> PRD 文档（`docs/PRD.md`）需在本 spec 通过 review 后另行撰写，包含：

1. 产品背景与市场分析（Seed 定位 vs 竞品）
2. 用户画像（3 类典型用户 + 对应场景 + Journey Map）
3. 六维能力模型理论依据（每维展开：定义、理论出处、评分锚点、典型行为）
4. 题库设计说明（改编来源、信效度说明、题目示例）
5. 功能需求（含用户故事地图）
6. 交互流程图（含注册漏斗、测评对话、分享裂变）
7. UX 设计稿（移动端聊天式界面 + PWA 规范）
8. 非功能需求（性能、安全、隐私合规、PWA 离线策略）
9. 数据埋点方案与核心指标（完成率、注册转化率、分享率、NPS）
10. AI 效果评估体系（选题质量、报告满意度、置信度准确性）
11. 版本迭代路线图

---

> **✅ spec.md v2.0 已定稿。所有关键决策已通过 /grill-me 确认。**
> **进入下一阶段：【冻结边界】— 生成 contract.md + 更新项目目录结构 + .cursorrules。**
