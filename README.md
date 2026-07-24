# Seed 🌱

> **AI 自适应人才优势测评系统** — 不是"用 AI 做了个测评"，而是"用 AI PM 的方法论从 0 到 1 设计了一款 AI-native 产品"。

[![Tests](https://img.shields.io/badge/backend_tests-28%2F28%20pass-brightgreen)](backend/tests/)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://python.org)
[![Vue](https://img.shields.io/badge/vue-3.4+-green)](https://vuejs.org)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 为什么做这个项目

2025 年的 AI 产品经理面试，面试官不再满足于"我用 Coze 搭了个工作流"。他们想看的是：**你是否理解 AI 产品的不确定性管理？你能否为 LLM 的行为划定边界？你是否设计了兜底逻辑和评估体系？**

Seed 是我从需求分析→PRD 撰写→全栈开发→AI 6 层架构设计→测试部署的完整 AI 产品实践。它的目标不是做"又一个 MBTI 测试"，而是展示一个 AI PM 如何将不可控的 LLM 输出转化为可控、可评估、可迭代的产品系统。

---

## 产品理念

### AI 不是出题者，而是选题者

市面上大多数 AI 测评让模型生成题目——好看但不靠谱。Seed 的做法相反：

- **题库固定**：36 道题全部改编自大五人格（IPIP-50）、RIASEC、Grit 坚毅量表、自我决定理论（SDT）、认知需求量表（NFC）等经学术验证的心理测量工具
- **AI 做自适应选题**：Claude Agent SDK 根据用户的答题历史，从题库中轮巡+加权选择最具区分度的下一题
- **计分在沙箱中执行**：0-100 的六维评分由确定性算法计算，不依赖 LLM 的数值输出
- **AI 做个性化解读**：每个维度的文字报告由 LLM 基于分数生成，但配备 5 档模板兜底

### 不是"你是什么人"，而是"你倾向于如何应对世界"

测评结果不贴标签（"你是 INTJ"），而是呈现六维能力画像 + 置信度区间 + 基于答题数据的证据链解读。

---

## 产品文档

> **面试官请从这里开始**——这些文档记录了一个 AI 产品从想法到交付的完整过程。

| 文档 | 说明 | 适合 |
|------|------|------|
| [📋 **PRD.md**](docs/PRD.md) | 完整 AI 产品需求文档。含 3 个用户画像、功能需求、**6 层 AI 架构（输入层/Prompt 策略层/行为边界层/兜底层/评估层/迭代观测层）**、指标体系和里程碑 | AI PM 面试核心 |
| [📐 **spec.md**](docs/spec.md) | 17 章技术规格书。技术栈、目录结构、数据模型、Claude Agent SDK 架构、计分算法、PWA 部署方案 | 了解技术决策 |
| [📄 **contract.md**](docs/contract.md) | 14 个 API 的接口契约。请求/响应格式、错误码、SSE 流式协议 | 了解接口设计 |

---

## 技术栈

| 层 | 选型 | 为什么 |
|----|------|--------|
| **前端** | Vue 3 + Vite + TypeScript + TailwindCSS + ECharts + PWA | 移动优先，雷达图可视化，可添加到主屏幕 |
| **后端** | Python FastAPI + SQLAlchemy + Pydantic v2 | 异步高性能，类型安全 |
| **AI 引擎** | Claude Agent SDK (Anthropic) | 自适应选题 + 沙箱计分，非 Coze 低代码 |
| **数据库** | PostgreSQL 16 + Redis 7 | 测评数据和缓存 |
| **测试** | pytest + vitest | 28 个后端测试，全通过 |

---

## 项目结构

```
├── frontend/              # 7 个页面（首页/登录/注册/测评/报告/历史/分享）
├── backend/
│   ├── app/
│   │   ├── agents/        # Claude Agent SDK 引擎（选题器/计分沙箱/报告生成）
│   │   ├── api/           # 14 个 REST API + SSE 流式端点
│   │   ├── data/          # 36 题科学量标题库（JSON，版本化管理）
│   │   ├── models/        # 5 张数据表（User/Assessment/Answer/Report/ShareLink）
│   │   └── services/      # 业务逻辑层
│   └── tests/             # 28 个测试用例
├── docs/
│   ├── PRD.md             # 🏆 AI 产品需求文档（含 6 层 AI 架构）
│   ├── spec.md            # 技术规格说明书
│   └── contract.md        # 接口契约
└── .cursorrules           # AI 辅助开发行为约束规则
```

---

## 快速开始

### 环境要求
- Python 3.11+ / Node.js 18+

### 启动

```bash
# 后端
cd backend
pip install -r requirements.txt
DATABASE_URL="sqlite+aiosqlite:///seed.db" uvicorn app.main:app --reload

# 前端
cd frontend
npm install
npm run dev
```

打开 http://localhost:3000

### 运行测试

```bash
cd backend
DATABASE_URL="sqlite+aiosqlite:///:memory:" pytest tests/ -v
```

---

## 我学到了什么

这个项目让我深入理解了 AI 产品与传统软件产品的本质区别：

1. **不确定性管理 > 功能列表**：AI 产品的 PRD 核心不是"功能有哪些"，而是"当模型输出不符合预期时，系统如何兜底"（见 PRD §7.4）
2. **Prompt 即产品逻辑**：选题 Agent 的 Prompt 策略直接决定了测评质量和用户体验（见 PRD §7.2）
3. **评估体系是 AI 产品的质量底线**：传统测试用例不够用，需要选题质量、报告一致性、无幻觉率等 AI 特有指标（见 PRD §7.5）
4. **SDD（规范驱动开发）比 Vibe Coding 更可靠**：先写 spec 再写代码，冻结边界后再让 AI 辅助实现，效率和质量都更高

---

## License

MIT
