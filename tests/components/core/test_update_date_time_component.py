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

from jimuflow.components.core import UpdateDateTimeComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component

date1 = datetime.datetime(2024, 9, 28, 19, 30, 45, 123456)


@pytest.mark.asyncio
@pytest.mark.parametrize("originalDateTime,adjustmentType,adjustmentValue,adjustmentUnit,expected", [
    (date1, 'increment', '1', 'microseconds',
     datetime.datetime(2024, 9, 28, 19, 30, 45, 123457)),
    (date1, 'decrement', '1', 'microseconds',
     datetime.datetime(2024, 9, 28, 19, 30, 45, 123455)),
    (date1, 'increment', '1', 'milliseconds',
     datetime.datetime(2024, 9, 28, 19, 30, 45, 124456)),
    (date1, 'decrement', '1', 'milliseconds',
     datetime.datetime(2024, 9, 28, 19, 30, 45, 122456)),
    (date1, 'increment', '1', 'seconds',
     datetime.datetime(2024, 9, 28, 19, 30, 46, 123456)),
    (date1, 'decrement', '1', 'seconds',
     datetime.datetime(2024, 9, 28, 19, 30, 44, 123456)),
    (date1, 'increment', '1', 'minutes',
     datetime.datetime(2024, 9, 28, 19, 31, 45, 123456)),
    (date1, 'decrement', '1', 'minutes',
     datetime.datetime(2024, 9, 28, 19, 29, 45, 123456)),
    (date1, 'increment', '1', 'hours',
     datetime.datetime(2024, 9, 28, 20, 30, 45, 123456)),
    (date1, 'decrement', '1', 'hours',
     datetime.datetime(2024, 9, 28, 18, 30, 45, 123456)),
    (date1, 'increment', '1', 'days',
     datetime.datetime(2024, 9, 29, 19, 30, 45, 123456)),
    (date1, 'decrement', '1', 'days',
     datetime.datetime(2024, 9, 27, 19, 30, 45, 123456)),
    (date1, 'increment', '1', 'weeks',
     datetime.datetime(2024, 10, 5, 19, 30, 45, 123456)),
    (date1, 'decrement', '1', 'weeks',
     datetime.datetime(2024, 9, 21, 19, 30, 45, 123456)),
    (date1, 'increment', '1', 'months',
     datetime.datetime(2024, 10, 28, 19, 30, 45, 123456)),
    (date1, 'decrement', '1', 'months',
     datetime.datetime(2024, 8, 28, 19, 30, 45, 123456)),
    (date1, 'increment', '1', 'years',
     datetime.datetime(2025, 9, 28, 19, 30, 45, 123456)),
    (date1, 'decrement', '1', 'years',
     datetime.datetime(2023, 9, 28, 19, 30, 45, 123456)),
])
async def test_execute(originalDateTime, adjustmentType, adjustmentValue, adjustmentUnit, expected):
    component = create_component(UpdateDateTimeComponent)
    await component.process.update_variable('d', originalDateTime)
    component.node.inputs = {
        "originalDateTime": 'd',
        "adjustmentType": adjustmentType,
        "adjustmentValue": adjustmentValue,
        "adjustmentUnit": adjustmentUnit
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
