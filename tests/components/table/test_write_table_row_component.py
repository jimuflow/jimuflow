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

from jimuflow.components.table import WriteTableRowComponent
from jimuflow.datatypes import Table
from jimuflow.runtime.execution_engine import ControlFlow
from jimuflow.runtime.expression import escape_string
from tests.utils import create_component, random_string


@pytest.mark.asyncio
async def test_append_row():
    table = Table(['ID', '名称'])
    component = create_component(WriteTableRowComponent)
    id = 1
    name = random_string()
    row = [id, name]
    await component.process.update_variable("t", table)
    await component.process.update_variable("r", row)
    component.node.inputs = {
        "table": 't',
        "writeType": 'append',
        "rowInputType": 'row',
        "row": 'r'
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert table.numberOfRows == 1
    assert table.rows[0] == [id, name]


@pytest.mark.asyncio
async def test_insert_row():
    table = Table(['ID', '名称'])
    component = create_component(WriteTableRowComponent)
    name1 = random_string()
    row1 = [1, name1]
    table.rows.append(row1)
    name2 = random_string()
    await component.process.update_variable("t", table)
    component.node.inputs = {
        "table": 't',
        "writeType": 'insert',
        "rowNo": '1',
        "rowInputType": 'columns',
        "columns": [('1', '2'), ('"名称"', escape_string(name2))]
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert table.numberOfRows == 2
    assert table.rows == [[2, name2], [1, name1]]


@pytest.mark.asyncio
async def test_update_row():
    table = Table(['ID', '名称'])
    component = create_component(WriteTableRowComponent)
    name1 = random_string()
    row1 = [1, name1]
    table.rows.append(row1)
    name2 = random_string()
    await component.process.update_variable("t", table)
    component.node.inputs = {
        "table": 't',
        "writeType": 'update',
        "rowNo": '1',
        "rowInputType": 'columns',
        "columns": [('1', '2'), ('"名称"', escape_string(name2))]
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert table.numberOfRows == 1
    assert table.rows == [[2, name2]]


@pytest.mark.asyncio
async def test_out_of_range():
    table = Table(['ID', '名称'])
    component = create_component(WriteTableRowComponent)
    name1 = random_string()
    row1 = [1, name1]
    table.rows.append(row1)
    name2 = random_string()
    await component.process.update_variable("t", table)
    component.node.inputs = {
        "table": 't',
        "writeType": 'update',
        "rowNo": '2',
        "rowInputType": 'columns',
        "columns": [('1', '2'), ('"名称"', escape_string(name2))]
    }
    with pytest.raises(Exception):
        await component.execute()


@pytest.mark.asyncio
async def test_append_if_out_of_range():
    table = Table(['ID', '名称'])
    component = create_component(WriteTableRowComponent)
    name1 = random_string()
    row1 = [1, name1]
    table.rows.append(row1)
    name2 = random_string()
    await component.process.update_variable("t", table)
    component.node.inputs = {
        "table": 't',
        "writeType": 'update',
        "rowNo": '2',
        "rowInputType": 'columns',
        "columns": [('"ID"', '2'), ('2', escape_string(name2))],
        "appendRowIfOutOfRange": 'true',
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert table.numberOfRows == 2
    assert table.rows == [[1, name1], [2, name2]]
