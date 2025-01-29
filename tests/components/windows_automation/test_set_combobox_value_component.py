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
    from pywinauto.controls.uia_controls import ComboBoxWrapper
    from jimuflow.components.windows_automation import SetComboBoxValueComponent
    from tests.utils import create_component_context, add_test_window_element
    from jimuflow.runtime.expression import escape_string

    test_app_script = 'set_combobox_value_test_app.py'


    @pytest.mark.asyncio
    @pytest.mark.parametrize("select_type, option_content, match_type, option_index, delay_after_action, expected", [
        ("by_content", "龙", "contains", 0, 0, "Apple"),
        ("by_content", "火龙果", "equals", 0, 0, "Apple"),
        ("by_content", ".*龙.*", "regex", 0, 0, "Apple"),
        ("by_index", "", "", 2, 0, "Apple"),
    ])
    async def test_execute(start_python_process, select_type, option_content, match_type, option_index,
                           delay_after_action, expected):
        start_python_process(test_app_script, wait_time=0)
        combobox: ComboBoxWrapper = pywinauto.Desktop(backend='uia').window(
            auto_id="QApplication.SetComboBoxValueTestApp").child_window(
            auto_id='QApplication.SetComboBoxValueTestApp.QComboBox').wrapper_object()
        assert combobox.selected_text() == 'Apple'
        async with create_component_context(SetComboBoxValueComponent) as component:
            component.node.inputs = {
                "elementUri": add_test_window_element(
                    component,
                    "/ComboBox[@automation_id='QApplication.SetComboBoxValueTestApp.QComboBox']",
                    "/Window[@automation_id='QApplication.SetComboBoxValueTestApp']"),
                "selectType": select_type,
                "optionContent": escape_string(option_content),
                "matchType": match_type,
                "optionIndex": f'"{option_index}"',
                "delayAfterAction": f'"{delay_after_action}"',
                "waitTime": '"5"',
            }
            with pytest.raises(IndexError):
                await component.execute()
