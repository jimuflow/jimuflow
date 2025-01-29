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
from PIL import Image

from jimuflow.components.web_automation import ScreenshotWebElementComponent
from jimuflow.components.web_automation.playwright_utils import open_web_browser
from jimuflow.runtime.execution_engine import ControlFlow
from jimuflow.runtime.expression import escape_string
from tests.utils import create_component_context, add_test_web_element


@pytest.mark.asyncio
@pytest.mark.parametrize('headless, screenshotArea, xpath, fileFormat, fileNamingType', [
    (True, 'element', '//*[@id="div2"]', 'png', 'random'),
    (True, 'viewport', None, 'jpeg', 'custom'),
    (True, 'full_page', None, 'png', 'random'),
    (False, 'element', '//*[@id="div2"]', 'png', 'random'),
    (False, 'viewport', None, 'jpeg', 'custom'),
    (False, 'full_page', None, 'png', 'random'),
])
async def test_execute(http_server, headless, screenshotArea, xpath, fileFormat, fileNamingType):
    with tempfile.TemporaryDirectory() as temp_dir:
        async with create_component_context(ScreenshotWebElementComponent) as component:
            browser_context = await open_web_browser(component.process, headless=headless)
            page = await browser_context.new_page()
            await page.set_viewport_size({"width": 640, "height": 480})
            await page.goto(f'{http_server}/page2.html')
            await component.process.update_variable('wp', page)
            component.node.inputs = {
                "webPage": 'wp',
                "screenshotArea": screenshotArea,
                "elementUri": add_test_web_element(component, xpath) if xpath else None,
                "saveFolder": escape_string(str(temp_dir)),
                "fileFormat": fileFormat,
                "fileNamingType": fileNamingType,
                "customFilename": '"test"' if fileNamingType == 'custom' else None,
                "overrideExistingFile": False,
            }
            component.node.outputs = {
                "snapshotFilename": 'r'
            }
            assert (await component.execute()) == ControlFlow.NEXT
            result = component.process.get_variable('r')
            assert os.path.isfile(result)
            assert result.endswith(f'.{fileFormat}')
            if fileNamingType == 'custom':
                assert result == os.path.join(temp_dir, f'test.{fileFormat}')
            img = Image.open(result)
            try:
                if screenshotArea == 'element':
                    assert 600 < img.size[0] <= 640
                    assert img.size[1] == 1000
                elif screenshotArea == 'viewport':
                    assert img.size == (640, 480)
                elif screenshotArea == 'full_page':
                    assert 600 < img.size[0] <= 640
                    assert img.size[1] == 2000
            finally:
                img.close()
