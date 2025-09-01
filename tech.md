违约客户管理系统 - 技术实现与选型文档 (v2.0)
1. 具体实现目标
1.1 数据库层

目标: 使用PostgreSQL设计并创建数据库表结构，以支持所有业务需求。

核心实体:

新增: users, roles, audit_logs 表用于支持权限和审计功能。

customers: 客户主表，包含行业、区域等信息，并有一个核心的is_default状态字段。

reasons: 统一管理违约和重生原因的配置表。

applications: 记录所有违约和重生申请的核心流水表。

application_attachments: 存储申请相关的附件信息。

1.2 后端服务层

目标: 使用Python开发一套遵循RESTful风格的API服务。

任务:

实现所有业务功能的接口。

新增: 实现基于JWT (JSON Web Tokens) 的用户认证和基于角色的授权机制。FastAPI的依赖注入系统非常适合实现此功能。

确保API的性能和安全性。

1.3 核心业务逻辑实现

目标: 在后端服务中精确实现核心业务规则。

关键点:

状态机: 实现applications表的状态流转逻辑（PENDING -> APPROVED / REJECTED）。

数据同步: 在审核通过时，通过事务确保applications状态和customers的is_default状态同步更新。

统计查询: 编写高效的SQL聚合查询。

新增 - 审计日志: 使用中间件 (Middleware) 或装饰器 (Decorator) 自动为标记为关键操作的API端点创建审计日志。

2. 技术选型 (无变化)
遵循“务实、高效、稳定”的原则，技术选型保持不变：

整体架构: 单体三层架构 (Monolithic Three-Tier Architecture)

数据库: PostgreSQL

后端技术栈:

语言: Python 3.9+

包管理器： uv

Web框架: FastAPI

ORM: SQLAlchemy

部署方案: Docker + Docker Compose