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

import ctypes
import os
import stat
import tempfile
import time

import pytest

from jimuflow.components.core import ListFilesComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component


@pytest.fixture(scope='module')
def temp_folder():
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建文件和文件夹
        os.makedirs(os.path.join(temp_dir, 'folder1'), exist_ok=True)
        time.sleep(0.01)

        # 创建文件
        with open(os.path.join(temp_dir, 'file1.txt'), 'w', encoding='utf-8') as f:
            f.write('12')
        time.sleep(0.01)

        with open(os.path.join(temp_dir, '文件1.txt'), 'w', encoding='utf-8') as f:
            f.write('1')
        time.sleep(0.01)

        hidden_file = os.path.join(temp_dir, '.hidden1.txt')
        with open(hidden_file, 'w', encoding='utf-8') as f:
            f.write('123')
        if os.name == 'nt':
            ctypes.windll.kernel32.SetFileAttributesW(hidden_file, stat.FILE_ATTRIBUTE_HIDDEN)
        time.sleep(0.01)

        with open(os.path.join(temp_dir, 'folder1', '文件1.txt'), 'w', encoding='utf-8') as f:
            f.write('12345')
        time.sleep(0.01)

        with open(os.path.join(temp_dir, 'folder1', 'file1.txt'), 'w', encoding='utf-8') as f:
            f.write('1234')
        time.sleep(0.01)

        yield temp_dir


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "filenamePattern,findSubFolders,ignoreHiddenFiles,sortingFiles,sortingFactor,sortOrder,expected", [
        ('"file?.txt"', False, True, False, None, None, ['file1.txt']),
        ('"file[0-9].txt"', False, True, False, None, None, ['file1.txt']),
        ('"file[!a-z].txt"', False, True, False, None, None, ['file1.txt']),
        ('".hidden*.txt"', False, True, False, None, None, []),
        ('".hidden*.txt"', False, False, False, None, None, ['.hidden1.txt']),
        ('"文件*.txt"', False, True, False, None, None, ['文件1.txt']),
        ('"file*.txt"', True, True, False, None, None, ['file1.txt', 'folder1/file1.txt']),
        ('"**/file*.txt"', False, True, False, None, None, ['file1.txt', 'folder1/file1.txt']),
        ('"文件*.txt"', True, True, False, None, None, ['文件1.txt', 'folder1/文件1.txt']),
        ('"**/*.txt"', False, True, False, None, None,
         ['file1.txt', '文件1.txt', 'folder1/file1.txt', 'folder1/文件1.txt']),
        ('"**/*.txt"', False, True, True, 'name', 'asc',
         ['file1.txt', 'folder1/file1.txt', '文件1.txt', 'folder1/文件1.txt']),
        ('"**/*.txt"', False, True, True, 'name', 'desc',
         ['文件1.txt', 'folder1/文件1.txt', 'file1.txt', 'folder1/file1.txt']),
        ('"**/*.txt"', False, True, True, 'size', 'asc',
         ['文件1.txt', 'file1.txt', 'folder1/file1.txt', 'folder1/文件1.txt']),
        ('"**/*.txt"', False, True, True, 'size', 'desc',
         ['folder1/文件1.txt', 'folder1/file1.txt', 'file1.txt', '文件1.txt']),
        ('"**/*.txt"', False, True, True, 'creationTime', 'asc',
         ['file1.txt', '文件1.txt', 'folder1/文件1.txt', 'folder1/file1.txt']),
        ('"**/*.txt"', False, True, True, 'creationTime', 'desc',
         ['folder1/file1.txt', 'folder1/文件1.txt', '文件1.txt', 'file1.txt']),
        ('"**/*.txt"', False, True, True, 'lastModified', 'asc',
         ['file1.txt', '文件1.txt', 'folder1/文件1.txt', 'folder1/file1.txt']),
        ('"**/*.txt"', False, True, True, 'lastModified', 'desc',
         ['folder1/file1.txt', 'folder1/文件1.txt', '文件1.txt', 'file1.txt']),
    ])
async def test_execute(temp_folder, filenamePattern, findSubFolders, ignoreHiddenFiles, sortingFiles, sortingFactor,
                       sortOrder, expected):
    component = create_component(ListFilesComponent)
    await component.process.update_variable('folder', temp_folder)
    component.node.inputs = {
        "folder": 'folder',
        "filenamePattern": filenamePattern,
        "findSubFolders": findSubFolders,
        "ignoreHiddenFiles": ignoreHiddenFiles,
        "sortingFiles": sortingFiles,
        "sortingFactor": sortingFactor,
        "sortOrder": sortOrder
    }
    component.node.outputs = {
        "result": "r"
    }
    if isinstance(expected, type):
        with pytest.raises(expected):
            await component.execute()
    else:
        assert (await component.execute()) == ControlFlow.NEXT
        result = component.process.get_variable('r')
        if sortingFiles:
            assert result == [os.path.join(temp_folder, os.path.normcase(x)) for x in expected]
        else:
            result.sort()
            sorted_expected = [os.path.join(temp_folder, os.path.normcase(x)) for x in expected]
            sorted_expected.sort()
            assert result == sorted_expected
