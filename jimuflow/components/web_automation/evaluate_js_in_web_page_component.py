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

from playwright.async_api import Page

from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class EvaluateJsInWebPageComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext(
            'Evaluate js ##{jsCode}## in web page ##{webPage}##, and save the result to ##{output}##').format(
            jsCode=flow_node.input('jsCode'),
            webPage=flow_node.input('webPage'), output=flow_node.output('output'))

    async def execute(self) -> ControlFlow:
        page: Page = self.read_input('webPage')
        js_code = self.read_input('jsCode')
        output = await page.evaluate(js_code)
        await self.write_output('output', output)
        return ControlFlow.NEXT
