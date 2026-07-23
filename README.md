# Seed 🌱

> AI 自适应人才优势测评系统 — 基于科学量表 + Claude Agent SDK，发现你的六维能力画像

[![Tests](https://img.shields.io/badge/tests-28%2F28%20pass-brightgreen)](backend/tests/)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://python.org)
[![Vue](https://img.shields.io/badge/vue-3.4+-green)](https://vuejs.org)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Demo

🌐 **线上体验**: *（即将上线）*

## 这是什么？

Seed 是一款面向大学生和职场新人的 AI 自适应人才优势测评产品。与传统固定题量的问卷不同，Seed 的 AI 不负责出题，而是负责**从科学验证的题库中自适应选择最能区分你能力维度的题目**。

### 核心特点

- **科学量表题库**：36 道题改编自 Big Five、RIASEC、Grit、SDT、NFC 等经典学术量表
- **AI 自适应选题**：不是随机出题，而是轮巡基线 + 加权追问 + 置信度收束
- **证据链报告**：每个维度的评分都引用你的原始回答作为依据
- **可分享**：生成分享链接，支持社交传播

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- PostgreSQL 16+
- Redis 7+

### 后端

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # 编辑 .env 填入你的 API Key
uvicorn app.main:app --reload
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

### Docker（一键启动数据库）

```bash
docker-compose up -d
```

## 运行测试

```bash
cd backend
DATABASE_URL="sqlite+aiosqlite:///:memory:" pytest tests/ -v
```

## 技术栈

| 层 | 技术 | 
|----|------|
| 前端 | Vue 3, Vite, TypeScript, TailwindCSS, ECharts, PWA |
| 后端 | Python FastAPI, SQLAlchemy, Pydantic v2 |
| AI | Claude Agent SDK (Anthropic) |
| 数据库 | PostgreSQL 16, Redis 7 |
| 部署 | Vercel (前端) + Railway (后端) |

## 项目结构

```
├── frontend/              # Vue 3 前端（PWA）
│   └── src/
│       ├── views/         # 7 个页面
│       ├── api/           # API 调用层
│       ├── stores/        # Pinia 状态管理
│       └── components/    # 通用组件
├── backend/               # FastAPI 后端
│   └── app/
│       ├── api/           # 14 个 REST API
│       ├── agents/        # Claude Agent 引擎
│       ├── models/        # 5 张数据表
│       └── services/      # 业务逻辑层
├── docs/
│   ├── PRD.md             # AI 产品需求文档（含 6 层 AI 架构）
│   ├── spec.md            # 技术规格说明书
│   └── contract.md        # 接口契约
└── .cursorrules           # AI 行为约束
```

## 产品文档

> 如果你是面试官或想深入了解产品设计，请从这里开始：

| 文档 | 内容 |
|------|------|
| [📋 PRD.md](docs/PRD.md) | 产品需求文档：用户画像、功能需求、**6 层 AI 架构（Prompt 策略/行为边界/兜底/评估/迭代）** |
| [📐 spec.md](docs/spec.md) | 技术规格书：技术栈、目录结构、数据模型、Agent 架构 |
| [📄 contract.md](docs/contract.md) | 接口契约：14 个 API 的请求/响应规范 |

## 为什么叫 Seed？

每个人都是一颗种子。测评帮助你找到最适合自己的土壤和生长方向。

## License

MIT
