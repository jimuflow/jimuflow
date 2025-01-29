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
    import pytest
    import pywinauto

    from jimuflow.components.windows_automation import ExtractWindowElementComponent
    from jimuflow.runtime.execution_engine import ControlFlow
    from jimuflow.runtime.expression import escape_string
    from tests.utils import create_component_context, add_test_window_element

    test_app_script = 'extract_window_element_test_app.py'


    @pytest.mark.asyncio
    @pytest.mark.parametrize('xpath, extractType, attributeName, expected', [
        ("/Text[@automation_id='QApplication.ExtractWindowElementTestApp.QLabel']", 'text', None, 'label text'),
        ("/Edit[@automation_id='QApplication.ExtractWindowElementTestApp.QLineEdit']", 'value', None, 'line edit'),
        ("/Edit[@automation_id='QApplication.ExtractWindowElementTestApp.QTextEdit']", 'value', None, 'text edit'),
        ("/CheckBox[@automation_id='QApplication.ExtractWindowElementTestApp.QCheckBox' and position()=1]", 'value',
         None,
         False),
        ("/CheckBox[@automation_id='QApplication.ExtractWindowElementTestApp.QCheckBox' and position()=2]", 'value',
         None,
         True),
        ("/ComboBox[@automation_id='QApplication.ExtractWindowElementTestApp.QComboBox']", 'value', None, 'item 2'),
        ("/Text[@automation_id='QApplication.ExtractWindowElementTestApp.QLabel']", 'attribute_value', "class_name",
         'QLabel'),
        ("/ComboBox[@automation_id='QApplication.ExtractWindowElementTestApp.QComboBox']", 'position', None,
         {'x': 0, 'y': 0}),
    ])
    async def test_execute(start_python_process, xpath, extractType, attributeName, expected):
        start_python_process(test_app_script, wait_time=0)
        window = pywinauto.Desktop(backend='uia').window(
            auto_id="QApplication.ExtractWindowElementTestApp")
        window.wait('exists')
        async with create_component_context(ExtractWindowElementComponent) as component:
            component.node.inputs = {
                "elementUri": add_test_window_element(
                    component,
                    xpath,
                    "/Window[@automation_id='QApplication.ExtractWindowElementTestApp']"),
                "extractType": extractType,
                "attributeName": escape_string(attributeName) if attributeName else None
            }
            component.node.outputs = {
                "result": 'r'
            }
            assert (await component.execute()) == ControlFlow.NEXT
            if extractType == 'position':
                rect = window.child_window(auto_id="QApplication.ExtractWindowElementTestApp.QComboBox").rectangle()
                assert component.process.get_variable('r') == {"x": rect.left, "y": rect.top}
            else:
                assert component.process.get_variable('r') == expected
