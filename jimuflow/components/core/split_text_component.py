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

standard_delimiters = {
    'space': gettext('space character'), 'line_break': gettext('line break character'), 'tab': gettext('tab character')
}


class SplitTextComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        delimiter_type = flow_node.input('delimiterType')
        filter_empty_items = flow_node.input('filterEmptyItems')
        if delimiter_type == 'standard':
            if filter_empty_items:
                return gettext(
                    'Split ##{textToBeSplit}## by ##{standardDelimiter}##, filter empty items, and save the result to ##{result}##').format(
                    textToBeSplit=flow_node.input('textToBeSplit'),
                    standardDelimiter=standard_delimiters[flow_node.input('standardDelimiter')],
                    result=flow_node.output('result'))
            else:
                return gettext(
                    'Split ##{textToBeSplit}## by ##{standardDelimiter}##, and save the result to ##{result}##').format(
                    textToBeSplit=flow_node.input('textToBeSplit'),
                    standardDelimiter=standard_delimiters[flow_node.input('standardDelimiter')],
                    result=flow_node.output('result'))
        else:
            use_regular_expr = flow_node.input('useRegularExpr')
            if use_regular_expr:
                if filter_empty_items:
                    return gettext(
                        'Split ##{textToBeSplit}## by regular expression ##{customDelimiter}##, filter empty items, and save the result to ##{result}##').format(
                        textToBeSplit=flow_node.input('textToBeSplit'),
                        customDelimiter=flow_node.input('customDelimiter'),
                        result=flow_node.output('result'))
                else:
                    return gettext(
                        'Split ##{textToBeSplit}## by regular expression ##{customDelimiter}##, and save the result to ##{result}##').format(
                        textToBeSplit=flow_node.input('textToBeSplit'),
                        customDelimiter=flow_node.input('customDelimiter'),
                        result=flow_node.output('result'))
            else:
                if filter_empty_items:
                    return gettext(
                        'Split ##{textToBeSplit}## by ##{customDelimiter}##, filter empty items, and save the result to ##{result}##').format(
                        textToBeSplit=flow_node.input('textToBeSplit'),
                        customDelimiter=flow_node.input('customDelimiter'),
                        result=flow_node.output('result'))
                else:
                    return gettext(
                        'Split ##{textToBeSplit}## by ##{customDelimiter}##, and save the result to ##{result}##').format(
                        textToBeSplit=flow_node.input('textToBeSplit'),
                        customDelimiter=flow_node.input('customDelimiter'),
                        result=flow_node.output('result'))

    async def execute(self) -> ControlFlow:
        text_to_be_split: str = self.read_input('textToBeSplit')
        if text_to_be_split is None or text_to_be_split == '':
            result = []
        else:
            delimiter_type = self.read_input('delimiterType')
            if delimiter_type == 'standard':
                standard_delimiter = self.read_input('standardDelimiter')
                if standard_delimiter == 'space':
                    delimiter = r'\s'
                elif standard_delimiter == 'line_break':
                    delimiter = r'\r?\n'
                else:
                    delimiter = r'\t'
            else:
                delimiter = self.read_input('customDelimiter')
                use_regular_expr = self.read_input('useRegularExpr')
                if not use_regular_expr:
                    delimiter = re.escape(delimiter)
            result = re.split(delimiter, text_to_be_split)
        filter_empty_items = self.read_input('filterEmptyItems')
        if filter_empty_items:
            result = [item for item in result if item != '']
        await self.write_output('result', result)
        return ControlFlow.NEXT
