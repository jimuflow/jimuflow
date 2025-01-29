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

from jimuflow.components.core import CreateDateComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component

expected = datetime.date(2012, 1, 14)


@pytest.mark.asyncio
@freeze_time(expected)
async def test_create_today_date():
    component = create_component(CreateDateComponent)
    component.node.inputs = {
        "initType": 'today',
    }
    component.node.outputs = {
        "result": "r"
    }

    assert (await component.execute()) == ControlFlow.NEXT
    assert component.process.get_variable('r') == expected


@pytest.mark.asyncio
async def test_create_date_with_timestamp():
    component = create_component(CreateDateComponent)
    ts = 1727491981.123
    component.node.inputs = {
        "initType": 'timestamp',
        "timestamp": f'{ts}'
    }
    component.node.outputs = {
        "result": "r"
    }

    assert (await component.execute()) == ControlFlow.NEXT
    assert component.process.get_variable('r') == datetime.date.fromtimestamp(ts)


@pytest.mark.asyncio
@pytest.mark.parametrize("dateString,dateFormat,expected", [
    ('"2018-02-14"', '"YYYY-MM-DD"',
     datetime.date(2018, 2, 14)),
    ('"2018-02-14"', '"YYYY.MM.DD"', ValueError),
])
async def test_create_date_with_string(dateString, dateFormat, expected):
    component = create_component(CreateDateComponent)
    component.node.inputs = {
        "initType": 'parse',
        "dateString": dateString,
        "dateFormat": dateFormat
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
