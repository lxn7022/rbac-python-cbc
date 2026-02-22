#!/bin/bash

# RBAC Python 启动脚本

echo "============================================"
echo "RBAC Python - CodeBuddy Edition"
echo "============================================"
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "[错误] 虚拟环境不存在，请先创建："
    echo "  python -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "[警告] .env 文件不存在，使用 .env.example 创建："
    echo "  cp .env.example .env"
    echo "  然后编辑 .env 文件配置数据库连接"
    echo ""
fi

# 运行应用
echo "[启动] 启动应用服务器..."
echo ""
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
