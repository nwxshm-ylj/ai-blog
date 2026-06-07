FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/library/node:22-alpine AS assets

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY tailwind.config.js ./
COPY app/static/src ./app/static/src
COPY app/templates ./app/templates

RUN npm run build:css


FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/library/python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app

COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip -i https://mirrors.cloud.tencent.com/pypi/simple \
    && pip install --no-cache-dir -r requirements.txt -i https://mirrors.cloud.tencent.com/pypi/simple

COPY --chown=app:app . .

COPY --from=assets --chown=app:app /app/app/static/css/app.css ./app/static/css/app.css

RUN mkdir -p /app/app/static/uploads \
    && chown -R app:app /app/app/static/uploads

USER app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]