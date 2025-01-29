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

from jimuflow.components.core.condition_utils import evaluate_condition


@pytest.mark.parametrize("operand1,op,operand2,expected", [
    (1, '==', 1, True),
    (1.2, '==', 1.2, True),
    (1, '==', 2, False),
    (1, '==', '1', True),
    (1.2, '==', '1.2', True),
    ('abc', '==', 'abc', True),
    ('abc', '==', 'abc1', False),
    (1, '!=', 1, False),
    (1, '!=', 2, True),
    (1, '!=', '1', False),
    ('abc', '!=', 'abc', False),
    ('abc', '!=', 'abc1', True),
    (1, '>', 1, False),
    (2, '>', 1, True),
    (2, '>', '1', True),
    ('abc', '>', 'abc', False),
    ('abc1', '>', 'abc', True),
    (1, '<', 1, False),
    (1, '<', 2, True),
    ('1', '<', 2, True),
    ('abc', '<', 'abc', False),
    ('abc', '<', 'abc1', True),
    (0, '>=', 1, False),
    (1, '>=', 1, True),
    (2, '>=', 1, True),
    (2, '>=', '1', True),
    (0, '>=', '1', False),
    ('abc', '>=', 'abc', True),
    ('abc1', '>=', 'abc', True),
    (2, '<=', 1, False),
    (1, '<=', 1, True),
    (1, '<=', 2, True),
    ('1', '<=', 2, True),
    ('1', '<=', 0, False),
    ('abc', '<=', 'abc', True),
    ('abc', '<=', 'abc1', True),
    ('abc1', 'contains', 'abc', True),
    ('abc1', 'contains', 'efg', False),
    (['abc', 'efg'], 'contains', 'abc', True),
    (['abc1', 'efg1'], 'contains', 'efg', False),
    ('abc1', 'not_contains', 'abc', False),
    ('abc1', 'not_contains', 'efg', True),
    (['abc', 'efg'], 'not_contains', 'abc', False),
    (['abc1', 'efg1'], 'not_contains', 'efg', True),
    ('', 'is_empty', None, True),
    ('abc', 'is_empty', None, False),
    ('', 'not_empty', None, False),
    ('abc', 'not_empty', None, True),
    ('abc', 'starts_with', "a", True),
    ('abc', 'starts_with', "", False),
    ('abc', 'starts_with', "e", False),
    ('', 'starts_with', "", False),
    ('abc', 'not_starts_with', "a", False),
    ('abc', 'not_starts_with', "", True),
    ('abc', 'not_starts_with', "e", True),
    ('', 'not_starts_with', "", True),
    ('abc', 'ends_with', "c", True),
    ('abc', 'ends_with', "", False),
    ('abc', 'ends_with', "e", False),
    ('', 'ends_with', "", False),
    ('abc', 'not_ends_with', "c", False),
    ('abc', 'not_ends_with', "", True),
    ('abc', 'not_ends_with', "e", True),
    ('', 'not_ends_with', "", True),
])
def test_evaluate_condition(operand1, op, operand2, expected):
    assert evaluate_condition(operand1, op, operand2) == expected
