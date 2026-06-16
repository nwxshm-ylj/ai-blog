# 李宝帅 | 工业AI与制造数字化作品集

这是一个个人 AI 工程作品集网站，用于展示工业 AI、制造数字化、工业视觉检测、制造质量数据分析、Python 后端系统、半导体数据分析实践，以及 RAG / Agent 应用探索。

网站定位为可发布、可后台维护、支持 SEO 和中英文切换的个人技术作品集。

## 技术栈

- FastAPI async routes
- Jinja2 templates
- TailwindCSS
- SQLAlchemy 2.0 async ORM
- PostgreSQL
- Alembic
- Docker Compose
- Session-based auth

## 项目模块

```text
app/
  api/routes/        首页、项目、博客、后台、登录、SEO、健康检查路由
  core/              配置与日志
  db/                async SQLAlchemy engine 与 session
  dependencies/      依赖注入与权限校验
  middleware/        请求中间件
  models/            SQLAlchemy 模型
  repositories/      数据访问层
  schemas/           Pydantic schema
  services/          业务服务层
  static/            Tailwind 构建产物、上传文件与静态资源
  templates/         Jinja2 页面与组件
  utils/             上传等通用工具
  web/               i18n、模板、Markdown、CSRF、flash helpers
alembic/             数据库迁移
```

## 功能说明

- Projects：展示工业视觉、OCR、制造质量分析、扭矩监控、SECOM 半导体分析和 RAG 工业知识库等项目案例。
- Blog：展示工业 AI、制造数据分析、半导体数据分析、RAG 和 FastAPI 工程方向的文章。
- Admin：管理文章、项目和评论审核。
- Auth：支持登录、注册、session、CSRF 校验和管理员权限。
- SEO：提供页面 meta、Open Graph、Twitter Card、RSS、sitemap 和 robots.txt。
- i18n：支持中文和英文页面文案切换。

当数据库中没有已发布项目或文章时，服务层会展示作品集方向的 fallback 内容；后台发布真实内容后会优先展示数据库内容。

## 本地启动

```bash
cp .env.example .env
python -m venv .venv
pip install -r requirements.txt
python -m alembic upgrade head
uvicorn app.main:app --reload
```

默认 `.env.example` 面向本机开发，PostgreSQL 地址为 `localhost:15432`。Docker Compose 会覆盖 API 容器内的 `DATABASE_URL`，让容器连接到 `db:5432`。

健康检查：

```bash
curl http://localhost:8000/health
```

## TailwindCSS

```bash
npm install
npm run build:css
```

开发时监听样式变化：

```bash
npm run dev:css
```

## Docker 启动

```bash
cp .env.example .env
docker compose up --build
```

首次启动数据库后执行迁移：

```bash
docker compose exec api python -m alembic upgrade head
```

也可以在本机虚拟环境中执行：

```bash
python -m alembic upgrade head
```

生产环境需要准备真实环境变量：

```bash
cp .env.production.example .env.production
# edit .env.production and replace POSTGRES_PASSWORD, DATABASE_URL, SECRET_KEY
docker compose -f docker-compose.prod.yml --env-file .env.production config
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
```

`SECRET_KEY` 必须在生产环境中设置为足够长的随机值，不要复用本地开发值。

## 数据库迁移

创建迁移：

```bash
alembic revision --autogenerate -m "describe change"
```

执行迁移：

```bash
python -m alembic upgrade head
```

## 后台管理

本地开发可以创建或重置管理员账号：

```bash
python -m app.scripts.create_dev_admin
```

默认本地账号：

```text
email: admin@example.com
username: admin
password: admin123
```

登录地址：

```text
http://127.0.0.1:8000/auth/login
```

后台入口：

```text
http://127.0.0.1:8000/admin
```
