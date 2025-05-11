FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    mariadb-client \
    libmariadb-dev \
    build-essential \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /server

COPY src/server .
COPY assets ./static

RUN pip install --no-cache-dir -r requirements.txt
CMD [
  "uvicorn", "app.app", "--host", "0.0.0.0", "--port", "8080", "--log-level", "info", "--timeout-keep-alive", "60","--http", "httptools"]