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

import os
import tempfile

import pytest

from jimuflow.components.core import CreateFolderComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component


@pytest.mark.asyncio
async def test_execute():
    component = create_component(CreateFolderComponent)
    with tempfile.TemporaryDirectory() as temp_dir:
        await component.process.update_variable('d', str(temp_dir))
        component.node.inputs = {
            "parentFolder": 'd',
            "newFolderName": '"new_folder"',
        }
        component.node.outputs = {
            "newFolderPath": 'r'
        }
        expected = os.path.join(temp_dir, 'new_folder')
        assert not os.path.exists(expected)
        assert (await component.execute()) == ControlFlow.NEXT
        assert component.process.get_variable('r') == expected
        assert os.path.exists(expected)
