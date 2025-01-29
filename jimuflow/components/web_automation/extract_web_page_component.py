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


class ExtractWebPageComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        extract_type = flow_node.input('extractType')
        if extract_type == 'title':
            extract_data = gettext('title')
        elif extract_type == 'url':
            extract_data = gettext('url')
        elif extract_type == 'html':
            extract_data = gettext('html content')
        elif extract_type == 'text':
            extract_data = gettext('text content')
        else:
            extract_data = gettext('?')
        return gettext(
            'Extract the ##{extractData}## of web page ##{webPage}##, and save to ##{result}##').format(
            extractData=extract_data, webPage=flow_node.input('webPage'),
            result=flow_node.output('result'))

    async def execute(self) -> ControlFlow:
        page: Page = self.read_input("webPage")
        extract_type = self.read_input('extractType')
        if extract_type == 'title':
            result = await page.title()
        elif extract_type == 'url':
            result = page.url
        elif extract_type == 'html':
            result = await page.locator("xpath=/html").inner_html()
        elif extract_type == 'text':
            result = await page.locator("xpath=/html").inner_text()
        else:
            raise Exception('Unsupported extract type: ' + extract_type)
        await self.write_output('result', result)
        return ControlFlow.NEXT
