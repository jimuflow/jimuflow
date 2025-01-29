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
import re

from playwright.async_api import Page

from jimuflow.common.uri_utils import describe_element_uri
from jimuflow.components.web_automation.playwright_utils import get_element_by_uri
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class SetWebSelectValueComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        select_type = flow_node.input('selectType')
        if select_type == 'by_content':
            match_content = flow_node.input("optionContent")
            match_type = flow_node.input('matchType')
            if match_type == 'equals':
                return gettext(
                    'Select option in drop-down box ##{element}## with content ##{content}##').format(
                    element=describe_element_uri(flow_node.process_def.package, flow_node.input('elementUri')),
                    content=match_content)
            elif match_type == 'contains':
                return gettext(
                    'Select option in drop-down box ##{element}## with content containing ##{content}##').format(
                    element=describe_element_uri(flow_node.process_def.package, flow_node.input('elementUri')),
                    content=match_content)
            else:
                return gettext(
                    'Select option in drop-down box ##{element}## with content matching regex ##{content}##').format(
                    element=describe_element_uri(flow_node.process_def.package, flow_node.input('elementUri')),
                    content=match_content)
        else:
            return gettext(
                'Select the option indexed as ##{index}## in the drop-down box ##{element}##').format(
                index=flow_node.input('optionIndex'),
                element=describe_element_uri(flow_node.process_def.package, flow_node.input('elementUri')))

    async def execute(self) -> ControlFlow:
        element_uri = self.read_input("elementUri")
        page: Page = self.read_input("webPage")
        select_type = self.read_input('selectType')
        delay_after_action = float(self.read_input("delayAfterAction"))
        wait_time = float(self.read_input("waitTime"))
        element = await get_element_by_uri(self, page, element_uri, wait_time)
        if select_type == 'by_content':
            match_content = self.read_input("optionContent")
            match_type = self.read_input('matchType')
            if match_type == 'equals':
                await element.select_option(label=match_content, timeout=wait_time * 1000)
            else:
                found_option = None
                options = element.locator("xpath=//option")
                for option in await options.all():
                    option_content = await option.inner_text()
                    if match_type == 'contains' and match_content in option_content:
                        found_option = option_content
                        break
                    elif match_type == 'regex' and re.search(match_content, option_content):
                        found_option = option_content
                        break
                if found_option:
                    await element.select_option(label=found_option, timeout=wait_time * 1000)
        else:
            option_index = int(self.read_input("optionIndex"))
            await element.select_option(index=option_index, timeout=wait_time * 1000)
        if delay_after_action > 0:
            await asyncio.sleep(delay_after_action)
        return ControlFlow.NEXT
