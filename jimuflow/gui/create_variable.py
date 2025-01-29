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

from PySide6.QtCore import Slot, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QLabel, \
    QDialogButtonBox, QMessageBox, QComboBox, QGridLayout, QCheckBox, QWidget, QTextEdit

from jimuflow.datatypes import DataTypeDef
from jimuflow.definition import VariableDef, VariableDirection, VariableUiGroup, VariableUiInputType
from jimuflow.gui.app import AppContext, ProcessModel
from jimuflow.gui.components.NumberEdit import NumberEdit
from jimuflow.gui.components.bool_combo_box import BoolComboBox
from jimuflow.gui.components.variable_option_list_editor import VariableOptionsEditor
from jimuflow.gui.components.variable_type_editor import VariableTypeComboBox
from jimuflow.gui.components.variable_ui_dependency_editor import VariableUiDependencyEditor
from jimuflow.locales.i18n import gettext


class CreateVariableDialog(QDialog):
    def __init__(self, process_model: ProcessModel, var_def: VariableDef | None, parent=None):
        super().__init__(parent)
        self._process_model = process_model
        self.new_var_def: VariableDef | None = None

        self.setWindowTitle(gettext('Modify Variable') if var_def else gettext('Add Variable'))
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        form_layout = QGridLayout()
        form_layout.setContentsMargins(0, 0, 0, 0)
        self._form_layout = form_layout
        engine = AppContext.engine()

        self._name = QLineEdit()
        self._name.setMaxLength(50)
        self._name.setToolTip(
            gettext(
                'Any non blank characters and underscores other than punctuation can be used, and the length cannot exceed 50 characters.'))
        self._name.setValidator(
            QRegularExpressionValidator(QRegularExpression(R"([^\s\p{P}]|_)+"), self))
        if var_def:
            self._name.setText(var_def.name)
            var_type = engine.type_registry.get_data_type(var_def.type)
        else:
            var_type = engine.type_registry.get_data_type('text')

        row = 0
        form_layout.addWidget(QLabel(gettext("Variable Name:")), row, 0)
        form_layout.addWidget(self._name, row, 1)

        self._type = VariableTypeComboBox(engine.type_registry)
        self._type.set_value(var_type.name if var_type else var_def.type)
        self._type.currentIndexChanged.connect(self._on_type_changed)
        row += 1
        form_layout.addWidget(QLabel(gettext("Variable Type:")), row, 0)
        form_layout.addWidget(self._type, row, 1)

        self._direction = QComboBox()
        for direction in VariableDirection:
            self._direction.addItem(gettext(direction.name + " VARIABLE"), direction)
        if var_def:
            self._direction.setCurrentIndex(self._direction.findData(var_def.direction))
        row += 1
        form_layout.addWidget(QLabel(gettext("Variable Direction:")), row, 0)
        form_layout.addWidget(self._direction, row, 1)

        self._element_type = VariableTypeComboBox(engine.type_registry)
        if var_def and var_def.elementType:
            self._element_type.set_value(var_def.elementType)
        row += 1
        form_layout.addWidget(QLabel(gettext("Element Type:")), row, 0)
        form_layout.addWidget(self._element_type, row, 1)
        if var_type and not var_type.is_list:
            self._element_type.hide()
            self._get_label_widget(self._element_type).hide()

        type_name = self._type.get_value()
        if type_name == 'bool':
            self._default_value = BoolComboBox()
            if var_def:
                self._default_value.set_value(var_def.defaultValue)
        elif type_name == 'number':
            self._default_value = NumberEdit()
            if var_def:
                self._default_value.set_value(var_def.defaultValue)
        elif type_name == 'text':
            self._default_value = QTextEdit()
            self._default_value.setFixedHeight(55)
            if var_def:
                self._default_value.setText(var_def.defaultValue)
        else:
            self._default_value = QLabel()
        row += 1
        form_layout.addWidget(QLabel(gettext("Default Value:")), row, 0)
        form_layout.addWidget(self._default_value, row, 1)
        if isinstance(self._default_value, QLabel):
            self._default_value.hide()
            self._get_label_widget(self._default_value).hide()

        self._ui_config_label = QLineEdit()
        self._ui_config_label.setMaxLength(50)
        self._ui_config_label.setToolTip(
            gettext(
                'Any non blank characters and underscores other than punctuation can be used, and the length cannot exceed 50 characters.'))
        self._ui_config_label.setValidator(
            QRegularExpressionValidator(QRegularExpression(R"([^\s\p{P}]|_)+"), self))
        if var_def:
            self._ui_config_label.setText(var_def.ui_config.label)
        row += 1
        form_layout.addWidget(QLabel(gettext("UI Label:")), row, 0)
        form_layout.addWidget(self._ui_config_label, row, 1)

        self._ui_config_group = QComboBox()
        groups = {
            VariableUiGroup.GENERAL: gettext('General'),
            VariableUiGroup.ADVANCED: gettext('Advanced')
        }
        for group in VariableUiGroup:
            self._ui_config_group.addItem(groups[group], group)
        if var_def:
            self._ui_config_group.setCurrentIndex(self._ui_config_group.findData(var_def.ui_config.group))
        row += 1
        form_layout.addWidget(QLabel(gettext("UI Group:")), row, 0)
        form_layout.addWidget(self._ui_config_group, row, 1)

        self._ui_config_required = QCheckBox(gettext("Required"))
        if var_def:
            self._ui_config_required.setChecked(var_def.ui_config.required)
        row += 1
        form_layout.addWidget(self._ui_config_required, row, 1)

        self._ui_config_sort_no = QLineEdit()
        self._ui_config_sort_no.setMaxLength(3)
        self._ui_config_sort_no.setToolTip(gettext('Not exceeding 999, the smaller the number, the higher the ranking'))
        self._ui_config_sort_no.setValidator(
            QRegularExpressionValidator(QRegularExpression(R"\d{1,3}"), self))
        if var_def:
            self._ui_config_sort_no.setText(str(var_def.ui_config.sort_no))
        row += 1
        form_layout.addWidget(QLabel(gettext("UI Sort No:")), row, 0)
        form_layout.addWidget(self._ui_config_sort_no, row, 1)

        self._ui_config_input_type = QComboBox()
        for input_type in VariableUiInputType:
            if input_type.support(type_name):
                self._ui_config_input_type.addItem(input_type.display_name, input_type)
        if var_def:
            self._ui_config_input_type.setCurrentIndex(
                self._ui_config_input_type.findData(var_def.ui_config.input_type))
        row += 1
        form_layout.addWidget(QLabel(gettext("UI Input Type:")), row, 0)
        form_layout.addWidget(self._ui_config_input_type, row, 1)

        self._ui_config_input_editor_type = QLineEdit()
        self._ui_config_input_editor_type.setToolTip(gettext('The class name of the custom input control'))
        if var_def:
            self._ui_config_input_editor_type.setText(var_def.ui_config.input_editor_type)
        row += 1
        form_layout.addWidget(QLabel(gettext("UI Custom Input Control:")), row, 0)
        form_layout.addWidget(self._ui_config_input_editor_type, row, 1)

        self._ui_config_placeholder = QLineEdit()
        if var_def:
            self._ui_config_placeholder.setText(var_def.ui_config.placeholder)
        row += 1
        form_layout.addWidget(QLabel(gettext("UI Placeholder:")), row, 0)
        form_layout.addWidget(self._ui_config_placeholder, row, 1)

        self._ui_config_options = VariableOptionsEditor(gettext('Add Option'))
        if var_def:
            self._ui_config_options.set_value(var_def.ui_config.options)
        row += 1
        form_layout.addWidget(QLabel(gettext("UI Options:")), row, 0)
        form_layout.addWidget(self._ui_config_options, row, 1)

        self._ui_config_help_info = QLineEdit()
        if var_def:
            self._ui_config_help_info.setText(var_def.ui_config.help_info)
        row += 1
        form_layout.addWidget(QLabel(gettext("UI Help Info:")), row, 0)
        form_layout.addWidget(self._ui_config_help_info, row, 1)

        self._ui_config_depends_on = VariableUiDependencyEditor()
        self._ui_config_depends_on.set_process_model(self._process_model, var_def)
        if var_def:
            self._ui_config_depends_on.set_value(var_def.ui_config.depends_on)
        row += 1
        form_layout.addWidget(QLabel(gettext("UI Depends On:")), row, 0)
        form_layout.addWidget(self._ui_config_depends_on, row, 1)

        form_layout.setRowStretch(row + 1, 1)
        self.layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.create_variable)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText(gettext('Ok'))
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(gettext('Cancel'))
        self.layout.addWidget(button_box)
        self._direction.currentIndexChanged.connect(self._on_direction_changed)
        self._on_direction_changed(self._direction.currentIndex())
        self._ui_config_input_type.currentIndexChanged.connect(self._on_input_type_changed)

    @Slot(int)
    def _on_type_changed(self, index: int):
        if index == -1:
            return
        type_def: DataTypeDef = self._type.itemData(index)
        if type_def.is_list:
            self._element_type.show()
            self._get_label_widget(self._element_type).show()
        else:
            self._element_type.hide()
            self._get_label_widget(self._element_type).hide()
        if type_def.name == "bool":
            self._get_label_widget(self._default_value).show()
            if not isinstance(self._default_value, BoolComboBox):
                self._default_value = self._replace_widget(self._default_value, BoolComboBox())
            self._default_value.show()
        elif type_def.name == "number":
            self._get_label_widget(self._default_value).show()
            if not isinstance(self._default_value, NumberEdit):
                self._default_value = self._replace_widget(self._default_value, NumberEdit())
            self._default_value.show()
        elif type_def.name == "text":
            self._get_label_widget(self._default_value).show()
            if not isinstance(self._default_value, QTextEdit):
                text_edit = QTextEdit()
                text_edit.setFixedHeight(55)
                self._default_value = self._replace_widget(self._default_value, text_edit)
            self._default_value.show()
        elif self._default_value is not None:
            self._default_value.hide()
            self._get_label_widget(self._default_value).hide()
        self._ui_config_input_type.clear()
        for input_type in VariableUiInputType:
            if input_type.support(type_def.name):
                self._ui_config_input_type.addItem(input_type.display_name, input_type)

    def _replace_widget(self, old_widget: QWidget, new_widget: QWidget):
        old_widget.hide()
        old_widget.deleteLater()
        self._form_layout.replaceWidget(old_widget, new_widget)
        return new_widget

    @Slot(int)
    def _on_direction_changed(self, index: int):
        direction = self._direction.itemData(index)
        if direction == VariableDirection.IN:
            if isinstance(self._default_value, QLabel):
                self._default_value.hide()
                self._get_label_widget(self._default_value).hide()
            else:
                self._default_value.show()
                self._get_label_widget(self._default_value).show()
            self._ui_config_label.show()
            self._get_label_widget(self._ui_config_label).show()
            self._ui_config_group.show()
            self._get_label_widget(self._ui_config_group).show()
            self._ui_config_required.show()
            self._ui_config_sort_no.show()
            self._get_label_widget(self._ui_config_sort_no).show()
            self._ui_config_input_type.show()
            self._get_label_widget(self._ui_config_input_type).show()
            self._ui_config_placeholder.show()
            self._get_label_widget(self._ui_config_placeholder).show()
            self._ui_config_help_info.show()
            self._get_label_widget(self._ui_config_help_info).show()
            self._ui_config_depends_on.show()
            self._get_label_widget(self._ui_config_depends_on).show()
            self._on_input_type_changed(self._ui_config_input_type.currentIndex())
        elif direction == VariableDirection.OUT:
            self._default_value.hide()
            self._get_label_widget(self._default_value).hide()
            self._ui_config_label.show()
            self._get_label_widget(self._ui_config_label).show()
            self._ui_config_group.hide()
            self._get_label_widget(self._ui_config_group).hide()
            self._ui_config_required.hide()
            self._ui_config_sort_no.show()
            self._get_label_widget(self._ui_config_sort_no).show()
            self._ui_config_input_type.hide()
            self._get_label_widget(self._ui_config_input_type).hide()
            self._ui_config_input_editor_type.hide()
            self._get_label_widget(self._ui_config_input_editor_type).hide()
            self._ui_config_placeholder.show()
            self._get_label_widget(self._ui_config_placeholder).show()
            self._ui_config_options.hide()
            self._get_label_widget(self._ui_config_options).hide()
            self._ui_config_help_info.show()
            self._get_label_widget(self._ui_config_help_info).show()
            self._ui_config_depends_on.hide()
            self._get_label_widget(self._ui_config_depends_on).hide()
        else:
            self._default_value.hide()
            self._get_label_widget(self._default_value).hide()
            self._ui_config_label.hide()
            self._get_label_widget(self._ui_config_label).hide()
            self._ui_config_group.hide()
            self._get_label_widget(self._ui_config_group).hide()
            self._ui_config_required.hide()
            self._ui_config_sort_no.hide()
            self._get_label_widget(self._ui_config_sort_no).hide()
            self._ui_config_input_type.hide()
            self._get_label_widget(self._ui_config_input_type).hide()
            self._ui_config_input_editor_type.hide()
            self._get_label_widget(self._ui_config_input_editor_type).hide()
            self._ui_config_placeholder.hide()
            self._get_label_widget(self._ui_config_placeholder).hide()
            self._ui_config_options.hide()
            self._get_label_widget(self._ui_config_options).hide()
            self._ui_config_help_info.hide()
            self._get_label_widget(self._ui_config_help_info).hide()
            self._ui_config_depends_on.hide()
            self._get_label_widget(self._ui_config_depends_on).hide()

    @Slot(int)
    def _on_input_type_changed(self, index: int):
        input_type = self._ui_config_input_type.currentData()
        if input_type == VariableUiInputType.COMBO_BOX:
            self._ui_config_options.show()
            self._get_label_widget(self._ui_config_options).show()
            self._ui_config_input_editor_type.hide()
            self._get_label_widget(self._ui_config_input_editor_type).hide()
        elif input_type == VariableUiInputType.CUSTOM:
            self._ui_config_options.hide()
            self._get_label_widget(self._ui_config_options).hide()
            self._ui_config_input_editor_type.show()
            self._get_label_widget(self._ui_config_input_editor_type).show()
        else:
            self._ui_config_options.hide()
            self._get_label_widget(self._ui_config_options).hide()
            self._ui_config_input_editor_type.hide()
            self._get_label_widget(self._ui_config_input_editor_type).hide()

    def _get_label_widget(self, editor) -> QWidget:
        return self._form_layout.itemAt(self._form_layout.indexOf(editor) - 1).widget()

    @Slot()
    def create_variable(self):
        name = self._name.text()
        if not name:
            QMessageBox.warning(self, gettext('Tips'), gettext('Variable name cannot be empty'))
            return
        type_index = self._type.currentIndex()
        if type_index == -1:
            QMessageBox.warning(self, gettext('Tips'), gettext('Please select variable type'))
            return
        type = self._type.itemData(type_index)

        direction_index = self._direction.currentIndex()
        if direction_index == -1:
            QMessageBox.warning(self, gettext('Tips'), gettext('Please select variable direction'))
            return
        direction = self._direction.itemData(direction_index)

        engine = AppContext.engine()
        if type == engine.type_registry.get_data_type("list"):
            element_type_index = self._element_type.currentIndex()
            if element_type_index == -1:
                QMessageBox.warning(self, gettext('Tips'), gettext('Please select element type'))
                return
            element_type = self._element_type.itemData(element_type_index)

        self.new_var_def = VariableDef()
        self.new_var_def.name = name
        self.new_var_def.type = type.name
        self.new_var_def.direction = direction
        if type == engine.type_registry.get_data_type("list"):
            self.new_var_def.elementType = element_type.name
        if isinstance(self._default_value, BoolComboBox):
            self.new_var_def.defaultValue = self._default_value.get_value()
        elif isinstance(self._default_value, NumberEdit):
            self.new_var_def.defaultValue = self._default_value.get_value()
        elif isinstance(self._default_value, QTextEdit):
            if self._default_value.toPlainText():
                self.new_var_def.defaultValue = self._default_value.toPlainText()
        if direction == VariableDirection.IN:
            if self._ui_config_label.text():
                self.new_var_def.ui_config.label = self._ui_config_label.text()
            if self._ui_config_group.currentIndex() != -1:
                self.new_var_def.ui_config.group = self._ui_config_group.currentData()
            self.new_var_def.ui_config.required = self._ui_config_required.isChecked()
            if self._ui_config_sort_no.text():
                self.new_var_def.ui_config.sort_no = int(self._ui_config_sort_no.text())
            if self._ui_config_input_type.currentIndex() != -1:
                self.new_var_def.ui_config.input_type = self._ui_config_input_type.currentData()
                if self.new_var_def.ui_config.input_type == VariableUiInputType.CUSTOM:
                    self.new_var_def.ui_config.input_editor_type = self._ui_config_input_editor_type.text()
                    if not self.new_var_def.ui_config.input_editor_type:
                        QMessageBox.warning(self, gettext('Tips'), gettext('Please input custom editor type'))
                        return
                elif self.new_var_def.ui_config.input_type == VariableUiInputType.COMBO_BOX:
                    self.new_var_def.ui_config.options = self._ui_config_options.get_value()
                    if not self.new_var_def.ui_config.options:
                        QMessageBox.warning(self, gettext('Tips'), gettext('Please input options'))
                        return
            else:
                QMessageBox.warning(self, gettext('Tips'), gettext('Please select input type'))
                return
            if self._ui_config_placeholder.text():
                self.new_var_def.ui_config.placeholder = self._ui_config_placeholder.text()
            if self._ui_config_help_info.text():
                self.new_var_def.ui_config.help_info = self._ui_config_help_info.text()
            self.new_var_def.ui_config.depends_on = self._ui_config_depends_on.get_value()
        elif direction == VariableDirection.OUT:
            if self._ui_config_label.text():
                self.new_var_def.ui_config.label = self._ui_config_label.text()
            if self._ui_config_sort_no.text():
                self.new_var_def.ui_config.sort_no = int(self._ui_config_sort_no.text())
            if self._ui_config_placeholder.text():
                self.new_var_def.ui_config.placeholder = self._ui_config_placeholder.text()
            if self._ui_config_help_info.text():
                self.new_var_def.ui_config.help_info = self._ui_config_help_info.text()
        self.accept()
