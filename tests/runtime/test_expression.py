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

from jimuflow.datatypes import builtin_data_type_registry
from jimuflow.runtime.expression import ExpressionToken, tokenize_expression, evaluate


@pytest.mark.parametrize("expression, expected", [
    ('收入 > "6000" && 收入 < "10000"',
     [ExpressionToken('收入'), ExpressionToken('>'), '6000', ExpressionToken('&&'), ExpressionToken('收入'),
      ExpressionToken('<'), '10000']),
    ('收入', [ExpressionToken('收入')]),
    ('"abc"', ["abc"]),
    ('100', [ExpressionToken("100")]),
    ('true', [ExpressionToken("true")]),
    ('false', [ExpressionToken("false")]),
    ('b.length', [ExpressionToken("b"), ExpressionToken("."), ExpressionToken("length")]),
    ('c["1"]', [ExpressionToken("c"), ExpressionToken("["), "1", ExpressionToken("]")]),
    ('!a', [ExpressionToken("!"), ExpressionToken("a")]),
    ('-1', [ExpressionToken("-"), ExpressionToken("1")]),
])
def test_tokenize_expression(expression, expected):
    tokens = tokenize_expression(expression)
    assert expected == tokens


@pytest.mark.parametrize("expression, expected", [
    ('(("100 "+"10"-5)*10/2)%11', 8),
    ('"abc"+123', 'abc123'),
    ('a>"50"&&a<"200"', True),
    ('a>"50"&&a<"100"', False),
    ('a>"100"&&a<"200"', False),
    ('a<"50"||a>"100"', False),
    ('a<"50"||a>="100"', True),
    ('a<="100"||a>"200"', True),
    ('a<"100"', False),
    ('a<="100"', True),
    ('a>"100"', False),
    ('a>="100"', True),
    ('a=="100"', True),
    ('b.length', 4),
    ('c["1"]', 7),
    ('d["name"]', 'Tom'),
    ('10**2', 100),
    ('9//2', 4),
])
def test_evaluate(expression, expected):
    result = evaluate(expression, {"a": 100, "b": "test", "c": [1, 7, 10], "d": {"name": 'Tom'}},
                      builtin_data_type_registry)
    assert result == expected
