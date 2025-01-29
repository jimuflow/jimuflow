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

from jimuflow.components.core import TrimTextComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component


@pytest.mark.asyncio
async def test_trim_both():
    component = create_component(TrimTextComponent)
    component.node.inputs = {
        "originalText": '" abc "',
        "trimType": 'both',
    }
    component.node.outputs = {
        "result": "r"
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert component.process.get_variable("r") == 'abc'


@pytest.mark.asyncio
async def test_trim_left():
    component = create_component(TrimTextComponent)
    component.node.inputs = {
        "originalText": '" abc "',
        "trimType": 'left',
    }
    component.node.outputs = {
        "result": "r"
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert component.process.get_variable("r") == 'abc '


@pytest.mark.asyncio
async def test_trim_right():
    component = create_component(TrimTextComponent)
    component.node.inputs = {
        "originalText": '" abc "',
        "trimType": 'right',
    }
    component.node.outputs = {
        "result": "r"
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert component.process.get_variable("r") == ' abc'
