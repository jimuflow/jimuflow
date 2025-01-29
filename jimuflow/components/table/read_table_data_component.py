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


class ReadTableDataComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        read_type = flow_node.input('readType')
        if read_type == 'row':
            return gettext(
                'Read row ##{rowNo}## of table ##{table}##, save result to ##{result}##').format(
                rowNo=flow_node.input('rowNo'),
                table=flow_node.input('table'),
                result=flow_node.output("result"))
        else:
            return gettext(
                'Read row ##{rowNo}## and column ##{columnNo}## of table ##{table}##, save result to ##{result}##').format(
                rowNo=flow_node.input('rowNo'),
                columnNo=flow_node.input('columnNo'),
                table=flow_node.input('table'),
                result=flow_node.output("result"))

    async def execute(self) -> ControlFlow:
        table: Table = self.read_input("table")
        read_type = self.read_input('readType')
        row_no = table.resolve_row_no(self.read_input('rowNo'))
        if read_type == 'row':
            await self.write_output('result', table.rows[row_no - 1])
        elif read_type == 'cell':
            column_no = table.resolve_column_no(self.read_input('columnNo'))
            await self.write_output('result', table.rows[row_no - 1][column_no - 1])
        else:
            raise Exception(gettext('Unsupported read type: {read_type}').format(read_type=read_type))
        return ControlFlow.NEXT
