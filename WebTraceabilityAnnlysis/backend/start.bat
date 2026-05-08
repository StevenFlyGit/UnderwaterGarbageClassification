@echo off
echo ========================================
echo 海洋垃圾溯源分析后端服务启动脚本 (Node.js)
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] 检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Node.js，请先安装Node.js 18+
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Node.js环境正常
echo.

echo [2/3] 安装依赖包...
npm install >nul 2>&1
if errorlevel 1 (
    echo ❌ 依赖安装失败，请检查网络连接
    pause
    exit /b 1
)

echo ✅ 依赖安装完成
echo.

echo [3/3] 启动后端服务...
echo.
echo ========================================
echo 🌊 海洋垃圾溯源分析API
echo ========================================
echo.
echo 服务地址: http://localhost:8080/trace
echo 健康检查: http://localhost:8080/health
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

npm start

pause
