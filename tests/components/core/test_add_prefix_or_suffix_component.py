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

from jimuflow.components.core import AddPrefixOrSuffixComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component


@pytest.mark.asyncio
async def test_add_suffix():
    component = create_component(AddPrefixOrSuffixComponent)
    component.node.inputs = {
        "originalText": '"abc"',
        "addType": 'suffix',
        "addText": '"123"'
    }
    component.node.outputs = {
        "result": "r"
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert component.process.get_variable("r") == 'abc123'


@pytest.mark.asyncio
async def test_add_suffix_to_none_string():
    component = create_component(AddPrefixOrSuffixComponent)
    component.node.inputs = {
        "originalText": 'a',
        "addType": 'suffix',
        "addText": '"123"'
    }
    component.node.outputs = {
        "result": "r"
    }
    with pytest.raises(TypeError):
        await component.execute()


@pytest.mark.asyncio
async def test_add_prefix():
    component = create_component(AddPrefixOrSuffixComponent)
    component.node.inputs = {
        "originalText": '"abc"',
        "addType": 'prefix',
        "addText": '"123"'
    }
    component.node.outputs = {
        "result": "r"
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert component.process.get_variable("r") == '123abc'
