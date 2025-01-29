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

from jimuflow.components.core import TextToNumberComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component


@pytest.mark.asyncio
async def test_convert_int_text():
    component = create_component(TextToNumberComponent)
    component.node.inputs = {
        "value": '"123"'
    }
    component.node.outputs = {
        "result": "r"
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert component.process.get_variable("r") == 123


@pytest.mark.asyncio
async def test_convert_float_text():
    component = create_component(TextToNumberComponent)
    component.node.inputs = {
        "value": '"1.2"'
    }
    component.node.outputs = {
        "result": "r"
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert component.process.get_variable("r") == 1.2


@pytest.mark.asyncio
async def test_convert_none_variable():
    component = create_component(TextToNumberComponent)
    component.node.inputs = {
        "value": 'v'
    }
    component.node.outputs = {
        "result": "r"
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert component.process.get_variable("r") is None


@pytest.mark.asyncio
async def test_convert_empty_text():
    component = create_component(TextToNumberComponent)
    component.node.inputs = {
        "value": '""'
    }
    component.node.outputs = {
        "result": "r"
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert component.process.get_variable("r") is None


@pytest.mark.asyncio
async def test_convert_non_number_text():
    component = create_component(TextToNumberComponent)
    component.node.inputs = {
        "value": '"abc"'
    }
    component.node.outputs = {
        "result": "r"
    }
    with pytest.raises(ValueError):
        await component.execute()
