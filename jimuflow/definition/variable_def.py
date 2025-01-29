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

from enum import Enum

from jimuflow.locales.i18n import gettext


class VariableDirection(Enum):
    IN = "IN"  # 输入变量
    OUT = "OUT"  # 输出变量
    LOCAL = "LOCAL"  # 本地变量


gettext("IN VARIABLE")
gettext("OUT VARIABLE")
gettext("LOCAL VARIABLE")


class VariableUiGroup(Enum):
    GENERAL = "general"
    ADVANCED = "advanced"


class VariableUiDependencyOperator(Enum):
    EQUALS = "=="
    NOT_EQUALS = "!="
    IN = "in"
    NOT_IN = "not_in"
    IS_EMPTY = "is_empty"
    NOT_EMPTY = "not_empty"
    IS_TRUE = "is_true"
    IS_FALSE = "is_false"

    @property
    def display_name(self) -> str:
        if self == VariableUiDependencyOperator.IN:
            return gettext("contains in")
        elif self == VariableUiDependencyOperator.NOT_IN:
            return gettext("not contains in")
        elif self == VariableUiDependencyOperator.IS_EMPTY:
            return gettext("is empty")
        elif self == VariableUiDependencyOperator.NOT_EMPTY:
            return gettext("is not empty")
        elif self == VariableUiDependencyOperator.EQUALS:
            return gettext("equals")
        elif self == VariableUiDependencyOperator.NOT_EQUALS:
            return gettext("not equals")
        elif self == VariableUiDependencyOperator.IS_TRUE:
            return gettext("is true")
        elif self == VariableUiDependencyOperator.IS_FALSE:
            return gettext("is false")
        else:
            return self.value


class VariableUiDependency():
    def __init__(self, variable_name: str, operator: str, value):
        self.variable_name = variable_name
        self.operator = operator
        self.value = value

    def is_satisfied(self, value):
        if self.operator == VariableUiDependencyOperator.IN.value:
            return value in self.value
        elif self.operator == VariableUiDependencyOperator.NOT_IN.value:
            return value not in self.value
        elif self.operator == VariableUiDependencyOperator.IS_EMPTY.value:
            return value is None or value == ''
        elif self.operator == VariableUiDependencyOperator.NOT_EMPTY.value:
            return value is not None and value != ''
        elif self.operator == VariableUiDependencyOperator.EQUALS.value:
            return value == self.value
        elif self.operator == VariableUiDependencyOperator.NOT_EQUALS.value:
            return value != self.value
        elif self.operator == VariableUiDependencyOperator.IS_TRUE.value:
            return value is True
        elif self.operator == VariableUiDependencyOperator.IS_FALSE.value:
            return value is False
        else:
            raise Exception(f"Unknown operator: {self.operator}")

    def is_valid(self):
        return bool(self.variable_name) and bool(self.operator)

    def to_json(self):
        json_data = {
            "variableName": self.variable_name,
            "operator": self.operator,
        }
        if self.value is not None:
            json_data["value"] = self.value
        return json_data

    def __eq__(self, other):
        return (self.variable_name == other.variable_name and self.operator == other.operator
                and self.value == other.value)


class VariableUiInputType(Enum):
    LINE_EDIT = "line_edit"  # 单行文本框
    TEXT_EDIT = "text_edit"  # 多行文本框
    NUMBER_EDIT = "number_edit"  # 数字输入框
    COMBO_BOX = "combo_box"  # 下拉框
    EXPRESSION = "expression"  # 表达式输入框
    VARIABLE = "variable"  # 变量选择框
    CHECK_BOX = "check_box"  # 复选框
    CUSTOM = "custom"  # 自定义输入组件

    @property
    def display_name(self) -> str:
        if self == VariableUiInputType.LINE_EDIT:
            return gettext("Text input box")
        elif self == VariableUiInputType.TEXT_EDIT:
            return gettext("Multi line text input box")
        elif self == VariableUiInputType.NUMBER_EDIT:
            return gettext("Number input box")
        elif self == VariableUiInputType.COMBO_BOX:
            return gettext("Drop down box")
        elif self == VariableUiInputType.EXPRESSION:
            return gettext("Expression input box")
        elif self == VariableUiInputType.VARIABLE:
            return gettext("Variable input box")
        elif self == VariableUiInputType.CHECK_BOX:
            return gettext("Check box")
        elif self == VariableUiInputType.CUSTOM:
            return gettext("Custom input control")
        else:
            return self.value

    def support(self, type_name: str) -> bool:
        if self == VariableUiInputType.LINE_EDIT:
            return type_name == "text"
        elif self == VariableUiInputType.TEXT_EDIT:
            return type_name == "text"
        elif self == VariableUiInputType.NUMBER_EDIT:
            return type_name == "number"
        elif self == VariableUiInputType.COMBO_BOX:
            return type_name == "text"
        elif self == VariableUiInputType.VARIABLE:
            return type_name == "text"
        elif self == VariableUiInputType.CHECK_BOX:
            return type_name == "bool"
        else:
            return True


class VariableUiInputValueType(Enum):
    EXPRESSION = "expression"
    LITERAL = "literal"


class VariableUiInputOption():
    def __init__(self, label: str, value: str):
        self.label = label
        self.value = value

    def to_json(self):
        return {
            "label": self.label,
            "value": self.value
        }

    def __eq__(self, other):
        return self.label == other.label and self.value == other.value


class VariableUiConfig:

    def __init__(self):
        self.label = ""
        self.group = VariableUiGroup.GENERAL
        self.required = True
        self.sort_no = 0
        self.depends_on = VariableUiDependency('', '', '')
        self.input_type = VariableUiInputType.LINE_EDIT
        self.input_editor_type = ""
        self.input_value_type = None
        self.placeholder = ""
        self.options: list[VariableUiInputOption] = []
        self.help_info = ""
        self.extra = {}

    def from_json(self, json_data: dict):
        if "label" in json_data:
            self.label = json_data["label"]
        if "group" in json_data:
            self.group = VariableUiGroup(json_data["group"])
        if "required" in json_data:
            self.required = json_data["required"]
        if "sortNo" in json_data:
            self.sort_no = json_data["sortNo"]
        if "dependsOn" in json_data:
            self.depends_on = VariableUiDependency(json_data["dependsOn"]["variableName"],
                                                   json_data["dependsOn"]["operator"],
                                                   json_data["dependsOn"].get("value", ""))
        if "inputType" in json_data:
            self.input_type = VariableUiInputType(json_data["inputType"])
        if "inputEditorType" in json_data:
            self.input_editor_type = json_data["inputEditorType"]
        if "inputValueType" in json_data:
            self.input_value_type = VariableUiInputValueType(json_data["inputValueType"])
        if "placeholder" in json_data:
            self.placeholder = json_data["placeholder"]
        if "options" in json_data:
            self.options = [VariableUiInputOption(o["label"], o["value"]) for o in json_data["options"]]
        if "helpInfo" in json_data:
            self.help_info = json_data["helpInfo"]
        if "extra" in json_data:
            self.extra = json_data["extra"]

    def to_json(self):
        json_data = {}
        if self.label:
            json_data["label"] = self.label
        if self.group != VariableUiGroup.GENERAL:
            json_data["group"] = self.group.value
        if not self.required:
            json_data["required"] = self.required
        if self.sort_no:
            json_data["sortNo"] = self.sort_no
        if self.input_type != VariableUiInputType.LINE_EDIT:
            json_data["inputType"] = self.input_type.value
        if self.input_type == VariableUiInputType.COMBO_BOX:
            json_data["options"] = [o.to_json() for o in self.options]
        elif self.input_type == VariableUiInputType.CUSTOM:
            json_data["inputEditorType"] = self.input_editor_type
        if self.placeholder:
            json_data["placeholder"] = self.placeholder
        if self.help_info:
            json_data["helpInfo"] = self.help_info
        if self.extra:
            json_data["extra"] = self.extra
        if self.depends_on and self.depends_on.is_valid():
            json_data["dependsOn"] = self.depends_on.to_json()
        return json_data

    def __eq__(self, other):
        result = (self.label == other.label and self.group == other.group and self.required == other.required
                  and self.sort_no == other.sort_no and self.depends_on == other.depends_on
                  and self.input_type == other.input_type and self.input_editor_type == other.input_editor_type
                  and self.input_value_type == other.input_value_type and self.placeholder == other.placeholder
                  and self.help_info == other.help_info and self.extra == other.extra
                  and len(self.options) == len(other.options))
        if not result:
            return False
        return all([o1 == o2 for o1, o2 in zip(self.options, other.options)])


class VariableDef:
    """变量定义"""

    def __init__(self, name="", var_type="", direction=VariableDirection.LOCAL, element_type="", default_value=None):
        self.name = name
        self.type = var_type
        self.direction = VariableDirection.LOCAL
        self.elementType = element_type
        self.defaultValue = default_value
        self.ui_config = VariableUiConfig()

    def load(self, json_data: dict):
        self.name = json_data["name"]
        self.type = json_data["type"]
        self.direction = VariableDirection(json_data["direction"])
        if self.type == 'list':
            self.elementType = json_data["elementType"]
        if "defaultValue" in json_data:
            self.defaultValue = json_data["defaultValue"]
        if "uiConfig" in json_data:
            self.ui_config.from_json(json_data["uiConfig"])

    def to_json(self):
        json_data = {
            "name": self.name,
            "type": self.type,
            "direction": self.direction.name,
        }
        if self.elementType:
            json_data["elementType"] = self.elementType
        if self.defaultValue is not None and self.defaultValue != '':
            json_data["defaultValue"] = self.defaultValue
        if self.direction != VariableDirection.LOCAL:
            ui_config_json = self.ui_config.to_json()
            if len(ui_config_json) > 0:
                json_data["uiConfig"] = ui_config_json
        return json_data

    @classmethod
    def from_json(cls, json_data: dict):
        input_def = cls()
        input_def.load(json_data)
        return input_def

    def __eq__(self, other):
        return (self.name == other.name and self.type == other.type and self.direction == other.direction
                and self.elementType == other.elementType and self.defaultValue == other.defaultValue
                and self.ui_config == other.ui_config)
