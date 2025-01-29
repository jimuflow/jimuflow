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

from jimuflow.components.core import DiffDateTimeComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component

date1 = datetime.datetime(2024, 9, 28, 19, 30, 45, 0)
date2 = datetime.datetime(2024, 9, 29, 20, 31, 46, 654321)


@pytest.mark.asyncio
@pytest.mark.parametrize("startingDate,endDate,timeUnit,expected", [
    (date1, date2, 'seconds', 90061),
    (date1, date2, 'minutes', 1501),
    (date1, date2, 'hours', 25),
    (date1, date2, 'days', 1),
    (date2, date1, 'seconds', -90061),
    (date2, date1, 'minutes', -1501),
    (date2, date1, 'hours', -25),
    (date2, date1, 'days', -1),
])
async def test_execute(startingDate, endDate, timeUnit, expected):
    component = create_component(DiffDateTimeComponent)
    await component.process.update_variable('d1', startingDate)
    await component.process.update_variable('d2', endDate)
    component.node.inputs = {
        "startingDate": 'd1',
        "endDate": 'd2',
        "timeUnit": timeUnit,
    }
    component.node.outputs = {
        "timeDifference": "r"
    }
    if isinstance(expected, type):
        with pytest.raises(expected):
            await component.execute()
    else:
        assert (await component.execute()) == ControlFlow.NEXT
        assert component.process.get_variable('r') == expected
