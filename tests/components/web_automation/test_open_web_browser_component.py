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

import pytest
from playwright.async_api import BrowserContext

from jimuflow.components.web_automation import OpenWebBrowserComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component_context


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_execute(http_server, headless):
    async with create_component_context(OpenWebBrowserComponent) as component:
        component.node.inputs = {
            "enableProxy": False,
            "headless": headless
        }
        component.node.outputs = {
            "webBrowser": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        page = component.process.get_variable('r')
        assert isinstance(page, BrowserContext)
