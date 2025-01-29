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
import platform
from enum import Enum
from pathlib import Path

from .package import Package
from .variable_def import VariableDef, VariableDirection
from ..locales.i18n import gettext


class ControlFlowType(Enum):
    NORMAL = "NORMAL" # 普通组件
    IF = "IF" # IF条件分支组件
    ELSE_IF = "ELSE_IF" # ELSE IF条件分支组件
    ELSE = "ELSE" # ELSE条件分支组件
    LOOP = "LOOP" # 循环组件
    BREAK = "BREAK" # 跳出循环组件
    CONTINUE = "CONTINUE" # 跳过循环组件
    RETURN = "RETURN" # 返回组件
    INVOKE = "INVOKE" # 调用流程组件
    EXIT = "EXIT" # 退出应用组件


class Platform(Enum):
    windows = "windows"
    linux = "linux"
    macos = "macos"
    other = "other"

    def localized_name(self):
        if self.value == 'windows':
            return gettext('Windows')
        elif self.value == 'linux':
            return gettext('Linux')
        elif self.value == 'macos':
            return gettext('MacOS')
        else:
            return gettext('Other')

system_name = platform.system()
if system_name == 'Windows':
    current_platform = Platform.windows
elif system_name == 'Linux':
    current_platform = Platform.linux
elif system_name == 'Darwin':
    current_platform = Platform.macos
else:
    current_platform = Platform.other


class ComponentDef:
    def __init__(self, package: Package):
        self.package = package
        self.name = ""
        self.display_name = ""
        self.variables: list[VariableDef] = []
        self.path: Path | None = None
        self.control_flow_type = ControlFlowType.NORMAL
        self.supports_error_handling = False
        self.primary_category = ""
        self.secondary_category = ""
        self.sort_no = 0
        self.help_url = ""
        self.categories = []
        self.platforms = set()

    def id(self, source_package: Package):
        if self.package.namespace == source_package.namespace and self.package.name == source_package.name:
            return self.name
        else:
            return self.package.namespace + ":" + self.package.name + ":" + self.name

    def input_variables(self) -> list[VariableDef]:
        return [v for v in self.variables if v.direction == VariableDirection.IN]

    def output_variables(self) -> list[VariableDef]:
        return [v for v in self.variables if v.direction == VariableDirection.OUT]

    def load(self, json_data: dict):
        self.name = json_data['name']
        if 'displayName' in json_data:
            self.display_name = json_data['displayName']
        if 'controlFlowType' in json_data:
            self.control_flow_type = ControlFlowType(json_data['controlFlowType'])
        if 'variables' in json_data:
            self.variables = [VariableDef.from_json(item) for item in json_data['variables']]
        if 'supportsErrorHandling' in json_data:
            self.supports_error_handling = json_data['supportsErrorHandling']
        if 'primaryCategory' in json_data:
            self.primary_category = json_data['primaryCategory']
        if 'secondaryCategory' in json_data:
            self.secondary_category = json_data['secondaryCategory']
        if 'sortNo' in json_data:
            self.sort_no = json_data['sortNo']
        if 'helpUrl' in json_data:
            self.help_url = json_data['helpUrl']
        if 'categories' in json_data:
            self.categories = json_data['categories']
        if 'platforms' in json_data:
            self.platforms = set([Platform(item) for item in json_data['platforms']])

    def load_from_file(self, path: Path):
        with open(path, 'r', encoding='utf-8') as f:
            self.load(json.load(f))
            self.path = path

    def get_variable(self, name: str):
        for v in self.variables:
            if v.name == name:
                return v

    def get_input_variable(self, name: str):
        for v in self.variables:
            if v.name == name and v.direction == VariableDirection.IN:
                return v

    def get_output_variable(self, name: str):
        for v in self.variables:
            if v.name == name and v.direction == VariableDirection.OUT:
                return v

    def ensure_output_name(self, output_name: str):
        if self.get_output_variable(output_name) is None:
            raise Exception(f"组件{self.name}未定义输出变量{output_name}")

    def is_supported_on_current_platform(self):
        return not self.platforms or current_platform in self.platforms

    def __eq__(self, other):
        return (self.package == other.package and self.name == other.name
                and self.control_flow_type == other.control_flow_type
                and self.supports_error_handling == other.supports_error_handling
                and self.primary_category == other.primary_category
                and self.secondary_category == other.secondary_category
                and self.sort_no == other.sort_no and self.help_url == other.help_url
                and len(self.variables) == len(other.variables)
                and all(v1 == v2 for v1, v2 in zip(self.variables, other.variables))
                and self.categories == other.categories
                and self.platforms == other.platforms)


class PrimitiveComponentDef(ComponentDef):
    def __init__(self, package: Package):
        super().__init__(package)
        self.module_name = ""
        self.class_name = ""
        self.ui_module_name = ""
        self.ui_class_name = ""

    def load(self, json_data: dict):
        super().load(json_data)
        type_name = json_data['type']
        last_dot_index = type_name.rindex('.')
        self.module_name = type_name[0:last_dot_index]
        self.class_name = type_name[last_dot_index + 1:]
        if 'uiType' in json_data:
            ui_type_name = json_data['uiType']
            last_dot_index = ui_type_name.rindex('.')
            self.ui_module_name = ui_type_name[0:last_dot_index]
            self.ui_class_name = ui_type_name[last_dot_index + 1:]
