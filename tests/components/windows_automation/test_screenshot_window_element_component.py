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

import sys

if sys.platform == "win32":
    import os.path
    import tempfile

    import pytest
    import pywinauto
    from PIL import Image

    from jimuflow.components.windows_automation import ScreenshotWindowElementComponent
    from jimuflow.gui.window_utils import logical_pixels_to_physical_pixels
    from jimuflow.runtime.execution_engine import ControlFlow
    from jimuflow.runtime.expression import escape_string
    from tests.utils import create_component_context, add_test_window_element

    test_app_script = 'get_window_test_app.py'


    @pytest.mark.asyncio
    @pytest.mark.parametrize('fileFormat, fileNamingType', [
        ('png', 'random'),
        ('jpeg', 'custom'),
        ('png', 'random'),
    ])
    async def test_execute(start_python_process, fileFormat, fileNamingType):
        start_python_process(test_app_script, wait_time=0)
        window = pywinauto.Desktop(backend='uia').window(
            auto_id="QApplication.GetWindowTestApp")
        window.wait('exists')
        with tempfile.TemporaryDirectory() as temp_dir:
            async with create_component_context(ScreenshotWindowElementComponent) as component:
                component.node.inputs = {
                    "elementUri": add_test_window_element(
                        component,
                        "/Text[@automation_id='QApplication.GetWindowTestApp.QLabel']",
                        "/Window[@automation_id='QApplication.GetWindowTestApp']"),
                    "saveFolder": escape_string(str(temp_dir)),
                    "fileFormat": fileFormat,
                    "fileNamingType": fileNamingType,
                    "customFilename": '"test"' if fileNamingType == 'custom' else None,
                    "overrideExistingFile": False,
                }
                component.node.outputs = {
                    "snapshotFilename": 'r'
                }
                assert (await component.execute()) == ControlFlow.NEXT
                result = component.process.get_variable('r')
                assert os.path.isfile(result)
                assert result.endswith(f'.{fileFormat}')
                if fileNamingType == 'custom':
                    assert result == os.path.join(temp_dir, f'test.{fileFormat}')
                img = Image.open(result)
                try:
                    assert abs(
                        logical_pixels_to_physical_pixels(400) - img.size[0]) < logical_pixels_to_physical_pixels(25)
                    assert abs(
                        logical_pixels_to_physical_pixels(300) - img.size[1]) < logical_pixels_to_physical_pixels(25)
                finally:
                    img.close()
