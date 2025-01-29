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

import datetime

import pytest
from freezegun import freeze_time

from jimuflow.components.core import CreateTimeComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component

expected = datetime.datetime(2012, 1, 14, 12, 30, 45)


@pytest.mark.asyncio
@freeze_time(expected)
async def test_create_now_time():
    component = create_component(CreateTimeComponent)
    component.node.inputs = {
        "initType": 'now',
    }
    component.node.outputs = {
        "result": "r"
    }

    assert (await component.execute()) == ControlFlow.NEXT
    assert component.process.get_variable('r') == expected.time()


@pytest.mark.asyncio
@pytest.mark.parametrize("timeString,timeFormat,expected", [
    ('"12:20:01"', '"HH:mm:ss"',
     datetime.time(12, 20, 1)),
    ('"06:20:01 PM"', '"hh:mm:ss A"',
     datetime.time(18, 20, 1)),
    ('"12:20:01.123456"', '"HH:mm:ss.SSSSSS"',
     datetime.time(12, 20, 1, 123456)),
    ('"12:20:01"', '"HH-mm-ss"', ValueError),
])
async def test_create_time_with_string(timeString, timeFormat, expected):
    component = create_component(CreateTimeComponent)
    component.node.inputs = {
        "initType": 'parse',
        "timeString": timeString,
        "timeFormat": timeFormat
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
