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
    QWidget, QMessageBox, QTabWidget, QComboBox, QCheckBox, QGridLayout, QTextEdit

from jimuflow.components.core.os_utils import is_macos
from jimuflow.definition import ComponentDef, FlowNode, ProcessDef, PrimitiveComponentDef, ErrorHandlingType, \
    VariableUiInputType, VariableUiGroup, VariableDirection, VariableDef
from jimuflow.gui.app import ProcessModel, AppContext
from jimuflow.gui.components.NumberEdit import NumberEdit
from jimuflow.gui.expression_edit_v3 import ExpressionEditV3
from jimuflow.gui.help_dialog import HelpDialog
from jimuflow.gui.utils import Utils
from jimuflow.gui.variable_line_edit import VariableLineEdit
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.common import is_empty
from jimuflow.runtime.expression import is_identifier


class ComponentForm(QWidget):
    def __init__(self, process_model: ProcessModel, comp_def: ComponentDef, node: FlowNode, parent=None):
        super().__init__(parent)
        self.process_model = process_model
        self.comp_def = comp_def
        self.node = node
        self.setMinimumWidth(600)

    def get_inputs(self):
        return {input_name: '' for input_name in self.comp_def.input_variables()}

    def get_outputs(self):
        return {output_name: '' for output_name in self.comp_def.output_variables()}

    def get_flow_node(self):
        node = {
            'component': self.comp_def.id(self.process_model.process_def.package),
            'inputs': self.get_inputs(),
            'outputs': self.get_outputs()
        }
        return node

    def validate(self):
        return []


class DefaultComponentForm(ComponentForm):
    def __init__(self, process_model: ProcessModel, comp_def: ComponentDef, node: FlowNode, parent=None):
        super().__init__(process_model, comp_def, node, parent)
        self.input_editors = {}
        self.output_editors = {}
        self._output_editors_on_error = {}
        tabs = QTabWidget()
        tabs.setContentsMargins(0, 0, 0, 0)
        if any((v.direction == VariableDirection.IN and v.ui_config.group == VariableUiGroup.GENERAL)
               or v.direction == VariableDirection.OUT for v in self.comp_def.variables):
            self._general_form = self._create_variables_form(VariableUiGroup.GENERAL)
            general_tab = QWidget()
            general_tab.setLayout(self._general_form)
            tabs.addTab(general_tab, gettext("General"))
        if any(v.ui_config.group == VariableUiGroup.ADVANCED for v in self.comp_def.variables):
            self._advanced_form = self._create_variables_form(VariableUiGroup.ADVANCED)
            advanced_tab = QWidget()
            advanced_tab.setLayout(self._advanced_form)
            tabs.addTab(advanced_tab, gettext("Advanced"))
        if self.comp_def.supports_error_handling:
            self._create_error_handling_form()
            error_handling_tab = QWidget()
            error_handling_tab.setLayout(self._error_form_layout)
            tabs.addTab(error_handling_tab, gettext("Error handling"))
        main_layout = QVBoxLayout()
        main_layout.addWidget(tabs)
        self.setLayout(main_layout)
        self._update_all_forms()

    def _create_variables_form(self, group: VariableUiGroup):
        layout = QGridLayout()
        row = 0
        input_variables = [v for v in self.comp_def.input_variables() if v.ui_config.group == group]
        if len(input_variables) > 0:
            input_variables.sort(key=lambda x: x.ui_config.sort_no)
            for input_def in input_variables:
                input_label = gettext(input_def.ui_config.label if input_def.ui_config.label else input_def.name)
                if input_def.ui_config.help_info:
                    help_text = gettext(input_def.ui_config.help_info)
                else:
                    help_text = ''
                no_label = False
                if input_def.ui_config.input_type == VariableUiInputType.EXPRESSION:
                    input_editor = ExpressionEditV3()
                    if input_def.ui_config.placeholder:
                        input_editor.setPlaceholderText(gettext(input_def.ui_config.placeholder))
                    if input_def.ui_config.help_info:
                        input_editor.setToolTip(gettext(input_def.ui_config.help_info))
                    input_editor.set_variables(self.process_model.process_def.variables,
                                               AppContext.engine().type_registry)
                    if self.node and input_def.name in self.node.inputs:
                        input_editor.setText(self.node.input(input_def.name))
                    elif input_def.defaultValue:
                        input_editor.setText(input_def.defaultValue)
                elif input_def.ui_config.input_type == VariableUiInputType.VARIABLE:
                    input_editor = VariableLineEdit()
                    if input_def.ui_config.placeholder:
                        input_editor.setPlaceholderText(gettext(input_def.ui_config.placeholder))
                    if input_def.ui_config.help_info:
                        input_editor.setToolTip(gettext(input_def.ui_config.help_info))
                    input_editor.set_variables(self.process_model.process_def.variables)
                    if self.node and input_def.name in self.node.inputs:
                        input_editor.setText(self.node.input(input_def.name))
                    elif input_def.defaultValue:
                        input_editor.setText(input_def.defaultValue)
                elif input_def.ui_config.input_type == VariableUiInputType.COMBO_BOX:
                    input_editor = QComboBox()
                    if input_def.ui_config.placeholder:
                        input_editor.setPlaceholderText(gettext(input_def.ui_config.placeholder))
                    if input_def.ui_config.help_info:
                        input_editor.setToolTip(gettext(input_def.ui_config.help_info))
                    for option in input_def.ui_config.options:
                        input_editor.addItem(gettext(option.label), option.value)
                    if self.node and self.node.input(input_def.name):
                        input_editor.setCurrentIndex(
                            [o.value for o in input_def.ui_config.options].index(self.node.input(input_def.name)))
                    elif input_def.defaultValue:
                        input_editor.setCurrentIndex(
                            [o.value for o in input_def.ui_config.options].index(input_def.defaultValue))
                    input_editor.currentIndexChanged.connect(lambda: self._update_all_forms())
                elif input_def.ui_config.input_type == VariableUiInputType.CHECK_BOX:
                    input_editor = QCheckBox(input_label)
                    if input_def.ui_config.help_info:
                        input_editor.setToolTip(gettext(input_def.ui_config.help_info))
                    no_label = True
                    if self.node and input_def.name in self.node.inputs:
                        input_editor.setCheckState(
                            Qt.CheckState.Checked if self.node.input(input_def.name) else Qt.CheckState.Unchecked)
                    elif input_def.defaultValue is not None:
                        input_editor.setCheckState(
                            Qt.CheckState.Checked if input_def.defaultValue else Qt.CheckState.Unchecked)
                    input_editor.checkStateChanged.connect(lambda: self._update_all_forms())
                elif input_def.ui_config.input_type == VariableUiInputType.CUSTOM:
                    editor_class = Utils.load_class(input_def.ui_config.input_editor_type)
                    input_editor = editor_class()
                    if input_def.ui_config.placeholder and getattr(input_editor, 'setPlaceholderText', None):
                        input_editor.setPlaceholderText(gettext(input_def.ui_config.placeholder))
                    if getattr(input_editor, 'set_variables', None):
                        input_editor.set_variables(self.process_model.process_def.variables,
                                                   AppContext.engine().type_registry)
                    if self.node and input_def.name in self.node.inputs:
                        input_editor.set_value(self.node.input(input_def.name))
                elif input_def.ui_config.input_type == VariableUiInputType.TEXT_EDIT:
                    input_editor = QTextEdit()
                    input_editor.setFixedHeight(55)
                    if input_def.ui_config.placeholder:
                        input_editor.setPlaceholderText(gettext(input_def.ui_config.placeholder))
                    if input_def.ui_config.help_info:
                        input_editor.setToolTip(gettext(input_def.ui_config.help_info))
                    if self.node and input_def.name in self.node.inputs:
                        input_editor.setText(self.node.input(input_def.name))
                    elif input_def.defaultValue:
                        input_editor.setText(input_def.defaultValue)
                elif input_def.ui_config.input_type == VariableUiInputType.NUMBER_EDIT:
                    input_editor = NumberEdit()
                    if input_def.ui_config.placeholder:
                        input_editor.setPlaceholderText(gettext(input_def.ui_config.placeholder))
                    if input_def.ui_config.help_info:
                        input_editor.setToolTip(gettext(input_def.ui_config.help_info))
                    if self.node and input_def.name in self.node.inputs:
                        input_editor.set_value(self.node.input(input_def.name))
                    elif input_def.defaultValue:
                        input_editor.set_value(input_def.defaultValue)
                else:
                    input_editor = QLineEdit()
                    if input_def.ui_config.placeholder:
                        input_editor.setPlaceholderText(gettext(input_def.ui_config.placeholder))
                    if input_def.ui_config.help_info:
                        input_editor.setToolTip(gettext(input_def.ui_config.help_info))
                    if self.node and input_def.name in self.node.inputs:
                        input_editor.setText(self.node.input(input_def.name))
                    elif input_def.defaultValue:
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
        output_variables = [v for v in self.comp_def.output_variables() if v.ui_config.group == group]
        if len(output_variables) > 0:
            output_variables.sort(key=lambda x: x.ui_config.sort_no)
            output_configs_label = QLabel(gettext('Output configs'))
            output_configs_label.setObjectName("outputConfigsLabel" + group.name)
            layout.addWidget(output_configs_label, row, 0, 1, 3)
            row += 1
            for output_def in output_variables:
                output_label = gettext(output_def.ui_config.label if output_def.ui_config.label else output_def.name)
                output_editor = VariableLineEdit()
                output_editor.setObjectName('outputVarEditor_' + output_def.name)
                if output_def.ui_config.placeholder:
                    output_editor.setPlaceholderText(gettext(output_def.ui_config.placeholder))
                if output_def.ui_config.help_info:
                    help_text = gettext(output_def.ui_config.help_info)
                else:
                    help_text = ''
                if output_def.ui_config.help_info:
                    output_editor.setToolTip(gettext(output_def.ui_config.help_info))
                output_editor.set_variables(self.process_model.process_def.variables)
                if self.node:
                    output_editor.setText(self.node.output(output_def.name))
                self.output_editors[output_def.name] = output_editor
                label = QLabel(output_label)
                label.setObjectName('outputVarLabel_' + output_def.name)
                layout.addWidget(label, row, 0)
                layout.addWidget(output_editor, row, 1)
                if help_text:
                    help_label = self._create_help_label(help_text)
                    help_label.setObjectName('outputVarHelp_' + output_def.name)
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

    def _create_error_handling_form(self):
        self._error_form_layout = QGridLayout()

        # 错误处理类型
        self._error_handling_type = QComboBox()
        self._error_handling_type.setObjectName("errorHandlingTypeEditor")
        self._error_handling_type.addItems([gettext('Stop'), gettext('Retry'), gettext('Ignore')])
        row = 0
        label = QLabel(gettext('Error handling type'))
        label.setObjectName("errorHandlingTypeLabel")
        self._error_form_layout.addWidget(label, row, 0)
        self._error_form_layout.addWidget(self._error_handling_type, row, 1)
        help_label = self._create_help_label(gettext('Error handling type'))
        help_label.setObjectName("errorHandlingTypeHelp")
        self._error_form_layout.addWidget(help_label, row, 2)
        row += 1

        # 最大重试次数
        self._max_retries = QLineEdit()
        self._max_retries.setObjectName("maxRetriesEditor")
        if self.node:
            self._max_retries.setText(str(self.node.max_retries))
        label = QLabel(gettext('Max retries'))
        label.setObjectName("maxRetriesLabel")
        help_label = self._create_help_label(gettext('Max retries'))
        help_label.setObjectName("maxRetriesHelp")
        self._error_form_layout.addWidget(label, row, 0)
        self._error_form_layout.addWidget(self._max_retries, row, 1)
        self._error_form_layout.addWidget(help_label, row, 2)
        row += 1

        # 重试间隔
        self._retry_interval = QLineEdit()
        self._retry_interval.setObjectName("retryIntervalEditor")
        if self.node:
            self._retry_interval.setText(str(self.node.retry_interval))
        label = QLabel(gettext('Retry interval (seconds)'))
        label.setObjectName("retryIntervalLabel")
        help_label = self._create_help_label(gettext('Retry interval (seconds)'))
        help_label.setObjectName("retryIntervalHelp")
        self._error_form_layout.addWidget(label, row, 0)
        self._error_form_layout.addWidget(self._retry_interval, row, 1)
        self._error_form_layout.addWidget(help_label, row, 2)
        row += 1

        if len(self.comp_def.output_variables()) > 0:
            label = QLabel(gettext('Outputs on error'))
            label.setObjectName("outputsOnErrorLabel")
            self._error_form_layout.addWidget(label, row, 0, 1, 3)
            row += 1
            for output_def in self.comp_def.output_variables():
                output_label = QLabel(
                    gettext(output_def.ui_config.label if output_def.ui_config.label else output_def.name))
                output_label.setObjectName("errorOutputVarLabel_" + output_def.name)
                output_editor = ExpressionEditV3()
                output_editor.setObjectName("errorOutputVarEditor_" + output_def.name)
                output_editor.set_variables(self.process_model.process_def.variables, AppContext.engine().type_registry)
                if self.node:
                    output_editor.setText(self.node.outputs_on_error.get(output_def.name))
                self._output_editors_on_error[output_def.name] = output_editor
                self._error_form_layout.addWidget(output_label, row, 0)
                self._error_form_layout.addWidget(output_editor, row, 1)
                if output_def.ui_config.placeholder:
                    output_editor.setPlaceholderText(gettext(output_def.ui_config.placeholder))
                if output_def.ui_config.help_info:
                    help_text = gettext(output_def.ui_config.help_info)
                    help_label = self._create_help_label(help_text)
                    help_label.setObjectName('errorOutputVarHelp_' + output_def.name)
                    self._error_form_layout.addWidget(help_label, row, 2)
                row += 1
        self._error_form_layout.setColumnStretch(0, 0)
        self._error_form_layout.setColumnStretch(1, 1)
        self._error_form_layout.setColumnStretch(2, 0)
        self._error_form_layout.setRowStretch(row, 1)
        if self.node:
            if self.node.error_handling_type == ErrorHandlingType.STOP:
                self._error_handling_type.setCurrentIndex(0)
            elif self.node.error_handling_type == ErrorHandlingType.RETRY:
                self._error_handling_type.setCurrentIndex(1)
            elif self.node.error_handling_type == ErrorHandlingType.IGNORE:
                self._error_handling_type.setCurrentIndex(2)
        self._error_handling_type.currentIndexChanged.connect(lambda: self._update_all_forms())

    def _update_all_forms(self):
        variables = [v for v in self.comp_def.variables]
        variables.sort(key=lambda x: x.ui_config.sort_no)
        general_outputs_visible = False
        advanced_outputs_visible = False
        out_var_satisfied_dict = {}
        for variable_def in variables:
            if variable_def.direction == VariableDirection.LOCAL:
                continue
            variable_dependency_satisfied = self._is_variable_dependency_satisfied(variable_def)
            if variable_def.direction == VariableDirection.IN:
                editor = self.findChild(QWidget, 'inputVarEditor_' + variable_def.name)
                label = self.findChild(QWidget, 'inputVarLabel_' + variable_def.name)
                help_label = self.findChild(QWidget, 'inputVarHelp_' + variable_def.name)
            else:
                out_var_satisfied_dict[variable_def.name] = variable_dependency_satisfied
                editor = self.findChild(QWidget, 'outputVarEditor_' + variable_def.name)
                label = self.findChild(QWidget, 'outputVarLabel_' + variable_def.name)
                help_label = self.findChild(QWidget, 'outputVarHelp_' + variable_def.name)
                if variable_dependency_satisfied:
                    if variable_def.ui_config.group == VariableUiGroup.GENERAL:
                        general_outputs_visible = True
                    elif variable_def.ui_config.group == VariableUiGroup.ADVANCED:
                        advanced_outputs_visible = True
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
        general_outputs_label = self.findChild(QLabel, "outputConfigsLabel" + VariableUiGroup.GENERAL.name)
        advanced_outputs_label = self.findChild(QLabel, "outputConfigsLabel" + VariableUiGroup.ADVANCED.name)
        if general_outputs_visible:
            general_outputs_label.show()
        elif general_outputs_label:
            general_outputs_label.hide()
        if advanced_outputs_visible:
            advanced_outputs_label.show()
        elif advanced_outputs_label:
            advanced_outputs_label.hide()
        if self.comp_def.supports_error_handling:
            index = self._error_handling_type.currentIndex()
            if index == 0:
                self._max_retries.hide()
                self.findChild(QWidget, 'maxRetriesLabel').hide()
                self.findChild(QWidget, 'maxRetriesHelp').hide()
                self._retry_interval.hide()
                self.findChild(QWidget, 'retryIntervalLabel').hide()
                self.findChild(QWidget, 'retryIntervalHelp').hide()
                self._hide_error_outputs()
            elif index == 1:
                self._max_retries.show()
                self.findChild(QWidget, 'maxRetriesLabel').show()
                self.findChild(QWidget, 'maxRetriesHelp').show()
                self._retry_interval.show()
                self.findChild(QWidget, 'retryIntervalLabel').show()
                self.findChild(QWidget, 'retryIntervalHelp').show()
                self._hide_error_outputs()
            elif index == 2:
                self._max_retries.hide()
                self.findChild(QWidget, 'maxRetriesLabel').hide()
                self.findChild(QWidget, 'maxRetriesHelp').hide()
                self._retry_interval.hide()
                self.findChild(QWidget, 'retryIntervalLabel').hide()
                self.findChild(QWidget, 'retryIntervalHelp').hide()
                self._show_error_outputs(out_var_satisfied_dict)

    def _hide_error_outputs(self):
        if not self.comp_def.output_variables():
            return
        self.findChild(QWidget, 'outputsOnErrorLabel').hide()
        for variable_def in self.comp_def.variables:
            if variable_def.direction != VariableDirection.OUT:
                continue
            error_editor = self.findChild(QWidget, 'errorOutputVarEditor_' + variable_def.name)
            error_label = self.findChild(QWidget, 'errorOutputVarLabel_' + variable_def.name)
            error_help_label = self.findChild(QWidget, 'errorOutputVarHelp_' + variable_def.name)
            error_editor.hide()
            error_label.hide()
            if error_help_label:
                error_help_label.hide()

    def _show_error_outputs(self, out_var_satisfied_dict: dict):
        if not self.comp_def.output_variables():
            return
        all_hide = True
        for variable_def in self.comp_def.variables:
            if variable_def.direction != VariableDirection.OUT:
                continue
            error_editor = self.findChild(QWidget, 'errorOutputVarEditor_' + variable_def.name)
            error_label = self.findChild(QWidget, 'errorOutputVarLabel_' + variable_def.name)
            error_help_label = self.findChild(QWidget, 'errorOutputVarHelp_' + variable_def.name)
            if out_var_satisfied_dict[variable_def.name]:
                all_hide = False
                error_editor.show()
                error_label.show()
                if error_help_label:
                    error_help_label.show()
            else:
                error_editor.hide()
                error_label.hide()
                if error_help_label:
                    error_help_label.hide()
        if all_hide:
            self.findChild(QWidget, 'outputsOnErrorLabel').hide()
        else:
            self.findChild(QWidget, 'outputsOnErrorLabel').show()

    def _is_variable_dependency_satisfied(self, var_def: VariableDef) -> bool:
        if not var_def.ui_config.depends_on.is_valid():
            return True
        dependency_var_def = self.comp_def.get_variable(var_def.ui_config.depends_on.variable_name)
        # 检查上级依赖是否满足
        if not self._is_variable_dependency_satisfied(dependency_var_def):
            return False
        # 检查当前依赖是否满足
        if dependency_var_def.direction == VariableDirection.IN:
            editor = self.input_editors[dependency_var_def.name]
        else:
            editor = self.output_editors[dependency_var_def.name]
        dependency_var_value = self._get_editor_value(editor)
        return var_def.ui_config.depends_on.is_satisfied(dependency_var_value)

    def _get_editor_value(self, editor):
        if isinstance(editor, QComboBox):
            return editor.currentData()
        elif isinstance(editor, QCheckBox):
            return editor.isChecked()
        elif isinstance(editor, QLineEdit):
            return editor.text()
        elif isinstance(editor, VariableLineEdit):
            return editor.text()
        elif isinstance(editor, ExpressionEditV3):
            return editor.get_expression()
        elif isinstance(editor, NumberEdit):
            return editor.get_value()
        elif isinstance(editor, QTextEdit):
            return editor.toPlainText()
        else:
            return editor.get_value()

    def get_inputs(self):
        inputs = {}
        for input_def in self.comp_def.input_variables():
            if self._is_variable_dependency_satisfied(input_def):
                editor = self.input_editors[input_def.name]
                inputs[input_def.name] = self._get_editor_value(editor)
        return inputs

    def get_outputs(self):
        outputs = {}
        for output_def in self.comp_def.output_variables():
            if self._is_variable_dependency_satisfied(output_def):
                outputs[output_def.name] = self.output_editors[output_def.name].text()
        return outputs

    def get_flow_node(self):
        node = super().get_flow_node()
        if self.comp_def.supports_error_handling:
            node['error_handling_type'] = \
                [ErrorHandlingType.STOP, ErrorHandlingType.RETRY, ErrorHandlingType.IGNORE][
                    self._error_handling_type.currentIndex()]
            if self._error_handling_type.currentIndex() == 1:
                node['max_retries'] = int(self._max_retries.text())
                node['retry_interval'] = int(self._retry_interval.text())
            elif self._error_handling_type.currentIndex() == 2:
                node['outputs_on_error'] = {}
                for output_def in self.comp_def.output_variables():
                    node['outputs_on_error'][output_def.name] = self._output_editors_on_error[output_def.name].text()
        return node

    def validate(self):
        errors = []
        for input_def in self.comp_def.input_variables():
            if self._is_variable_dependency_satisfied(input_def):
                editor = self.input_editors[input_def.name]
                editor_value = self._get_editor_value(editor)
                display_name = gettext(input_def.ui_config.label or input_def.name)
                if input_def.ui_config.input_type == VariableUiInputType.CUSTOM and getattr(editor, 'validate', None):
                    editor_errors = editor.validate()
                    if editor_errors:
                        errors.append(gettext('Input parameter {name} is invalid: {editor_errors}')
                                      .format(name=display_name, editor_errors=", ".join(editor_errors)))
                if input_def.ui_config.required and is_empty(editor_value):
                    errors.append(gettext('Input parameter {name} is required').format(name=display_name))
                elif not is_empty(editor_value) and isinstance(editor,
                                                               ExpressionEditV3) and not editor.validate_expression():
                    errors.append(gettext('Invalid expression for input {name}').format(name=display_name))
        for output_def in self.comp_def.output_variables():
            if self._is_variable_dependency_satisfied(output_def):
                editor = self.output_editors[output_def.name]
                editor_value = self._get_editor_value(editor)
                display_name = gettext(output_def.ui_config.label or output_def.name)
                if output_def.ui_config.required and is_empty(editor_value):
                    errors.append(gettext('Output parameter {name} is required').format(name=display_name))
                elif not is_empty(editor_value) and not is_identifier(editor_value):
                    errors.append(gettext('Invalid variable name for output {name}').format(name=display_name))
        if self.comp_def.supports_error_handling:
            if self._error_handling_type.currentIndex() == 0:
                pass
            elif self._error_handling_type.currentIndex() == 1:
                if not self._max_retries.text():
                    errors.append(gettext('Max retries is required'))
                elif not self._max_retries.text().isnumeric():
                    errors.append(gettext('Max retries must be a number'))
                elif int(self._max_retries.text()) < 0:
                    errors.append(gettext('Max retries must be greater than 0'))
                if not self._retry_interval.text():
                    errors.append(gettext('Retry interval is required'))
                elif not self._retry_interval.text().isnumeric():
                    errors.append(gettext('Retry interval must be a number'))
                elif int(self._retry_interval.text()) < 0:
                    errors.append(gettext('Retry interval must be greater than 0'))
            elif self._error_handling_type.currentIndex() == 2:
                for output_def in self.comp_def.output_variables():
                    if self._is_variable_dependency_satisfied(output_def):
                        display_name = gettext(output_def.ui_config.label or output_def.name)
                        if not self._output_editors_on_error[output_def.name].text():
                            errors.append(gettext('Output parameter {name} is required').format(name=display_name))
                        elif not self._output_editors_on_error[output_def.name].validate_expression():
                            errors.append(gettext('Invalid expression for output {name}').format(name=display_name))
        return errors


class ComponentDialog(QDialog):
    last_geometry = None

    def __init__(self, process_model: ProcessModel, comp_def: ComponentDef, node: FlowNode = None, parent=None):
        super().__init__(parent)
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.process_model = process_model
        self.comp_def = comp_def
        if isinstance(comp_def, ProcessDef):
            title = gettext('Process {name}').format(name=comp_def.name)
        else:
            component_class = AppContext.engine().load_component_class(comp_def)
            title = f'{gettext(comp_def.display_name)} - {comp_def.name}'
        # if ComponentDialog.last_geometry is not None:
        #     self.restoreGeometry(ComponentDialog.last_geometry)
        layout = QVBoxLayout(self)
        if is_macos():
            layout.addWidget(QLabel(title), alignment=Qt.AlignmentFlag.AlignCenter)
        else:
            self.setWindowTitle(title)
        if isinstance(comp_def, PrimitiveComponentDef) and comp_def.ui_module_name:
            component_ui_class = self.load_component_ui_class(comp_def)
            self.comp_form = component_ui_class(process_model, comp_def, node)
        else:
            self.comp_form = DefaultComponentForm(process_model, comp_def, node)
        layout.addWidget(self.comp_form)
        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        if comp_def.help_url:
            buttons |= QDialogButtonBox.StandardButton.Help
        button_box = QDialogButtonBox(buttons)
        button_box.accepted.connect(self.on_ok)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText(gettext('Ok'))
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(gettext('Cancel'))
        if comp_def.help_url:
            button_box.helpRequested.connect(self._show_help)
            button_box.button(QDialogButtonBox.StandardButton.Help).setText(gettext('Help'))
        layout.addWidget(button_box)

    @Slot()
    def _show_help(self):
        HelpDialog.show_help(self.comp_def.help_url)

    def load_component_ui_class(self, component_def: ComponentDef) -> type[ComponentForm]:
        component_ui_module = __import__(component_def.ui_module_name, fromlist=[component_def.ui_class_name])
        component_ui_class = getattr(component_ui_module, component_def.ui_class_name)
        return component_ui_class

    @Slot()
    def on_ok(self):
        errors = self.comp_form.validate()
        if len(errors) > 0:
            QMessageBox.critical(self, gettext('Error'), '\n'.join(errors))
            return
        self.accept()

    def done(self, r):
        ComponentDialog.last_geometry = self.saveGeometry()
        super().done(r)

    def get_flow_node(self):
        return self.comp_form.get_flow_node()
