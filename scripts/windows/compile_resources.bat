@echo off
setlocal enabledelayedexpansion

:: 获取当前脚本所在目录
set "scripts_dir=%~dp0"
set "scripts_dir=%scripts_dir:~0,-1%"

:: 获取上上级目录
for %%i in ("%scripts_dir%") do set "parent_dir=%%~dpi"
for %%i in ("%parent_dir:~0,-1%") do set "base_dir=%%~dpi"
set "base_dir=%base_dir:~0,-1%"

:: 执行 pyside6-rcc 命令
pyside6-rcc "%base_dir%\jimuflow\icons.qrc" -o $base_dir/jimuflow/rc_icons.py "%base_dir%\jimuflow\rc_icons.py"