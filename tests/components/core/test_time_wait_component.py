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

import time

import pytest

from jimuflow.components.core import TimeWaitComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component


@pytest.mark.asyncio
async def test_execute():
    component = create_component(TimeWaitComponent)
    component.node.inputs = {
        "seconds": "0.123"
    }
    start_time = time.perf_counter()
    assert (await component.execute()) == ControlFlow.NEXT
    assert (time.perf_counter() - start_time) >= 0.123
