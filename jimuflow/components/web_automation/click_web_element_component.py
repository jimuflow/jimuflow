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


class ClickWebElementComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        action = gettext('Single click') if flow_node.input('clickType') == 'single_click' else gettext(
            'Double click')
        return gettext(
            '{action} ##{element}## on web page ##{webPage}##').format(
            action=action,
            element=describe_element_uri(flow_node.process_def.package, flow_node.input('elementUri')),
            webPage=flow_node.input('webPage'))

    async def execute(self) -> ControlFlow:
        element_uri = self.read_input("elementUri")
        page: Page = self.read_input("webPage")
        simulate_human_click = self.read_input('simulateHumanClick')
        click_type = self.read_input('clickType')
        mouse_button = self.read_input('mouseButton')
        modifier_key = self.read_input('modifierKey')
        delay_after_action = float(self.read_input("delayAfterAction"))
        wait_time = float(self.read_input("waitTime"))
        element = await get_element_by_uri(self, page, element_uri, wait_time)
        if click_type == 'single_click':
            await element.click(force=not simulate_human_click, button=mouse_button,
                                modifiers=[modifier_key] if modifier_key != 'none' else None,
                                timeout=wait_time * 1000)
        else:
            await element.dblclick(force=not simulate_human_click, button=mouse_button,
                                   modifiers=[modifier_key] if modifier_key != 'none' else None,
                                   timeout=wait_time * 1000)
        if delay_after_action > 0:
            await asyncio.sleep(delay_after_action)
        return ControlFlow.NEXT
