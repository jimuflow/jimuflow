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


class SetWebCheckboxValueComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        check_type = flow_node.input('checkType')
        element = describe_element_uri(flow_node.process_def.package, flow_node.input('elementUri'))
        if check_type == 'check':
            return gettext(
                'Check checkbox ##{element}## on web page ##{webPage}##').format(
                checkType=flow_node.input('checkType'), element=element, webPage=flow_node.input('webPage'))
        elif check_type == 'uncheck':
            return gettext(
                'Uncheck checkbox ##{element}## on web page ##{webPage}##').format(
                checkType=flow_node.input('checkType'), element=element, webPage=flow_node.input('webPage'))
        else:
            return gettext(
                'Toggle checkbox ##{element}## on web page ##{webPage}##').format(
                checkType=flow_node.input('checkType'), element=element, webPage=flow_node.input('webPage'))

    async def execute(self) -> ControlFlow:
        element_uri = self.read_input("elementUri")
        page: Page = self.read_input("webPage")
        check_type = self.read_input('checkType')
        delay_after_action = float(self.read_input("delayAfterAction"))
        wait_time = float(self.read_input("waitTime"))
        checkbox = await get_element_by_uri(self, page, element_uri, wait_time)
        checked = await checkbox.is_checked(timeout=wait_time * 1000)
        if check_type == 'check':
            if not checked:
                await checkbox.set_checked(True, timeout=wait_time * 1000)
        elif check_type == 'uncheck':
            if checked:
                await checkbox.set_checked(False, timeout=wait_time * 1000)
        elif check_type == 'toggle':
            await checkbox.set_checked(not checked, timeout=wait_time * 1000)
        if delay_after_action > 0:
            await asyncio.sleep(delay_after_action)
        return ControlFlow.NEXT
