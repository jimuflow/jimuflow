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


class DeleteTableRowComponent(PrimitiveComponent):

    async def execute(self) -> ControlFlow:
        table: Table = self.read_input('table')
        delete_type = self.read_input('deleteType')
        if delete_type == 'all':
            table.rows.clear()
        else:
            row_no = int(self.read_input('rowNo'))
            row_no = table.resolve_row_no(row_no)
            table.rows.pop(row_no - 1)
        return ControlFlow.NEXT

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        delete_type = flow_node.input('deleteType')
        if delete_type == 'all':
            return gettext('Delete all rows of ##{table}##').format(table=flow_node.input('table'))
        else:
            return gettext('Delete row ##{rowNo}## of ##{table}##').format(rowNo=flow_node.input('rowNo'),
                                                                           table=flow_node.input('table'))
