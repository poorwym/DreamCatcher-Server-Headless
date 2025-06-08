FROM python:3.12-slim-bullseye

WORKDIR /app

COPY ./app /app
COPY ./configs /configs

# 替换为中科大APT源并安装依赖
RUN cp /etc/apt/sources.list /etc/apt/sources.list.bak && \
    sed -i 's|http://deb.debian.org|https://mirrors.ustc.edu.cn|g' /etc/apt/sources.list && \
    sed -i 's|http://security.debian.org|https://mirrors.ustc.edu.cn/debian-security|g' /etc/apt/sources.list && \
    apt-get update && apt-get install -y \
    wget \
    bzip2 \
    ca-certificates \
    curl \
    git \
    clang            \
    llvm-dev         \
    libclang-dev     \
    build-essential \
    gcc \
    cmake \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \

ENV LIBCLANG_PATH=/usr/lib/llvm-17/lib

RUN curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain stable --profile default && \
    echo '[source.crates-io]\nreplace-with = "ustc"\n[source.ustc]\nregistry = "https://mirrors.ustc.edu.cn/crates.io-index"' >> ~/.cargo/config

# 根据架构选择正确的Miniconda安装包并使用中科大镜像安装
RUN if [ "$(uname -m)" = "x86_64" ]; then \
        MINICONDA_URL="https://mirrors.ustc.edu.cn/anaconda/miniconda/Miniconda3-latest-Linux-x86_64.sh"; \
    elif [ "$(uname -m)" = "aarch64" ]; then \
        MINICONDA_URL="https://mirrors.ustc.edu.cn/anaconda/miniconda/Miniconda3-latest-Linux-aarch64.sh"; \
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

# 网络优化配置
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# 设置中科大 pip 源
RUN mkdir -p /root/.pip && echo "[global]\nindex-url = https://pypi.mirrors.ustc.edu.cn/simple" > /root/.pip/pip.conf

# 设置中科大 conda 源，删除默认源并设置conda-forge镜像映射
RUN rm -f /opt/conda/.condarc && \
    conda config --remove-key channels || true && \
    conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/conda-forge && \
    conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/main && \
    conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/free && \
    conda config --set show_channel_urls yes && \
    conda config --set channel_alias https://mirrors.ustc.edu.cn/anaconda && \
    conda config --set custom_channels.conda-forge https://mirrors.ustc.edu.cn/anaconda/cloud && \
    conda config --set auto_activate_base false && \
    conda config --set offline false && \
    conda env create -f /configs/environment.yml

# 设置默认环境路径
ENV PATH /opt/conda/envs/dreamcatcher/bin:/opt/conda/bin:$PATH

# 切换到 bash 环境

SHELL ["/bin/bash", "--login", "-c"]

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]