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

from jimuflow.datatypes import Table
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class AddTableColumnComponent(PrimitiveComponent):

    async def execute(self) -> ControlFlow:
        table: Table = self.read_input('table')
        column_name = self.read_input('columnName')
        table.columnNames.append(column_name)
        for row in table.rows:
            row.append('')
        return ControlFlow.NEXT

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext('Add column ##{columnName}## to ##{table}##').format(columnName=flow_node.input('columnName'),
                                                                            table=flow_node.input('table'))
