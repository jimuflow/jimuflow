#!/bin/bash
scripts_dir=$(dirname "$0")
base_dir=$(dirname "$scripts_dir")
old_pwd=$(pwd)
cd $base_dir
source venv/bin/activate

# 生成组件定义中引用的模块所需要的--hidden-import参数
HIDDEN_IMPORTS=$(python scripts/gen_hidden_imports.py)

python generate_version_info.py

mkdocs build -f config/en/mkdocs_help.yml
mkdocs build -f config/zh/mkdocs_help.yml

PLAYWRIGHT_BROWSERS_PATH=0 playwright install chromium

pyinstaller --name JimuFlow \
  --icon jimuflow/icons/jimuflow.png \
  --add-data "jimuflow/locales/zh_CN/LC_MESSAGES/messages.mo:./jimuflow/locales/zh_CN/LC_MESSAGES" \
  --add-data "jimuflow/packages:./jimuflow/packages" \
  --add-data "jimuflow/resources:./jimuflow/resources" \
  --add-data "help:./jimuflow/help" \
  $HIDDEN_IMPORTS \
  --noconsole \
  jimuflow/gui/main_window.py

cd $old_pwd
