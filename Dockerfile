FROM python:3.11-slim

WORKDIR /app

COPY ./app /app
COPY ./configs /app/configs

# 安装必要的依赖
RUN apt-get update && apt-get install -y \
    wget \
    bzip2 \
    ca-certificates \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 根据架构选择正确的Miniconda安装包
RUN if [ "$(uname -m)" = "x86_64" ]; then \
        MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"; \
    elif [ "$(uname -m)" = "aarch64" ]; then \
        MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh"; \
    else \
        echo "Unsupported architecture: $(uname -m)"; \
        exit 1; \
    fi && \
    wget $MINICONDA_URL -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p /opt/conda && \
    rm /tmp/miniconda.sh

# 设置环境变量
ENV PATH /opt/conda/bin:$PATH
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# 创建conda环境并激活
RUN conda env create -f configs/environment.yml && \
    echo "source activate dreamcatcher" > ~/.bashrc

# 使用conda运行环境
SHELL ["/bin/bash", "--login", "-c"]
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "dreamcatcher"]

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]