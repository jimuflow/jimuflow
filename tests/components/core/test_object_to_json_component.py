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

from jimuflow.components.core import ObjectToJsonComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component


@pytest.mark.asyncio
@pytest.mark.parametrize("obj,expected", [
    ({}, '{}'),
    ({"a": 1, "b": {"c": 2}}, '{"a": 1, "b": {"c": 2}}'),
    ([1, {"a": 1}, "abc", True, None], '[1, {"a": 1}, "abc", true, null]'),
    (None, 'null'),
    (123, '123'),
    ("abc", '"abc"'),
    (True, 'true'),
    (123.456, '123.456'),
])
async def test_execute(obj, expected):
    component = create_component(ObjectToJsonComponent)
    await component.process.update_variable('obj', obj)
    component.node.inputs = {
        "obj": 'obj',
    }
    component.node.outputs = {
        "result": "r"
    }
    if isinstance(expected, type):
        with pytest.raises(expected):
            await component.execute()
    else:
        assert (await component.execute()) == ControlFlow.NEXT
        assert component.process.get_variable('r') == expected
