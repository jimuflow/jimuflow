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

import asyncio
from pathlib import Path

from playwright.async_api import Page

from jimuflow.common.uri_utils import describe_element_uri
from jimuflow.components.web_automation.playwright_utils import get_element_by_uri
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class WebDownloadComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        download_type = flow_node.input("downloadType")
        if download_type == 'click_element':
            return gettext(
                'Click ##{element}## on web page ##{webPage}## to download, and save the downloaded file to ##{downloadFilename}##').format(
                element=describe_element_uri(flow_node.process_def.package, flow_node.input('elementUri')),
                webPage=flow_node.input('webPage'),
                downloadFilename=flow_node.output("downloadFilename"))
        else:
            return gettext(
                'Open ##{url}## on web page ##{webPage}## to download, and save the downloaded file to ##{downloadFilename}##').format(
                url=flow_node.input('url'), webPage=flow_node.input('webPage'),
                downloadFilename=flow_node.output("downloadFilename"))

    async def execute(self) -> ControlFlow:
        page: Page = self.read_input("webPage")
        download_type = self.read_input("downloadType")
        save_folder = self.read_input("saveFolder")
        file_naming_type = self.read_input("fileNamingType")
        wait_time = int(self.read_input("waitTime"))
        if download_type == 'click_element':
            async with page.expect_download(timeout=wait_time * 1000) as download_info:
                element_uri = self.read_input("elementUri")
                element = await get_element_by_uri(self, page, element_uri, wait_time)
                await element.click(timeout=wait_time * 1000)
        elif download_type == 'open_url':
            async with page.expect_download(timeout=wait_time * 1000) as download_info:
                download_url = self.read_input("url")
                await page.evaluate("""
                download_url=>{
                    window.open(download_url)
                }
                """, download_url)
        else:
            raise Exception("Invalid download type: " + download_type)
        download = await download_info.value
        if file_naming_type == "suggested":
            # 使用uuid生成随机文件名
            file_name = download.suggested_filename
        else:
            file_name = self.read_input("customFilename")
        file_path = Path(save_folder).absolute() / file_name
        override_existing_file = self.read_input("overrideExistingFile")
        if file_path.exists() and not override_existing_file:
            raise Exception("File already exists: " + str(file_path))
        download_timeout = int(self.read_input("downloadTimeout"))
        async with asyncio.timeout(download_timeout):
            await download.save_as(str(file_path))
        await self.write_output('downloadFilename', str(file_path))
        return ControlFlow.NEXT
