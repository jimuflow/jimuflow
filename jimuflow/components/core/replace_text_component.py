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

import re

from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class ReplaceTextComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        replace_type = flow_node.input('replaceType')
        if replace_type == 'text':
            something_to_replace = flow_node.input('textToReplace')
        else:
            something_to_replace = flow_node.input('regexToReplace')
        replace_first_match = flow_node.input('replaceFirstMatch')
        if replace_first_match:
            return gettext(
                'Replace the first ##{something_to_replace}## in text ##{originalText}## with ##{replacementText}## and save the result to ##{result}##').format(
                something_to_replace=something_to_replace,
                originalText=flow_node.input('originalText'),
                replacementText=flow_node.input('replacementText'),
                result=flow_node.output('result'))
        else:
            return gettext(
                'Replace all ##{something_to_replace}## in text ##{originalText}## with ##{replacementText}## and save the result to ##{result}##').format(
                something_to_replace=something_to_replace,
                originalText=flow_node.input('originalText'),
                replacementText=flow_node.input('replacementText'),
                result=flow_node.output('result'))

    async def execute(self) -> ControlFlow:
        original_text: str = self.read_input('originalText')
        if original_text is None or original_text == '':
            result = original_text
        else:
            replace_type = self.read_input('replaceType')
            if replace_type == 'text':
                text_to_replace = self.read_input('textToReplace')
                pattern = re.escape(text_to_replace)
            else:
                pattern = self.read_input('regexToReplace')
            replacement_text: str = self.read_input('replacementText')
            replace_first_match = self.read_input('replaceFirstMatch')
            ignore_case = self.read_input('ignoreCase')
            result = re.sub(pattern, replacement_text, original_text, count=1 if replace_first_match else 0,
                            flags=re.IGNORECASE if ignore_case else 0)
        await self.write_output('result', result)
        return ControlFlow.NEXT
