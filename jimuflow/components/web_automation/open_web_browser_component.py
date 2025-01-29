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

import functools

from jimuflow.components.web_automation.playwright_utils import open_web_browser, close_web_browser
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class OpenWebBrowserComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext('Open a new web browser, and save to ##{webBrowser}##').format(
            webBrowser=flow_node.output('webBrowser'))

    async def execute(self) -> ControlFlow:
        enable_proxy = self.read_input('enableProxy')
        kwargs = {}
        if enable_proxy:
            kwargs['proxy'] = {
                'server': self.read_input('proxyServer'),
                'bypass': self.read_input('proxyBypass'),
                'username': self.read_input('proxyUsername'),
                'password': self.read_input('proxyPassword')
            }
        headless = self.read_input('headless')
        web_browser = await open_web_browser(self.process, headless=headless, **kwargs)
        await self.write_output('webBrowser', web_browser,
                                functools.partial(close_web_browser, self.process))
        return ControlFlow.NEXT
