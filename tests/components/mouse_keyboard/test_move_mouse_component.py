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

import pyautogui
import pytest

from jimuflow.components.mouse_keyboard import MoveMouseComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component_context


@pytest.mark.asyncio
async def test_move_relative_to_screen_origin():
    async with create_component_context(MoveMouseComponent) as component:
        pyautogui.moveTo(100, 150)
        x, y = pyautogui.position()
        assert x == 100 and y == 150
        component.node.inputs = {
            "relativeTo": 'screen_origin',
            "offsetX": '"200"',
            "offsetY": '"350"',
            "moveSpeed": "instant"
        }
        assert (await component.execute()) == ControlFlow.NEXT
        x2, y2 = pyautogui.position()
        assert x2 == 200 and y2 == 350


@pytest.mark.asyncio
async def test_move_relative_to_current_position():
    async with create_component_context(MoveMouseComponent) as component:
        pyautogui.moveTo(100, 150)
        x, y = pyautogui.position()
        assert x == 100 and y == 150
        component.node.inputs = {
            "relativeTo": 'current_position',
            "offsetX": '"200"',
            "offsetY": '"350"',
            "moveSpeed": "instant"
        }
        assert (await component.execute()) == ControlFlow.NEXT
        x2, y2 = pyautogui.position()
        assert x2 == 300 and y2 == 500
