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

from jimuflow.components.core import SplitTextComponent
from jimuflow.runtime.execution_engine import ControlFlow
from jimuflow.runtime.expression import escape_string
from tests.utils import create_component


@pytest.mark.asyncio
@pytest.mark.parametrize("textToBeSplit,standardDelimiter,filterEmptyItems,expected", [
    ("a b  c", 'space', True, ['a', 'b', 'c']),
    ("a b  c", 'space', False, ['a', 'b', '', 'c']),
    ("a\nb\r\n\nc", 'line_break', True, ['a', 'b', 'c']),
    ("a\tb\t\tc", 'tab', True, ['a', 'b', 'c']),
])
async def test_split_with_standard_char(textToBeSplit, standardDelimiter, filterEmptyItems, expected):
    component = create_component(SplitTextComponent)
    component.node.inputs = {
        "textToBeSplit": escape_string(textToBeSplit),
        "delimiterType": 'standard',
        "standardDelimiter": standardDelimiter,
        "filterEmptyItems": filterEmptyItems
    }
    component.node.outputs = {
        "result": "r"
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert component.process.get_variable("r") == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("textToBeSplit,customDelimiter,filterEmptyItems,useRegularExpr,expected", [
    ("a,b,,c", ',', True, False, ['a', 'b', 'c']),
    ("a,b,,c", ',', True, True, ['a', 'b', 'c']),
    ("a,b,,c", ',', False, True, ['a', 'b', '', 'c']),
])
async def test_split_with_custom_delimiter(textToBeSplit, customDelimiter, filterEmptyItems, useRegularExpr, expected):
    component = create_component(SplitTextComponent)
    component.node.inputs = {
        "textToBeSplit": escape_string(textToBeSplit),
        "delimiterType": 'custom',
        "customDelimiter": escape_string(customDelimiter),
        "filterEmptyItems": filterEmptyItems,
        "useRegularExpr": useRegularExpr
    }
    component.node.outputs = {
        "result": "r"
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert component.process.get_variable("r") == expected
