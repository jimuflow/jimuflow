# This software is dual-licensed under the GNU General Public License (GPL)
# and a commercial license.
#
# You may use this software under the terms of the GNU GPL v3 (or, at your option,
# any later version) as published by the Free Software Foundation. See
# <https://www.gnu.org/licenses/> for details.
#
# If you require a proprietary/commercial license for this software, please
# contact us at jimuflow@gmail.com for more information.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# Copyright (C) 2024-2025  Weng Jing

import importlib
import locale
import os
import shutil
import subprocess
import sys

from PySide6.QtCore import QSettings, QObject

import jimuflow


class Utils:
    settings = QSettings(jimuflow.__project_organization__, jimuflow.__project_name__)

    @staticmethod
    def get_workspace_path():
        workspace_path = Utils.settings.value("workspace_path")
        if not workspace_path or not os.path.isdir(workspace_path):
            workspace_path = os.getcwd()
        return workspace_path

    @staticmethod
    def set_workspace_path(path: str):
        Utils.settings.setValue("workspace_path", path)

    @staticmethod
    def add_recent_app(app_path):
        recent_apps = Utils.get_recent_apps()
        if app_path in recent_apps:
            recent_apps.remove(app_path)
        recent_apps.insert(0, app_path)
        if len(recent_apps) > 10:
            recent_apps.pop()
        Utils.settings.setValue("recent_apps", recent_apps)

    @staticmethod
    def get_recent_apps():
        recent_apps = Utils.settings.value("recent_apps", [])
        if isinstance(recent_apps, str):
            recent_apps = [recent_apps]
        return recent_apps

    @staticmethod
    def load_class(type_name: str):
        module_name, class_name = type_name.rsplit('.', 1)
        module = importlib.import_module(module_name)
        return getattr(module, class_name)

    @staticmethod
    def find_ancestor(current: QObject, name: str):
        while current:
            if current.objectName() == name:
                return current
            current = current.parent()

    @staticmethod
    def get_language():
        language = Utils.settings.value("language")
        if language is None:
            language, _ = locale.getdefaultlocale()
        if language not in Utils.get_supported_languages():
            language = 'en_US'
        return language

    @staticmethod
    def set_language(language):
        Utils.settings.setValue("language", language)

    @staticmethod
    def get_supported_languages():
        return {'zh_CN': '简体中文', 'en_US': 'English (US)'}

    def open_file_in_explorer(filepath):
        """
        打开文件资源管理器并定位到指定文件或目录

        参数:
            filepath (str): 要定位的文件或目录路径
        """
        filepath = os.path.abspath(filepath)

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Path does not exist: {filepath}")

        try:
            if sys.platform == "win32":
                # Windows系统
                if os.path.isfile(filepath):
                    subprocess.run(f'explorer /select,"{filepath}"', shell=True)
                else:
                    subprocess.run(['explorer', filepath], shell=True)

            elif sys.platform == "darwin":
                # macOS系统
                if os.path.isfile(filepath):
                    subprocess.run(["open", "-R", filepath])
                else:
                    subprocess.run(["open", filepath])

            else:
                # Linux/Unix系统
                # 判断是文件还是目录
                if os.path.isfile(filepath):
                    dir_path = os.path.dirname(filepath)
                    target = filepath
                else:
                    dir_path = filepath
                    target = None

                # 尝试不同文件管理器
                managers = [
                    ["nautilus", "--select", target] if target else ["nautilus", dir_path],
                    ["dolphin", "--select", target] if target else ["dolphin", dir_path],
                    ["thunar", dir_path],
                    ["xdg-open", dir_path]
                ]

                for args in managers:
                    if args[0] and shutil.which(args[0]):
                        try:
                            subprocess.run([arg for arg in args if arg])
                            break
                        except:
                            return False
                else:
                    return False
            return True
        except:
            return False
