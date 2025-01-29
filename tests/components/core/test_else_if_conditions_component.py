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

import pytest

from jimuflow.components.core import ElseIfConditionsComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component


@pytest.mark.asyncio
async def test_all_matched():
    component = create_component(ElseIfConditionsComponent)
    component.node.inputs = {
        "relation": "all",
        "conditions": [
            {
                "operand1": '1',
                "op": "==",
                "operand2": '1'
            },
            {
                "operand1": '2',
                "op": "==",
                "operand2": '2'
            }
        ]
    }
    assert (await component.execute()) == ControlFlow.SKIP_ELSE_IF


@pytest.mark.asyncio
async def test_all_not_matched():
    component = create_component(ElseIfConditionsComponent)
    component.node.inputs = {
        "relation": "all",
        "conditions": [
            {
                "operand1": '1',
                "op": "==",
                "operand2": '1'
            },
            {
                "operand1": '1',
                "op": "==",
                "operand2": '2'
            }
        ]
    }
    assert (await component.execute()) == ControlFlow.NEXT


@pytest.mark.asyncio
async def test_any_matched():
    component = create_component(ElseIfConditionsComponent)
    component.node.inputs = {
        "relation": "any",
        "conditions": [
            {
                "operand1": '1',
                "op": "==",
                "operand2": '1'
            },
            {
                "operand1": '1',
                "op": "==",
                "operand2": '2'
            }
        ]
    }
    assert (await component.execute()) == ControlFlow.SKIP_ELSE_IF


@pytest.mark.asyncio
async def test_any_not_matched():
    component = create_component(ElseIfConditionsComponent)
    component.node.inputs = {
        "relation": "all",
        "conditions": [
            {
                "operand1": '1',
                "op": "==",
                "operand2": '2'
            },
            {
                "operand1": '3',
                "op": "==",
                "operand2": '4'
            }
        ]
    }
    assert (await component.execute()) == ControlFlow.NEXT
