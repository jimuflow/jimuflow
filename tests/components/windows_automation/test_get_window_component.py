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
    from pywinauto.controls.uiawrapper import UIAWrapper
    from pywinauto.findwindows import ElementNotFoundError

    from jimuflow.components.windows_automation import GetWindowComponent
    from jimuflow.runtime.execution_engine import ControlFlow
    from jimuflow.runtime.expression import escape_string
    from tests.utils import create_component_context, add_test_window_element

    test_app_script = 'get_window_test_app.py'


    @pytest.mark.asyncio
    async def test_get_current_active(start_python_process):
        process = start_python_process(test_app_script)

        async with create_component_context(GetWindowComponent) as component:
            component.node.inputs = {
                "getWindowMethod": 'current_active',
            }
            component.node.outputs = {
                "windowObject": 'r'
            }
            assert (await component.execute()) == ControlFlow.NEXT
            window: UIAWrapper = component.process.get_variable('r')
            assert window is not None
            assert window.automation_id() == 'QApplication.GetWindowTestApp'

        assert process.poll() is None, "The sub-process has been terminated, but it is expected to be running."


    @pytest.mark.asyncio
    async def test_get_by_title(start_python_process):
        process = start_python_process(test_app_script)

        async with create_component_context(GetWindowComponent) as component:
            component.node.inputs = {
                "getWindowMethod": 'title',
                "title": escape_string('Get Window Test App'),
                "useClassName": True,
                "className": escape_string('GetWindowTestApp'),
                "useRegexMatching": False,
                "waitTime": "5",
            }
            component.node.outputs = {
                "windowObject": 'r'
            }
            assert (await component.execute()) == ControlFlow.NEXT
            window: UIAWrapper = component.process.get_variable('r')
            assert window is not None
            assert window.automation_id() == 'QApplication.GetWindowTestApp'

        assert process.poll() is None, "The sub-process has been terminated, but it is expected to be running."


    @pytest.mark.asyncio
    async def test_get_by_title_when_match_failed(start_python_process):
        process = start_python_process(test_app_script)

        async with create_component_context(GetWindowComponent) as component:
            component.node.inputs = {
                "getWindowMethod": 'title',
                "title": escape_string('Non-existent App'),
                "useClassName": True,
                "className": escape_string('GetWindowTestApp'),
                "useRegexMatching": False,
                "waitTime": "5",
            }
            component.node.outputs = {
                "windowObject": 'r'
            }
            with pytest.raises(ElementNotFoundError):
                await component.execute()

        assert process.poll() is None, "The sub-process has been terminated, but it is expected to be running."


    @pytest.mark.asyncio
    async def test_get_by_title_use_regex_matching(start_python_process):
        process = start_python_process(test_app_script)

        async with create_component_context(GetWindowComponent) as component:
            component.node.inputs = {
                "getWindowMethod": 'title',
                "title": escape_string('^Get Window Test App$'),
                "useClassName": True,
                "className": escape_string('GetWindowTestApp'),
                "useRegexMatching": True,
                "waitTime": "5",
            }
            component.node.outputs = {
                "windowObject": 'r'
            }
            assert (await component.execute()) == ControlFlow.NEXT
            window: UIAWrapper = component.process.get_variable('r')
            assert window is not None
            assert window.automation_id() == 'QApplication.GetWindowTestApp'

        assert process.poll() is None, "The sub-process has been terminated, but it is expected to be running."


    @pytest.mark.asyncio
    async def test_get_by_element(start_python_process):
        process = start_python_process(test_app_script)

        async with create_component_context(GetWindowComponent) as component:
            component.node.inputs = {
                "getWindowMethod": 'element',
                "elementUri": add_test_window_element(
                    component,
                    "/Text[@automation_id='QApplication.GetWindowTestApp.QLabel']",
                    "/Window[@automation_id='QApplication.GetWindowTestApp']"),
                "waitTime": "5",
            }
            component.node.outputs = {
                "windowObject": 'r'
            }
            assert (await component.execute()) == ControlFlow.NEXT
            window: UIAWrapper = component.process.get_variable('r')
            assert window is not None
            assert window.automation_id() == 'QApplication.GetWindowTestApp'

        assert process.poll() is None, "The sub-process has been terminated, but it is expected to be running."
