#!/bin/bash
scripts_dir=$(dirname "$0")
base_dir=$(dirname "$scripts_dir")
old_pwd=$(pwd)
cd $base_dir
source venv/bin/activate

# 获取所有自定义编辑器模块的--hidden-import参数
PACKAGE_NAME="jimuflow.gui.components"
MODULES=$(python -c "
import pkgutil
import $PACKAGE_NAME
modules = [name for _, name, _ in pkgutil.walk_packages($PACKAGE_NAME.__path__, '$PACKAGE_NAME.')]
print(' '.join(modules))
")
HIDDEN_IMPORTS=""
for module in $MODULES; do
    HIDDEN_IMPORTS="$HIDDEN_IMPORTS --hidden-import=$module"
done

#PLAYWRIGHT_BROWSERS_PATH=0 playwright install chromium

python generate_version_info.py

mkdocs build -f config/en/mkdocs_help.yml
mkdocs build -f config/zh/mkdocs_help.yml

pyinstaller --name JimuFlow \
  --icon jimuflow/icons/jimuflow.png \
  --add-data "jimuflow/locales/zh_CN/LC_MESSAGES/messages.mo:./jimuflow/locales/zh_CN/LC_MESSAGES" \
  --add-data "jimuflow/packages:./jimuflow/packages" \
  --add-data "jimuflow/resources:./jimuflow/resources" \
  --add-data "help:./jimuflow/help" \
  --hidden-import=jimuflow.datatypes.web_page \
  --hidden-import=jimuflow.datatypes.windows_types \
  --hidden-import=jimuflow.components \
  --hidden-import=jimuflow.components.core \
  --hidden-import=jimuflow.components.table \
  --hidden-import=jimuflow.components.web_automation \
  --hidden-import=jimuflow.components.mouse_keyboard \
  --hidden-import=jimuflow.components.windows_automation \
  $HIDDEN_IMPORTS \
  --noconsole \
  jimuflow/gui/main_window.py

cd $old_pwd
