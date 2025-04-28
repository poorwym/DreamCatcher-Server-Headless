#!/usr/bin/env bash
set -e  # 任一命令非 0 立即退出

DATA_DIR="pgdata"
LOG_FILE="$DATA_DIR/server.log"
DB_NAME="dreamcatcher"
DB_PORT=5432

#------------------------------------------
# 1. 依赖检查
#------------------------------------------
command -v pg_ctl   >/dev/null || { echo "未找到 pg_ctl";   exit 1; }
command -v initdb   >/dev/null || { echo "未找到 initdb";   exit 1; }
command -v createdb >/dev/null || { echo "未找到 createdb"; exit 1; }

#------------------------------------------
# 2. 初始化（仅第一次）
#------------------------------------------
if [ ! -f "$DATA_DIR/PG_VERSION" ]; then
    echo "→ 初始化 PostgreSQL 数据目录 …"
    initdb -D "$DATA_DIR" -E UTF8 --locale=en_US.UTF-8 

    echo "→ 修改监听 & 认证配置 …"
    echo "listen_addresses = '*'" >> "$DATA_DIR/postgresql.conf"

    cat > "$DATA_DIR/pg_hba.conf" <<EOF
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     trust
host    all             all             127.0.0.1/32            trust
host    all             all             ::1/128                 trust
host    all             all             0.0.0.0/0               md5
host    all             all             ::/0                    md5
EOF
fi

#------------------------------------------
# 3. 若已在运行则跳过启动
#------------------------------------------
if pg_ctl -D "$DATA_DIR" status >/dev/null 2>&1; then
    echo "✓ PostgreSQL 已在运行，跳过启动"
else
    echo "→ 启动 PostgreSQL …"
    pg_ctl -D "$DATA_DIR" -l "$LOG_FILE" -o "-p $DB_PORT" start
fi

#------------------------------------------
# 4. 等待数据库就绪（最长 15 秒）
#------------------------------------------
echo -n "→ 等待数据库就绪"
for i in {1..15}; do
    if pg_isready -h localhost -p $DB_PORT -q; then
        echo " ✓"
        break
    fi
    echo -n "."
    sleep 1
done
#------------------------------------------
# 5. 创建超级用户 postgres
#------------------------------------------
if ! psql -h localhost -p $DB_PORT -U alexwu -d postgres -At -c "SELECT 1 FROM pg_roles WHERE rolname='postgres';" | grep -q 1; then
    echo "→ 创建超级用户 postgres"
    psql -h localhost -p $DB_PORT -U alexwu -d postgres -c "CREATE ROLE postgres WITH LOGIN SUPERUSER CREATEDB CREATEROLE PASSWORD 'postgres';"
fi

#------------------------------------------
# 6. 创建业务库（若不存在）
#------------------------------------------
if ! psql -h localhost -p $DB_PORT -U postgres -Atcq \
        "SELECT 1 FROM pg_database WHERE datname='${DB_NAME}'"; then
    echo "→ 创建业务库 ${DB_NAME}"
    createdb -h localhost -p $DB_PORT -U postgres "$DB_NAME"

    echo "→ 执行初始化 SQL …"
    [ -f db/init.sql ]          && psql -h localhost -p $DB_PORT -U postgres -d "$DB_NAME" -f db/init.sql
    # [ -f db/create_tables.sql ] && psql -h localhost -p $DB_PORT -U postgres -d "$DB_NAME" -f db/create_tables.sql
fi

# 确认pg_ctl真正启动成功
if ! pg_ctl -D "$DATA_DIR" status >/dev/null 2>&1; then
    echo "❌ PostgreSQL 启动失败，请检查日志"
    exit 1
fi

echo "✓ 数据库准备完毕"
