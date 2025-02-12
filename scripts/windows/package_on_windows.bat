@echo off

set oldPath=%cd%

set scriptPath=%~dp0
echo "%scriptPath%"

cd /d "%scriptPath%"
cd ..\..

@REM call venv\Scripts\activate

mkdocs build -f config\en\mkdocs_help.yml
mkdocs build -f config\zh\mkdocs_help.yml

:: 获取所有自定义编辑器模块的--hidden-import参数
set "PACKAGE_NAME=jimuflow.gui.components"
setlocal enabledelayedexpansion
for /f "delims=" %%A in ('python -c "import pkgutil, importlib; package = importlib.import_module('%PACKAGE_NAME%'); modules = [module.name for module in pkgutil.iter_modules(package.__path__)]; print(','.join(modules))" 2^>nul') do set "MODULES=%%A"
if "%MODULES%"=="" (
    echo Failed to retrieve modules for package %PACKAGE_NAME%. Ensure the package is installed and valid.
    exit /b 1
)
echo Modules found: %MODULES%
echo Generating hidden-import arguments...
set "HIDDEN_IMPORTS="
for %%M in (%MODULES%) do (
    set "HIDDEN_IMPORTS=!HIDDEN_IMPORTS! --hidden-import=%PACKAGE_NAME%.%%M"
)

@REM echo %HIDDEN_IMPORTS%

@REM set PLAYWRIGHT_BROWSERS_PATH=0
@REM playwright install chromium

pyinstaller --name JimuFlow ^
  --icon jimuflow\icons\jimuflow.png ^
  --add-data "jimuflow\locales\zh_CN\LC_MESSAGES\messages.mo:.\jimuflow\locales\zh_CN\LC_MESSAGES" ^
  --add-data "jimuflow\packages:.\jimuflow\packages" ^
  --add-data "jimuflow\resources:.\jimuflow\resources" ^
  --add-data "help:.\jimuflow\help" ^
  --hidden-import=jimuflow.datatypes.web_page ^
  --hidden-import=jimuflow.datatypes.windows_types ^
  --hidden-import=jimuflow.components ^
  --hidden-import=jimuflow.components.core ^
  --hidden-import=jimuflow.components.table ^
  --hidden-import=jimuflow.components.web_automation ^
  --hidden-import=jimuflow.components.mouse_keyboard ^
  --hidden-import=jimuflow.components.windows_automation ^
  %HIDDEN_IMPORTS% ^
  --noconsole ^
  jimuflow\gui\main_window.py

endlocal

deactivate

cd /d "%oldPath%"
