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

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QGridLayout, QComboBox

from jimuflow.datatypes import DataTypeRegistry
from jimuflow.definition import VariableDef
from jimuflow.gui.components.file_path_editor import OpenFilePathEdit
from jimuflow.gui.components.list_editor import ListEditor
from jimuflow.gui.expression_edit_v3 import ExpressionEditV3
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.expression import rename_variable_in_dict, \
    get_variable_reference_in_dict


class FormDataRowEditor(QWidget):
    def __init__(self, multipart_form: bool, name_placeholder: str, value_placeholder: str, parent: QWidget = None):
        super().__init__(parent)
        self._multipart_form = multipart_form
        self._name_placeholder = name_placeholder
        self._value_placeholder = value_placeholder
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._name_editor = ExpressionEditV3()
        self._name_editor.setPlaceholderText(self._name_placeholder)
        self._layout.addWidget(self._name_editor, 0, 0)
        self._layout.setColumnStretch(0, 1)
        column_no = 1
        if multipart_form:
            self._type_editor = QComboBox()
            self._type_editor.addItem(gettext("Text"), "text")
            self._type_editor.addItem(gettext("File"), "file")
            self._type_editor.setCurrentIndex(0)
            self._layout.addWidget(self._type_editor, 0, column_no)
            self._layout.setColumnStretch(column_no, 0)
            self._type_editor.currentIndexChanged.connect(self._on_type_changed)
            column_no += 1
        self._value_editor = self._create_text_editor()
        self._layout.addWidget(self._value_editor, 0, column_no)
        self._layout.setColumnStretch(column_no, 2)
        self.setContentsMargins(0, 0, 0, 0)

    def _create_text_editor(self):
        value_editor = ExpressionEditV3()
        value_editor.setPlaceholderText(self._value_placeholder)
        return value_editor

    def _create_file_editor(self):
        value_editor = OpenFilePathEdit()
        value_editor.setPlaceholderText(self._value_placeholder)
        return value_editor

    @Slot(int)
    def _on_type_changed(self, index: int):
        if index == 0 and not isinstance(self._value_editor, ExpressionEditV3):
            value_editor = self._create_text_editor()
            self._layout.replaceWidget(self._value_editor, value_editor)
            self._value_editor.deleteLater()
            self._value_editor = value_editor
        elif index == 1 and not isinstance(self._value_editor, OpenFilePathEdit):
            value_editor = self._create_file_editor()
            self._layout.replaceWidget(self._value_editor, value_editor)
            self._value_editor.deleteLater()
            self._value_editor = value_editor

    def get_value(self):
        if not self._name_editor.get_expression():
            return
        if self._multipart_form:
            return {"name": self._name_editor.get_expression(), "type": self._type_editor.currentData(),
                    "value": self._value_editor.get_expression() if isinstance(self._value_editor,
                                                                               ExpressionEditV3) else self._value_editor.get_value()}
        else:
            return {"name": self._name_editor.get_expression(), "value": self._value_editor.get_expression()}

    def set_value(self, value: dict):
        self._name_editor.set_expression(value.get('name', ''))
        if self._multipart_form:
            self._type_editor.setCurrentIndex(self._type_editor.findData(value.get('type', 'text')))
            self._on_type_changed(self._type_editor.currentIndex())
        if isinstance(self._value_editor, ExpressionEditV3):
            self._value_editor.set_expression(value.get('value', ''))
        else:
            self._value_editor.set_value(value.get('value', ''))

    def clear(self):
        self.set_value({})

    def set_variables(self, variables: list[VariableDef], type_registry: DataTypeRegistry):
        self._name_editor.set_variables(variables, type_registry)
        self._value_editor.set_variables(variables, type_registry)

    def validate(self):
        errors = []
        if self._name_editor.get_expression() and not self._name_editor.validate_expression():
            errors.append(gettext("name is invalid"))
        if isinstance(self._value_editor, ExpressionEditV3):
            if self._value_editor.get_expression() and not self._value_editor.validate_expression():
                errors.append(gettext("value is invalid"))
            if self._value_editor.get_expression() and not self._name_editor.get_expression():
                errors.append(gettext("name is required"))
        else:
            errors.extend(self._value_editor.validate())
            if self._value_editor.get_value() and not self._name_editor.get_expression():
                errors.append(gettext("name is required"))
        return errors


gettext('Add')
gettext('Field Name')
gettext('Field Value')


class FormDataEditor(ListEditor):
    def __init__(self, add_button_label='Add', multipart_form=False, name_placeholder="Field Name",
                 value_placeholder="Field Value", parent: QWidget = None):
        self._multipart_form = multipart_form
        self._name_placeholder = gettext(name_placeholder)
        self._value_placeholder = gettext(value_placeholder)
        super().__init__(gettext(add_button_label), parent)

    def create_row_editor(self) -> FormDataRowEditor:
        return FormDataRowEditor(self._multipart_form, self._name_placeholder, self._value_placeholder)

    def get_editor_value(self, editor: FormDataRowEditor):
        return editor.get_value()

    def set_editor_value(self, editor: FormDataRowEditor, value):
        editor.set_value(value)

    def clear_editor_value(self, editor: FormDataRowEditor):
        editor.clear()

    def validate_editor(self, editor: QWidget) -> list[str]:
        return editor.validate()

    def set_variables(self, variables: list[VariableDef], type_registry: DataTypeRegistry):
        for editor, _ in self.get_rows():
            editor.set_variables(variables, type_registry)

    def rename_variable_in_value(self, value, old_name, new_name):
        if value is None:
            return value, False
        update_count = 0
        for item in value:
            if rename_variable_in_dict(item, ['name', 'value'], old_name, new_name):
                update_count += 1
        return value, update_count > 0

    def get_variable_reference_in_value(self, value, var_name):
        if value is None:
            return 0
        count = 0
        for item in value:
            count += get_variable_reference_in_dict(item, ['name', 'value'], var_name)
        return count


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    editor = FormDataEditor(multipart_form=True)
    editor.show()
    app.exec()
