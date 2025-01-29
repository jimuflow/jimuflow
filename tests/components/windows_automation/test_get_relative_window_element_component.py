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

    from jimuflow.components.windows_automation import GetRelativeWindowElementComponent
    from jimuflow.runtime.execution_engine import ControlFlow
    from jimuflow.runtime.expression import escape_string
    from tests.utils import create_component_context, add_test_window_element

    test_app_script = 'get_relative_window_element_test_app.py'


    @pytest.mark.asyncio
    @pytest.mark.parametrize('xpath, locateType, descendantRelativeXpath, childPosition, expected', [
        ('/Group/Text[1]', 'parent', '', '', 'Level 1'),
        ('/Group/Text[2]', 'prev_sibling', '', '', 'Level 1 - 0'),
        ('/Group/Text[2]', 'next_sibling', '', '', 'Level 1 - 2'),
        ('/Group', 'first_matched_descendant', 'Group/Text[2]', '', 'Level 2 - 1'),
        ('/Group', 'all_matched_descendants', '//Text', '',
         ['Level 1 - 0', 'Level 1 - 1', 'Level 1 - 2', 'Level 2 - 0', 'Level 2 - 1', 'Level 2 - 2']),
        ('/Group', 'all_children', '', '',
         ['Level 1 - 0', 'Level 1 - 1', 'Level 1 - 2', 'Level 2']),
        ('/Group', 'specified_child', '', '1', 'Level 1 - 1')
    ])
    async def test_execute(start_python_process, xpath, locateType, descendantRelativeXpath, childPosition, expected):
        start_python_process(test_app_script, wait_time=0)
        pywinauto.Desktop(backend='uia').window(
            auto_id="QApplication.GetRelativeWindowElementTestApp").wait('exists')
        async with create_component_context(GetRelativeWindowElementComponent) as component:
            component.node.inputs = {
                "elementUri": add_test_window_element(
                    component,
                    xpath,
                    "/Window[@automation_id='QApplication.GetRelativeWindowElementTestApp']"),
                "locateType": locateType,
                "descendantRelativeXpath": escape_string(descendantRelativeXpath),
                "childPosition": escape_string(childPosition),
                "waitTime": '"5"'
            }
            component.node.outputs = {
                "result": 'r'
            }
            assert (await component.execute()) == ControlFlow.NEXT
            if isinstance(expected, list):
                result = [item.window_text() for item in component.process.get_variable('r')]
            else:
                result = component.process.get_variable('r').window_text()
            assert result == expected
