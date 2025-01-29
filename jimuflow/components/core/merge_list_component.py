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

from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class MergeListComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext('Merge list ##{firstList}## with ##{secondList}##, saving result to ##{list}##').format(
            firstList=flow_node.input('firstList'), secondList=flow_node.input('secondList'),
            list=flow_node.output('list'))

    async def execute(self) -> ControlFlow:
        first_list: list = self.read_input('firstList')
        second_list: list = self.read_input('secondList')
        merged_list: list = first_list + second_list
        await self.write_output('list', merged_list)
        return ControlFlow.NEXT
