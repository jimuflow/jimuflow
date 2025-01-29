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

from jimuflow.components.core import DeleteDictKeyComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component


@pytest.mark.asyncio
@pytest.mark.parametrize("dict,key,expected", [
    ({"a": 1, "b": 2}, '"b"', {"a": 1}),
    ({"a": 1}, '"a"', {}),
    (None, '"b"', TypeError),
])
async def test_execute(dict, key, expected):
    component = create_component(DeleteDictKeyComponent)
    await component.process.update_variable('d', dict)
    component.node.inputs = {
        "dict": 'd',
        "key": key,
    }
    if isinstance(expected, type):
        with pytest.raises(expected):
            await component.execute()
    else:
        assert (await component.execute()) == ControlFlow.NEXT
        assert dict == expected
