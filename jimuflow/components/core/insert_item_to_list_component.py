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


class InsertItemToListComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        insert_type = flow_node.input('insertType')
        if insert_type == 'append':
            return gettext('Append ##{value}## to list ##{list}##').format(value=flow_node.input('value'),
                                                                           list=flow_node.input('list'))
        else:
            return gettext('Insert ##{value}## at position ##{insertPosition}## in list ##{list}##').format(
                value=flow_node.input('value'), insertPosition=flow_node.input('insertPosition'),
                list=flow_node.input('list'))

    async def execute(self) -> ControlFlow:
        l: list = self.read_input('list')
        v = self.read_input('value')
        insert_type = self.read_input('insertType')
        if insert_type == 'append':
            l.append(v)
        else:
            insert_position = int(self.read_input('insertPosition'))
            l.insert(insert_position, v)
        return ControlFlow.NEXT
