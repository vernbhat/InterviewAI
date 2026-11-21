# Single-service image: builds the web app, then serves it from FastAPI.
FROM node:20-slim AS web
WORKDIR /src
COPY package.json package-lock.json ./
COPY apps/web/package.json apps/web/
RUN npm ci
COPY apps/web apps/web
RUN npm run build

FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends g++ && rm -rf /var/lib/apt/lists/*
WORKDIR /app/services/ai
COPY services/ai/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/ai .
COPY --from=web /src/apps/web/dist /app/apps/web/dist
RUN useradd --create-home runner && mkdir -p /data && chown runner /data
USER runner
ENV INTERVIEWAI_DB=/data/interviewai.db STATIC_DIR=/app/apps/web/dist PORT=8000
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
