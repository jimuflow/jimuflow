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

from jimuflow.components.table import LoopTableRowsComponent
from jimuflow.datatypes import Table
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component, add_mock_component, MockComponent


@pytest.fixture
async def loop_component():
    table = Table(['ID', '名称'])
    table.rows = [[1, "abc"], [2, "efg"], [3, "hij"]]
    component = create_component(LoopTableRowsComponent)
    await component.process.update_variable("t", table)
    component.node.inputs = {
        "table": "t",
    }
    component.node.outputs = {
        "currentRow": "i"
    }
    return component


@pytest.mark.asyncio
async def test_execute(loop_component):
    loop_component = await loop_component
    loop_component.node.inputs["loopRange"] = 'all'
    loop_item_list = []

    async def mock_loop_body(component: MockComponent):
        loop_item_list.append(component.process.get_variable("i"))
        return ControlFlow.NEXT

    add_mock_component(loop_component, mock_loop_body)
    assert (await loop_component.execute()) == ControlFlow.NEXT
    assert loop_item_list == [[1, "abc"], [2, "efg"], [3, "hij"]]


@pytest.mark.asyncio
async def test_break(loop_component):
    loop_component = await loop_component
    loop_component.node.inputs["loopRange"] = 'range'
    loop_component.node.inputs["startRowNo"] = '2'
    loop_component.node.inputs["endRowNo"] = '3'

    loop_item_list = []

    async def mock_loop_body(component: MockComponent):
        i = component.process.get_variable("i")
        loop_item_list.append(i)
        if i[0] >= 2:
            return ControlFlow.BREAK
        return ControlFlow.NEXT

    add_mock_component(loop_component, mock_loop_body)
    assert (await loop_component.execute()) == ControlFlow.NEXT
    assert loop_item_list == [[2, "efg"]]


@pytest.mark.asyncio
async def test_return(loop_component):
    loop_component = await loop_component
    loop_component.node.inputs["loopRange"] = 'all'
    loop_item_list = []

    async def mock_loop_body(component: MockComponent):
        i = component.process.get_variable("i")
        loop_item_list.append(i)
        if i[0] >= 2:
            return ControlFlow.RETURN
        return ControlFlow.NEXT

    add_mock_component(loop_component, mock_loop_body)
    assert (await loop_component.execute()) == ControlFlow.RETURN
    assert loop_item_list == [[1, "abc"], [2, "efg"]]


@pytest.mark.asyncio
async def test_exit(loop_component):
    loop_component = await loop_component
    loop_component.node.inputs["loopRange"] = 'all'
    loop_component.node.inputs["reversedLoop"] = 'true'
    loop_item_list = []

    async def mock_loop_body(component: MockComponent):
        i = component.process.get_variable("i")
        loop_item_list.append(i)
        if i[0] == 2:
            return ControlFlow.EXIT
        return ControlFlow.NEXT

    add_mock_component(loop_component, mock_loop_body)
    assert (await loop_component.execute()) == ControlFlow.EXIT
    assert loop_item_list == [[3, "hij"], [2, "efg"]]
