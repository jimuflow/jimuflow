#!/bin/bash
scripts_dir=$(dirname "$0")
base_dir=$(dirname "$scripts_dir")
old_pwd=$(pwd)
cd $base_dir
source venv/bin/activate

python generate_version_info.py

mkdocs build -f config/en/mkdocs_help.yml
mkdocs build -f config/zh/mkdocs_help.yml

# 生成组件定义中引用的模块所需要的--hidden-import参数
HIDDEN_IMPORTS=$(python scripts/gen_hidden_imports.py)

# 生成pyinstaller的spec文件
pyi-makespec --name JimuFlow \
  --icon jimuflow/icons/jimuflow.png \
  --add-data "jimuflow/locales/zh_CN/LC_MESSAGES/messages.mo:./jimuflow/locales/zh_CN/LC_MESSAGES" \
  --add-data "jimuflow/packages:./jimuflow/packages" \
  --add-data "jimuflow/resources:./jimuflow/resources" \
  --add-data "help:./jimuflow/help" \
  $HIDDEN_IMPORTS \
  --noconsole \
  jimuflow/gui/main_window.py

# 自定义pyinstaller的spec文件，添加版本号
python scripts/customize_macos_pyinstaller_spec.py

# 生成macOS的app
pyinstaller JimuFlow.spec

# 安装浏览器
PLAYWRIGHT_BROWSERS_PATH=dist/JimuFlow.app/Contents/Resources/playwright/driver/package/.local-browsers playwright install chromium

# 添加文件后需要重新签名
codesign --force --deep --sign - dist/JimuFlow.app

cd $old_pwd
