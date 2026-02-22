@echo off
REM RBAC Python 启动脚本

echo ============================================
echo RBAC Python - CodeBuddy Edition
echo ============================================
echo.

REM 检查虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo [错误] 虚拟环境不存在，请先创建：
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 检查 .env 文件
if not exist ".env" (
    echo [警告] .env 文件不存在，使用 .env.example 创建：
    echo   copy .env.example .env
    echo   然后编辑 .env 文件配置数据库连接
    echo.
)

REM 运行应用
echo [启动] 启动应用服务器...
echo.
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

pause
