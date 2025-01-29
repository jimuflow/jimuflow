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
import os

from PySide6.QtCore import QSettings, QObject

from jimuflow.common.constants import APP_NAME, APP_ORGANIZATION


class Utils:
    settings = QSettings(APP_ORGANIZATION, APP_NAME)

    @staticmethod
    def get_workspace_path():
        return Utils.settings.value("workspace_path", os.getcwd())

    @staticmethod
    def set_workspace_path(path):
        Utils.settings.setValue("workspace_path", path)

    @staticmethod
    def add_recent_app(app_path):
        recent_apps = Utils.get_recent_apps()
        if app_path not in recent_apps:
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
