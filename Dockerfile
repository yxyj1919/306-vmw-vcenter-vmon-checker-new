# 构建阶段
FROM python:3.11-alpine AS builder

# 设置工作目录
WORKDIR /build

# 安装构建依赖
RUN apk add --no-cache \
    gcc \
    g++ \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev \
    openblas-dev \
    gfortran \
    build-base \
    linux-headers \
    cargo \
    git \
    make \
    cmake \
    && python -m venv /opt/venv \
    && . /opt/venv/bin/activate

# 复制依赖文件
COPY requirements.txt .

# 构建依赖
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

# 运行阶段
FROM python:3.11-alpine

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    PORT=5000 \
    PATH="/opt/venv/bin:$PATH"

# 安装运行时依赖
RUN apk add --no-cache \
    libstdc++ \
    openblas \
    curl \
    && adduser -D appuser \
    && mkdir -p uploads \
    && chown -R appuser:appuser /app \
    && chmod 777 uploads

# 从构建阶段复制虚拟环境和构建好的 wheels
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /build/wheels /wheels

# 安装 Python 包
RUN . /opt/venv/bin/activate \
    && pip install --no-cache-dir /wheels/*

# 切换到非 root 用户
USER appuser

# 复制应用文件
COPY --chown=appuser:appuser . .

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# 暴露端口
EXPOSE ${PORT}

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "2", "--timeout", "120", "app:app"] 