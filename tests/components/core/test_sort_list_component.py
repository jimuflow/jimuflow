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

from jimuflow.components.core import SortListComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component


@pytest.mark.asyncio
@pytest.mark.parametrize("list,sortOrder,expected", [
    ([1, 2, 3], 'desc', [3, 2, 1]),
    ([3, 2, 1], 'asc', [1, 2, 3]),
    (None, 'asc', AttributeError),
])
async def test_execute(list, sortOrder, expected):
    component = create_component(SortListComponent)
    await component.process.update_variable('l', list)
    component.node.inputs = {
        "list": 'l',
        "sortOrder": sortOrder,
    }
    if isinstance(expected, type):
        with pytest.raises(expected):
            await component.execute()
    else:
        assert (await component.execute()) == ControlFlow.NEXT
        assert list == expected
