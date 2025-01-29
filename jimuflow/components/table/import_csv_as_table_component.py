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

import csv

from jimuflow.datatypes import Table
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class ImportCsvAsTableComponent(PrimitiveComponent):

    async def execute(self) -> ControlFlow:
        file_path = self.read_input('filePath')
        file_encoding = self.read_input('fileEncoding')
        if file_encoding == 'system_default':
            encoding = None
        else:
            encoding = file_encoding
        use_custom_delimiter = self.read_input('useCustomDelimiter')
        if use_custom_delimiter:
            delimiter = self.read_input('customDelimiter')
        else:
            delimiter = ','
        with open(file_path, mode='r', encoding=encoding) as file:
            reader = csv.reader(file, delimiter=delimiter)
            use_first_row_as_header = self.read_input('useFirstRowAsHeader')
            first_row = True
            for row in reader:
                if first_row:
                    if use_first_row_as_header:
                        table = Table(row)
                    else:
                        table = Table([f'column{i + 1}' for i in range(len(row))])
                        table.rows.append(row)
                    first_row = False
                else:
                    table.rows.append(row)

        await self.write_output('table', table)
        return ControlFlow.NEXT

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext(
            'Import csv file ##{filePath}## as table ##{table}##').format(
            filePath=flow_node.input('filePath'), table=flow_node.output('table'))
