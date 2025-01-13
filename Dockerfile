# 使用官方 Python 基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production

# 安装系统依赖
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
COPY app.py .
COPY utils/ utils/
COPY templates/ templates/
COPY vmon-json-services/ vmon-json-services/

# 创建上传目录
RUN mkdir uploads && chmod 777 uploads

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 5000

# 修改启动命令，确保监听所有网络接口
CMD ["python", "-c", "from app import app; app.run(host='0.0.0.0', port=5000, debug=True)"] 