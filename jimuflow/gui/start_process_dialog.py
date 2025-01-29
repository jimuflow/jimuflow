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

from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox, QLineEdit, \
    QWidget, QMessageBox, QTabWidget, QComboBox, QCheckBox, QGridLayout

from jimuflow.definition import ProcessDef, VariableUiInputType, VariableUiGroup, VariableDef
from jimuflow.gui.utils import Utils
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.common import is_empty


class StartProcessForm(QWidget):
    def __init__(self, process_def: ProcessDef, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(400)
        self.process_def = process_def
        self.input_editors = {}
        tabs = QTabWidget()
        tabs.setContentsMargins(0, 0, 0, 0)
        self._general_form = self._create_variables_form(VariableUiGroup.GENERAL)
        general_tab = QWidget()
        general_tab.setLayout(self._general_form)
        tabs.addTab(general_tab, gettext("General"))
        if len([v for v in self.process_def.variables if v.ui_config.group == VariableUiGroup.ADVANCED]) > 0:
            self._advanced_form = self._create_variables_form(VariableUiGroup.ADVANCED)
            advanced_tab = QWidget()
            advanced_tab.setLayout(self._advanced_form)
            tabs.addTab(advanced_tab, gettext("Advanced"))
        main_layout = QVBoxLayout()
        main_layout.addWidget(tabs)
        self.setLayout(main_layout)
        self._update_all_forms()

    def _create_variables_form(self, group: VariableUiGroup):
        layout = QGridLayout()
        row = 0
        input_variables = [v for v in self.process_def.input_variables() if v.ui_config.group == group]
        if len(input_variables) > 0:
            input_variables.sort(key=lambda x: x.ui_config.sort_no)
            for input_def in input_variables:
                input_label = gettext(input_def.ui_config.label if input_def.ui_config.label else input_def.name)
                if input_def.ui_config.help_info:
                    help_text = gettext(input_def.ui_config.help_info)
                else:
                    help_text = ''
                no_label = False
                if input_def.ui_config.input_type == VariableUiInputType.COMBO_BOX:
                    input_editor = QComboBox()
                    if input_def.ui_config.placeholder:
                        input_editor.setPlaceholderText(gettext(input_def.ui_config.placeholder))
                    if input_def.ui_config.help_info:
                        input_editor.setToolTip(gettext(input_def.ui_config.help_info))
                    for option in input_def.ui_config.options:
                        input_editor.addItem(gettext(option.label), option.value)
                    if input_def.defaultValue:
                        input_editor.setCurrentIndex(
                            [o.value for o in input_def.ui_config.options].index(input_def.defaultValue))
                    input_editor.currentIndexChanged.connect(lambda: self._update_all_forms())
                elif input_def.ui_config.input_type == VariableUiInputType.CHECK_BOX:
                    input_editor = QCheckBox(input_label)
                    if input_def.ui_config.help_info:
                        input_editor.setToolTip(gettext(input_def.ui_config.help_info))
                    no_label = True
                    if input_def.defaultValue is not None:
                        input_editor.setCheckState(
                            Qt.CheckState.Checked if input_def.defaultValue else Qt.CheckState.Unchecked)
                    input_editor.checkStateChanged.connect(lambda: self._update_all_forms())
                elif input_def.ui_config.input_type == VariableUiInputType.CUSTOM:
                    editor_class = Utils.load_class(input_def.ui_config.input_editor_type)
                    input_editor = editor_class()
                    if getattr(input_editor, 'setPlaceholderText', None):
                        input_editor.setPlaceholderText(gettext(input_def.ui_config.placeholder))
                else:
                    input_editor = QLineEdit()
                    if input_def.ui_config.placeholder:
                        input_editor.setPlaceholderText(gettext(input_def.ui_config.placeholder))
                    if input_def.ui_config.help_info:
                        input_editor.setToolTip(gettext(input_def.ui_config.help_info))
                    if input_def.defaultValue:
                        input_editor.setText(input_def.defaultValue)
                self.input_editors[input_def.name] = input_editor
                input_editor.setObjectName('inputVarEditor_' + input_def.name)
                if no_label:
                    layout.addWidget(input_editor, row, 0, 1, 2)
                else:
                    label = QLabel(input_label)
                    label.setObjectName('inputVarLabel_' + input_def.name)
                    layout.addWidget(label, row, 0)
                    layout.addWidget(input_editor, row, 1)
                if help_text:
                    help_label = self._create_help_label(help_text)
                    help_label.setObjectName('inputVarHelp_' + input_def.name)
                    layout.addWidget(help_label, row, 2)
                row += 1
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 0)
        layout.setRowStretch(row, 1)
        return layout

    def _create_help_label(self, help_text):
        label = QLabel()
        label.setPixmap(QIcon.fromTheme(QIcon.ThemeIcon.HelpAbout).pixmap(16, 16))
        label.setToolTip(help_text)
        return label

    def _update_all_forms(self):
        variables = self.process_def.input_variables()
        variables.sort(key=lambda x: x.ui_config.sort_no)
        for variable_def in variables:
            variable_dependency_satisfied = self._is_variable_dependency_satisfied(variable_def)
            editor = self.findChild(QWidget, 'inputVarEditor_' + variable_def.name)
            label = self.findChild(QWidget, 'inputVarLabel_' + variable_def.name)
            help_label = self.findChild(QWidget, 'inputVarHelp_' + variable_def.name)
            if variable_dependency_satisfied:
                editor.show()
                if label:
                    label.show()
                if help_label:
                    help_label.show()
            else:
                editor.hide()
                if label:
                    label.hide()
                if help_label:
                    help_label.hide()

    def _is_variable_dependency_satisfied(self, var_def: VariableDef) -> bool:
        if not var_def.ui_config.depends_on.is_valid():
            return True
        dependency_var_def = self.process_def.get_variable(var_def.ui_config.depends_on.variable_name)
        # 检查上级依赖是否满足
        if not self._is_variable_dependency_satisfied(dependency_var_def):
            return False
        # 检查当前依赖是否满足
        editor = self.input_editors[dependency_var_def.name]
        dependency_var_value = self._get_editor_value(editor)
        return var_def.ui_config.depends_on.is_satisfied(dependency_var_value)

    def _get_editor_value(self, editor):
        if isinstance(editor, QComboBox):
            return editor.currentData()
        elif isinstance(editor, QCheckBox):
            return editor.isChecked()
        elif isinstance(editor, QLineEdit):
            return editor.text()
        else:
            return editor.get_value()

    def get_inputs(self):
        inputs = {}
        for input_def in self.process_def.input_variables():
            if self._is_variable_dependency_satisfied(input_def):
                editor = self.input_editors[input_def.name]
                inputs[input_def.name] = self._get_editor_value(editor)
        return inputs

    def validate(self):
        errors = []
        for input_def in self.process_def.input_variables():
            if self._is_variable_dependency_satisfied(input_def):
                editor = self.input_editors[input_def.name]
                editor_value = self._get_editor_value(editor)
                display_name = gettext(input_def.ui_config.label or input_def.name)
                if input_def.ui_config.input_type == VariableUiInputType.CUSTOM:
                    editor_errors = editor.validate()
                    if editor_errors:
                        errors.append(gettext('Input parameter {name} is invalid: {editor_errors}')
                                      .format(name=display_name, editor_errors=", ".join(editor_errors)))
                if input_def.ui_config.required and is_empty(editor_value):
                    errors.append(gettext('Input parameter {name} is required').format(name=display_name))
        return errors


class StartProcessDialog(QDialog):
    last_geometry = None

    def __init__(self, process_def: ProcessDef, parent=None):
        super().__init__(parent)
        self.process_def = process_def
        self.setWindowTitle(gettext('Process {name} startup parameter configuration').format(name=process_def.name))
        layout = QVBoxLayout(self)
        self.process_form = StartProcessForm(process_def)
        layout.addWidget(self.process_form)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.on_ok)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText(gettext('Ok'))
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(gettext('Cancel'))
        layout.addWidget(button_box)

    @Slot()
    def on_ok(self):
        errors = self.process_form.validate()
        if len(errors) > 0:
            QMessageBox.critical(self, gettext('Error'), '\n'.join(errors))
            return
        self.accept()

    def get_inputs(self):
        return self.process_form.get_inputs()
