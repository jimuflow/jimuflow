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
from dateutil.tz import tzoffset, gettz

from jimuflow.components.core import FormatDateTimeComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component


@pytest.mark.asyncio
@pytest.mark.parametrize("dt,datetimeFormat,expected", [
    (datetime.datetime(2028, 9, 28, 19, 30, 45, 123456),
     '"YYYY-MM-DDTHH:mm:ss.SSSSSS"', '2028-09-28T19:30:45.123456'),
    (datetime.datetime(2028, 9, 28, 19, 30, 45, 123456, tzinfo=tzoffset("", 28800)),
     '"YYYY-MM-DDTHH:mm:ss.SSSSSSZZ"', '2028-09-28T19:30:45.123456+08:00'),
    (datetime.datetime(2028, 9, 28, 19, 30, 45, 123456, tzinfo=gettz("Asia/Shanghai")),
     '"YYYY-MM-DDTHH:mm:ss.SSSSSSZZ"', '2028-09-28T19:30:45.123456+08:00'),
    (datetime.datetime(2028, 9, 28, 19, 30, 45, 123456, tzinfo=gettz("Asia/Shanghai")),
     '"YYYY-MM-DDTHH:mm:ss.SSSSSS ZZZ"', '2028-09-28T19:30:45.123456 CST'),
])
async def test_execute(dt, datetimeFormat, expected):
    component = create_component(FormatDateTimeComponent)
    await component.process.update_variable('dt', dt)
    component.node.inputs = {
        "datetime": 'dt',
        "datetimeFormat": datetimeFormat,
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
