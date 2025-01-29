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

from jimuflow.components.core import SliceTextComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component


@pytest.mark.asyncio
@pytest.mark.parametrize("originalText,slicedLength,expected", [
    ('"abc"', -1, 'abc'),
    ('"abc"', 1, 'a'),
    ('"abc"', 2, 'ab'),
])
async def test_slice_from_first_char(originalText, slicedLength, expected):
    component = create_component(SliceTextComponent)
    component.node.inputs = {
        "originalText": originalText,
        "fromWhere": 'first_char',
        "toWhere": 'end' if slicedLength == -1 else 'specified_length',
        "slicedLength": f'{slicedLength}',
    }
    component.node.outputs = {
        "result": "r"
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert component.process.get_variable("r") == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("originalText,startingPosition,slicedLength,expected", [
    ('"abcdef"', 1, -1, 'bcdef'),
    ('"abcdef"', 1, 1, 'b'),
    ('"abcdef"', 1, 2, 'bc'),
    ('"abcdef"', -3, 2, 'de'),
    ('"abcdef"', -9, 2, ''),
    ('"abcdef"', -9, 4, 'a'),
])
async def test_slice_from_specified_position(originalText, startingPosition, slicedLength, expected):
    component = create_component(SliceTextComponent)
    component.node.inputs = {
        "originalText": originalText,
        "fromWhere": 'specified_position',
        "startingPosition": f'{startingPosition}',
        "toWhere": 'end' if slicedLength == -1 else 'specified_length',
        "slicedLength": f'{slicedLength}',
    }
    component.node.outputs = {
        "result": "r"
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert component.process.get_variable("r") == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("originalText,startingText,slicedLength,expected", [
    ('"abcdef"', '"b"', -1, 'bcdef'),
    ('"abcdef"', '"b"', 1, 'b'),
    ('"abcdef"', '"b"', 2, 'bc'),
    ('"abcdef"', '"g"', 2, ''),
])
async def test_slice_from_specified_text(originalText, startingText, slicedLength, expected):
    component = create_component(SliceTextComponent)
    component.node.inputs = {
        "originalText": originalText,
        "fromWhere": 'specified_text',
        "startingText": startingText,
        "toWhere": 'end' if slicedLength == -1 else 'specified_length',
        "slicedLength": f'{slicedLength}',
    }
    component.node.outputs = {
        "result": "r"
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert component.process.get_variable("r") == expected
