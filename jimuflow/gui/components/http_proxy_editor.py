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

from PySide6.QtWidgets import QWidget, QGridLayout, QComboBox

from jimuflow.datatypes import DataTypeRegistry
from jimuflow.definition import VariableDef
from jimuflow.gui.expression_edit_v3 import ExpressionEditV3
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.expression import rename_variable_in_dict, get_variable_reference_in_dict


class HttpProxyEditor(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._proxy_type_editor = QComboBox()
        self._proxy_type_editor.addItems(["HTTP", "HTTPS", "SOCKS5"])
        self._proxy_host_editor = ExpressionEditV3()
        self._proxy_host_editor.setPlaceholderText(gettext("host"))
        self._proxy_port_editor = ExpressionEditV3()
        self._proxy_port_editor.setPlaceholderText(gettext("port"))
        self._proxy_user_editor = ExpressionEditV3()
        self._proxy_user_editor.setPlaceholderText(gettext("user"))
        self._proxy_password_editor = ExpressionEditV3()
        self._proxy_password_editor.setPlaceholderText(gettext("password"))
        self._layout.addWidget(self._proxy_type_editor, 0, 0)
        self._layout.addWidget(self._proxy_host_editor, 0, 1)
        self._layout.addWidget(self._proxy_port_editor, 0, 2)
        self._layout.addWidget(self._proxy_user_editor, 0, 3)
        self._layout.addWidget(self._proxy_password_editor, 0, 4)
        self._layout.setColumnStretch(0, 0)
        self._layout.setColumnStretch(1, 2)
        self._layout.setColumnStretch(2, 1)
        self._layout.setColumnStretch(3, 1)
        self._layout.setColumnStretch(4, 1)

    def get_value(self):
        return {
            "type": self._proxy_type_editor.currentText(),
            "host": self._proxy_host_editor.get_expression(),
            "port": self._proxy_port_editor.get_expression(),
            "user": self._proxy_user_editor.get_expression(),
            "password": self._proxy_password_editor.get_expression(),
        }

    def set_value(self, value: dict):
        self._proxy_type_editor.setCurrentText(value.get("type", "HTTP"))
        self._proxy_host_editor.set_expression(value.get("host", ""))
        self._proxy_port_editor.set_expression(value.get("port", ""))
        self._proxy_user_editor.set_expression(value.get("user", ""))
        self._proxy_password_editor.set_expression(value.get("password", ""))

    def set_variables(self, variables: list[VariableDef], type_registry: DataTypeRegistry):
        self._proxy_host_editor.set_variables(variables, type_registry)
        self._proxy_port_editor.set_variables(variables, type_registry)
        self._proxy_user_editor.set_variables(variables, type_registry)
        self._proxy_password_editor.set_variables(variables, type_registry)

    def validate(self):
        errors = []
        if not self._proxy_host_editor.get_expression():
            errors.append(gettext("proxy host is required"))
        elif not self._proxy_host_editor.validate_expression():
            errors.append(gettext("proxy host is invalid"))

        if not self._proxy_port_editor.get_expression():
            errors.append(gettext("proxy port is required"))
        elif not self._proxy_port_editor.validate_expression():
            errors.append(gettext("proxy port is invalid"))

        if self._proxy_user_editor.get_expression() and not self._proxy_user_editor.validate_expression():
            errors.append(gettext("proxy user is invalid"))

        if self._proxy_password_editor.get_expression() and not self._proxy_password_editor.validate_expression():
            errors.append(gettext("proxy password is invalid"))

        if self._proxy_password_editor.get_expression() and not self._proxy_user_editor.get_expression():
            errors.append(gettext("proxy user is required when proxy password is set"))

        return errors

    def rename_variable_in_value(self, value, old_name, new_name):
        if value is None:
            return value, False
        update_count = 0
        for item in value:
            if rename_variable_in_dict(item, ['host', 'port', 'user', 'password'], old_name, new_name):
                update_count += 1
        return value, update_count > 0

    def get_variable_reference_in_value(self, value, var_name):
        if value is None:
            return 0
        count = 0
        for item in value:
            count += get_variable_reference_in_dict(item, ['host', 'port', 'user', 'password'], var_name)
        return count
