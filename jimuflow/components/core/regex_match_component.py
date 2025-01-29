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

import re

from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class RegexMatchComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        find_first_match = flow_node.input('findFirstMatch')
        if find_first_match:
            return gettext(
                'Find the first ##{regex}## in text ##{originalText}## and save the matched text to ##{result}##').format(
                regex=flow_node.input('regex'),
                originalText=flow_node.input('originalText'),
                result=flow_node.output('result'))
        else:
            return gettext(
                'Find all ##{regex}## in text ##{originalText}## and save the matched text list to ##{result}##').format(
                regex=flow_node.input('regex'),
                originalText=flow_node.input('originalText'),
                result=flow_node.output('result'))

    async def execute(self) -> ControlFlow:
        original_text: str = self.read_input('originalText')
        find_first_match = self.read_input('findFirstMatch')
        ignore_case = self.read_input('ignoreCase')
        regex = self.read_input('regex')
        if original_text is None:
            result = None if find_first_match else []
        else:
            if find_first_match:
                result = re.search(regex, original_text, flags=re.IGNORECASE if ignore_case else 0)
                if result is not None:
                    result = result[0]
                else:
                    result = None
            else:
                result = [match[0] for match in
                          re.finditer(regex, original_text, flags=re.IGNORECASE if ignore_case else 0)]
        await self.write_output('result', result)
        return ControlFlow.NEXT
