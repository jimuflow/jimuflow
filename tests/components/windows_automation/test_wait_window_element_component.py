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
    from jimuflow.components.windows_automation import WaitWindowElementComponent
    from jimuflow.runtime.execution_engine import ControlFlow
    from tests.utils import create_component_context, add_test_window_element

    test_app_script = 'wait_window_element_test_app.py'


    @pytest.mark.asyncio
    async def test_wait_include_element_failed(start_python_process):
        start_python_process(test_app_script, wait_time=0)

        async with create_component_context(WaitWindowElementComponent) as component:
            add_button: BaseWrapper = pywinauto.Desktop(backend='uia').window(
                auto_id="QApplication.WaitWindowElementTestApp").child_window(
                auto_id='QApplication.WaitWindowElementTestApp.QPushButton', title='Add Label').wrapper_object()
            component.node.inputs = {
                "waitElementUri": add_test_window_element(
                    component,
                    "/Text[@automation_id='QApplication.WaitWindowElementTestApp.QLabel' and @name='Added Label']",
                    "/Window[@automation_id='QApplication.WaitWindowElementTestApp']"),
                "waitType": 'include_element',
                "withTimeout": False
            }
            component.node.outputs = {
                "waitResult": 'r'
            }
            assert (await component.execute()) == ControlFlow.NEXT
            success = component.process.get_variable('r')
            assert not success


    @pytest.mark.asyncio
    async def test_wait_include_element_success(start_python_process):
        start_python_process(test_app_script, wait_time=0)

        async with create_component_context(WaitWindowElementComponent) as component:
            add_button: BaseWrapper = pywinauto.Desktop(backend='uia').window(
                auto_id="QApplication.WaitWindowElementTestApp").child_window(
                auto_id='QApplication.WaitWindowElementTestApp.QPushButton', title='Add Label').wrapper_object()
            component.node.inputs = {
                "waitElementUri": add_test_window_element(
                    component,
                    "/Text[@automation_id='QApplication.WaitWindowElementTestApp.QLabel' and @name='Added Label']",
                    "/Window[@automation_id='QApplication.WaitWindowElementTestApp']"),
                "waitType": 'include_element',
                "withTimeout": True,
                "timeout": '5',
            }
            component.node.outputs = {
                "waitResult": 'r'
            }
            add_button.click_input()
            assert (await component.execute()) == ControlFlow.NEXT
            success = component.process.get_variable('r')
            assert success


    @pytest.mark.asyncio
    async def test_wait_exclude_element_failed(start_python_process):
        start_python_process(test_app_script, wait_time=0)

        async with create_component_context(WaitWindowElementComponent) as component:
            remove_button: BaseWrapper = pywinauto.Desktop(backend='uia').window(
                auto_id="QApplication.WaitWindowElementTestApp").child_window(
                auto_id='QApplication.WaitWindowElementTestApp.QPushButton', title='Remove Label').wrapper_object()
            component.node.inputs = {
                "waitElementUri": add_test_window_element(
                    component,
                    "/Text[@automation_id='QApplication.WaitWindowElementTestApp.QLabel' and @name='Label to remove']",
                    "/Window[@automation_id='QApplication.WaitWindowElementTestApp']"),
                "waitType": 'exclude_element',
                "withTimeout": False
            }
            component.node.outputs = {
                "waitResult": 'r'
            }
            assert (await component.execute()) == ControlFlow.NEXT
            success = component.process.get_variable('r')
            assert not success


    @pytest.mark.asyncio
    async def test_wait_exclude_element_success(start_python_process):
        start_python_process(test_app_script, wait_time=0)

        async with create_component_context(WaitWindowElementComponent) as component:
            remove_button: BaseWrapper = pywinauto.Desktop(backend='uia').window(
                auto_id="QApplication.WaitWindowElementTestApp").child_window(
                auto_id='QApplication.WaitWindowElementTestApp.QPushButton', title='Remove Label').wrapper_object()
            component.node.inputs = {
                "waitElementUri": add_test_window_element(
                    component,
                    "/Text[@automation_id='QApplication.WaitWindowElementTestApp.QLabel' and @name='Label to remove']",
                    "/Window[@automation_id='QApplication.WaitWindowElementTestApp']"),
                "waitType": 'exclude_element',
                "withTimeout": True,
                "timeout": '5',
            }
            component.node.outputs = {
                "waitResult": 'r'
            }
            remove_button.click_input()
            assert (await component.execute()) == ControlFlow.NEXT
            success = component.process.get_variable('r')
            assert success
