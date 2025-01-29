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
    from jimuflow.components.windows_automation import LoopWindowElementsComponent
    from jimuflow.runtime.execution_engine import ControlFlow
    from tests.utils import add_mock_component, MockComponent, create_component_context, add_test_window_element

    test_app_script = 'loop_window_elements_test_app.py'


    @pytest.mark.asyncio
    @pytest.mark.parametrize('reversed_loop', [False, True])
    async def test_execute(start_python_process, reversed_loop):
        start_python_process(test_app_script, wait_time=0)
        pywinauto.Desktop(backend='uia').window(
            auto_id="QApplication.LoopWindowElementsTestApp").child_window(
            auto_id='QApplication.LoopWindowElementsTestApp.QLabel', found_index=0).wait("exists")

        async with create_component_context(LoopWindowElementsComponent) as component:
            component.node.inputs = {
                "elementsUri": add_test_window_element(
                    component,
                    "/Text[@automation_id='QApplication.LoopWindowElementsTestApp.QLabel']",
                    "/Window[@automation_id='QApplication.LoopWindowElementsTestApp']"),
                "reversedLoop": reversed_loop,
                "waitTime": '"5"'
            }
            component.node.outputs = {
                "currentElement": 'r'
            }
            loop_item_list = []

            async def mock_loop_body(component: MockComponent):
                loop_item_list.append(component.process.get_variable("r").window_text())
                return ControlFlow.NEXT

            add_mock_component(component, mock_loop_body)
            assert (await component.execute()) == ControlFlow.NEXT
            if reversed_loop:
                loop_item_list.reverse()
            assert loop_item_list == ['label 1', 'label 2', 'label 3']


    @pytest.mark.asyncio
    @pytest.mark.parametrize("control_flow", [ControlFlow.BREAK, ControlFlow.RETURN, ControlFlow.EXIT])
    async def test_break(start_python_process, control_flow):
        start_python_process(test_app_script, wait_time=0)
        pywinauto.Desktop(backend='uia').window(
            auto_id="QApplication.LoopWindowElementsTestApp").child_window(
            auto_id='QApplication.LoopWindowElementsTestApp.QLabel', found_index=0).wait("exists")
        async with create_component_context(LoopWindowElementsComponent) as component:
            component.node.inputs = {
                "elementsUri": add_test_window_element(
                    component,
                    "/Text[@automation_id='QApplication.LoopWindowElementsTestApp.QLabel']",
                    "/Window[@automation_id='QApplication.LoopWindowElementsTestApp']"),
                "waitTime": '"5"'
            }
            component.node.outputs = {
                "currentElement": 'r'
            }
            loop_item_list = []

            async def mock_loop_body(component: MockComponent):
                loop_item_list.append(component.process.get_variable("r").window_text())
                if len(loop_item_list) >= 2:
                    return control_flow
                return ControlFlow.NEXT

            add_mock_component(component, mock_loop_body)
            assert (await component.execute()) == (
                ControlFlow.NEXT if control_flow == ControlFlow.BREAK else control_flow)
            assert loop_item_list == ['label 1', 'label 2']
