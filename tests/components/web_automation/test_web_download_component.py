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

import os.path
import tempfile

import pytest

from jimuflow.components.web_automation import WebDownloadComponent
from jimuflow.components.web_automation.playwright_utils import open_web_browser
from jimuflow.runtime.execution_engine import ControlFlow
from jimuflow.runtime.expression import escape_string
from tests.utils import create_component_context, add_test_web_element


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_download_with_button(http_server, headless):
    with tempfile.TemporaryDirectory() as temp_dir:
        async with create_component_context(WebDownloadComponent) as component:
            browser_context = await open_web_browser(component.process, headless=headless)
            page = await browser_context.new_page()
            await page.goto(f'{http_server}/page1.html')
            await component.process.update_variable('wp', page)
            component.node.inputs = {
                "webPage": 'wp',
                "downloadType": 'click_element',
                "elementUri": add_test_web_element(component, '//*[@id="test16"]'),
                "saveFolder": escape_string(str(temp_dir)),
                "fileNamingType": 'suggested',
                "overrideExistingFile": False,
                "downloadTimeout": '"300"'
            }
            component.node.outputs = {
                "downloadFilename": 'r'
            }
            assert (await component.execute()) == ControlFlow.NEXT
            result = component.process.get_variable('r')
            assert os.path.isfile(result)
            assert os.path.basename(result) == 'file.dat'
            assert os.path.dirname(result) == str(temp_dir)
            with open(result, 'r') as f:
                assert f.read() == 'hdwkc\n'


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_download_with_link(http_server, headless):
    with tempfile.TemporaryDirectory() as temp_dir:
        async with create_component_context(WebDownloadComponent) as component:
            browser_context = await open_web_browser(component.process, headless=headless)
            page = await browser_context.new_page()
            await page.goto(f'{http_server}/page1.html')
            await component.process.update_variable('wp', page)
            component.node.inputs = {
                "webPage": 'wp',
                "downloadType": 'open_url',
                "url": escape_string(f'{http_server}/file.dat'),
                "saveFolder": escape_string(str(temp_dir)),
                "fileNamingType": 'custom',
                "customFilename": escape_string('custom.dat'),
                "overrideExistingFile": False,
                "downloadTimeout": '"300"'
            }
            component.node.outputs = {
                "downloadFilename": 'r'
            }
            assert (await component.execute()) == ControlFlow.NEXT
            result = component.process.get_variable('r')
            assert os.path.isfile(result)
            assert os.path.basename(result) == 'custom.dat'
            assert os.path.dirname(result) == str(temp_dir)
            with open(result, 'r') as f:
                assert f.read() == 'hdwkc\n'


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_download_timeout(http_server, headless):
    with tempfile.TemporaryDirectory() as temp_dir:
        async with create_component_context(WebDownloadComponent) as component:
            browser_context = await open_web_browser(component.process, headless=headless)
            page = await browser_context.new_page()
            await page.goto(f'{http_server}/page1.html')
            await component.process.update_variable('wp', page)
            component.node.inputs = {
                "webPage": 'wp',
                "downloadType": 'open_url',
                "url": escape_string(f'{http_server}/file.dat?delay=2'),
                "saveFolder": escape_string(str(temp_dir)),
                "fileNamingType": 'custom',
                "customFilename": escape_string('custom.dat'),
                "overrideExistingFile": False,
                "downloadTimeout": '"1"',
                "waitTime": '"1"',
            }
            component.node.outputs = {
                "downloadFilename": 'r'
            }
            with pytest.raises(Exception):
                await component.execute()
