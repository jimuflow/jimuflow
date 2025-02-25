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

import urllib.parse

from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class UrlDecodeComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext('Url decode ##{textToDecode}##, and save the result to ##{result}##').format(
            textToDecode=flow_node.input('textToDecode'),
            result=flow_node.output('result')
        )

    async def execute(self) -> ControlFlow:
        text_to_decode: str = self.read_input('textToDecode')
        if text_to_decode is None:
            result = None
        else:
            result = urllib.parse.unquote_plus(text_to_decode)
        await self.write_output('result', result)
        return ControlFlow.NEXT
