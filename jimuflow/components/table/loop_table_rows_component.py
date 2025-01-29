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


class LoopTableRowsComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        loop_range = flow_node.input('loopRange')
        if loop_range == 'all':
            return gettext(
                'Loop through all rows of table ##{table}##, save current row to ##{currentRow}##').format(
                table=flow_node.input('table'),
                currentRow=flow_node.output("currentRow"))
        else:
            return gettext(
                'Loop through row ##{startRowNo}## to row ##{endRowNo}## of table ##{table}##, save current row to ##{currentRow}##').format(
                startRowNo=flow_node.input('startRowNo'),
                endRowNo=flow_node.input('endRowNo'),
                table=flow_node.input('table'),
                currentRow=flow_node.output("currentRow"))

    async def execute(self) -> ControlFlow:
        table: Table = self.read_input("table")
        loop_range = self.read_input('loopRange')
        if loop_range == 'all':
            start_row_no = 1
            end_row_no = table.numberOfRows
        else:
            start_row_no = table.resolve_row_no(int(self.read_input("startRowNo")))
            end_row_no = table.resolve_row_no(int(self.read_input("endRowNo")))
        rows = table.rows[start_row_no - 1:end_row_no]
        reversed_loop = self.read_input('reversedLoop')
        if reversed_loop:
            rows = rows[::-1]
        for row in rows:
            await self.write_output('currentRow', row)
            control_flow = await self.execute_flow()
            if control_flow == ControlFlow.BREAK:
                break
            elif control_flow == ControlFlow.RETURN or control_flow == ControlFlow.EXIT:
                return control_flow
        return ControlFlow.NEXT
