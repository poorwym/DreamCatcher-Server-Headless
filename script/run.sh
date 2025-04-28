# !/bin/bash
chmod +x script/run_db.sh
chmod +x script/run_app.sh

./script/run_db.sh

sleep 3

./script/run_app.sh


# 注意：此脚本不会自动关闭数据库，需要手动关闭
# 可以使用 pg_ctl -D pgdata stop 命令关闭数据库
