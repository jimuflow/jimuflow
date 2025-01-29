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

from jimuflow.components.core import NumberToTextComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component


@pytest.mark.asyncio
@pytest.mark.parametrize("value,scale,useThousandsSeparator,expected", [
    ('123456.789', '1', False, '123456.8'),
    ('123456.749', '1', False, '123456.7'),
    ('123456.789', '0', False, '123457'),
    ('123456.789', '1', True, '123,456.8'),
])
async def test_execute(value, scale, useThousandsSeparator, expected):
    component = create_component(NumberToTextComponent)
    component.node.inputs = {
        "value": value,
        "scale": scale,
        "useThousandsSeparator": useThousandsSeparator,
    }
    component.node.outputs = {
        "result": "r"
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert component.process.get_variable("r") == expected
