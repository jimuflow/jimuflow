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

from jimuflow.common.uri_utils import describe_element_uri
from jimuflow.components.web_automation.playwright_utils import get_element_by_uri
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class WebUploadComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext(
            'Click ##{element}## on web page ##{webPage}## to upload ##{filePath}##').format(
            element=describe_element_uri(flow_node.process_def.package, flow_node.input('elementUri')),
            webPage=flow_node.input('webPage'), filePath=flow_node.input('filePath'))

    async def execute(self) -> ControlFlow:
        page: Page = self.read_input("webPage")
        wait_time = int(self.read_input("waitTime"))
        wait_dialog_time = int(self.read_input("waitDialogTime"))
        file_path = self.read_input('filePath')
        element_uri = self.read_input("elementUri")
        element = await get_element_by_uri(self, page, element_uri, wait_time)
        async with page.expect_file_chooser(timeout=wait_dialog_time * 1000) as fc_info:
            await element.click(timeout=wait_time * 1000)
        file_chooser = await fc_info.value
        await file_chooser.set_files(file_path)
        return ControlFlow.NEXT
