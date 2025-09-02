# ⑥ 答辩PPT（Markdown 版提纲）

## 1. 封面
- 题目：违约客户管理系统
- 小组成员：组员1、组员2、组员3、组员4、组员5、组员6
- 日期：2025-09-01

## 2. 项目背景与目标
- 痛点：违约/重生流程分散、缺少审计与统计
- 目标：标准化流程、审计留痕、指标洞察、角色分权

## 3. 需求概览（功能为主）
- 角色：Admin/Reviewer/Operator
- 申请类型：DEFAULT/REBIRTH，核心业务规则（DEFAULT 审批需附件）
- 模块：客户、原因、申请、审批、附件、统计、审计、通知、用户管理

## 4. 整体架构
- 后端：FastAPI + SQLAlchemy + Alembic + JWT/RBAC
- 前端：React + Vite + Ant Design + React Query
- 存储：本地/S3；静态 /files 与预签名 URL
- 部署：uv，本地；Docker/Compose 可选

## 5. 核心设计与亮点
- RBAC 与依赖注入；审计中间件（中文 action、actor/resource/IP）
- 审批联动客户状态；search 富信息；统计 detailed 占比+12月趋势
- 幂等用户创建；附件校验拦截 DEFAULT 审批

## 6. 关键流程演示（Demo 路线）
- 登录（Admin）→ 原因维护 → 用户管理
- 登录（Operator）→ 发起 DEFAULT → 上传附件
- 登录（Reviewer）→ 审批通过 → 通知生成
- 管理员查看统计与审计

## 7. 测试与质量
- 自动化：pytest 已执行 16 条；边界用例覆盖
- 报告：report_backend.xml；TEST_REPORT.md
- 后续：补充前端 E2E（可选 Playwright）

## 8. 项目进度与分工
- 见 02_进度计划表.md
- 关键负责人：
  - 后端：组员3/4/5
  - 前端：组员5/6
  - 测试与文档：组员1/2/6

## 9. 风险与改进
- 风险：需求变更、接口对齐、时间压力
- 改进：增加契约测试、完善 E2E、监控与告警

## 10. 总结与Q&A
- 价值：流程沉淀、合规可追溯、效率提升
- 谢谢！
