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


class CreateTableComponent(PrimitiveComponent):

    async def execute(self) -> ControlFlow:
        column_names = self.read_input('columnNames').split(',')
        table = Table(column_names)
        await self.write_output('table', table)
        return ControlFlow.NEXT

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext(
            'Create an empty data table with the headers ##{columnNames}##, and save the table to ##{table}##').format(
            columnNames=flow_node.input('columnNames'), table=flow_node.output('table'))
