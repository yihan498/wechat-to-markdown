@echo off
chcp 65001 >nul
cd /d "%~dp0"

:: 先生成图标（如果还没有）
if not exist "assets\icon.ico" (
    echo 正在生成图标...
    where python >nul 2>&1 && python assets\make_icon.py && goto make_shortcut
    where python3 >nul 2>&1 && python3 assets\make_icon.py && goto make_shortcut
    where py >nul 2>&1 && py assets\make_icon.py && goto make_shortcut
    echo [警告] 未找到 Python，将使用系统默认图标
)

:make_shortcut
:: 用 PowerShell 在桌面创建快捷方式
set BAT=%~dp0抓取公众号文章.bat
set ICO=%~dp0assets\icon.ico
set WORK=%~dp0

powershell -ExecutionPolicy Bypass -Command ^
  "$wsh = New-Object -ComObject WScript.Shell; ^
   $desktop = [Environment]::GetFolderPath('Desktop'); ^
   $lnk = $wsh.CreateShortcut(\"$desktop\微信公众号 → Markdown.lnk\"); ^
   $lnk.TargetPath = '%BAT%'; ^
   $lnk.WorkingDirectory = '%WORK%'; ^
   $lnk.WindowStyle = 1; ^
   $lnk.Description = '抓取微信公众号文章，保存为 Markdown 文件'; ^
   if (Test-Path '%ICO%') { $lnk.IconLocation = '%ICO%' }; ^
   $lnk.Save(); ^
   Write-Host '快捷方式已创建到桌面！'"

echo.
echo 完成！桌面上已生成"微信公众号 → Markdown"快捷方式。
pause
