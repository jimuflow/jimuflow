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

from jimuflow.components.core import KillProcessComponent
from jimuflow.components.core.os_utils import launch_app, is_process_alive, sleep_at_least
from jimuflow.runtime.execution_engine import ControlFlow
from jimuflow.runtime.expression import escape_string
from tests.utils import create_component, random_string, get_test_app_path


@pytest.mark.asyncio
async def test_kill_pid_exists():
    _, app_path = get_test_app_path()
    process = await launch_app(app_path)
    try:
        component = create_component(KillProcessComponent)
        component.node.inputs = {
            "processProp": 'pid',
            "pid": f'{process.pid}',
        }
        assert is_process_alive(process.pid)
        assert (await component.execute()) == ControlFlow.NEXT
        await sleep_at_least(2)
        assert not is_process_alive(process.pid)
    finally:
        if is_process_alive(process.pid):
            process.kill()


@pytest.mark.asyncio
async def test_kill_name_exists():
    app_name, app_path = get_test_app_path()
    process = await launch_app(app_path)
    try:
        component = create_component(KillProcessComponent)
        component.node.inputs = {
            "processProp": 'name',
            "name": escape_string(app_name),
        }
        assert is_process_alive(process.pid)
        assert (await component.execute()) == ControlFlow.NEXT
        await sleep_at_least(2)
        assert not is_process_alive(process.pid)
    finally:
        if is_process_alive(process.pid):
            process.kill()


@pytest.mark.asyncio
async def test_kill_pid_not_exists():
    _, app_path = get_test_app_path()
    process = await launch_app(app_path)
    try:
        pid = process.pid
        component = create_component(KillProcessComponent)
        component.node.inputs = {
            "processProp": 'pid',
            "pid": f'{pid}',
        }
        process.kill()
        assert (await component.execute()) == ControlFlow.NEXT
    finally:
        if is_process_alive(process.pid):
            process.kill()


@pytest.mark.asyncio
async def test_kill_name_not_exists():
    component = create_component(KillProcessComponent)
    component.node.inputs = {
        "processProp": 'name',
        "name": f'"{random_string(prefix="NotExistedApp")}"',
    }
    assert (await component.execute()) == ControlFlow.NEXT
