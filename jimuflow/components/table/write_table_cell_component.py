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


class WriteTableCellComponent(PrimitiveComponent):

    async def execute(self) -> ControlFlow:
        table: Table = self.read_input('table')
        row_no = table.resolve_row_no(self.read_input('rowNo'), check_out_of_range=False)
        append_row_if_out_of_range = self.read_input('appendRowIfOutOfRange')
        if row_no <= 0:
            if append_row_if_out_of_range:
                table.rows.insert(0, [''] * table.numberOfColumns)
                row_no = 1
            else:
                raise Exception(gettext('Row no is out of range: {row_no}').format(row_no=row_no))
        elif row_no > table.numberOfRows:
            if append_row_if_out_of_range:
                table.rows.append([''] * table.numberOfColumns)
                row_no = table.numberOfRows
            else:
                raise Exception(gettext('Row no is out of range: {row_no}').format(row_no=row_no))
        column_no = table.resolve_column_no(self.read_input('columnNo'))
        value = self.read_input('value')
        table.rows[row_no - 1][column_no - 1] = value
        return ControlFlow.NEXT

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return (gettext('Write the value ##{value}## to row ##{row_no}##, column ##{column_no}## of table ##{table}##')
                .format(value=flow_node.input('value'), row_no=flow_node.input('rowNo'),
                        column_no=flow_node.input('columnNo'), table=flow_node.input('table')))
