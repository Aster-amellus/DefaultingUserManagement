# 违约客户管理系统（全栈）

基于 FastAPI（后端）+ React/Vite（前端）。实现 JWT 登录、RBAC 权限（Admin/Reviewer/Operator）、违约/重生工作流、对象存储附件、统计（行业/区域/趋势/占比）与中文审计日志（含操作者/资源/IP）。

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
 - 初始原因（种子）：按“违约/重生”两类写入一组常用原因，便于开箱即用（可在“原因”页调整启用/排序）。

### 维护与常用命令

```bash
# 查看日志
docker compose logs -f api
docker compose logs -f frontend

# 重建并重启
docker compose up -d --build

# 进入 API 容器执行迁移/脚本
docker compose exec api alembic upgrade head
docker compose exec api uv run python scripts/seed_demo_data.py

# 停止
docker compose down
```

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

## 生产部署（Windows/Linux 通用，Docker）

使用 production 方案，前端打包为静态文件由 Nginx 提供，后端为 Uvicorn（不启用 reload），跨平台一致。

```bash
# 构建生产镜像
docker compose -f docker-compose.prod.yml build

# 启动
docker compose -f docker-compose.prod.yml up -d

# 查看
# 前端: http://localhost
# API:  http://localhost:8000 (Swagger: /docs)

# 停止
docker compose -f docker-compose.prod.yml down
```

注意：
- 如需自定义环境变量，复制 `.env.example` 为 `.env` 并按需修改，再通过 compose 的 environment 注入或扩展 `docker-compose.prod.yml`。
- Windows 与 Linux 使用同样命令即可（需安装 Docker Desktop / Docker Engine）。
- 生产环境建议在 API 前增加反向代理（Nginx/Traefik）和 HTTPS 证书（Let’s Encrypt）。

常用环境变量（.env）：
- DATABASE_URL：数据库连接串（例：postgresql+psycopg2://user:pass@host:5432/db 或 sqlite+pysqlite:///./dev.db）
- JWT_SECRET_KEY、JWT_ALGORITHM、ACCESS_TOKEN_EXPIRE_MINUTES
- ADMIN_DEFAULT_EMAIL、ADMIN_DEFAULT_PASSWORD（首次登录前会自动创建管理员）
 - REVIEWER_DEFAULT_EMAIL/REVIEWER_DEFAULT_PASSWORD、OPERATOR_DEFAULT_EMAIL/OPERATOR_DEFAULT_PASSWORD（首次登录时自动创建）
- STORAGE_BACKEND=local|s3；如为 s3，还需 S3_ENDPOINT、S3_BUCKET、AWS_ACCESS_KEY_ID、AWS_SECRET_ACCESS_KEY、S3_REGION

### 前端（Vite）

```bash
cd frontend
npm install
npm run dev
```

- 访问 http://localhost:5173
- `/api` 通过 Vite 代理到后端（默认 http://localhost:8000）。如后端地址不同，设置 `VITE_API_BASE` 或编辑 `vite.config.ts`。
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
	- 可见菜单：客户、申请、原因、统计、审计、用户

前端登录后会调用 `/users/me` 自动识别角色并限制可见菜单和路由；后端通过 `require_role` 做接口鉴权（如 `/audit-logs/` 仅 Admin）。

## 功能概览
- 登录鉴权（/auth/token）+ 管理员首登种子
- 客户主数据：新增/查询
- 原因维护：违约/重生原因的增删改、启用/禁用（Admin）
- 申请流程：发起/附件上传/审批（通过/拒绝），通过后联动 `customers.is_default`
- 业务规则：
	- 已是违约客户禁止再次发起违约认定；非违约客户禁止发起重生。
	- 审批“违约认定”通过前，须至少上传1个附件。
- 统计分析：按行业/区域
- 统计增强：支持 detailed=true 返回各项占比与12个月趋势数组。
- 通知提醒：审批后自动通知
- 审计日志（中文）：记录操作者、动作（中文）、资源、IP、时间；提供筛选查询（Admin）
- 对象存储：本地或 S3/MinIO，预签名下载/预览

## 管理用户（Admin）
- 页面：侧边栏“用户”（Admin专属），支持创建/列表/编辑（姓名、密码、角色）/删除。
- API：
	- POST /users/（创建或幂等更新）
	- GET /users/、GET /users/{id}
	- PATCH /users/{id}、DELETE /users/{id}

## 查询/审批页面
- 申请：支持按客户名/状态/类型查询（后端提供 `/applications/search` 返回富信息字段）。
- 附件：每条申请可上传，审批违约需先上传。
- 审计：仅 Admin，可筛选动作/时间区间，输出包含操作者姓名/邮箱、动作（中文）、资源与IP。

## API 文档
- 访问 http://localhost:8000/docs（Swagger）
- 常用：
	- 认证：`/auth/token` 登录、`/users/me` 当前用户
	- 用户：`/users/*`（Admin）
	- 客户：`/customers/*`
	- 原因：`/reasons/*`（支持 `?type=DEFAULT|REBIRTH`）
	- 申请：`/applications/*`、`/applications/search`、`/applications/{id}/attachments`
	- 统计：`/stats/industry|region`（可带 `detailed=true`）
	- 审计：`/audit-logs/`（Admin）

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
 - 违约审批失败“需要附件”：请先在该申请条目点击“上传附件”，再由 Reviewer/ Admin 审批“同意”。