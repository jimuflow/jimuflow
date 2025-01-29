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

from playwright.async_api import Page

from jimuflow.common.uri_utils import describe_element_uri
from jimuflow.components.web_automation.playwright_utils import get_element_by_uri
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class WebInputComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext(
            'Input ##{content}## into element ##{element}## on web page ##{webPage}##').format(
            content=flow_node.input('content'),
            element=describe_element_uri(flow_node.process_def.package, flow_node.input('elementUri')),
            webPage=flow_node.input('webPage'))

    async def execute(self) -> ControlFlow:
        element_uri = self.read_input("elementUri")
        page: Page = self.read_input("webPage")
        content = self.read_input("content")
        append = self.read_input("append")
        press_enter_after_input = self.read_input("pressEnterAfterInput")
        press_tab_after_input = self.read_input("pressTabAfterInput")
        simulate_human_input = self.read_input('simulateHumanInput')
        delay_after_focus = float(self.read_input("delayAfterFocus"))
        delay_after_action = float(self.read_input("delayAfterAction"))
        wait_time = float(self.read_input("waitTime"))
        element = await get_element_by_uri(self, page, element_uri, wait_time)
        if simulate_human_input:
            click_before_input = self.read_input("clickBeforeInput")
            input_interval = self.read_input('inputInterval')
            if click_before_input:
                await element.click(timeout=wait_time * 1000)
            if delay_after_focus > 0:
                await asyncio.sleep(delay_after_focus)
            if not append:
                await element.press("ControlOrMeta+a", timeout=wait_time * 1000)
                await element.press("Backspace", timeout=wait_time * 1000)
            await element.press_sequentially(content, delay=int(input_interval), timeout=wait_time * 1000)
        else:
            await element.focus(timeout=wait_time * 1000)
            if delay_after_focus > 0:
                await asyncio.sleep(delay_after_focus)
            if append:
                content = await element.input_value(timeout=wait_time * 1000) + content
            await element.fill(content, timeout=wait_time * 1000)
        if press_enter_after_input:
            await element.press("Enter", timeout=wait_time * 1000)
        if press_tab_after_input:
            await element.press("Tab", timeout=wait_time * 1000)
        if delay_after_action > 0:
            await asyncio.sleep(delay_after_action)
        return ControlFlow.NEXT
