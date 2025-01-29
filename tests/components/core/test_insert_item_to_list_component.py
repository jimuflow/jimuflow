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

from jimuflow.components.core import InsertItemToListComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component


@pytest.mark.asyncio
@pytest.mark.parametrize("list,value,expected", [
    ([], '1', [1]),
    ([1, 2], '3', [1, 2, 3]),

])
async def test_append_item(list, value, expected):
    component = create_component(InsertItemToListComponent)
    await component.process.update_variable('l', list)
    component.node.inputs = {
        "list": 'l',
        "value": value,
        "insertType": 'append',
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert list == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("list,insertPosition,value,expected", [
    ([], '0', '1', [1]),
    ([1, 2], '2', '3', [1, 2, 3]),
    ([1, 2], '3', '3', [1, 2, 3]),
    ([1, 2], '-1', '3', [1, 3, 2]),
    ([1, 2], '-3', '3', [3, 1, 2]),
])
async def test_insert_item(list, insertPosition, value, expected):
    component = create_component(InsertItemToListComponent)
    await component.process.update_variable('l', list)
    component.node.inputs = {
        "list": 'l',
        "insertType": 'insert',
        "insertPosition": insertPosition,
        "value": value,
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert list == expected
