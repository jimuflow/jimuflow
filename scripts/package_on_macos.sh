#!/bin/bash
scripts_dir=$(dirname "$0")
base_dir=$(dirname "$scripts_dir")
old_pwd=$(pwd)
cd $base_dir
source venv/bin/activate

python generate_version_info.py

mkdocs build -f config/en/mkdocs_help.yml
mkdocs build -f config/zh/mkdocs_help.yml

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

# 生成pyinstaller的spec文件
pyi-makespec --name JimuFlow \
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

# 自定义pyinstaller的spec文件，添加版本号
python scripts/customize_macos_pyinstaller_spec.py

# 生成macOS的app
pyinstaller JimuFlow.spec

# 安装浏览器
PLAYWRIGHT_BROWSERS_PATH=dist/JimuFlow.app/Contents/Resources/playwright/driver/package/.local-browsers playwright install chromium

# 添加文件后需要重新签名
codesign --force --deep --sign - dist/JimuFlow.app

# 生成macOS的dmg
cd dist
git clone https://github.com/create-dmg/create-dmg.git
cd ..
mkdir dist/dmg
mv dist/JimuFlow.app dist/dmg/JimuFlow.app
dist/create-dmg/create-dmg \
  --volname "JimuFlow" \
  --background "scripts/dmg_bg.png" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --icon "JimuFlow.app" 200 190 \
  --hide-extension "JimuFlow.app" \
  --app-drop-link 600 185 \
  "dist/JimuFlow.dmg" \
  "dist/dmg"

cd $old_pwd
