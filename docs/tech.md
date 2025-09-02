违约客户管理系统 - 技术实现与选型文档 (v2.1)

总体架构
- 单体三层：FastAPI + SQLAlchemy + React/Vite
- 身份认证：JWT（OAuth2 Password），前端持久化令牌；RBAC（Admin/Reviewer/Operator）在依赖中强制
- 运行方式：uv 本地开发；Docker/Compose 一键启停

后端（FastAPI）
- 依赖与管理：uv + pyproject/requirements.txt
- 关键模块
	- app/main.py：应用入口、CORS、静态文件、审计中间件挂载
	- app/security.py：JWT 签发与校验、密码哈希
	- app/deps.py：鉴权依赖、角色校验
	- app/routers/*.py：按域拆分路由（auth/users/customers/reasons/applications/notifications/stats/audit_logs）
	- app/audit.py：统一审计写入；中间件按 HTTP 方法映射中文动作并记录 IP
	- app/storage.py：本地/S3 后端，上传与预签名下载
- 业务关键点
	- 审批前附件要求：当 type=DEFAULT 且 decision=APPROVED，必须先上传附件
	- 幂等创建：用户创建按 email 幂等更新，避免重复数据导致测试/种子冲突
	- 搜索富信息：/applications/search、/applications/{id} 返回人名/原因描述等拓展字段
	- 统计 detailed：支持 detailed=true 返回占比与近12个月趋势
	- 审计中文化：action 转中文（登录/新增/审核/上传附件等），输出 actor、resource、ip

数据库与迁移
- ORM：SQLAlchemy；迁移：Alembic
- 主要表：users、customers、reasons、applications、application_attachments、audit_logs、notifications
- 迁移脚本：alembic/versions/*（含为审计增加 IP 字段的迁移）

配置与种子
- .env（示例见 .env.example）
	- DATABASE_URL、JWT_SECRET_KEY/ALGORITHM/EXPIRE
	- 初始账号：ADMIN/REVIEWER/OPERATOR 默认邮箱/密码（启动后自动创建，不重复创建）
	- STORAGE_BACKEND=local|s3 及对应 S3_ENDPOINT / S3_BUCKET / AWS_* / S3_REGION
- 初始原因：默认写入一组违约/重生原因，可在前端“原因”页调整

对象存储
- local：保存到 uploads/ 并通过 /files 路由提供静态访问
- s3/minio：boto3 客户端，保存至桶内；下载通过预签名 URL

前端（React + Vite + Ant Design）
- 路由与权限：React Router + 角色菜单过滤（Admin 多“用户”菜单）
- 数据：React Query + Axios，统一带上 Authorization
- 状态：Zustand 轻量存储用户/令牌
- 关键页面：登录、客户、原因、申请、统计、审计（Admin）、用户（Admin）

测试与质量
- 后端：pytest；测试前重置测试库，避免重复数据冲突
- 前端：Vite 构建校验；可扩展 Playwright 端到端测试

部署与运行
- 本地：uv run fastapi/pytest；frontend 使用 Vite dev server
- Docker：docker-compose up -d 同启前后端与数据库（如配置）