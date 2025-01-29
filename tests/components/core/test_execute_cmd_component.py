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

import os.path
import tempfile

import pytest

from jimuflow.components.core import ExecuteCmdComponent
from jimuflow.components.core.os_utils import is_windows
from jimuflow.runtime.execution_engine import ControlFlow
from jimuflow.runtime.expression import escape_string
from tests.utils import create_component, random_string


@pytest.mark.asyncio
async def test_execute():
    component = create_component(ExecuteCmdComponent)
    message = random_string()
    component.node.inputs = {
        "cmd": f'"echo {message}"',
    }
    component.node.outputs = {
        "result": 'r'
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert component.process.get_variable('r') == message + os.linesep


@pytest.mark.asyncio
async def test_execute_with_word_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        component = create_component(ExecuteCmdComponent)
        message = random_string()
        with open(os.path.join(temp_dir, 'test.txt'), 'w') as f:
            f.write(message)
        component.node.inputs = {
            "cmd": f'"cat test.txt"' if not is_windows() else f'"type test.txt"',
            "workDir": escape_string(temp_dir)
        }
        component.node.outputs = {
            "result": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        assert component.process.get_variable('r') == message


@pytest.mark.asyncio
async def test_execute_with_timeout():
    component = create_component(ExecuteCmdComponent)
    component.node.inputs = {
        "cmd": f'"sleep 2"' if not is_windows() else f'"ping -n 3 127.0.0.1"',
        "waitTimeout": '1',
    }
    component.node.outputs = {
        "result": 'r'
    }
    with pytest.raises(TimeoutError):
        await component.execute()
