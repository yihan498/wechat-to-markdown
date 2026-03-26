@echo off
chcp 65001 >nul
cd /d "%~dp0"

:: Read clipboard via PowerShell (no pyperclip needed)
for /f "delims=" %%C in ('powershell -NoProfile -Command "Get-Clipboard"') do set CLIP=%%C

:: Validate it's a WeChat URL
echo %CLIP% | findstr /i "mp.weixin.qq.com" >nul
if errorlevel 1 (
    echo [ERROR] Clipboard does not contain a WeChat article link.
    echo         Please copy the article link in WeChat first, then run again.
    echo.
    echo Current clipboard: %CLIP%
    pause
    exit /b 1
)

:: Find Python
where python  >nul 2>&1 && set PY=python  && goto run
where python3 >nul 2>&1 && set PY=python3 && goto run
where py      >nul 2>&1 && set PY=py      && goto run

echo [ERROR] Python not found. Install Python 3.9+ from https://www.python.org/downloads/
pause
exit /b 1

:run
%PY% app\main.py --url "%CLIP%" %*
if errorlevel 1 (
    echo.
    echo [ERROR] Program exited with an error. See details above.
    pause
)
