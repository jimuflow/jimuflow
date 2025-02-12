@echo off
setlocal enabledelayedexpansion

:: 获取当前脚本所在目录
set "scripts_dir=%~dp0"
set "scripts_dir=%scripts_dir:~0,-1%"

:: 获取上上级目录
for %%i in ("%scripts_dir%") do set "parent_dir=%%~dpi"
for %%i in ("%parent_dir:~0,-1%") do set "base_dir=%%~dpi"
set "base_dir=%base_dir:~0,-1%"

:: 设置 PYTHONPATH 环境变量
set "PYTHONPATH=%base_dir%"

:: 执行 pybabel 命令
pybabel update -D messages -i "%base_dir%\jimuflow\locales\messages.pot" -d "%base_dir%\jimuflow\locales" -l zh_CN --omit-header
