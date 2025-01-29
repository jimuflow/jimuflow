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
from dateutil.tz import tzutc, tzlocal
from freezegun import freeze_time

from jimuflow.components.core import CreateDateTimeComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component

expected = datetime.datetime(2012, 1, 14)


@pytest.mark.asyncio
@freeze_time(expected)
async def test_create_now_datetime():
    component = create_component(CreateDateTimeComponent)
    component.node.inputs = {
        "initType": 'now',
    }
    component.node.outputs = {
        "result": "r"
    }

    assert (await component.execute()) == ControlFlow.NEXT
    assert component.process.get_variable('r') == expected


@pytest.mark.asyncio
async def test_create_datetime_with_timestamp():
    component = create_component(CreateDateTimeComponent)
    ts = 1727491981.123
    component.node.inputs = {
        "initType": 'timestamp',
        "timestamp": f'{ts}'
    }
    component.node.outputs = {
        "result": "r"
    }

    assert (await component.execute()) == ControlFlow.NEXT
    assert component.process.get_variable('r').timestamp() == ts


@pytest.mark.asyncio
@pytest.mark.parametrize("datetimeString,datetimeFormat,expected", [
    ('"2018-02-14 12:30:31"', '"YYYY-MM-DD HH:mm:ss"',
     datetime.datetime(2018, 2, 14, 12, 30, 31, tzinfo=tzlocal())),
    ('"2018-02-14 12:30:31 UTC"', '"YYYY-MM-DD HH:mm:ss ZZZ"',
     datetime.datetime(2018, 2, 14, 12, 30, 31, tzinfo=tzutc())),
    ('"2018-02-14 12:30:31.123456"', '"YYYY-MM-DD HH:mm:ss.SSSSSS"',
     datetime.datetime(2018, 2, 14, 12, 30, 31, 123456, tzinfo=tzlocal())),
    ('"2018-02-14 12:30:31.123456+0700"', '"YYYY-MM-DD HH:mm:ss.SSSSSSZ"',
     datetime.datetime(2018, 2, 14, 12, 30, 31, 123456, tzinfo=datetime.timezone(datetime.timedelta(hours=7)))),
    ('"2018-02-14T12:30:31.123456+07:00"', '"YYYY-MM-DDTHH:mm:ss.SSSSSSZZ"',
     datetime.datetime(2018, 2, 14, 12, 30, 31, 123456, tzinfo=datetime.timezone(datetime.timedelta(hours=7)))),
    ('"2018-02-14T12:30:31.123456 GMT+08:00"', '"YYYY-MM-DDTHH:mm:ss.SSSSSS [GMT]ZZ"',
     datetime.datetime(2018, 2, 14, 12, 30, 31, 123456, tzinfo=datetime.timezone(datetime.timedelta(hours=8)))),
    ('"2018-02-14 12:30:31"', '"YYYY-MM-DD HH-mm-ss"', ValueError),
])
async def test_create_datetime_with_string(datetimeString, datetimeFormat, expected):
    component = create_component(CreateDateTimeComponent)
    component.node.inputs = {
        "initType": 'parse',
        "datetimeString": datetimeString,
        "datetimeFormat": datetimeFormat
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
