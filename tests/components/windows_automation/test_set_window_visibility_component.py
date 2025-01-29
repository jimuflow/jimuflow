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

    from jimuflow.components.windows_automation import SetWindowVisibilityComponent, SetWindowVisibilityComponent, \
        SetWindowVisibilityComponent
    from jimuflow.runtime.execution_engine import ControlFlow
    from jimuflow.runtime.expression import escape_string
    from tests.utils import create_component_context, add_test_window_element
    from jimuflow.components.windows_automation.pywinauto_utill import hide_window, is_control_visible

    test_app_script = 'get_window_test_app.py'


    @pytest.mark.asyncio
    @pytest.mark.parametrize("window_visibility", [
        "show",
        "hide",
    ])
    async def test_set_window_visibility_by_variable(start_python_process, window_visibility):
        start_python_process(test_app_script, wait_time=0)

        async with create_component_context(SetWindowVisibilityComponent) as component:
            window: UIAWrapper = pywinauto.Desktop(backend='uia').window(
                auto_id="QApplication.GetWindowTestApp").wrapper_object()
            assert window.element_info.control_type == 'Window'
            await component.process.update_variable('winObj', window)
            if window_visibility == 'show':
                hide_window(window)
                await asyncio.sleep(1)
                assert not is_control_visible(window)
            else:
                assert is_control_visible(window)
            component.node.inputs = {
                "getWindowMethod": 'window_object',
                "windowObject": 'winObj',
                "windowVisibility": window_visibility
            }
            assert (await component.execute()) == ControlFlow.NEXT
            await asyncio.sleep(1)
            if window_visibility == 'show':
                assert is_control_visible(window)
            else:
                assert not is_control_visible(window)


    @pytest.mark.asyncio
    @pytest.mark.parametrize("window_visibility", [
        "show",
        "hide",
    ])
    async def test_set_window_visibility_by_title(start_python_process, window_visibility):
        start_python_process(test_app_script, wait_time=0)

        async with create_component_context(SetWindowVisibilityComponent) as component:
            window: UIAWrapper = pywinauto.Desktop(backend='uia').window(
                auto_id="QApplication.GetWindowTestApp").wrapper_object()
            assert window.element_info.control_type == 'Window'
            if window_visibility == 'show':
                hide_window(window)
                await asyncio.sleep(1)
                assert not is_control_visible(window)
            else:
                assert is_control_visible(window)
            component.node.inputs = {
                "getWindowMethod": 'title',
                "title": escape_string('Get Window Test App'),
                "useClassName": True,
                "className": escape_string('GetWindowTestApp'),
                "useRegexMatching": False,
                "windowVisibility": window_visibility
            }
            if window_visibility == 'show':
                # UIA 无法获取隐藏的窗口
                with pytest.raises(ElementNotFoundError):
                    await component.execute()
            else:
                assert (await component.execute()) == ControlFlow.NEXT
                await asyncio.sleep(1)
                assert not is_control_visible(window)


    @pytest.mark.asyncio
    @pytest.mark.parametrize("window_visibility", [
        "show",
        "hide",
    ])
    async def test_set_window_visibility_by_title_when_match_failed(window_visibility):
        async with create_component_context(SetWindowVisibilityComponent) as component:
            component.node.inputs = {
                "getWindowMethod": 'title',
                "title": escape_string('Non-existent App'),
                "useClassName": True,
                "className": escape_string('GetWindowTestApp'),
                "useRegexMatching": False,
                "windowVisibility": window_visibility
            }
            with pytest.raises(ElementNotFoundError):
                await component.execute()


    @pytest.mark.asyncio
    @pytest.mark.parametrize("window_visibility", [
        "show",
        "hide",
    ])
    async def test_set_window_visibility_by_title_use_regex_matching(start_python_process, window_visibility):
        start_python_process(test_app_script, wait_time=0)

        async with create_component_context(SetWindowVisibilityComponent) as component:
            window: UIAWrapper = pywinauto.Desktop(backend='uia').window(
                auto_id="QApplication.GetWindowTestApp").wrapper_object()
            assert window.element_info.control_type == 'Window'
            if window_visibility == 'show':
                hide_window(window)
                await asyncio.sleep(1)
                assert not is_control_visible(window)
            else:
                assert is_control_visible(window)
            component.node.inputs = {
                "getWindowMethod": 'title',
                "title": escape_string('^Get Window Test App$'),
                "useClassName": True,
                "className": escape_string('GetWindowTestApp'),
                "useRegexMatching": True,
                "windowVisibility": window_visibility
            }
            if window_visibility == 'show':
                # UIA 无法获取隐藏的窗口
                with pytest.raises(ElementNotFoundError):
                    await component.execute()
            else:
                assert (await component.execute()) == ControlFlow.NEXT
                await asyncio.sleep(1)
                assert not is_control_visible(window)


    @pytest.mark.asyncio
    @pytest.mark.parametrize("window_visibility", [
        "show",
        "hide",
    ])
    async def test_set_window_visibility_by_element(start_python_process, window_visibility):
        start_python_process(test_app_script, wait_time=0)

        async with create_component_context(SetWindowVisibilityComponent) as component:
            window: UIAWrapper = pywinauto.Desktop(backend='uia').window(
                auto_id="QApplication.GetWindowTestApp").wrapper_object()
            assert window.element_info.control_type == 'Window'
            if window_visibility == 'show':
                hide_window(window)
                await asyncio.sleep(1)
                assert not is_control_visible(window)
            else:
                assert is_control_visible(window)
            component.node.inputs = {
                "getWindowMethod": 'element',
                "elementUri": add_test_window_element(
                    component,
                    "/Text[@automation_id='QApplication.GetWindowTestApp.QLabel']",
                    "/Window[@automation_id='QApplication.GetWindowTestApp']"),
                "waitTime": "5",
                "windowVisibility": window_visibility
            }
            if window_visibility == 'show':
                # UIA 无法获取隐藏的窗口
                with pytest.raises(ElementNotFoundError):
                    await component.execute()
            else:
                assert (await component.execute()) == ControlFlow.NEXT
                await asyncio.sleep(1)
                assert not is_control_visible(window)
