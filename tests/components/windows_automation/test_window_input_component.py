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
from pathlib import Path

from jimuflow.runtime.expression import escape_string

if sys.platform == "win32":
    import pytest
    import pywinauto
    from pywinauto.controls.uiawrapper import UIAWrapper
    from jimuflow.components.windows_automation import WindowInputComponent
    from jimuflow.runtime.execution_engine import ControlFlow
    from tests.utils import create_component_context, add_test_window_element

    test_app_script = 'window_input_test_app.py'


    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "content,append,press_enter_after_input,press_tab_after_input,input_method,include_shortcut_keys,click_before_input,input_interval,delay_after_focus,delay_after_action,expected",
        [
            ("abc\n 中\t文", False, False, False, "simulate", False, True, 100, 1, 0, "abc\n 中\t文"),
            ("abc\n 中\t文", False, False, False, "simulate", True, True, 100, 1, 0, "abc\n 中\t文"),
            ("abc\n 中\t文", True, True, True, "simulate", True, False, 100, 1, 0, "你好helloabc\n 中\t文\n\t"),
            ("^{END}", False, False, False, "simulate", True, True, 100, 1, 0, ""),
            ("abc\n 中\t文", False, False, False, "automate", False, False, 100, 1, 0, "abc\n 中\t文"),
            ("abc\n 中\t文", True, True, True, "automate", False, False, 100, 1, 0, "你好helloabc\n 中\t文\n\t"),
            ("^{END}", False, False, False, "automate", False, False, 100, 1, 0, "^{END}"),
        ]
    )
    async def test_execute(start_python_process, content, append, press_enter_after_input, press_tab_after_input,
                           input_method, include_shortcut_keys, click_before_input, input_interval, delay_after_focus,
                           delay_after_action, expected):
        start_python_process(test_app_script, wait_time=0)
        edit: UIAWrapper = pywinauto.Desktop(backend='uia').window(
            auto_id="QApplication.WindowInputTestApp").child_window(
            auto_id='QApplication.WindowInputTestApp.QTextEdit').wrapper_object()
        assert edit.window_text() == '你好hello'

        async with create_component_context(WindowInputComponent) as component:
            component.node.inputs = {
                "elementUri": add_test_window_element(
                    component,
                    "/Edit[@automation_id='QApplication.WindowInputTestApp.QTextEdit']",
                    "/Window[@automation_id='QApplication.WindowInputTestApp']"),
                "content": escape_string(content),
                "append": append,
                "pressEnterAfterInput": press_enter_after_input,
                "pressTabAfterInput": press_tab_after_input,
                "inputMethod": input_method,
                "includeShortcutKeys": include_shortcut_keys,
                "clickBeforeInput": click_before_input,
                "inputInterval": f'"{input_interval}"',
                "delayAfterFocus": f'"{delay_after_focus}"',
                "delayAfterAction": f'"{delay_after_action}"',
                "waitTime": '"5"',
            }
            assert (await component.execute()) == ControlFlow.NEXT
            assert edit.window_text() == expected


    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "content,append,press_enter_after_input,press_tab_after_input,input_method,include_shortcut_keys,click_before_input,input_interval,delay_after_focus,delay_after_action,expected",
        [
            ("abc\n 中\t文", False, False, False, "simulate", False, True, 100, 1, 0, "abc\r 中\t文"),
            ("abc\n 中\t文", False, False, False, "simulate", True, True, 100, 1, 0, "abc\r 中\t文"),
            ("abc\n 中\t文", True, True, True, "simulate", True, False, 100, 1, 0, "你好hello\r第二行abc\r 中\t文\r\t"),
            ("^{END}", False, False, False, "simulate", True, True, 100, 1, 0, ""),
            ("abc\n 中\t文", False, False, False, "automate", False, False, 100, 1, 0, "abc\r 中\t文"),
            (
            "abc\n 中\t文", True, True, True, "automate", False, False, 100, 1, 0, "你好hello\r第二行abc\r 中\t文\r\t"),
            ("^{END}", False, False, False, "automate", False, False, 100, 1, 0, "^{END}"),
        ]
    )
    async def test_win_forms_rich_text_box(start_app_process, content, append, press_enter_after_input,
                                           press_tab_after_input,
                                           input_method, include_shortcut_keys, click_before_input, input_interval,
                                           delay_after_focus,
                                           delay_after_action, expected):
        app_path = Path(__file__).parent / "../../windows_apps/JimuFlowWinFormsTestApp/JimuFlowWinFormsTestApp.exe"
        start_app_process(str(app_path), wait_time=0)
        edit: UIAWrapper = pywinauto.Desktop(backend='uia').window(
            title="JimuFlow WinForms Test APP").child_window(
            auto_id='richTextBox1').wrapper_object()
        assert edit.window_text() == '你好hello\r第二行'

        async with create_component_context(WindowInputComponent) as component:
            component.node.inputs = {
                "elementUri": add_test_window_element(
                    component,
                    "/Document[@automation_id='richTextBox1']",
                    "/Window[@name='JimuFlow WinForms Test APP']"),
                "content": escape_string(content),
                "append": append,
                "pressEnterAfterInput": press_enter_after_input,
                "pressTabAfterInput": press_tab_after_input,
                "inputMethod": input_method,
                "includeShortcutKeys": include_shortcut_keys,
                "clickBeforeInput": click_before_input,
                "inputInterval": f'"{input_interval}"',
                "delayAfterFocus": f'"{delay_after_focus}"',
                "delayAfterAction": f'"{delay_after_action}"',
                "waitTime": '"5"',
            }
            assert (await component.execute()) == ControlFlow.NEXT
            assert edit.window_text() == expected
