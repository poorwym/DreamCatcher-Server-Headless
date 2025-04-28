#!/bin/bash

# 优先关掉 brew 的 postgresql@14 服务
if brew list | grep -q postgresql@14; then
    echo "→ 检测到 Homebrew 安装了 postgresql@14"
    if brew services list | grep postgresql@14 | grep started; then
        echo "→ 正在停止 Homebrew 的 postgresql@14 服务..."
        brew services stop postgresql@14
    fi
fi

# 然后关掉自己 pgdata 下的 PostgreSQL
if [ -d "pgdata" ]; then
    echo "→ 正在关闭 pgdata 下的 PostgreSQL..."
    pg_ctl -D pgdata stop
else
    echo "pgdata 目录不存在，跳过本地 PostgreSQL 停止"
fi

echo "✓ 数据库已处理完毕"