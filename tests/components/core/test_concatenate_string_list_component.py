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

from jimuflow.components.core import ConcatenateStringListComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component


@pytest.mark.asyncio
@pytest.mark.parametrize("stringList,delimiter,ignoreEmptyItem,expected", [
    (['Hello', 'World', 'Test'], '', False, 'HelloWorldTest'),
    (['Hello', 'World', 'Test'], None, False, 'HelloWorldTest'),
    (['Hello', 'World', 'Test'], ' ', False, 'Hello World Test'),
    (['Hello', 'World', 'Test'], ', ', False, 'Hello, World, Test'),
    (['Hello','', 'World', None, 'Test'], ', ', False, 'Hello, , World, None, Test'),
    (['Hello','', 'World', None, 'Test'], ', ', True, 'Hello, World, Test'),
    ([], ', ', False, ''),
    ([1, 2, 3], '-', False, '1-2-3'),
    (None, ',', False, ''),
])
async def test_execute(stringList, delimiter, ignoreEmptyItem, expected):
    component = create_component(ConcatenateStringListComponent)
    await component.process.update_variable('list', stringList)
    if delimiter is not None:
        await component.process.update_variable('delim', delimiter)
    component.node.inputs = {
        "stringList": 'list',
        "delimiter": 'delim',
        "ignoreEmptyItem": ignoreEmptyItem
    }
    component.node.outputs = {
        "result": 'r'
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert component.process.get_variable('r') == expected
