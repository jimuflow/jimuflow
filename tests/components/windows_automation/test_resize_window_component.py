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
    from pywinauto.base_wrapper import BaseWrapper
    from pywinauto.findwindows import ElementNotFoundError

    from jimuflow.components.windows_automation import ResizeWindowComponent, ResizeWindowComponent
    from jimuflow.runtime.execution_engine import ControlFlow
    from jimuflow.runtime.expression import escape_string
    from tests.utils import create_component_context, add_test_window_element
    from jimuflow.gui.window_utils import logical_pixels_to_physical_pixels

    test_app_script = 'get_window_test_app.py'


    @pytest.mark.asyncio
    async def test_resize_by_variable(start_python_process):
        start_python_process(test_app_script, wait_time=0)

        async with create_component_context(ResizeWindowComponent) as component:
            window: BaseWrapper = pywinauto.Desktop(backend='uia').window(
                auto_id="QApplication.GetWindowTestApp").wrapper_object()
            assert window.element_info.control_type == 'Window'
            await component.process.update_variable('winObj', window)
            rect = window.rectangle()
            assert rect.width() == logical_pixels_to_physical_pixels(400)
            assert rect.height() == logical_pixels_to_physical_pixels(300)
            new_width = logical_pixels_to_physical_pixels(300)
            new_height = logical_pixels_to_physical_pixels(200)
            component.node.inputs = {
                "getWindowMethod": 'window_object',
                "windowObject": 'winObj',
                "windowSize": (str(new_width), str(new_height))
            }
            assert (await component.execute()) == ControlFlow.NEXT
            await asyncio.sleep(1)
            rect = window.rectangle()
            assert abs(rect.width() - new_width) < 30
            assert abs(rect.height() - new_height) < 80


    @pytest.mark.asyncio
    async def test_resize_by_title(start_python_process):
        start_python_process(test_app_script, wait_time=0)

        async with create_component_context(ResizeWindowComponent) as component:
            window: BaseWrapper = pywinauto.Desktop(backend='uia').window(
                auto_id="QApplication.GetWindowTestApp").wrapper_object()
            assert window.element_info.control_type == 'Window'
            rect = window.rectangle()
            assert rect.width() == logical_pixels_to_physical_pixels(400)
            assert rect.height() == logical_pixels_to_physical_pixels(300)
            new_width = logical_pixels_to_physical_pixels(300)
            new_height = logical_pixels_to_physical_pixels(200)
            component.node.inputs = {
                "getWindowMethod": 'title',
                "title": escape_string('Get Window Test App'),
                "useClassName": True,
                "className": escape_string('GetWindowTestApp'),
                "useRegexMatching": False,
                "windowSize": (str(new_width), str(new_height))
            }
            assert (await component.execute()) == ControlFlow.NEXT
            await asyncio.sleep(1)
            rect = window.rectangle()
            assert abs(rect.width() - new_width) < 30
            assert abs(rect.height() - new_height) < 80


    @pytest.mark.asyncio
    async def test_resize_by_title_when_match_failed():
        async with create_component_context(ResizeWindowComponent) as component:
            new_width = logical_pixels_to_physical_pixels(300)
            new_height = logical_pixels_to_physical_pixels(200)
            component.node.inputs = {
                "getWindowMethod": 'title',
                "title": escape_string('Non-existent App'),
                "useClassName": True,
                "className": escape_string('GetWindowTestApp'),
                "useRegexMatching": False,
                "windowSize": (str(new_width), str(new_height))
            }
            with pytest.raises(ElementNotFoundError):
                await component.execute()


    @pytest.mark.asyncio
    async def test_resize_by_title_use_regex_matching(start_python_process):
        start_python_process(test_app_script, wait_time=0)

        async with create_component_context(ResizeWindowComponent) as component:
            window: BaseWrapper = pywinauto.Desktop(backend='uia').window(
                auto_id="QApplication.GetWindowTestApp").wrapper_object()
            assert window.element_info.control_type == 'Window'
            rect = window.rectangle()
            assert rect.width() == logical_pixels_to_physical_pixels(400)
            assert rect.height() == logical_pixels_to_physical_pixels(300)
            new_width = logical_pixels_to_physical_pixels(300)
            new_height = logical_pixels_to_physical_pixels(200)
            component.node.inputs = {
                "getWindowMethod": 'title',
                "title": escape_string('^Get Window Test App$'),
                "useClassName": True,
                "className": escape_string('GetWindowTestApp'),
                "useRegexMatching": True,
                "windowSize": (str(new_width), str(new_height))
            }
            assert (await component.execute()) == ControlFlow.NEXT
            await asyncio.sleep(1)
            rect = window.rectangle()
            assert abs(rect.width() - new_width) < 30
            assert abs(rect.height() - new_height) < 80


    @pytest.mark.asyncio
    async def test_resize_by_element(start_python_process):
        start_python_process(test_app_script, wait_time=0)

        async with create_component_context(ResizeWindowComponent) as component:
            window: BaseWrapper = pywinauto.Desktop(backend='uia').window(
                auto_id="QApplication.GetWindowTestApp").wrapper_object()
            assert window.element_info.control_type == 'Window'
            rect = window.rectangle()
            assert rect.width() == logical_pixels_to_physical_pixels(400)
            assert rect.height() == logical_pixels_to_physical_pixels(300)
            new_width = logical_pixels_to_physical_pixels(300)
            new_height = logical_pixels_to_physical_pixels(200)
            component.node.inputs = {
                "getWindowMethod": 'element',
                "elementUri": add_test_window_element(
                    component,
                    "/Text[@automation_id='QApplication.GetWindowTestApp.QLabel']",
                    "/Window[@automation_id='QApplication.GetWindowTestApp']"),
                "waitTime": "5",
                "windowSize": (str(new_width), str(new_height))
            }
            component.node.outputs = {
                "windowObject": 'r'
            }
            assert (await component.execute()) == ControlFlow.NEXT
            await asyncio.sleep(1)
            rect = window.rectangle()
            assert abs(rect.width() - new_width) < 30
            assert abs(rect.height() - new_height) < 80
