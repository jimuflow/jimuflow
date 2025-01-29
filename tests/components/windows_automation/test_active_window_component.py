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

import asyncio
import sys

if sys.platform == "win32":
    import pytest
    import pywinauto
    from pywinauto.controls.uiawrapper import UIAWrapper
    from pywinauto.findwindows import ElementNotFoundError

    from jimuflow.components.windows_automation import ActiveWindowComponent, ActiveWindowComponent
    from jimuflow.runtime.execution_engine import ControlFlow
    from jimuflow.runtime.expression import escape_string
    from tests.utils import create_component_context, add_test_window_element

    foreground_test_app_script = 'get_window_test_app.py'
    test_app_script = 'active_window_test_app.py'


    def start_windows(start_python_process):
        start_python_process(test_app_script, wait_time=0)
        window: UIAWrapper = pywinauto.Desktop(backend='uia').window(
            auto_id="QApplication.ActiveWindowTestApp").wrapper_object()
        assert window.element_info.control_type == 'Window'
        start_python_process(foreground_test_app_script, wait_time=0)
        foreground_window: UIAWrapper = pywinauto.Desktop(backend='uia').window(
            auto_id="QApplication.GetWindowTestApp").wrapper_object()
        assert foreground_window.element_info.control_type == 'Window'
        assert foreground_window.is_active()
        assert not window.is_active()
        return window


    @pytest.mark.asyncio
    async def test_active_by_variable(start_python_process):
        window: UIAWrapper = start_windows(start_python_process)

        async with create_component_context(ActiveWindowComponent) as component:
            await component.process.update_variable('winObj', window)
            component.node.inputs = {
                "getWindowMethod": 'window_object',
                "windowObject": 'winObj',
            }
            assert (await component.execute()) == ControlFlow.NEXT
            await asyncio.sleep(1)
            assert window.is_active()


    @pytest.mark.asyncio
    async def test_active_by_title(start_python_process):
        window: UIAWrapper = start_windows(start_python_process)

        async with create_component_context(ActiveWindowComponent) as component:
            component.node.inputs = {
                "getWindowMethod": 'title',
                "title": escape_string('Active Window Test App'),
                "useClassName": True,
                "className": escape_string('ActiveWindowTestApp'),
                "useRegexMatching": False,
            }
            assert (await component.execute()) == ControlFlow.NEXT
            await asyncio.sleep(1)
            assert window.is_active()


    @pytest.mark.asyncio
    async def test_active_by_title_when_match_failed():
        async with create_component_context(ActiveWindowComponent) as component:
            component.node.inputs = {
                "getWindowMethod": 'title',
                "title": escape_string('Non-existent App'),
                "useClassName": True,
                "className": escape_string('ActiveWindowTestApp'),
                "useRegexMatching": False,
            }
            with pytest.raises(ElementNotFoundError):
                await component.execute()


    @pytest.mark.asyncio
    async def test_active_by_title_use_regex_matching(start_python_process):
        window: UIAWrapper = start_windows(start_python_process)

        async with create_component_context(ActiveWindowComponent) as component:
            component.node.inputs = {
                "getWindowMethod": 'title',
                "title": escape_string('^Active Window Test App$'),
                "useClassName": True,
                "className": escape_string('ActiveWindowTestApp'),
                "useRegexMatching": True,
            }
            assert (await component.execute()) == ControlFlow.NEXT
            await asyncio.sleep(1)
            assert window.is_active()


    @pytest.mark.asyncio
    async def test_active_by_element(start_python_process):
        window: UIAWrapper = start_windows(start_python_process)

        async with create_component_context(ActiveWindowComponent) as component:
            component.node.inputs = {
                "getWindowMethod": 'element',
                "elementUri": add_test_window_element(
                    component,
                    "/Text[@automation_id='QApplication.ActiveWindowTestApp.QLabel']",
                    "/Window[@automation_id='QApplication.ActiveWindowTestApp']"),
                "waitTime": "5",
            }
            component.node.outputs = {
                "windowObject": 'r'
            }
            assert (await component.execute()) == ControlFlow.NEXT
            await asyncio.sleep(1)
            assert window.is_active()
