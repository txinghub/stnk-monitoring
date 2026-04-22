#!/bin/bash
# STNK Dashboard Auto-Start Script
# 确保端口8085的dashboard自动启动

DASHBOARD_DIR="/root/stnk_monitoring/web_dashboard_new"
LOG_FILE="$DASHBOARD_DIR/autostart.log"

echo "==========================================" >> "$LOG_FILE"
echo "$(date): Starting STNK Dashboard Auto-Start" >> "$LOG_FILE"

# 检查端口是否被占用
if ss -tlnp | grep -q :8085; then
    echo "$(date): Port 8085 is already in use" >> "$LOG_FILE"
    echo "$(date): Checking if it's our dashboard..." >> "$LOG_FILE"
    
    # 获取占用端口的PID
    PID=$(ss -tlnp | grep :8085 | awk '{print $NF}' | cut -d= -f2 | cut -d, -f1)
    if ps -p "$PID" -o cmd= | grep -q "server.py"; then
        echo "$(date): Dashboard is already running (PID: $PID)" >> "$LOG_FILE"
        exit 0
    else
        echo "$(date): Port 8085 occupied by other process (PID: $PID), killing..." >> "$LOG_FILE"
        kill -9 "$PID" 2>/dev/null
        sleep 2
    fi
fi

# 启动dashboard
echo "$(date): Starting dashboard on port 8085..." >> "$LOG_FILE"
cd "$DASHBOARD_DIR" || exit 1
nohup python3 server.py >> server.log 2>&1 &

# 等待启动
sleep 3

# 验证启动成功
if ss -tlnp | grep -q :8085; then
    NEW_PID=$(ss -tlnp | grep :8085 | awk '{print $NF}' | cut -d= -f2 | cut -d, -f1)
    echo "$(date): Dashboard started successfully (PID: $NEW_PID)" >> "$LOG_FILE"
    echo "$(date): Access at http://localhost:8085/" >> "$LOG_FILE"
else
    echo "$(date): ERROR: Failed to start dashboard" >> "$LOG_FILE"
    exit 1
fi

echo "$(date): Auto-start completed" >> "$LOG_FILE"
echo "==========================================" >> "$LOG_FILE"