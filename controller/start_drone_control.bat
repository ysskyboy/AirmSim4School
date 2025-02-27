@echo off
:: 请求管理员权限
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo Ask Administrator private...
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    if exist "%temp%\getadmin.vbs" ( del "%temp%\getadmin.vbs" )
    pushd "%CD%"
    CD /D "%~dp0"

echo Starting ADRL environment...
cd /D "%~dp0.."
start /WAIT "" "ADRL\ADRL.bat"

echo Starting drone control script...
cd /D "%~dp0.."
".venv\Scripts\python.exe" "pygame\airsim_keyboard_drone_control.py"

if errorlevel 1 (
    echo 运行出错，请检查Python虚拟环境是否正确配置
    pause
    exit /b 1
)

pause
