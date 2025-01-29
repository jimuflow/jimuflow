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

import json
import re
import shutil
import uuid
from datetime import datetime
from pathlib import Path

WEB_ELEMENT_GROUP_PREFIX = "group_"
WEB_ELEMENT_PREFIX = "element_"


class Package:

    def __init__(self):
        self.name = ""
        self.namespace = ""
        self.version = ""
        self.main_process = ""
        self.dependencies = []
        self.components = []
        self.path: Path | None = None

    def load(self, path: Path):
        package_json_file = path / "jimuflow.json"
        with open(package_json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            self.name = json_data["name"]
            self.namespace = json_data["namespace"]
            self.version = json_data["version"]
            if "mainProcess" in json_data:
                self.main_process = json_data["mainProcess"]
            if "dependencies" in json_data:
                self.dependencies = json_data["dependencies"]
            self.path = path

    def save(self):
        self.path.mkdir(parents=True, exist_ok=True)
        package_json_file = self.path / "jimuflow.json"
        with open(package_json_file, 'w', encoding='utf-8') as f:
            json_data = {
                "name": self.name,
                "namespace": self.namespace,
                "version": self.version,
                "mainProcess": self.main_process,
                "dependencies": self.dependencies
            }
            json.dump(json_data, f, ensure_ascii=False, indent=2)

    def get_web_elements_path(self, create_if_not_exists=False):
        web_elements_path = self.path / "elements" / "web_elements"
        if create_if_not_exists:
            web_elements_path.mkdir(parents=True, exist_ok=True)
        return web_elements_path

    def get_web_element_groups(self):
        web_elements_path = self.get_web_elements_path()
        if not web_elements_path.exists():
            return []
        result = []
        for child in web_elements_path.iterdir():
            if not child.is_dir() or not child.name.startswith(WEB_ELEMENT_GROUP_PREFIX):
                continue
            group_name = child.name[len(WEB_ELEMENT_GROUP_PREFIX):]
            group = {
                "name": group_name
            }
            group_icon = child / "group_icon.png"
            if group_icon.exists():
                group["icon"] = group_icon
            result.append(group)
        return result

    def add_web_element_group(self, name: str, icon: Path):
        """
        添加一个web元素组，如果组名已存在，则返回已存在的组名
        :param name: 组名，如果组名中包含空白符，则会被替换为下划线
        :param icon: 组图标
        :return: 组名
        """
        if icon and not icon.exists():
            raise FileNotFoundError(f"Icon file {icon} not found.")
        if icon and not icon.name.endswith(".png"):
            raise ValueError(f"Icon file {icon} must be a png file.")
        name = re.sub(r"\s+", "_", name)
        group_path = self.get_web_element_group_path(name)
        if group_path.exists():
            icon_path = group_path / "group_icon.png"
            return name, str(icon_path) if icon_path.exists() else None
        group_path.mkdir(parents=True)
        if icon:
            icon_path = group_path / "group_icon.png"
            shutil.copy(icon, icon_path)
            return name, str(icon_path)
        return name, None

    def get_web_element_group_path(self, group_name):
        web_elements_path = self.get_web_elements_path()
        return web_elements_path / f"{WEB_ELEMENT_GROUP_PREFIX}{group_name}"

    def remove_web_element_group(self, name: str):
        """
        删除一个web元素组，如果组不存在，则返回False
        :param name: 组名
        :return: 是否删除成功
        """
        group_path = self.get_web_element_group_path(name)
        if group_path.exists():
            shutil.rmtree(group_path)
            return True
        return False

    def get_web_elements_by_group(self, group_name: str):
        group_path = self.get_web_element_group_path(group_name)
        if not group_path.exists():
            return []
        result = []
        for child in group_path.iterdir():
            if not child.is_file() or not child.name.startswith(WEB_ELEMENT_PREFIX) or not child.name.endswith(
                    ".jsonl"):
                continue
            with open(child, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                element_basic_info = json.loads(first_line)
                element_basic_info['id'] = child.name[len(WEB_ELEMENT_PREFIX):-len(".jsonl")]
                result.append(element_basic_info)
        return result

    def add_web_element(self, group_name: str, element_info: dict, element_snapshot: Path):
        """
        添加一个web元素，如果元素已存在，则返回已存在的元素id
        :param group_name: 组名
        :param element_info: 元素信息
        :param element_snapshot: 元素截图
        :return: 元素id
        """
        group_path = self.get_web_element_group_path(group_name)
        if not group_path.exists():
            raise ValueError(f"Group {group_name} not found.")
        if element_snapshot and not element_snapshot.name.endswith(".png"):
            raise ValueError(f"Element snapshot {element_snapshot} must be a png file.")
        element_id = uuid.uuid4().hex
        if element_snapshot:
            snapshot_path = group_path / f"{WEB_ELEMENT_PREFIX}{element_id}.png"
            shutil.copy(element_snapshot, snapshot_path)
        element_path = group_path / f"{WEB_ELEMENT_PREFIX}{element_id}.jsonl"
        self._write_element_jsonl(element_path, element_info)
        return element_id

    def _write_element_jsonl(self, element_path, element_info):
        basic_info = {
            "name": element_info['name'],
            "iframeXPath": element_info["iframeXPath"],
            "elementXPath": element_info["elementXPath"],
        }
        if "createdAt" not in element_info:
            element_info["createdAt"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            element_info["updatedAt"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        details = {
            "webPageUrl": element_info["webPageUrl"],
            "inIframe": element_info["inIframe"],
            "useCustomIframeXPath": element_info["useCustomIframeXPath"],
            "iframePath": element_info["iframePath"],
            "customIframeXPath": element_info["customIframeXPath"],
            "useCustomElementXPath": element_info["useCustomElementXPath"],
            "elementPath": element_info["elementPath"],
            "customElementXPath": element_info["customElementXPath"]
        }
        with open(element_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(basic_info, ensure_ascii=False) + "\n")
            f.write(json.dumps(details, ensure_ascii=False))

    def update_web_element(self, group_name: str, element_id: str, element_info: dict):
        group_path = self.get_web_element_group_path(group_name)
        if not group_path.exists():
            raise ValueError(f"Group {group_name} not found.")
        element_path = group_path / f"{WEB_ELEMENT_PREFIX}{element_id}.jsonl"
        if not element_path.exists():
            raise ValueError(f"Element {element_id} not found.")
        self._write_element_jsonl(element_path, element_info)

    def remove_web_element(self, group_name: str, element_id: str):
        group_path = self.get_web_element_group_path(group_name)
        if not group_path.exists():
            raise ValueError(f"Group {group_name} not found.")
        element_path = group_path / f"{WEB_ELEMENT_PREFIX}{element_id}.jsonl"
        if not element_path.exists():
            raise ValueError(f"Element {element_id} not found.")
        snapshot_path = group_path / f"{WEB_ELEMENT_PREFIX}{element_id}.png"
        if snapshot_path.exists():
            snapshot_path.unlink()
        element_path.unlink()

    def get_web_element_by_id(self, element_id):
        web_elements_path = self.get_web_elements_path()
        if not web_elements_path.exists():
            return None
        for group_path in web_elements_path.iterdir():
            if not group_path.is_dir() or not group_path.name.startswith(WEB_ELEMENT_GROUP_PREFIX):
                continue
            for child in group_path.iterdir():
                if not child.is_file() or not child.name.startswith(WEB_ELEMENT_PREFIX) or not child.name.endswith(
                        ".jsonl"):
                    continue
                id = child.name[len(WEB_ELEMENT_PREFIX):-len(".jsonl")]
                if id != element_id:
                    continue
                group_name = group_path.name[len(WEB_ELEMENT_GROUP_PREFIX):]
                group_icon_path: Path = group_path / "group_icon.png"
                with open(child, 'r', encoding='utf-8') as f:
                    element_basic_info = json.loads(f.readline())
                    element_details_info = json.loads(f.readline())
                    element_basic_info.update(element_details_info)
                    element_basic_info['id'] = id
                    element_basic_info['groupName'] = group_name
                    if group_icon_path.exists():
                        element_basic_info['groupIcon'] = str(group_icon_path)
                    snapshot_path = group_path / f"{WEB_ELEMENT_PREFIX}{element_id}.png"
                    if snapshot_path.exists():
                        element_basic_info['snapshot'] = str(snapshot_path)
                    return element_basic_info

    def get_window_elements_path(self, create_if_not_exists=False):
        window_elements_path = self.path / "elements" / "window_elements"
        if create_if_not_exists:
            window_elements_path.mkdir(parents=True, exist_ok=True)
        return window_elements_path

    def get_window_element_groups(self):
        window_elements_path = self.get_window_elements_path()
        if not window_elements_path.exists():
            return []
        result = []
        for child in window_elements_path.iterdir():
            if not child.is_dir() or not child.name.startswith(WEB_ELEMENT_GROUP_PREFIX):
                continue
            group_name = child.name[len(WEB_ELEMENT_GROUP_PREFIX):]
            group = {
                "name": group_name
            }
            group_icon = child / "group_icon.png"
            if group_icon.exists():
                group["icon"] = group_icon
            result.append(group)
        return result

    def add_window_element_group(self, name: str, icon: Path):
        """
        添加一个window元素组，如果组名已存在，则返回已存在的组名
        :param name: 组名，如果组名中包含空白符，则会被替换为下划线
        :param icon: 组图标
        :return: 组名
        """
        if icon and not icon.exists():
            raise FileNotFoundError(f"Icon file {icon} not found.")
        if icon and not icon.name.endswith(".png"):
            raise ValueError(f"Icon file {icon} must be a png file.")
        name = re.sub(r"\s+", "_", name)
        group_path = self.get_window_element_group_path(name)
        if group_path.exists():
            icon_path = group_path / "group_icon.png"
            return name, str(icon_path) if icon_path.exists() else None
        group_path.mkdir(parents=True)
        if icon:
            icon_path = group_path / "group_icon.png"
            shutil.copy(icon, icon_path)
            return name, str(icon_path)
        return name, None

    def get_window_element_group_path(self, group_name):
        window_elements_path = self.get_window_elements_path()
        return window_elements_path / f"{WEB_ELEMENT_GROUP_PREFIX}{group_name}"

    def remove_window_element_group(self, name: str):
        """
        删除一个window元素组，如果组不存在，则返回False
        :param name: 组名
        :return: 是否删除成功
        """
        group_path = self.get_window_element_group_path(name)
        if group_path.exists():
            shutil.rmtree(group_path)
            return True
        return False

    def get_window_elements_by_group(self, group_name: str):
        group_path = self.get_window_element_group_path(group_name)
        if not group_path.exists():
            return []
        result = []
        for child in group_path.iterdir():
            if not child.is_file() or not child.name.startswith(WEB_ELEMENT_PREFIX) or not child.name.endswith(
                    ".jsonl"):
                continue
            with open(child, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                element_basic_info = json.loads(first_line)
                element_basic_info['id'] = child.name[len(WEB_ELEMENT_PREFIX):-len(".jsonl")]
                result.append(element_basic_info)
        return result

    def add_window_element(self, group_name: str, element_info: dict, element_snapshot: Path):
        """
        添加一个window元素，如果元素已存在，则返回已存在的元素id
        :param group_name: 组名
        :param element_info: 元素信息
        :param element_snapshot: 元素截图
        :return: 元素id
        """
        group_path = self.get_window_element_group_path(group_name)
        if not group_path.exists():
            raise ValueError(f"Group {group_name} not found.")
        if element_snapshot and not element_snapshot.name.endswith(".png"):
            raise ValueError(f"Element snapshot {element_snapshot} must be a png file.")
        element_id = uuid.uuid4().hex
        if element_snapshot:
            snapshot_path = group_path / f"{WEB_ELEMENT_PREFIX}{element_id}.png"
            shutil.copy(element_snapshot, snapshot_path)
        element_path = group_path / f"{WEB_ELEMENT_PREFIX}{element_id}.jsonl"
        self._write_window_element_jsonl(element_path, element_info)
        return element_id

    def _write_window_element_jsonl(self, element_path, element_info):
        basic_info = {
            "name": element_info['name'],
            "windowXPath": element_info["windowXPath"],
            "elementXPath": element_info["elementXPath"],
        }
        if "createdAt" not in element_info:
            element_info["createdAt"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            element_info["updatedAt"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        details = {
            "useCustomWindowXPath": element_info["useCustomWindowXPath"],
            "windowPath": element_info["windowPath"],
            "customWindowXPath": element_info["customWindowXPath"],
            "useCustomElementXPath": element_info["useCustomElementXPath"],
            "elementPath": element_info["elementPath"],
            "customElementXPath": element_info["customElementXPath"]
        }
        with open(element_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(basic_info, ensure_ascii=False) + "\n")
            f.write(json.dumps(details, ensure_ascii=False))

    def update_window_element(self, group_name: str, element_id: str, element_info: dict):
        group_path = self.get_window_element_group_path(group_name)
        if not group_path.exists():
            raise ValueError(f"Group {group_name} not found.")
        element_path = group_path / f"{WEB_ELEMENT_PREFIX}{element_id}.jsonl"
        if not element_path.exists():
            raise ValueError(f"Element {element_id} not found.")
        self._write_window_element_jsonl(element_path, element_info)

    def remove_window_element(self, group_name: str, element_id: str):
        group_path = self.get_window_element_group_path(group_name)
        if not group_path.exists():
            raise ValueError(f"Group {group_name} not found.")
        element_path = group_path / f"{WEB_ELEMENT_PREFIX}{element_id}.jsonl"
        if not element_path.exists():
            raise ValueError(f"Element {element_id} not found.")
        snapshot_path = group_path / f"{WEB_ELEMENT_PREFIX}{element_id}.png"
        if snapshot_path.exists():
            snapshot_path.unlink()
        element_path.unlink()

    def get_window_element_by_id(self, element_id):
        window_elements_path = self.get_window_elements_path()
        if not window_elements_path.exists():
            return None
        for group_path in window_elements_path.iterdir():
            if not group_path.is_dir() or not group_path.name.startswith(WEB_ELEMENT_GROUP_PREFIX):
                continue
            for child in group_path.iterdir():
                if not child.is_file() or not child.name.startswith(WEB_ELEMENT_PREFIX) or not child.name.endswith(
                        ".jsonl"):
                    continue
                id = child.name[len(WEB_ELEMENT_PREFIX):-len(".jsonl")]
                if id != element_id:
                    continue
                group_name = group_path.name[len(WEB_ELEMENT_GROUP_PREFIX):]
                group_icon_path: Path = group_path / "group_icon.png"
                with open(child, 'r', encoding='utf-8') as f:
                    element_basic_info = json.loads(f.readline())
                    element_details_info = json.loads(f.readline())
                    element_basic_info.update(element_details_info)
                    element_basic_info['id'] = id
                    element_basic_info['groupName'] = group_name
                    if group_icon_path.exists():
                        element_basic_info['groupIcon'] = str(group_icon_path)
                    snapshot_path = group_path / f"{WEB_ELEMENT_PREFIX}{element_id}.png"
                    if snapshot_path.exists():
                        element_basic_info['snapshot'] = str(snapshot_path)
                    return element_basic_info

    def __eq__(self, other):
        return self.name == other.name and self.namespace == other.namespace and self.version == other.version
