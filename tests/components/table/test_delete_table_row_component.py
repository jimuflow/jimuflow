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

from jimuflow.components.table import DeleteTableRowComponent
from jimuflow.datatypes import Table
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component


@pytest.mark.asyncio
async def test_delete_one():
    table = Table(['ID', '名称'])
    component = create_component(DeleteTableRowComponent)
    table.rows.append([1, "abc"])
    table.rows.append([2, "efg"])
    await component.process.update_variable("t", table)
    component.node.inputs = {
        "table": 't',
        "deleteType": 'one',
        "rowNo": '1',
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert table.numberOfRows == 1
    assert table.rows == [[2, "efg"]]


@pytest.mark.asyncio
async def test_out_of_range():
    table = Table(['ID', '名称'])
    component = create_component(DeleteTableRowComponent)
    table.rows.append([1, "abc"])
    table.rows.append([2, "efg"])
    await component.process.update_variable("t", table)
    component.node.inputs = {
        "table": 't',
        "deleteType": 'one',
        "rowNo": '3',
    }
    with pytest.raises(Exception):
        await component.execute()
    assert table.numberOfRows == 2
    assert table.rows == [[1, "abc"], [2, "efg"]]


@pytest.mark.asyncio
async def test_delete_all():
    table = Table(['ID', '名称'])
    component = create_component(DeleteTableRowComponent)
    table.rows.append([1, "abc"])
    table.rows.append([2, "efg"])
    await component.process.update_variable("t", table)
    component.node.inputs = {
        "table": 't',
        "deleteType": 'all',
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert table.numberOfRows == 0
