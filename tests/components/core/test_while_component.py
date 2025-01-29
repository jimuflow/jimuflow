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

from jimuflow.components.core import WhileComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component, add_mock_component, MockComponent


@pytest.fixture
async def while_component():
    component = create_component(WhileComponent)
    component.node.inputs = {
        "operand1": "a",
        "op": "<",
        "operand2": "3",
    }
    await component.process.update_variable("a", 0)
    return component


@pytest.mark.asyncio
async def test_execute(while_component):
    while_component = await while_component
    loop_count = [0]

    async def mock_loop_body(component: MockComponent):
        loop_count[0] = loop_count[0] + 1
        a = component.process.get_variable("a")
        await component.process.update_variable("a", a + 1)
        return ControlFlow.NEXT

    add_mock_component(while_component, mock_loop_body)
    assert (await while_component.execute()) == ControlFlow.NEXT
    assert loop_count == [3]


@pytest.mark.asyncio
async def test_break(while_component):
    while_component = await while_component
    loop_count = [0]

    async def mock_loop_body(component: MockComponent):
        loop_count[0] = loop_count[0] + 1
        a = component.process.get_variable("a")
        await component.process.update_variable("a", a + 1)
        if a >= 1:
            return ControlFlow.BREAK
        return ControlFlow.NEXT

    add_mock_component(while_component, mock_loop_body)
    assert (await while_component.execute()) == ControlFlow.NEXT
    assert loop_count == [2]


@pytest.mark.asyncio
async def test_return(while_component):
    while_component = await while_component
    loop_count = [0]

    async def mock_loop_body(component: MockComponent):
        loop_count[0] = loop_count[0] + 1
        a = component.process.get_variable("a")
        await component.process.update_variable("a", a + 1)
        if a >= 1:
            return ControlFlow.RETURN
        return ControlFlow.NEXT

    add_mock_component(while_component, mock_loop_body)
    assert (await while_component.execute()) == ControlFlow.RETURN
    assert loop_count == [2]


@pytest.mark.asyncio
async def test_exit(while_component):
    while_component = await while_component
    loop_count = [0]

    async def mock_loop_body(component: MockComponent):
        loop_count[0] = loop_count[0] + 1
        a = component.process.get_variable("a")
        await component.process.update_variable("a", a + 1)
        if a >= 1:
            return ControlFlow.EXIT
        return ControlFlow.NEXT

    add_mock_component(while_component, mock_loop_body)
    assert (await while_component.execute()) == ControlFlow.EXIT
    assert loop_count == [2]
