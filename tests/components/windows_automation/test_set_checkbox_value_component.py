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
    from pywinauto.controls.uia_controls import ButtonWrapper
    from jimuflow.components.windows_automation import SetCheckboxValueComponent
    from tests.utils import create_component_context, add_test_window_element
    from pywinauto.uia_defines import toggle_state_on, toggle_state_off
    from jimuflow.runtime.execution_engine import ControlFlow

    test_app_script = 'set_checkbox_value_test_app.py'


    @pytest.mark.asyncio
    @pytest.mark.parametrize("checkbox_index, check_type, delay_after_action, expected", [
        (0, "check", 0, toggle_state_on),
        (1, "uncheck", 0, toggle_state_off),
        (0, "toggle", 0, toggle_state_on),
        (1, "toggle", 0, toggle_state_off),
    ])
    async def test_execute(start_python_process, checkbox_index, check_type, delay_after_action, expected):
        start_python_process(test_app_script, wait_time=0)
        checkbox: ButtonWrapper = pywinauto.Desktop(backend='uia').window(
            auto_id="QApplication.SetCheckBoxValueTestApp").child_window(
            auto_id='QApplication.SetCheckBoxValueTestApp.QCheckBox', found_index=checkbox_index).wrapper_object()
        async with create_component_context(SetCheckboxValueComponent) as component:
            component.node.inputs = {
                "elementUri": add_test_window_element(
                    component,
                    f"/CheckBox[@automation_id='QApplication.SetCheckBoxValueTestApp.QCheckBox' and position()={checkbox_index + 1}]",
                    "/Window[@automation_id='QApplication.SetCheckBoxValueTestApp']"),
                "checkType": check_type,
                "delayAfterAction": f'"{delay_after_action}"',
                "waitTime": '"5"',
            }
            assert await component.execute() == ControlFlow.NEXT
            assert checkbox.get_toggle_state() == expected
