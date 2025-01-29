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
    from jimuflow.components.windows_automation import HoverWindowElementComponent
    from jimuflow.runtime.execution_engine import ControlFlow
    from tests.utils import create_component_context, add_test_window_element

    test_app_script = 'hover_window_element_test_app.py'


    @pytest.mark.asyncio
    async def test_execute(start_python_process):
        start_python_process(test_app_script, wait_time=0)

        async with create_component_context(HoverWindowElementComponent) as component:
            label: BaseWrapper = pywinauto.Desktop(backend='uia').window(
                auto_id="QApplication.HoverWindowElementTestApp").child_window(
                auto_id='QApplication.HoverWindowElementTestApp.QLabel').wrapper_object()
            assert label.window_text() == "Not Hovered"
            component.node.inputs = {
                "elementUri": add_test_window_element(
                    component,
                    "/Button[@automation_id='QApplication.HoverWindowElementTestApp.QPushButton']",
                    "/Window[@automation_id='QApplication.HoverWindowElementTestApp']"),
                "waitTime": "5",
            }
            assert (await component.execute()) == ControlFlow.NEXT
            assert label.window_text() == 'Hovered'
