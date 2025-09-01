# 违约客户管理系统 - 后端服务

基于 FastAPI + PostgreSQL 的单体服务，实现 RBAC、JWT 鉴权、违约/重生工作流、查询统计与审计日志（最小可用版本）。

## 快速开始（Docker Compose）

```bash
docker compose up --build
```

启动后：
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- 初始管理员: admin@example.com / admin123

## 本地运行（使用 uv）

```bash
# 1) 创建虚拟环境并安装依赖
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt

# 2) 配置环境变量（复制 .env.example 为 .env 并按需修改）
cp -n .env.example .env || true

# 3) 启动服务
uvicorn app.main:app --reload
```

## 目录结构
- app/main.py: FastAPI 入口
- app/models.py: 数据模型
- app/routers/: 业务路由
- app/security.py: 密码与JWT
- app/deps.py: 鉴权依赖、RBAC
- app/audit.py: 审计日志

## 覆盖需求要点
- 原因维护（违约/重生）
- 客户主数据维护
- 违约认定申请、审核（状态 PENDING -> APPROVED/REJECTED）
- 重生申请、审核（同上）
- 审核通过影响 customers.is_default
- 统一查询 + 行业/区域统计
- 站内通知（审核后自动发送）
- 审计日志（关键动作记录）

后续建议：接入 Alembic 版本化迁移、对象存储附件、细化审计与通知、完善测试。