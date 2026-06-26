# IndusAI Lab | 工业 AI 与制造数字化技术站

这是一个聚焦工业 AI 与制造数字化实践的技术站，核心展示“基于 AI 的整车视觉检测系统”和“螺栓扭矩质量预测系统”两个生产项目。

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

- Projects：展示整车视觉检测和螺栓扭矩质量预测两个核心项目案例。
- Blog：展示两个核心项目从方案、数据、模型到生产部署的工程复盘。
- Admin：管理文章、项目和评论审核。
- Auth：支持登录、注册、session、CSRF 校验和管理员权限。
- SEO：提供页面 meta、Open Graph、Twitter Card、RSS、sitemap 和 robots.txt。
- i18n：支持中文和英文页面文案切换。

当数据库不可用或没有已发布内容时，公共页面会展示两个核心项目及其工程复盘作为 fallback；后台中同 slug 的内容仍可覆盖默认项目内容。

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
