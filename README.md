# Seed 🌱

> AI 自适应人才优势测评系统 — 从 PRD 到全栈实现的 AI-native 产品实践

[![Tests](https://img.shields.io/badge/backend_tests-28%2F28%20pass-brightgreen)](backend/tests/)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://python.org)
[![Vue](https://img.shields.io/badge/vue-3.4+-green)](https://vuejs.org)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 这是什么

Seed 是一款面向自我探索者的自适应人才优势测评工具。用户完成 24 道基于经典心理量表改编的选择题后，系统通过 AI 自适应选题和加权计分生成六维能力画像（思维力、创造力、执行力、社交力、情绪力、驱动力），输出含证据链的可视化报告。

与普通测评工具不同的是，AI 在这里不负责生成题目——题库全部改编自大五人格（IPIP-50）、RIASEC、Grit 坚毅量表、自我决定理论（SDT）、认知需求量表（NFC）等经学术验证的心理学测量工具。AI 的职责是从题库中自适应选择最能减小评分不确定性的题目，并在完成测评后为每个维度生成个性化解读。

---

## 📂 项目文件说明

```
Seed/
├── README.md                  # 项目概述（你在这里）
├── docs/                      # 📋 产品与技术文档
│   ├── PRD.md                 #   产品需求文档：用户画像、功能需求、
│   │                          #   6 层 AI 架构（输入/Prompt/边界/兜底/评估/迭代）
│   ├── spec.md                #   技术规格书：技术栈、数据模型、Agent 架构
│   └── contract.md            #   接口契约：14 个 API 的请求/响应/错误码
├── frontend/                  # 🎨 Vue 3 前端
│   └── src/
│       ├── views/             #   7 个页面（首页/登录/注册/测评/报告/历史/分享）
│       ├── api/               #   API 调用层（axios + 拦截器）
│       ├── router/            #   路由 + 导航守卫
│       └── stores/            #   Pinia 状态管理（auth/assessment）
├── backend/                   # 🔧 Python FastAPI 后端
│   └── app/
│       ├── agents/            #   Claude Agent SDK（选题器/计分沙箱/报告生成器）
│       ├── api/v1/endpoints/  #   14 个 REST API + SSE 流式端点
│       ├── data/              #   36 题科学量标题库（JSON，版本化管理）
│       ├── models/            #   5 张数据表（User/Assessment/Answer/Report/ShareLink）
│       ├── services/          #   业务逻辑层
│       └── schemas/           #   Pydantic 数据校验
├── backend/tests/             # 🧪 28 个测试用例（pytest）
├── .opencode/skills/          # 🛠 AI 辅助开发技能
│   ├── brainstorming/         #   Spec-first 设计方法论（obra/superpowers）
│   ├── grill-me/              #   决策链完整度审查（mattpocock/skills）
│   └── grilling/              #   逐问制决策收敛
├── .cursorrules               #   AI 行为约束规则
└── docker-compose.yml         #   开发环境（PostgreSQL + Redis）
```

---

## 技术选型

| 层 | 选型 | 说明 |
|----|------|------|
| 前端 | Vue 3 + Vite + TailwindCSS + ECharts + PWA | 移动优先，雷达图可视化 |
| 后端 | Python FastAPI + SQLAlchemy + Pydantic v2 | 异步高性能，类型安全 |
| AI 引擎 | Claude Agent SDK | 自适应选题 + 确定性计分 |
| 数据库 | PostgreSQL 16 + Redis 7 | 测评数据 + 会话缓存 |
| 测试 | pytest + vitest | 28 个后端测试全通过 |

---

## 产品文档

> 文档记录了从需求分析到交付的完整过程。

| 文档 | 内容 | 
|------|------|
| [PRD.md](docs/PRD.md) | 产品需求文档：用户画像、功能需求、6 层 AI 架构、指标、里程碑 |
| [spec.md](docs/spec.md) | 技术规格书：技术栈、目录结构、数据模型、Agent 架构、部署方案 |
| [contract.md](docs/contract.md) | 接口契约：14 个 API 的请求/响应格式、错误码、SSE 协议 |

---

## 快速开始

```bash
# 后端
cd backend && pip install -r requirements.txt
DATABASE_URL="sqlite+aiosqlite:///seed.db" uvicorn app.main:app --reload

# 前端
cd frontend && npm install && npm run dev
```

打开 http://localhost:3000

```bash
# 测试
cd backend
DATABASE_URL="sqlite+aiosqlite:///:memory:" pytest tests/ -v
```

---

## License

MIT
