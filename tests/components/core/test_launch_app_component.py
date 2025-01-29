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

import tempfile

import psutil
import pytest

from jimuflow.components.core import LaunchAppComponent
from jimuflow.components.core.os_utils import is_macos, get_macos_app_bin_path
from jimuflow.runtime.execution_engine import ControlFlow
from jimuflow.runtime.expression import escape_string
from tests.utils import create_component, get_test_app_path


@pytest.mark.asyncio
async def test_execute():
    app_name, app_path = get_test_app_path()
    component = create_component(LaunchAppComponent)
    with tempfile.TemporaryDirectory() as temp_dir:
        component.node.inputs = {
            "appPath": escape_string(app_path),
            "args": '"--test"',
            "workDir": escape_string(str(temp_dir))
        }
        component.node.outputs = {
            "pid": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        pid = component.process.get_variable('r')
        assert isinstance(pid, int)
        process = psutil.Process(pid)
        try:
            if is_macos() and app_path.endswith('.app'):
                app_path = get_macos_app_bin_path(app_path)
            assert process.cmdline() == [app_path, '--test']
            assert process.cwd() == '/private' + str(temp_dir) if is_macos() and str(temp_dir).startswith(
                '/var/') else str(temp_dir)
            assert process.name() == app_name
        finally:
            process.kill()


@pytest.mark.asyncio
async def test_execute_with_wait_timeout():
    app_name, app_path = get_test_app_path()
    component = create_component(LaunchAppComponent)
    component.node.inputs = {
        "appPath": escape_string(app_path),
        "actionAfterLaunch": 'wait_complete',
        "waitTimeout": '1',
    }
    component.node.outputs = {
        "pid": 'r'
    }
    with pytest.raises(TimeoutError):
        await component.execute()
    pid = component.process.get_variable('r')
    assert isinstance(pid, int)
    process = psutil.Process(pid)
    assert process.name() == app_name
    process.kill()
