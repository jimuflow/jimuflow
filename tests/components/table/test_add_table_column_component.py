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

from jimuflow.components.table import AddTableColumnComponent
from jimuflow.datatypes import Table
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component


@pytest.mark.asyncio
async def test_execute():
    table = Table(['ID', '名称'])
    component = create_component(AddTableColumnComponent)
    table.rows.append([1, "abc"])
    await component.process.update_variable("t", table)
    component.node.inputs = {
        "table": 't',
        "columnName": '"说明"',
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert table.numberOfRows == 1
    assert table.columnNames == ['ID', '名称', '说明']
    assert table.rows == [[1, "abc", ""]]
