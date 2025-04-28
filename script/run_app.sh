#!/bin/bash

# 启动应用
echo "启动应用服务..."
cd app && uvicorn main:app --host 0.0.0.0 --port 8000 --reload