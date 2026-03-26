@echo off
cd /d "%~dp0"

echo === wechat-to-markdown setup ===
echo.

:: ── 1. Find Python ──────────────────────────────────────────────────────────
where python >nul 2>&1 && set PY=python && goto check_ver
where python3 >nul 2>&1 && set PY=python3 && goto check_ver
where py     >nul 2>&1 && set PY=py     && goto check_ver

echo [ERROR] Python not found. Install Python 3.9+ from https://www.python.org/downloads/
pause
exit /b 1

:check_ver
for /f "tokens=2" %%v in ('%PY% --version 2^>^&1') do set PYVER=%%v
echo [OK] Python %PYVER% found (%PY%)

:: ── 2. Install dependencies ─────────────────────────────────────────────────
echo.
echo Installing dependencies...
%PY% -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] pip install failed.
    pause
    exit /b 1
)
echo [OK] Dependencies installed.

:: ── 3. Create config.yaml from example if missing ───────────────────────────
echo.
if not exist "config\config.yaml" (
    copy "config\config.example.yaml" "config\config.yaml" >nul
    echo [OK] config\config.yaml created from example.
    echo      ^>^> Please edit config\config.yaml and set your save_dir path.
) else (
    echo [OK] config\config.yaml already exists.
)

:: ── 4. Generate icon.ico from icon_source.png if both exist ─────────────────
echo.
if exist "icon_source.png" (
    if not exist "assets\icon.ico" (
        echo Generating icon...
        %PY% assets\make_icon.py
    )
)

:: ── 5. Create desktop shortcut ──────────────────────────────────────────────
echo.
echo Creating desktop shortcut...
set BAT=%~dp0run_wechat_to_markdown.bat
set ICO=%~dp0assets\icon.ico
set WORK=%~dp0
set PS1=%TEMP%\mk_lnk_%RANDOM%.ps1

echo $wsh  = New-Object -ComObject WScript.Shell                          > "%PS1%"
echo $dest = [Environment]::GetFolderPath('Desktop')                     >> "%PS1%"
echo $lnk  = $wsh.CreateShortcut("$dest\wechat-to-markdown.lnk")        >> "%PS1%"
echo $lnk.TargetPath       = '%BAT%'                                     >> "%PS1%"
echo $lnk.WorkingDirectory = '%WORK%'                                    >> "%PS1%"
echo $lnk.WindowStyle      = 1                                           >> "%PS1%"
echo $lnk.Description      = 'Fetch WeChat articles to Markdown'        >> "%PS1%"
echo if (Test-Path '%ICO%') { $lnk.IconLocation = '%ICO%' }             >> "%PS1%"
echo $lnk.Save()                                                         >> "%PS1%"
echo Write-Host '[OK] Shortcut created on Desktop: wechat-to-markdown'  >> "%PS1%"

powershell -ExecutionPolicy Bypass -File "%PS1%"
del "%PS1%"

echo.
echo ════════════════════════════════════════════════
echo  Setup complete!
echo  Next step: edit config\config.yaml
echo    - Set save_dir to your Obsidian folder path
echo  Then: double-click wechat-to-markdown on Desktop
echo ════════════════════════════════════════════════
echo.
pause
