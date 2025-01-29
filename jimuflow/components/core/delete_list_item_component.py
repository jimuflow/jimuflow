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


class DeleteListItemComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        delete_type = flow_node.input('deleteType')
        if delete_type == 'by_position':
            return gettext('Delete item at position ##{position}## in list ##{list}##').format(
                position=flow_node.input('position'), list=flow_node.input('list'))
        else:
            return gettext('Delete item ##{value}## in list ##{list}##').format(
                value=flow_node.input('value'), list=flow_node.input('list'))

    async def execute(self) -> ControlFlow:
        l: list = self.read_input('list')
        delete_type = self.read_input('deleteType')
        if delete_type == 'by_position':
            position = int(self.read_input('position'))
            l.pop(position)
        else:
            v = self.read_input('value')
            if v in l:
                l.remove(v)
        return ControlFlow.NEXT
