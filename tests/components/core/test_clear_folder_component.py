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

from jimuflow.components.core import ClearFolderComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component


@pytest.mark.asyncio
async def test_execute():
    component = create_component(ClearFolderComponent)
    with tempfile.TemporaryDirectory() as temp_dir:
        folder = os.path.join(temp_dir, 'folder')
        os.mkdir(folder)
        with open(os.path.join(folder, 'file.txt'), 'w') as f:
            f.write('123')
        sub_folder = os.path.join(folder, 'subfolder')
        os.mkdir(sub_folder)
        with open(os.path.join(sub_folder, 'file2.txt'), 'w') as f:
            f.write('456')
        await component.process.update_variable('f', folder)
        component.node.inputs = {
            "folderPath": 'f',
        }
        assert (await component.execute()) == ControlFlow.NEXT
        assert os.path.exists(folder)
        assert not os.listdir(folder)
