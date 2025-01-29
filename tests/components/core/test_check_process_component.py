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

from jimuflow.components.core import CheckProcessComponent
from jimuflow.components.core.os_utils import launch_app, sleep_at_least
from jimuflow.runtime.execution_engine import ControlFlow
from jimuflow.runtime.expression import escape_string
from tests.utils import create_component, random_string, get_test_app_path


@pytest.mark.asyncio
async def test_check_pid_exists():
    _, app_path = get_test_app_path()
    process = await launch_app(app_path)
    try:
        component = create_component(CheckProcessComponent)
        component.node.inputs = {
            "processProp": 'pid',
            "pid": f'{process.pid}',
        }
        component.node.outputs = {
            "result": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        assert component.process.get_variable('r')
    finally:
        process.kill()


@pytest.mark.asyncio
async def test_check_name_exists():
    app_name, app_path = get_test_app_path()
    process = await launch_app(app_path)
    try:
        component = create_component(CheckProcessComponent)
        component.node.inputs = {
            "processProp": 'name',
            "name": escape_string(app_name),
        }
        component.node.outputs = {
            "result": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        assert component.process.get_variable('r')
    finally:
        process.kill()


@pytest.mark.asyncio
async def test_check_pid_not_exists():
    _, app_path = get_test_app_path()
    process = await launch_app(app_path)
    pid = process.pid
    process.kill()
    await sleep_at_least(0.5)
    component = create_component(CheckProcessComponent)
    component.node.inputs = {
        "processProp": 'pid',
        "pid": f'{pid}',
    }
    component.node.outputs = {
        "result": 'r'
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert not component.process.get_variable('r')


@pytest.mark.asyncio
async def test_check_name_not_exists():
    component = create_component(CheckProcessComponent)
    component.node.inputs = {
        "processProp": 'name',
        "name": f'"{random_string(prefix="NotExistedApp")}"',
    }
    component.node.outputs = {
        "result": 'r'
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert not component.process.get_variable('r')
