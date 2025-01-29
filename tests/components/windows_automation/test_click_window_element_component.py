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
    from pywinauto.base_wrapper import BaseWrapper
    from jimuflow.components.windows_automation import ClickWindowElementComponent
    from jimuflow.runtime.execution_engine import ControlFlow
    from tests.utils import create_component_context, add_test_window_element

    test_app_script = 'click_window_element_test_app.py'


    @pytest.mark.asyncio
    @pytest.mark.parametrize("click_type,mouse_button,modifier_key,expected", [
        ("single_click", "left", "none", "Left Clicked"),
        ("single_click", "right", "none", "Right Clicked"),
        ("single_click", "middle", "none", "Middle Clicked"),
        ("single_click", "left", "shift", "Shift+Left Clicked"),
        ("single_click", "left", "control", "Ctrl+Left Clicked"),
        ("single_click", "left", "alt", "Alt+Left Clicked"),
        ("double_click", "left", "none", "Left Double Clicked"),
        ("double_click", "right", "none", "Right Double Clicked"),
        ("double_click", "middle", "none", "Middle Double Clicked"),
        ("double_click", "left", "shift", "Shift+Left Double Clicked"),
        ("double_click", "left", "control", "Ctrl+Left Double Clicked"),
        ("double_click", "left", "alt", "Alt+Left Double Clicked"),
    ])
    async def test_execute(start_python_process, click_type, mouse_button, modifier_key, expected):
        start_python_process(test_app_script, wait_time=0)

        async with create_component_context(ClickWindowElementComponent) as component:
            label: BaseWrapper = pywinauto.Desktop(backend='uia').window(
                auto_id="QApplication.ClickWindowElementTestApp").child_window(
                auto_id='QApplication.ClickWindowElementTestApp.QLabel').wrapper_object()
            assert label.window_text() == "Not Clicked"
            component.node.inputs = {
                "elementUri": add_test_window_element(
                    component,
                    "/Button[@automation_id='QApplication.ClickWindowElementTestApp.QPushButton']",
                    "/Window[@automation_id='QApplication.ClickWindowElementTestApp']"),
                "clickType": click_type,
                "mouseButton": mouse_button,
                "modifierKey": modifier_key,
                "waitTime": "5",
            }
            assert (await component.execute()) == ControlFlow.NEXT
            assert label.window_text() == expected
