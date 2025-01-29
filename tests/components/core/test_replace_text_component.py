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

from jimuflow.components.core import ReplaceTextComponent
from jimuflow.runtime.execution_engine import ControlFlow
from jimuflow.runtime.expression import escape_string
from tests.utils import create_component


@pytest.mark.asyncio
@pytest.mark.parametrize("originalText,textToReplace,replacementText,replaceFirstMatch,ignoreCase,expected", [
    ("abcbeBg", 'b', "1", False, False, "a1c1eBg"),
    ("abcbeBg", 'b', "1", False, True, "a1c1e1g"),
    ("abcbeBg", 'b', "1", True, False, "a1cbeBg"),
    ("abcbeBg", 'f', "1", False, False, "abcbeBg"),
])
async def test_replace_with_text(originalText, textToReplace, replacementText, replaceFirstMatch, ignoreCase, expected):
    component = create_component(ReplaceTextComponent)
    component.node.inputs = {
        "originalText": escape_string(originalText),
        "replaceType": 'text',
        "textToReplace": escape_string(textToReplace),
        "replacementText": escape_string(replacementText),
        "replaceFirstMatch": replaceFirstMatch,
        "ignoreCase": ignoreCase
    }
    component.node.outputs = {
        "result": "r"
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert component.process.get_variable("r") == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("originalText,regexToReplace,replacementText,replaceFirstMatch,ignoreCase,expected", [
    ("abcbeBg", 'b', "1", False, False, "a1c1eBg"),
    ("abcbeBg", 'b', "1", False, True, "a1c1e1g"),
    ("abcbeBg", 'b', "1", True, False, "a1cbeBg"),
    ("abcbeBg", 'f', "1", False, False, "abcbeBg"),
])
async def test_replace_with_regex(originalText, regexToReplace, replacementText, replaceFirstMatch, ignoreCase,
                                  expected):
    component = create_component(ReplaceTextComponent)
    component.node.inputs = {
        "originalText": escape_string(originalText),
        "replaceType": 'regex',
        "regexToReplace": escape_string(regexToReplace),
        "replacementText": escape_string(replacementText),
        "replaceFirstMatch": replaceFirstMatch,
        "ignoreCase": ignoreCase
    }
    component.node.outputs = {
        "result": "r"
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert component.process.get_variable("r") == expected
