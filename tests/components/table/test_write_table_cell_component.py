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

from jimuflow.components.table import WriteTableCellComponent
from jimuflow.datatypes import Table
from jimuflow.runtime.execution_engine import ControlFlow
from jimuflow.runtime.expression import escape_string
from tests.utils import create_component, random_string


@pytest.mark.asyncio
async def test_execute():
    table = Table(['ID', '名称'])
    table.rows.append([1, random_string("o")])
    component = create_component(WriteTableCellComponent)
    await component.process.update_variable("t", table)
    new_value = random_string("n")
    component.node.inputs = {
        "table": 't',
        "rowNo": '1',
        "columnNo": '2',
        "value": escape_string(new_value)
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert table.numberOfRows == 1
    assert table.rows[0] == [1, new_value]


@pytest.mark.asyncio
async def test_write_not_existed_row():
    table = Table(['ID', '名称'])
    table.rows.append([1, random_string("o")])
    component = create_component(WriteTableCellComponent)
    await component.process.update_variable("t", table)
    new_value = random_string("n")
    component.node.inputs = {
        "table": 't',
        "rowNo": '2',
        "columnNo": '2',
        "value": escape_string(new_value)
    }
    with pytest.raises(Exception):
        await component.execute()


@pytest.mark.asyncio
async def test_write_not_existed_column():
    table = Table(['ID', '名称'])
    table.rows.append([1, random_string("o")])
    component = create_component(WriteTableCellComponent)
    await component.process.update_variable("t", table)
    new_value = random_string("n")
    component.node.inputs = {
        "table": 't',
        "rowNo": '1',
        "columnNo": '3',
        "value": escape_string(new_value)
    }
    with pytest.raises(Exception):
        await component.execute()


@pytest.mark.asyncio
async def test_append_row():
    table = Table(['ID', '名称'])
    old_value = random_string("o")
    table.rows.append([1, old_value])
    component = create_component(WriteTableCellComponent)
    await component.process.update_variable("t", table)
    new_value = random_string("n")
    component.node.inputs = {
        "table": 't',
        "rowNo": '2',
        "columnNo": '2',
        "value": escape_string(new_value),
        "appendRowIfOutOfRange": 'true'
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert table.numberOfRows == 2
    assert table.rows == [[1, old_value], ['', new_value]]
