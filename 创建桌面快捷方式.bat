@echo off
cd /d "%~dp0"

:: ── Step 1: generate icon.ico from source image (optional, non-blocking) ──
if not exist "assets\icon.ico" (
    where python >nul 2>&1 && python assets\make_icon.py
    where python3 >nul 2>&1 && python3 assets\make_icon.py
    where py     >nul 2>&1 && py      assets\make_icon.py
)

:: ── Step 2: write a temp PowerShell script (ASCII only, no inline escaping) ──
set BAT=%~dp0run_wechat_to_markdown.bat
set ICO=%~dp0assets\icon.ico
set WORK=%~dp0
set PS1=%TEMP%\mk_lnk_%RANDOM%.ps1

echo $wsh  = New-Object -ComObject WScript.Shell                          > "%PS1%"
echo $dest = [Environment]::GetFolderPath('Desktop')                     >> "%PS1%"
echo $lnk  = $wsh.CreateShortcut("$dest\wechat-to-markdown.lnk")        >> "%PS1%"
echo $lnk.TargetPath      = '%BAT%'                                      >> "%PS1%"
echo $lnk.WorkingDirectory = '%WORK%'                                    >> "%PS1%"
echo $lnk.WindowStyle     = 1                                            >> "%PS1%"
echo $lnk.Description     = 'Fetch WeChat articles to Markdown'         >> "%PS1%"
echo if (Test-Path '%ICO%') { $lnk.IconLocation = '%ICO%' }             >> "%PS1%"
echo $lnk.Save()                                                         >> "%PS1%"
echo Write-Host 'Shortcut created on Desktop: wechat-to-markdown.lnk'  >> "%PS1%"

powershell -ExecutionPolicy Bypass -File "%PS1%"
del "%PS1%"

echo.
echo Done.
pause
