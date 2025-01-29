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

from jimuflow.components.core import RegexMatchComponent
from jimuflow.runtime.execution_engine import ControlFlow
from jimuflow.runtime.expression import escape_string
from tests.utils import create_component


@pytest.mark.asyncio
@pytest.mark.parametrize("originalText,regex,findFirstMatch,ignoreCase,expected", [
    ("abcbeBg", 'b', False, False, ['b', 'b']),
    ("abcbeBg", 'b', False, True, ['b', 'b', 'B']),
    ("abcbeBg", 'b', True, False, 'b'),
    ("abcbeBg", 'f', False, False, []),
])
async def test_execute(originalText, regex, findFirstMatch, ignoreCase, expected):
    component = create_component(RegexMatchComponent)
    component.node.inputs = {
        "originalText": escape_string(originalText),
        "regex": escape_string(regex),
        "findFirstMatch": findFirstMatch,
        "ignoreCase": ignoreCase
    }
    component.node.outputs = {
        "result": "r"
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert component.process.get_variable("r") == expected
