FROM python:3.11-slim

WORKDIR /app

# 安装 Pillow 所需系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    libjpeg62-turbo-dev \
    libpng-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 不设置固定 PORT，让平台通过环境变量注入
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:$PORT", "--workers", "2", "--timeout", "120"]
