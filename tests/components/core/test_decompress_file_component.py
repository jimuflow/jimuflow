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
import zipfile

import pytest

from jimuflow.components.core import DecompressFileComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component


def create_sample_zip_file(content, zip_path):
    try:
        with tempfile.NamedTemporaryFile(delete=False, mode='w') as f:
            f.write(content)
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.write(f.name, 'file.txt')
    finally:
        if os.path.exists(f.name):
            os.remove(f.name)


def create_encrypted_zip_file(zip_path):
    with open(zip_path, 'wb') as f:
        with open(os.path.join(os.path.dirname(__file__), 'encrypted.zip'), 'rb') as f2:
            f.write(f2.read())


@pytest.mark.asyncio
async def test_decompress_file_to_same_folder():
    component = create_component(DecompressFileComponent)
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, 'sample.zip')
        create_sample_zip_file('123', zip_path)
        await component.process.update_variable('f1', zip_path)
        component.node.inputs = {
            "filePath": 'f1',
            "decompressTo": 'source',
            "createFolder": True
        }
        component.node.outputs = {
            "result": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        expected = os.path.join(temp_dir, 'sample')
        assert component.process.get_variable('r') == expected
        assert os.path.exists(zip_path)
        assert os.path.exists(expected)
        extracted_file = os.path.join(expected, 'file.txt')
        assert os.path.exists(extracted_file)
        assert open(extracted_file, 'r').read() == '123'


@pytest.mark.asyncio
async def test_decompress_encrypted_file_to_specified_folder():
    component = create_component(DecompressFileComponent)
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, 'sample.zip')
        create_encrypted_zip_file(zip_path)
        await component.process.update_variable('f1', zip_path)
        save_folder = os.path.join(temp_dir, 'save')
        await component.process.update_variable('save_folder', save_folder)
        component.node.inputs = {
            "filePath": 'f1',
            "decompressTo": 'specified',
            "saveFolder": 'save_folder',
            "password": '"123456"',
            "createFolder": False
        }
        component.node.outputs = {
            "result": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        assert component.process.get_variable('r') == save_folder
        assert os.path.exists(zip_path)
        assert os.path.exists(save_folder)
        extracted_file = os.path.join(save_folder, 'file.txt')
        assert os.path.exists(extracted_file)
        assert open(extracted_file, 'r').read() == '123'


@pytest.mark.asyncio
async def test_decompress_encrypted_file_to_specified_folder_without_password():
    component = create_component(DecompressFileComponent)
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, 'sample.zip')
        create_encrypted_zip_file(zip_path)
        await component.process.update_variable('f1', zip_path)
        save_folder = os.path.join(temp_dir, 'save')
        await component.process.update_variable('save_folder', save_folder)
        component.node.inputs = {
            "filePath": 'f1',
            "decompressTo": 'specified',
            "saveFolder": 'save_folder',
            "createFolder": False
        }
        component.node.outputs = {
            "result": 'r'
        }
        with pytest.raises(Exception):
            await component.execute()
        assert os.path.exists(zip_path)
