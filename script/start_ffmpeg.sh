#!/bin/sh

# 等待 RTMP 服务可连接（mediamtx 启动成功）
until nc -z mediamtx 1935; do
  echo "Waiting for mediamtx (RTMP port 1935)..."
  sleep 2
done

echo "mediamtx is up. Starting ffmpeg..."

# 启动推流，不断重试（例如连接失败自动重试）
while true; do
  ffmpeg -re -f lavfi -i color=c=red:size=1280x720:rate=30 \
    -vcodec libx264 -preset veryfast -tune zerolatency \
    -f flv rtmp://mediamtx:1935/mystream

  echo "ffmpeg exited, retrying in 5s..."
  sleep 5
done