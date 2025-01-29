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


class SortListComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        sort_order = flow_node.input('sortOrder')
        if sort_order == 'asc':
            return gettext('Sort list ##{list}## in ascending order').format(list=flow_node.input('list'))
        else:
            return gettext('Sort list ##{list}## in descending order').format(list=flow_node.input('list'))

    async def execute(self) -> ControlFlow:
        l: list = self.read_input('list')
        sort_order = self.read_input('sortOrder')
        l.sort(reverse=sort_order == 'desc')
        return ControlFlow.NEXT
