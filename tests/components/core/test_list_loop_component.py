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

from jimuflow.components.core import ListLoopComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component, add_mock_component, MockComponent


@pytest.fixture
async def loop_component():
    component = create_component(ListLoopComponent)
    component.node.inputs = {
        "list": "items"
    }
    component.node.outputs = {
        "loopItem": "i"
    }
    await component.process.update_variable("items", [0, 1, 2])
    return component


@pytest.mark.asyncio
async def test_execute(loop_component):
    loop_component = await loop_component
    loop_items = []

    async def mock_loop_body(component: MockComponent):
        loop_items.append(component.process.get_variable("i"))
        return ControlFlow.NEXT

    add_mock_component(loop_component, mock_loop_body)
    assert (await loop_component.execute()) == ControlFlow.NEXT
    assert loop_items == [0, 1, 2]


@pytest.mark.asyncio
async def test_break(loop_component):
    loop_component = await loop_component
    loop_items = []

    async def mock_loop_body(component: MockComponent):
        i = component.process.get_variable("i")
        loop_items.append(i)
        if i >= 1:
            return ControlFlow.BREAK
        return ControlFlow.NEXT

    add_mock_component(loop_component, mock_loop_body)
    assert (await loop_component.execute()) == ControlFlow.NEXT
    assert loop_items == [0, 1]


@pytest.mark.asyncio
async def test_return(loop_component):
    loop_component = await loop_component
    loop_items = []

    async def mock_loop_body(component: MockComponent):
        i = component.process.get_variable("i")
        loop_items.append(i)
        if i >= 1:
            return ControlFlow.RETURN
        return ControlFlow.NEXT

    add_mock_component(loop_component, mock_loop_body)
    assert (await loop_component.execute()) == ControlFlow.RETURN
    assert loop_items == [0, 1]


@pytest.mark.asyncio
async def test_exit(loop_component):
    loop_component = await loop_component
    loop_items = []

    async def mock_loop_body(component: MockComponent):
        i = component.process.get_variable("i")
        loop_items.append(i)
        if i >= 1:
            return ControlFlow.EXIT
        return ControlFlow.NEXT

    add_mock_component(loop_component, mock_loop_body)
    assert (await loop_component.execute()) == ControlFlow.EXIT
    assert loop_items == [0, 1]
