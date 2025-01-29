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

from jimuflow.components.table import ReadTableDataComponent
from jimuflow.datatypes import Table
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component


@pytest.mark.asyncio
async def test_read_row():
    table = Table(['ID', '名称'])
    component = create_component(ReadTableDataComponent)
    table.rows.append([1, "abc"])
    table.rows.append([2, "efg"])
    table.rows.append([3, "ijk"])
    await component.process.update_variable("t", table)
    component.node.inputs = {
        "table": 't',
        "readType": 'row',
        "rowNo": '2',
    }
    component.node.outputs = {
        "result": 'r'
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert component.process.get_variable('r') == [2, "efg"]


@pytest.mark.asyncio
async def test_read_cell():
    table = Table(['ID', '名称'])
    component = create_component(ReadTableDataComponent)
    table.rows.append([1, "abc"])
    table.rows.append([2, "efg"])
    table.rows.append([3, "ijk"])
    await component.process.update_variable("t", table)
    component.node.inputs = {
        "table": 't',
        "readType": 'cell',
        "rowNo": '2',
        "columnNo": '2'
    }
    component.node.outputs = {
        "result": 'r'
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert component.process.get_variable('r') == "efg"


@pytest.mark.asyncio
async def test_read_out_of_range():
    table = Table(['ID', '名称'])
    component = create_component(ReadTableDataComponent)
    table.rows.append([1, "abc"])
    table.rows.append([2, "efg"])
    table.rows.append([3, "ijk"])
    await component.process.update_variable("t", table)
    component.node.inputs = {
        "table": 't',
        "readType": 'cell',
        "rowNo": '4',
        "columnNo": '2'
    }
    component.node.outputs = {
        "result": 'r'
    }
    with pytest.raises(Exception):
        await component.execute()
