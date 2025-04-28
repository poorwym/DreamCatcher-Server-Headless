#!/bin/bash

# 直接找到 uvicorn 的 pid 并杀掉
PIDS=$(ps aux | grep "uvicorn main:app" | grep -v grep | awk '{print $2}')

if [ -z "$PIDS" ]; then
    echo "未找到运行中的 FastAPI 应用"
else
    echo "正在关闭 FastAPI 应用..."
    kill $PIDS

    sleep 2

    # 确认是否彻底杀掉了
    for pid in $PIDS; do
        if ps -p $pid > /dev/null; then
            echo "PID $pid 仍在运行，强制杀掉..."
            kill -9 $pid
        fi
    done

    echo "✓ FastAPI 应用已关闭"
fi