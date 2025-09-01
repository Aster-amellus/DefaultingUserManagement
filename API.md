违约客户管理系统 - API 文档（v2.1）

说明：本文件列出后端 REST API 的路径、参数、权限与关键业务约束，覆盖认证、用户、客户、原因、申请、附件、统计与审计模块。

身份与权限
- 认证：OAuth2 Password（JWT）。登录成功后在请求头携带 Authorization: Bearer <token>
- 角色：Admin、Reviewer、Operator。标注“(Admin)”表示仅管理员可用；“(Reviewer|Admin)”表示审核角色和管理员均可调用；未注明则三种角色均可用（登录后）。

认证与当前用户
- POST /auth/token
	- form: username, password
	- 响应：{ access_token, token_type }
- GET /users/me
	- 响应：当前登录用户信息

用户管理（Admin）
- POST /users/
	- body: { email, password, full_name?, role? }
	- 幂等：若 email 存在则更新姓名/密码/角色
- GET /users/
- GET /users/{id}
- PATCH /users/{id}
	- body: { full_name?, password?, role? }
- DELETE /users/{id}

客户（Customers）
- POST /customers/
- GET /customers/
- GET /customers/{id}
- PATCH /customers/{id}
- DELETE /customers/{id}

原因（Reasons）
- GET /reasons/
	- query: type=DEFAULT|REBIRTH（可选，过滤类型）
- POST /reasons/ (Admin)
- PATCH /reasons/{id} (Admin)
- DELETE /reasons/{id} (Admin)

申请（Applications）
- POST /applications/
	- body: { type: DEFAULT|REBIRTH, customer_id, latest_external_rating?, reason_id, severity: HIGH|MEDIUM|LOW, remark? }
	- 规则校验：
		- 客户已违约时禁止发起 DEFAULT；客户非违约时禁止发起 REBIRTH
		- reason 必须启用
- GET /applications/
	- query: customer_name?, status?
- GET /applications/search
	- query: customer_name?, status?, type?
	- 响应：富信息（含 customer_name、reason_description、创建/审核人姓名等）
- GET /applications/{id}
	- 响应：同上（富信息）
- POST /applications/{id}/review (Reviewer|Admin)
	- body: { decision: APPROVED|REJECTED }
	- 规则：当 type=DEFAULT 且 decision=APPROVED 时，必须先上传至少一个附件，否则 400: "Attachment required for DEFAULT approval"
	- 通过后自动联动 customers.is_default（DEFAULT->True / REBIRTH->False）并向申请人发通知

附件（Attachments）
- POST /applications/{id}/attachments
	- form: file（单文件）
- GET /applications/{id}/attachments
- GET /applications/{id}/attachments/presign
	- query: filename
	- 响应：{ url }（S3 场景返回预签名 URL；本地返回可直接访问的 /files/... 路径）

统计（Stats）
- GET /stats/industry
	- query: year?、detailed?=true|false（默认 false）
	- detailed=true 时：额外返回各类占比、近12个月趋势数组
- GET /stats/region
	- 同上

审计日志（Audit Logs, Admin）
- GET /audit-logs/
	- query: user_id?, action?, target_type?, start?, end?, limit?（默认100）
	- 响应：{ items: [ { id, timestamp, actor, action, resource, ip } ] }
	- 说明：action 为中文标签（如 登录/新增/审核/上传附件等），resource 形如 "Application:123" 或 "HTTP:/path"

错误码约定
- 400 业务规则不满足（如重复发起、原因禁用、审批缺少附件、状态非待审等）
- 401 未认证或令牌失效
- 403 无权限访问
- 404 资源不存在

版本与兼容
- 当前版本 v2.1，与前端 1.x 兼容。后续增加字段时遵循向后兼容策略，新增只读字段不破坏现有客户端。