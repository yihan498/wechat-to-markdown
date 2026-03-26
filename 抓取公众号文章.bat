@echo off
chcp 65001 >nul
cd /d "%~dp0"

:: 自动查找 Python（优先 python，其次 python3，最后 py 启动器）
where python >nul 2>&1 && set PY=python && goto run
where python3 >nul 2>&1 && set PY=python3 && goto run
where py >nul 2>&1 && set PY=py && goto run

echo [错误] 未找到 Python，请先安装 Python 3.9+
echo 下载地址：https://www.python.org/downloads/
pause
exit /b 1

:run
%PY% app\main.py %*
if errorlevel 1 (
    echo.
    echo [错误] 程序运行失败，请查看上方错误信息
    pause
)
