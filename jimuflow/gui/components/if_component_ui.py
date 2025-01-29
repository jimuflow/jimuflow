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

from PySide6.QtWidgets import QVBoxLayout, QFormLayout, QLabel, QComboBox

from jimuflow.components.core.if_component import op_i18n
from jimuflow.definition import ComponentDef, FlowNode
from jimuflow.gui.app import ProcessModel, AppContext
from jimuflow.gui.component_dialog import ComponentForm
from jimuflow.gui.expression_edit_v2 import ExpressionEdit
from jimuflow.locales.i18n import gettext


class IfComponentForm(ComponentForm):
    def __init__(self, process_model: ProcessModel, comp_def: ComponentDef, node: FlowNode, parent=None):
        super().__init__(process_model, comp_def, node, parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(gettext('Input configs')))
        form_layout = QFormLayout()
        operand1_editor = ExpressionEdit()
        operand1_editor.setMinimumWidth(400)
        operand1_editor.set_variables(process_model.process_def.variables, AppContext.engine().type_registry)
        if self.node:
            operand1_editor.setText(self.read_input('operand1'))
        form_layout.addRow(QLabel(gettext('The first operand')), operand1_editor)
        self.operand1_editor = operand1_editor

        op_editor = QComboBox()
        for key, label in op_i18n.items():
            op_editor.addItem(label, key)
        if self.node and self.read_input('op'):
            op_editor.setCurrentIndex(list(op_i18n.keys()).index(self.read_input('op')))
        form_layout.addRow(QLabel(gettext('Operator')), op_editor)
        self.op_editor = op_editor

        operand2_editor = ExpressionEdit()
        operand2_editor.setMinimumWidth(400)
        operand2_editor.set_variables(process_model.process_def.variables, AppContext.engine().type_registry)
        if self.node:
            operand2_editor.setText(self.read_input('operand2'))
        form_layout.addRow(QLabel(gettext('The second operand')), operand2_editor)
        self.operand2_editor = operand2_editor

        layout.addLayout(form_layout)

    def get_inputs(self):
        inputs = {
            'operand1': self.operand1_editor.text(),
            'op': self.op_editor.currentData(),
            'operand2': self.operand2_editor.text()
        }
        return inputs

    def get_outputs(self):
        return {}

    def validate(self):
        errors = []
        if not self.operand1_editor.text():
            errors.append(gettext('Input parameter {name} is required').format(name=gettext('The first operand')))
        elif not self.operand1_editor.validate_expression():
            errors.append(gettext('Invalid expression for input {name}').format(name=gettext('The first operand')))
        if not self.operand1_editor.text():
            errors.append(gettext('Input parameter {name} is required').format(name=gettext('The second operand')))
        elif not self.operand2_editor.validate_expression():
            errors.append(gettext('Invalid expression for input {name}').format(name=gettext('The second operand')))
        return errors
