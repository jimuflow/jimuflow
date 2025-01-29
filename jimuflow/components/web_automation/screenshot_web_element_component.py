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

import uuid
from pathlib import Path

from playwright.async_api import Page

from jimuflow.common.uri_utils import describe_element_uri
from jimuflow.components.web_automation.playwright_utils import get_element_by_uri
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class ScreenshotWebElementComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        screenshot_area = flow_node.input("screenshotArea")
        if screenshot_area == 'element':
            return gettext(
                'Screenshot ##{element}## on web page ##{webPage}##, and save to ##{snapshotFilename}##').format(
                element=describe_element_uri(flow_node.process_def.package, flow_node.input('elementUri')),
                webPage=flow_node.input('webPage'),
                snapshotFilename=flow_node.output("snapshotFilename"))
        else:
            return gettext(
                'Screenshot web page ##{webPage}##, and save to ##{snapshotFilename}##').format(
                webPage=flow_node.input('webPage'),
                snapshotFilename=flow_node.output("snapshotFilename"))

    async def execute(self) -> ControlFlow:
        page: Page = self.read_input("webPage")
        screenshot_area = self.read_input("screenshotArea")
        save_folder = self.read_input("saveFolder")
        file_format = self.read_input("fileFormat")
        file_naming_type = self.read_input("fileNamingType")
        if file_naming_type == "random":
            # 使用uuid生成随机文件名
            file_name = "screenshot_" + str(uuid.uuid4()) + "." + file_format
        else:
            file_name = self.read_input("customFilename") + "." + file_format
        file_path = Path(save_folder).absolute() / file_name
        override_existing_file = self.read_input("overrideExistingFile")
        if file_path.exists() and not override_existing_file:
            raise Exception("File already exists: " + str(file_path))
        wait_time = int(self.read_input("waitTime"))
        if screenshot_area == 'element':
            element_uri = self.read_input("elementUri")
            element = await get_element_by_uri(self, page, element_uri, wait_time)
            await element.screenshot(path=str(file_path), timeout=wait_time * 1000)
        elif screenshot_area == 'viewport':
            await page.screenshot(path=str(file_path), timeout=wait_time * 1000)
        elif screenshot_area == 'full_page':
            await page.screenshot(path=str(file_path), full_page=True, timeout=wait_time * 1000)
        await self.write_output('snapshotFilename', str(file_path))
        return ControlFlow.NEXT
