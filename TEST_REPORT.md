# 违约客户管理系统 测试报告（v2.1）

- 日期：2025-09-01
- 范围：后端 API、RBAC、用户管理、客户/原因、申请/审批（含附件校验）、附件/预签名、统计（detailed）、审计日志（中文/actor/resource/IP）、通知、前端角色菜单与关键流程
- 环境：本地开发（默认 http://localhost:8000 / http://localhost:5173，STORAGE_BACKEND=local）
- 执行说明：本报告含已执行的后端自动化结果与少量人工验证项；自动化结果详见下方概要与 report_backend.xml。

## 概要
- 用例总数：24
- 已执行：16（后端 pytest）
- 通过：16
- 失败：0
- 阻塞：0
- 报告：report_backend.xml（JUnit）

## 用例结果速览
| ID | 场景 | 结果 |
|---|---|---|
| TC-AUTH-001 | 登录成功（Admin） | 通过 |
| TC-AUTH-002 | 登录失败（错误密码） | 通过 |
| TC-RBAC-001 | 审计接口仅 Admin 可访问 | 通过 |
| TC-USER-001 | 管理员创建用户（幂等） | 通过 |
| TC-USER-002 | 管理员查/改/删用户 | 通过 |
| TC-CUST-001 | 创建客户（Operator） | 通过 |
| TC-REAS-001 | 获取违约/重生原因 | 通过 |
| TC-APP-001 | 发起违约认定 DEFAULT 成功 | 通过 |
| TC-APP-002 | DEFAULT 对已违约客户报错 | 通过 |
| TC-APP-003 | REBIRTH 对非违约客户报错 | 通过 |
| TC-APP-004 | 审批 DEFAULT 无附件报错 | 通过 |
| TC-ATT-001 | 上传附件成功 | 通过 |
| TC-APP-005 | 审批 DEFAULT 通过（有附件） | 通过 |
| TC-APP-006 | 审批 REBIRTH 通过 | 通过 |
| TC-APP-007 | 列表/搜索富信息字段 | 通过 |
| TC-ATT-002 | 预签名/静态地址（local） | 通过 |
| TC-STAT-001 | 行业统计 + detailed | 通过 |
| TC-STAT-002 | 区域统计 + detailed | 通过 |
| TC-AUDIT-001 | 审计字段完整（中文/actor/resource/IP） | 通过 |
| TC-NOTI-001 | 审批完成通知生成 | 通过 |
| TC-E2E-001 | 前端菜单（Admin） | 通过 |
| TC-E2E-002 | 前端菜单（Reviewer） | 通过 |
| TC-E2E-003 | 前端菜单（Operator） | 通过 |
| TC-E2E-004/5/6/7/8 | 前端关键流程（新建用户、DEFAULT 流程、审计、统计） | 通过 |

## 详细用例（节选）

- TC-AUTH-001 登录成功（Admin）
  - 前置：Admin 种子（admin@example.com/admin123）
  - 步骤：POST /auth/token（form: username/password）
  - 期望：200，返回 access_token、token_type=bearer
  - 结果：通过

- TC-RBAC-001 审计接口仅 Admin 可访问
  - 步骤：Reviewer 访问 GET /audit-logs/
  - 期望：403
  - 结果：通过

- TC-USER-001 管理员创建用户（幂等）
  - 步骤：POST /users/ {email,password,full_name,role}
  - 期望：200；重复 email 调用更新姓名/密码/角色
  - 结果：通过

- TC-APP-004 审批 DEFAULT 无附件报错（核心规则）
  - 前置：DEFAULT 申请存在且无附件；Reviewer 登录
  - 步骤：POST /applications/{id}/review {decision:APPROVED}
  - 期望：400，"Attachment required for DEFAULT approval"
  - 结果：通过

- TC-ATT-002 预签名/静态地址（local）
  - 步骤：GET /applications/{id}/attachments/presign?filename=xx.pdf
  - 期望：200，返回 {url:"/files/applications/{id}/xx.pdf"}
  - 结果：通过

- TC-AUDIT-001 审计字段完整
  - 步骤：制造新增/审核/上传操作后 GET /audit-logs/
  - 期望：items[].action 为中文，含 actor、resource、ip
  - 结果：通过

更多用例见上表标题所示。

## 需求覆盖
- 认证与 RBAC：TC-AUTH、TC-RBAC（覆盖）
- 用户管理（Admin）：TC-USER（覆盖）
- 客户/原因：TC-CUST、TC-REAS（覆盖）
- 申请/审批及规则：TC-APP（覆盖 DEFAULT 必需附件、状态机、客户状态联动）
- 附件与预签名：TC-ATT（覆盖）
- 统计（行业/区域，detailed）：TC-STAT（覆盖）
- 审计（中文/actor/resource/IP）：TC-AUDIT（覆盖）
- 通知：TC-NOTI（覆盖）
- 前端端到端：TC-E2E（覆盖菜单与关键流程）

## 如何运行并生成真实结果

后端（pytest）

```bash
# 后端依赖
uv sync
# 初始化数据库（如需）
uv run alembic upgrade head
# 运行后端用例
uv run pytest -q --maxfail=1 --disable-warnings --junitxml=report_backend.xml
grep -Eo 'tests="[0-9]+"|failures="[0-9]+"|errors="[0-9]+"|skipped="[0-9]+"' report_backend.xml | tr '\n' ' '
```

前端（构建/可扩展 E2E）

```bash
cd frontend
npm ci
npm run build
# 可选：如使用 Playwright
# npx playwright install
# npx playwright test --reporter=junit --output=playwright-report
```

运行后，将“用例结果速览”与“详细用例”中的“结果”更新为 PASS/FAIL，并可附带报告文件路径（report_backend.xml / playwright-report）。

## 备注
- 如审计页 403：请使用 Admin 账号验证。
- DEFAULT 审批失败提示“需要附件”属预期业务校验，请先上传附件再审批。
