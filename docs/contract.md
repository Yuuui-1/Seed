# Contract: Seed API 接口契约

> **版本**: v1.0  
> **状态**: 冻结（所有接口实现必须遵守本契约）  
> **Base URL**: `/api/v1`

---

## 统一响应格式

```json
{
  "code": 0,
  "data": {},
  "msg": "success"
}
```

### 错误码

| code | 含义 |
|------|------|
| 0 | 成功 |
| 1001 | 参数校验失败 |
| 1002 | 认证失败 / Token 过期 |
| 1003 | 资源不存在 |
| 1004 | 权限不足 |
| 1005 | 重复操作 |
| 2001 | AI 服务异常 |
| 2002 | AI 输出格式错误 |
| 5000 | 服务器内部错误 |

### 分页

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

## 1. 认证模块 `/api/v1/auth`

### 1.1 注册 `POST /register`

```yaml
Request:
  email: str        # 邮箱，格式校验
  password: str     # 8-32 位，含大小写+数字
  nickname: str     # 2-20 字符

Response 200:
  {
    "code": 0,
    "data": {
      "user": {"id": 1, "email": "user@example.com", "nickname": "张三"},
      "access_token": "eyJ...",
      "refresh_token": "eyJ..."
    }
  }

Response 1001:
  {"code": 1001, "data": null, "msg": "邮箱已被注册"}
```

### 1.2 登录 `POST /login`

```yaml
Request:
  email: str
  password: str

Response 200:
  {
    "code": 0,
    "data": {
      "user": {"id": 1, "email": "user@example.com", "nickname": "张三"},
      "access_token": "eyJ...",
      "refresh_token": "eyJ..."
    }
  }

Response 1002:
  {"code": 1002, "data": null, "msg": "邮箱或密码错误"}
```

### 1.3 刷新 Token `POST /refresh`

```yaml
Request:
  refresh_token: str

Response 200:
  {"code": 0, "data": {"access_token": "eyJ...", "refresh_token": "eyJ..."}}

Response 1002:
  {"code": 1002, "data": null, "msg": "Token 无效或已过期"}
```

### 1.4 登出 `POST /logout`

```yaml
Headers:
  Authorization: Bearer {access_token}

Response 200:
  {"code": 0, "data": null, "msg": "success"}
```

### 1.5 获取当前用户 `GET /me`

```yaml
Headers:
  Authorization: Bearer {access_token}

Response 200:
  {
    "code": 0,
    "data": {
      "id": 1,
      "email": "user@example.com",
      "nickname": "张三",
      "created_at": "2026-01-01T00:00:00Z"
    }
  }
```

---

## 2. 测评模块 `/api/v1/assessment`

### 2.1 开始/继续测评 `POST /start`

> 支持已登录和未登录状态。未登录用户用 session_id 追踪。

```yaml
Headers:
  Authorization: Bearer {access_token}  # 可选

Response 200（新测评）:
  {
    "code": 0,
    "data": {
      "assessment_id": 1,
      "total_rounds": 0,        # 自适应，开始时不固定
      "current_round": 1,
      "status": "in_progress",
      "session_id": "anon_abc123"  # 未登录时返回
    }
  }

Response 200（继续测评）:
  {
    "code": 0,
    "data": {
      "assessment_id": 1,
      "current_round": 4,       # 续接上次进度
      "status": "in_progress"
    }
  }
```

### 2.2 获取下一题 `GET /{assessment_id}/next-question`

> Agent 自适应选题后返回，SSE 流式。

```yaml
Headers:
  Authorization: Bearer {access_token}  # 可选

Response (SSE 流):
  event: question
  data: {
    "question_id": "q_012",
    "round": 4,
    "agent_message": "接下来我想了解你在团队中的角色...",
    "question_text": "在团队项目中，我更倾向于承担组织和协调的角色",
    "options": [
      {"value": 1, "label": "非常不符合"},
      {"value": 2, "label": "不太符合"},
      {"value": 3, "label": "一般"},
      {"value": 4, "label": "比较符合"},
      {"value": 5, "label": "非常符合"}
    ],
    "target_dimension": "social"
  }

  event: preview     # 第 3 题答完后触发
  data: {
    "dimension": "thinking",
    "score": 78,
    "message": "你的思维力初步评估为 78 分，想查看完整六维报告吗？",
    "show_register_prompt": true
  }

  event: complete    # 全部答题完成
  data: {
    "assessment_id": 1,
    "message": "测评已完成，正在分析中..."
  }
```

### 2.3 提交答案 `POST /{assessment_id}/answer`

```yaml
Request:
  question_id: str
  answer_value: int     # 1-5
  session_id: str       # 未登录时必传

Response 200:
  {"code": 0, "data": {"round": 4, "answered": true}}

Response 1005:
  {"code": 1005, "data": null, "msg": "该题已作答，请获取下一题"}
```

### 2.4 获取进度 `GET /{assessment_id}/progress`

```yaml
Response 200:
  {
    "code": 0,
    "data": {
      "assessment_id": 1,
      "status": "in_progress",
      "current_round": 6,
      "dimensions_progress": {
        "thinking": {"rounds_done": 2, "confidence": 0.72},
        "creativity": {"rounds_done": 1, "confidence": 0.45},
        "execution": {"rounds_done": 1, "confidence": 0.40},
        "social": {"rounds_done": 1, "confidence": 0.38},
        "emotional": {"rounds_done": 1, "confidence": 0.35},
        "drive": {"rounds_done": 0, "confidence": 0}
      }
    }
  }
```

### 2.5 绑定未登录测评到用户 `POST /{assessment_id}/bind`

> 注册后调用，将匿名测评数据转移到用户下

```yaml
Headers:
  Authorization: Bearer {access_token}

Request:
  session_id: str

Response 200:
  {"code": 0, "data": {"bound": true}}
```

---

## 3. 报告模块 `/api/v1/reports`

### 3.1 报告列表 `GET /`

```yaml
Headers:
  Authorization: Bearer {access_token}

Query:
  page: int      # default 1
  page_size: int # default 20

Response 200:
  {
    "code": 0,
    "data": {
      "items": [
        {
          "id": 1,
          "created_at": "2026-01-15T10:00:00Z",
          "dimensions": {
            "thinking": {"score": 85, "label": "思维力"},
            "creativity": {"score": 72, "label": "创造力"},
            "execution": {"score": 68, "label": "执行力"},
            "social": {"score": 90, "label": "社交力"},
            "emotional": {"score": 75, "label": "情绪力"},
            "drive": {"score": 80, "label": "驱动力"}
          }
        }
      ],
      "total": 3,
      "page": 1,
      "page_size": 20
    }
  }
```

### 3.2 报告详情 `GET /{report_id}`

```yaml
Headers:
  Authorization: Bearer {access_token}

Response 200:
  {
    "code": 0,
    "data": {
      "id": 1,
      "assessment_id": 1,
      "dimensions": {
        "thinking": {
          "score": 85,
          "confidence_interval": [75, 95],
          "label": "思维力",
          "strengths": "你在面对复杂问题时展现出系统性的分析能力...",
          "areas_for_improvement": "可以尝试更多跨领域思维训练...",
          "description": "思维力反映逻辑推理和问题解决能力。你的高分表明...",
          "evidence": [
            "第3题：'我习惯先拆解再解决' → 非常符合",
            "第12题：'我享受解决复杂问题' → 比较符合"
          ]
        },
        "creativity": {},
        "execution": {},
        "social": {},
        "emotional": {},
        "drive": {}
      },
      "summary": "综合来看，你是一位系统性思考者...",
      "career_suggestions": [
        {"direction": "产品经理", "match": 92, "reason": "..."},
        {"direction": "管理咨询", "match": 87, "reason": "..."},
        {"direction": "数据分析师", "match": 82, "reason": "..."}
      ],
      "created_at": "2026-01-15T10:00:00Z",
      "shared": false
    }
  }
```

### 3.3 生成分享链接 `POST /{report_id}/share`

```yaml
Headers:
  Authorization: Bearer {access_token}

Response 200:
  {
    "code": 0,
    "data": {
      "share_url": "https://seed.vercel.app/share/abc123xy",
      "token": "abc123xy",
      "expires_at": "2026-02-14T10:00:00Z"
    }
  }
```

### 3.4 查看分享报告 `GET /shared/{token}`

> 无需登录

```yaml
Response 200:
  {
    "code": 0,
    "data": {
      # 同 3.2 报告详情，但不包含 assessment_id
      "dimensions": {},
      "summary": "...",
      "career_suggestions": [],
      "share_from": "张三"
    }
  }

Response 1003:
  {"code": 1003, "data": null, "msg": "分享链接不存在或已过期"}
```

---

## 4. 用户模块 `/api/v1/users`

### 4.1 获取个人信息 `GET /profile`

```yaml
Headers:
  Authorization: Bearer {access_token}

Response 200:
  {
    "code": 0,
    "data": {
      "id": 1,
      "email": "user@example.com",
      "nickname": "张三",
      "total_assessments": 3,
      "joined_at": "2026-01-01T00:00:00Z"
    }
  }
```

### 4.2 更新个人信息 `PUT /profile`

```yaml
Headers:
  Authorization: Bearer {access_token}

Request:
  nickname: str     # 可选

Response 200:
  {"code": 0, "data": {"nickname": "新昵称"}, "msg": "更新成功"}
```

---

## 鉴权方案（重申冻结）

| 项目 | 方案 |
|------|------|
| 认证方式 | JWT（Access Token + Refresh Token） |
| Access Token | 30 分钟过期 |
| Refresh Token | 7 天过期 |
| 传输方式 | `Authorization: Bearer {token}` |
| 登出 | 前端清 Token + 后端 Redis 黑名单 |
| 未登录 | 允许体验 3 题，用 session_id 追踪 |
| 密码 | bcrypt 哈希 |

---

## 接口契约版本规则

- 路径变更 → 开新版本 `/api/v2/`
- 响应字段新增 → v1 兼容（不删字段、不改类型）
- 响应字段删除/改名 → 开新版本

---

> ✅ **contract.md 已冻结。所有后端实现必须严格遵循上述请求/响应结构。前端 API 调用层以此为准。**
