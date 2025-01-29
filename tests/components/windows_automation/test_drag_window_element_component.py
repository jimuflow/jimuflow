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

    from jimuflow.components.windows_automation import DragWindowElementComponent
    from jimuflow.gui.window_utils import logical_pixels_to_physical_pixels, physical_pixels_to_logical_pixels
    from jimuflow.runtime.execution_engine import ControlFlow
    from tests.utils import create_component_context, add_test_window_element

    test_app_script = 'drag_window_element_test_app.py'


    @pytest.mark.asyncio
    async def test_drag_to_element(start_python_process):
        start_python_process(test_app_script, wait_time=0)
        window = pywinauto.Desktop(backend='uia').window(
            auto_id="QApplication.DragWindowElementTestApp")
        button: ButtonWrapper = window.child_window(
            auto_id='QApplication.DragWindowElementTestApp.QPushButton').wrapper_object()
        async with create_component_context(DragWindowElementComponent) as component:
            component.node.inputs = {
                "sourceElementUri": add_test_window_element(
                    component,
                    "/Button[@automation_id='QApplication.DragWindowElementTestApp.QPushButton']",
                    "/Window[@automation_id='QApplication.DragWindowElementTestApp']"),
                "dragType": 'to_element',
                "targetElementUri": add_test_window_element(
                    component,
                    "/Text[@automation_id='QApplication.DragWindowElementTestApp.QLabel']",
                    "/Window[@automation_id='QApplication.DragWindowElementTestApp']"),
            }
            assert (await component.execute()) == ControlFlow.NEXT
            window_rect = window.rectangle()
            button_rect = button.rectangle()
            button_x = button_rect.left - window_rect.left
            button_y = button_rect.top - window_rect.top
            assert button_x == logical_pixels_to_physical_pixels(250)
            assert button_y == logical_pixels_to_physical_pixels(250)


    @pytest.mark.asyncio
    async def test_drag_to_element_with_offset(start_python_process):
        start_python_process(test_app_script, wait_time=0)
        window = pywinauto.Desktop(backend='uia').window(
            auto_id="QApplication.DragWindowElementTestApp")
        button: ButtonWrapper = window.child_window(
            auto_id='QApplication.DragWindowElementTestApp.QPushButton').wrapper_object()
        async with create_component_context(DragWindowElementComponent) as component:
            component.node.inputs = {
                "sourceElementUri": add_test_window_element(
                    component,
                    "/Button[@automation_id='QApplication.DragWindowElementTestApp.QPushButton']",
                    "/Window[@automation_id='QApplication.DragWindowElementTestApp']"),
                "sourceOffset": True,
                "sourceX": '"10"',
                "sourceY": '"20"',
                "dragType": 'to_element',
                "targetElementUri": add_test_window_element(
                    component,
                    "/Text[@automation_id='QApplication.DragWindowElementTestApp.QLabel']",
                    "/Window[@automation_id='QApplication.DragWindowElementTestApp']"),
                "targetOffset": True,
                "targetX": '"30"',
                "targetY": '"40"',
                "dragSpeed": 'slow'
            }
            assert (await component.execute()) == ControlFlow.NEXT
            window_rect = window.rectangle()
            button_rect = button.rectangle()
            button_x = button_rect.left - window_rect.left
            button_y = button_rect.top - window_rect.top
            assert button_x == logical_pixels_to_physical_pixels(250 + physical_pixels_to_logical_pixels(20))
            assert button_y == logical_pixels_to_physical_pixels(250 + physical_pixels_to_logical_pixels(20))


    @pytest.mark.asyncio
    async def test_drag_by_offset(start_python_process):
        start_python_process(test_app_script, wait_time=0)
        window = pywinauto.Desktop(backend='uia').window(
            auto_id="QApplication.DragWindowElementTestApp")
        button: ButtonWrapper = window.child_window(
            auto_id='QApplication.DragWindowElementTestApp.QPushButton').wrapper_object()
        async with create_component_context(DragWindowElementComponent) as component:
            component.node.inputs = {
                "sourceElementUri": add_test_window_element(
                    component,
                    "/Button[@automation_id='QApplication.DragWindowElementTestApp.QPushButton']",
                    "/Window[@automation_id='QApplication.DragWindowElementTestApp']"),
                "sourceOffset": True,
                "sourceX": '"10"',
                "sourceY": '"20"',
                "dragType": 'by_offset',
                "targetOffset": True,
                "dragOffsetX": '"100"',
                "dragOffsetY": '"80"',
                "dragSpeed": 'fast'
            }
            assert (await component.execute()) == ControlFlow.NEXT
            window_rect = window.rectangle()
            button_rect = button.rectangle()
            button_x = button_rect.left - window_rect.left
            button_y = button_rect.top - window_rect.top
            assert button_x == logical_pixels_to_physical_pixels(150 + physical_pixels_to_logical_pixels(100))
            assert button_y == logical_pixels_to_physical_pixels(100 + physical_pixels_to_logical_pixels(80))
