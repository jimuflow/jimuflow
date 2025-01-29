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


class WriteTableRowComponent(PrimitiveComponent):

    async def execute(self) -> ControlFlow:
        table: Table = self.read_input('table')
        write_type = self.read_input('writeType')
        if write_type == 'append':
            table.rows.append([''] * table.numberOfColumns)
            row_no = table.numberOfRows
        else:
            inserted = False
            row_no = table.resolve_row_no(self.read_input('rowNo'), check_out_of_range=False)
            append_row_if_out_of_range = self.read_input('appendRowIfOutOfRange')
            if row_no <= 0:
                if append_row_if_out_of_range:
                    table.rows.insert(0, [''] * table.numberOfColumns)
                    row_no = 1
                    inserted = True
                else:
                    raise Exception(gettext('Row no is out of range: {row_no}').format(row_no=row_no))
            elif row_no > table.numberOfRows:
                if append_row_if_out_of_range:
                    table.rows.append([''] * table.numberOfColumns)
                    row_no = table.numberOfRows
                    inserted = True
                else:
                    raise Exception(gettext('Row no is out of range: {row_no}').format(row_no=row_no))
            if write_type == 'insert' and not inserted:
                table.rows.insert(row_no - 1, [''] * table.numberOfColumns)
        row_input_type = self.read_input('rowInputType')
        if row_input_type == 'row':
            row = self.read_input('row')
            for i in range(len(row)):
                table.rows[row_no - 1][i] = row[i]
        elif row_input_type == 'columns':
            columns = self.read_input('columns')
            for column in columns:
                column_no = table.resolve_column_no(self.evaluate_expression_in_process(column[0]))
                column_value = self.evaluate_expression_in_process(column[1])
                table.rows[row_no - 1][column_no - 1] = column_value
        else:
            raise Exception(gettext('Invalid row type'))
        return ControlFlow.NEXT

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        write_type = flow_node.input('writeType')
        if write_type == 'append':
            return gettext('Append a row to table ##{table}##').format(table=flow_node.input('table'))
        elif write_type == 'insert':
            return gettext('Insert a row to table ##{table}##').format(table=flow_node.input('table'))
        else:
            return gettext('Update a row in table ##{table}##').format(table=flow_node.input('table'))
