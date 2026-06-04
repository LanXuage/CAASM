# CAASM — Cyber Asset Attack Surface Management

网络资产攻击面管理系统，基于图数据库（Nebula Graph）的资产建模与管理平台。

## 架构概览

```
┌──────────┐     ┌──────────────┐     ┌──────────────┐
│   ui     │────▶│  web (API)   │────▶│    worker    │
│  Vue 3   │     │  FastAPI     │     │  Kafka       │
│  :5173   │     │  :8000       │     │  Consumer    │
└──────────┘     └──────┬───────┘     └──────┬───────┘
                        │                    │
        ┌───────────────┼────────────────────┼────────┐
        ▼               ▼                    ▼        │
  ┌──────────┐   ┌──────────┐   ┌──────────────┐     │
  │  Redis   │   │  Kafka   │   │ Nebula Graph │     │
  │  :6379   │   │  :9092   │   │   :9669      │     │
  └──────────┘   └──────────┘   └──────────────┘     │
                                ┌──────────┐         │
                                │    ES    │         │
                                │  :9200   │         │
                                └──────────┘         │
└────────────────────────────────────────────────────┘
```

## 技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| 后端框架 | FastAPI (Python) | 3.12+ |
| 前端 | Vue 3 + TypeScript + Vite | — |
| 主数据库 | Nebula Graph | 3.6 |
| 搜索引擎 | Elasticsearch | 7.17 |
| 消息队列 | Apache Kafka | 3.8 |
| 缓存 | Redis | 7.4 |
| 依赖管理 | **uv** | latest |
| 容器化 | Docker + Docker Compose | — |

## 快速开始

### 前置条件

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)（Python 包管理器）
- Docker & Docker Compose

```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 本地开发

```bash
# 克隆项目
git clone <repo-url> && cd CAASM

# 同步依赖（创建 .venv + 安装所有 workspace 成员）
uv sync --all-packages

# 启动基础设施（Nebula / Redis / Kafka / ES）
docker compose --profile dev up -d metad-dev storaged-dev graphd-dev redis-dev queue-dev es-dev init-dev

# 运行 web 服务（开发模式，热重载）
uv run --directory web uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 运行 worker 服务
uv run --directory worker python main.py
```

### 运行测试

```bash
# Web 单元测试（60 个）
PYTHONPATH=web uv run pytest tests/unit/ -q

# Worker 单元测试（12 个）
uv run pytest tests/unit_worker/ -q

# 覆盖率报告
PYTHONPATH=web uv run pytest tests/unit/ --cov=shared --cov=web --cov-report=term-missing

# 集成测试（需要 Docker）
uv run pytest tests/integration/ -m integration
```

### Docker 部署

```bash
# 构建镜像
docker build -f web/Dockerfile -t caasm-web .
docker build -f worker/Dockerfile -t caasm-worker .

# 开发模式（源码挂载，热重载）
docker compose --profile dev up -d

# 生产模式
docker compose --profile prod up -d
```

## 项目结构

```
CAASM/
├── pyproject.toml          # 根 workspace 定义 + 开发依赖
├── uv.lock                 # 锁定依赖版本（自动生成）
├── .python-version         # Python 版本声明
├── compose.yml             # Docker Compose 入口
├── base.yml                # 基础设施定义（Nebula/Redis/Kafka/ES）
├── dev.yml / prod.yml      # 环境覆盖
│
├── shared/                 # 共享 Python 包（workspace member）
│   ├── pyproject.toml
│   ├── nebula.py           # NebulaFacade（图数据库客户端）
│   ├── datetime.py         # 时区工具
│   ├── log.py              # 日志工厂
│   ├── module.py           # 配置加载
│   └── models/             # 共享 Pydantic 模型
│       └── task.py         # Task / BulkTask / 枚举
│
├── web/                    # Web API 服务（workspace member）
│   ├── pyproject.toml
│   ├── Dockerfile
│   ├── main.py             # 入口：FastAPI App + lifespan
│   ├── api/v1/             # API 路由
│   │   ├── user.py         # 用户管理 + 认证
│   │   ├── role.py         # 角色管理
│   │   ├── perm.py         # 权限管理
│   │   ├── field.py        # 字段管理
│   │   ├── field_collect.py
│   │   ├── common.py       # 验证码 / WebSocket / 文件上传
│   │   └── task.py
│   ├── model/              # Pydantic 数据模型
│   ├── common/             # 基础设施封装
│   └── deps/               # FastAPI 依赖（鉴权）
│
├── worker/                 # 后台任务 Worker（workspace member）
│   ├── pyproject.toml
│   ├── Dockerfile
│   ├── main.py
│   ├── settings.py
│   └── core/
│       ├── worker.py       # Kafka 消费循环
│       ├── task.py         # BulkTask 实现（DELETE/POST/PUT）
│       └── queue.py        # Kafka 消费者
│
├── tests/                  # 测试套件
│   ├── unit/               # 单元测试（60）
│   ├── unit_worker/        # Worker 测试（12）
│   ├── integration/        # 集成测试
│   └── pytest.ini
│
├── ui/                     # 前端（Vue 3）
├── initdb.d/               # Nebula 初始化脚本（nGQL）
└── docker/                 # 非 Python Dockerfile（ES / Spark）
```

## Workspace 依赖关系

```
caasm (root)
├── shared          # 共享包：nebula3-python, pydantic
├── web             # API 服务：FastAPI, uvicorn, redis, kafka, captcha...
│   └── depends on shared
└── worker          # 后台任务：aiokafka, msgpack
    └── depends on shared
```

使用 `uv sync --all-packages` 一次性安装所有 workspace 成员的依赖。

## 数据模型

### RBAC（用户 / 角色 / 权限）

```
caasm_user ──user_e_role──▶ caasm_role ◀──perm_e_role── caasm_perm
     │                           │                            │
     │                    role_inherit                  perm_include
     │                    role_mutex                   perm_e_group
     │                           │                            │
     ▼                           ▼                            ▼
caasm_user_group         caasm_role (继承/互斥)      caasm_perm_group
```

### BGMF（图 / 模型 / 字段）

```
caasm_graph ──model_e_graph──▶ model ──model_e_model──▶ model
                                   │
                              field_e_model
                                   │
                                   ▼
                                field ──field_e_collect──▶ field_collect
```

## API 端点

### 认证
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/captcha` | 获取图片验证码 |
| POST | `/api/v1/user/action/login` | 用户登录 |
| GET | `/api/v1/user/action/logout` | 用户登出 |
| GET | `/api/v1/user` | 获取当前用户信息 |
| GET | `/api/v1/user/menus` | 获取用户菜单权限树 |

### 用户管理
| 方法 | 路径 | 权限 |
|------|------|------|
| GET | `/api/v1/users` | user_read |
| POST | `/api/v1/user` | user_create |
| GET | `/api/v1/user/{id}` | user_read |
| PUT | `/api/v1/user/{id}` | user_modify |
| DELETE | `/api/v1/user/{id}` | user_modify |
| POST | `/api/v1/user/{id}/status` | user_modify |
| POST | `/api/v1/user/{id}/roles` | user_modify |

### 角色管理
| 方法 | 路径 | 权限 |
|------|------|------|
| GET | `/api/v1/roles` | role_read |
| POST | `/api/v1/role` | role_create |
| GET | `/api/v1/role/{id}` | role_read |
| PUT | `/api/v1/role/{id}` | role_modify |
| DELETE | `/api/v1/role/{id}` | role_modify |
| POST | `/api/v1/role/{id}/perms` | role_modify |
| POST | `/api/v1/role/{id}/users` | role_modify |
| POST | `/api/v1/role/{id}/inherit` | role_modify |
| POST | `/api/v1/role/{id}/mutex` | role_modify |

### 权限管理
| 方法 | 路径 | 权限 |
|------|------|------|
| GET | `/api/v1/perms` | perm_read |
| POST | `/api/v1/perm` | perm_create |
| GET | `/api/v1/perm/{id}` | perm_read |
| PUT | `/api/v1/perm/{id}` | perm_modify |
| DELETE | `/api/v1/perm/{id}` | perm_modify |
| POST | `/api/v1/perm/{id}/include` | perm_modify |
| GET | `/api/v1/perm-groups` | perm_read |
| POST | `/api/v1/perm-group` | perm_create |

### 字段管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/fields` | 列出字段 |
| POST | `/api/v1/field` | 创建字段 |
| PUT | `/api/v1/field/{vid}` | 更新字段 |
| DELETE | `/api/v1/field/{vid}` | 删除字段 |
| POST | `/api/v1/fields/bulk` | 批量操作（入队 Kafka） |
| GET | `/api/v1/field-collects` | 列出字段集 |

### 通用
| 方法 | 路径 | 说明 |
|------|------|------|
| WS | `/api/v1/notify` | WebSocket 实时通知 |
| POST | `/api/v1/upload` | 文件上传 |

## 功能设计

```
菜单功能
├── 概览
├── 资产查询
│   ├── 实时查询
│   ├── 资产台账
│   ├── 导出记录
│   └── 查询场景
├── 用户和权限
│   ├── 用户管理 ✅
│   ├── 权限管理 ✅
│   └── 角色管理 ✅
├── 字段和模型
│   ├── 字段管理 ✅
│   ├── 字段集管理 ✅
│   ├── 模型管理
│   └── 图管理
├── 适配器和任务
│   ├── 适配器管理
│   ├── 映射管理
│   ├── 计划管理
│   └── 任务管理
└── 系统设置
    ├── 授权许可
    └── 关于系统
```

## License

MIT