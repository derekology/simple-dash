FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package*.json ./

RUN npm ci

COPY frontend/ ./

RUN npm run build

FROM python:3.11-slim AS backend-builder

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir --user -r requirements.txt

COPY app/ ./app/

FROM python:3.11-slim

WORKDIR /app

RUN addgroup --gid 1001 --system python && \
    adduser --system --uid 1001 --gid 1001 python

COPY --from=backend-builder --chown=python:python /root/.local /home/python/.local
COPY --from=backend-builder --chown=python:python /app/app ./app
COPY --from=frontend-builder --chown=python:python /app/frontend/dist ./frontend/dist

USER python

ENV PATH=/home/python/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    MAX_FILE_SIZE=10485760 \
    MAX_FILES=12 \
    DEV=False

EXPOSE $PORT

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT:-8000}/health').read()" || exit 1

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
