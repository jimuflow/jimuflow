@echo off

set oldPath=%cd%

set scriptPath=%~dp0
echo "%scriptPath%"

cd /d "%scriptPath%"
cd ..\..

call venv\Scripts\activate

python generate_version_info.py

mkdocs build -f config\en\mkdocs_help.yml
mkdocs build -f config\zh\mkdocs_help.yml

:: 生成组件定义中引用的模块所需要的--hidden-import参数
for /f "delims=" %%A in ('python scripts\gen_hidden_imports.py') do set HIDDEN_IMPORTS=%%A

set PLAYWRIGHT_BROWSERS_PATH=0
playwright install chromium

pyinstaller --name JimuFlow ^
  --icon jimuflow\icons\jimuflow.png ^
  --add-data "jimuflow\locales\zh_CN\LC_MESSAGES\messages.mo:.\jimuflow\locales\zh_CN\LC_MESSAGES" ^
  --add-data "jimuflow\packages:.\jimuflow\packages" ^
  --add-data "jimuflow\resources:.\jimuflow\resources" ^
  --add-data "help:.\jimuflow\help" ^
  %HIDDEN_IMPORTS% ^
  --noconsole ^
  jimuflow\gui\main_window.py

endlocal

deactivate

cd /d "%oldPath%"
