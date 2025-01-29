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

from jimuflow.components.core import MergeListComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component


@pytest.mark.asyncio
@pytest.mark.parametrize("firstList,secondList,expected", [
    ([1], [2], [1, 2]),
    ([1], [1], [1, 1]),
    ([1], None, TypeError),
    (None, [1], TypeError),
    (None, None, TypeError),
])
async def test_execute(firstList, secondList, expected):
    component = create_component(MergeListComponent)
    await component.process.update_variable('l1', firstList)
    await component.process.update_variable('l2', secondList)
    component.node.inputs = {
        "firstList": 'l1',
        "secondList": 'l2',
    }
    component.node.outputs = {
        "list": 'r'
    }
    if isinstance(expected, type):
        with pytest.raises(expected):
            await component.execute()
    else:
        assert (await component.execute()) == ControlFlow.NEXT
        assert component.process.get_variable('r') == expected
