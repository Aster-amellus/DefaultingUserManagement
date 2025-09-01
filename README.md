# 违约客户管理系统（全栈）

基于 FastAPI（后端）+ React/Vite（前端）。实现 JWT 登录、RBAC 角色权限（Admin/Reviewer/Operator）、违约/重生工作流、对象存储附件、统计与审计日志。

## 一键启动（Docker Compose）

```bash
docker compose up -d --build
```

启动后：
- 后端 API: http://localhost:8000（Swagger: /docs）
- 前端 Web: http://localhost:5173
- 初始账户（自动种子，首次登录前创建，可在 .env 覆盖）：
	- Admin: admin@example.com / admin123
	- Reviewer: reviewer@example.com / reviewer123
	- Operator: operator@example.com / operator123

## 本地开发

### 后端（uv + Alembic）

```bash
# 1) 创建虚拟环境并安装依赖
uv venv
uv pip install -r requirements.txt

# 2) 配置环境变量（复制 .env.example 为 .env 并按需修改）
cp -n .env.example .env || true

# 3) 初始化数据库（Alembic 迁移）
uv run alembic upgrade head

# 4) 启动后端（FastAPI/Uvicorn）
uv run uvicorn app.main:app --reload --port 8000
```

常用环境变量（.env）：
- DATABASE_URL：数据库连接串（例：postgresql+psycopg2://user:pass@host:5432/db 或 sqlite+pysqlite:///./dev.db）
- JWT_SECRET_KEY、JWT_ALGORITHM、ACCESS_TOKEN_EXPIRE_MINUTES
- ADMIN_DEFAULT_EMAIL、ADMIN_DEFAULT_PASSWORD（首次登录前会自动创建管理员）
- STORAGE_BACKEND=local|s3；如为 s3，还需 S3_ENDPOINT、S3_BUCKET、AWS_ACCESS_KEY_ID、AWS_SECRET_ACCESS_KEY、S3_REGION

### 前端（Vite）

```bash
cd frontend
npm install
npm run dev
```

- 访问 http://localhost:5173
- `/api` 将通过 Vite 代理到后端（默认 http://localhost:8000）。若后端地址不同，可设置 `VITE_API_BASE`。
- 生产构建/预览：

```bash
npm run build
npm run preview
```

### 测试
- 后端：`uv run pytest`
- 前端：`cd frontend && npm run test`

## 角色与界面权限

- 业务人员（Operator）
	- 核心：发起“违约认定/重生”申请
	- 辅助：可维护客户主数据
	- 可见菜单：客户、申请、统计
- 审核人员（Reviewer）
	- 核心：审批申请（同意/拒绝）
	- 辅助：查询所有申请
	- 可见菜单：申请、统计
- 系统管理员（Admin）
	- 核心：用户与权限管理、原因维护、系统配置
	- 辅助：拥有系统全部权限
	- 可见菜单：客户、申请、原因、统计、审计（等）

前端登录后会调用 `/users/me` 自动识别角色并限制可见菜单和路由；后端通过 `require_role` 做接口鉴权（如 `/audit-logs/` 仅 Admin）。

## 功能概览
- 登录鉴权（/auth/token）+ 管理员首登种子
- 客户主数据：新增/查询
- 原因维护：违约/重生原因的增删改、启用/禁用（Admin）
- 申请流程：发起/附件上传/审批（通过/拒绝），通过后联动 `customers.is_default`
- 统计分析：按行业/区域
- 通知提醒：审批后自动通知
- 审计日志：中间件记录关键操作；提供筛选查询（Admin）
- 对象存储：本地或 S3/MinIO，预签名下载/预览

## API 文档
- 访问 http://localhost:8000/docs（Swagger）
- 常用：`/auth/token` 登录、`/users/me` 当前用户、`/applications/*` 工作流、`/reasons/*` 原因、`/customers/*` 客户、`/stats/*` 统计、`/audit-logs/` 审计

## 目录结构（摘）
- app/main.py：FastAPI 入口、路由注册、CORS、审计中间件
- app/models.py / app/schemas.py：ORM 模型与 Pydantic 模型
- app/routers/*：业务路由（auth/users/customers/reasons/applications/notifications/stats/audit_logs）
- app/storage.py：本地/S3 存储
- alembic/*：数据库迁移
- frontend/*：React + Vite 前端

## 常见问题（FAQ）
- 首次登录 401：确认已使用 `.env` 中的管理员邮箱/密码调用 `/auth/token` 获取 JWT，并在前端完成登录；前端会自动附带 Authorization 头。
- 审计页无权限：`/audit-logs/` 仅 Admin 可访问，使用管理员账号登录；非 Admin 将提示“无权限查看审计日志”。
- 代理问题：后端不在默认 8000 端口时，设置 `VITE_API_BASE` 或修改 `frontend/vite.config.ts` 代理目标。