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

import ast
import re

from lark import Lark, Transformer, Token

from jimuflow.datatypes import DataTypeRegistry, DataTypeProperty, builtin_data_type_registry
from jimuflow.definition import VariableDef

expr_grammar = r"""
    ?expression: logical_or
    ?logical_or: logical_and ( "||" logical_and )*
    ?logical_and: equality ( "&&" equality )*
    ?equality: relational ( equality_operator relational )?
    equality_operator:  "==" -> equals | "!=" -> not_equals
    ?relational: additive ( relational_operator additive )?
    relational_operator: ">" -> gt | ">=" -> ge | "<" -> lt | "<=" -> le
    ?additive: multiplicative ( additive_operator multiplicative )*
    additive_operator: "+" -> add | "-" -> subtract
    ?multiplicative: unary ( multiplicative_operator unary )*
    multiplicative_operator: "*" -> multiply | "/" -> divide | "%" -> mod | "**" -> power | "//" -> divide_whole
    ?unary: unary_operator? primary_expression
    unary_operator: "!" -> not | "-" -> negative
    ?primary_expression: LPRA expression RPRA | value
    LPRA: "("
    RPRA: ")"
    ?value: TEXT -> string | NUMBER -> number | boolean | variable
    TEXT: ESCAPED_STRING
    boolean: "true" -> true | "false" -> false
    variable: IDENTIFIER ( DOT IDENTIFIER | LSB expression RSB )*
    IDENTIFIER: /(_|[a-zA-Z]|[\u4e00-\u9fa5])\w*/
    DOT: "."
    LSB: "["
    RSB: "]"
    
    
    %import common.ESCAPED_STRING
    %import common.NUMBER
    %import common.LETTER
    %import common.CNAME
    %import common.WS
    %ignore WS
    """

# expr_parser = Lark(expr_grammar, start='expression')
expr_parser = Lark(expr_grammar, start='expression', parser='lalr')


class ExpressionEvaluator(Transformer):
    def __init__(self, variables: dict, type_registry: DataTypeRegistry):
        super().__init__()
        self.variables = variables
        self.type_registry = type_registry

    def logical_or(self, nodes):
        result = nodes[0]
        for node in nodes[1:]:
            result = result or node
        return result

    def logical_and(self, nodes):
        result = nodes[0]
        for node in nodes[1:]:
            result = result and node
        return result

    def equality(self, nodes):
        return self.calc(nodes[0], nodes[1].data, nodes[2])

    def primary_expression(self, nodes):
        return nodes[1]

    def calc(self, operand1, op, operand2):
        operand1 = self.try_convert_to_number(operand1)
        operand2 = self.try_convert_to_number(operand2)
        # 有三种情况：number+number number+obj obj+obj
        if op == 'equals':
            return operand1 == operand2
        elif op == 'not_equals':
            return operand1 != operand2
        elif op == 'gt':
            return operand1 > operand2
        elif op == 'ge':
            return operand1 >= operand2
        elif op == 'lt':
            return operand1 < operand2
        elif op == 'le':
            return operand1 <= operand2
        elif op == 'add':
            if isinstance(operand1, (int, float)) and isinstance(operand2, (int, float)):
                return operand1 + operand2
            return str(operand1) + str(operand2)
        elif op == 'subtract':
            return operand1 - operand2
        elif op == 'multiply':
            return operand1 * operand2
        elif op == 'divide':
            return operand1 / operand2
        elif op == 'mod':
            return operand1 % operand2
        elif op == 'power':
            return operand1 ** operand2
        elif op == 'divide_whole':
            return operand1 // operand2
        else:
            raise Exception(f'Unknown operator: {op}')

    def try_convert_to_number(self, value):
        if isinstance(value, (int, float)):
            return value
        elif isinstance(value, str) and re.match(r"^\d+(\.\d*)?$", value.strip()):
            if "." in value:
                return float(value)
            else:
                return int(value)
        else:
            return value

    def try_convert_to_boolean(self, value):
        if isinstance(value, bool):
            return value
        elif value == 'true':
            return True
        elif value == 'false':
            return False
        else:
            value = self.try_convert_to_number(value)
            if isinstance(value, (int, float)):
                return value != 0
            else:
                return value is not None

    def relational(self, nodes):
        return self.calc(nodes[0], nodes[1].data, nodes[2])

    def additive(self, nodes):
        result = nodes[0]
        for i in range(2, len(nodes), 2):
            result = self.calc(result, nodes[i - 1].data, nodes[i])
        return result

    def multiplicative(self, nodes):
        result = nodes[0]
        for i in range(2, len(nodes), 2):
            result = self.calc(result, nodes[i - 1].data, nodes[i])
        return result

    def unary(self, nodes):
        if nodes[0].data == 'negative':
            # 算术取负操作
            return -self.try_convert_to_number(nodes[1])
        elif nodes[0].data == 'not':
            # 逻辑取非操作
            return not self.try_convert_to_boolean(nodes[1])

    def string(self, nodes):
        return ast.literal_eval(nodes[0])

    def number(self, nodes):
        if "." in nodes[0]:
            return float(nodes[0])
        else:
            return int(nodes[0])

    def true(self, nodes):
        return True

    def false(self, nodes):
        return False

    def variable(self, nodes):
        root = self.variables.get(nodes[0], None)
        idx = 1
        while idx < len(nodes) and root:
            data_type = self.type_registry.get_obj_data_type(root)
            if nodes[idx] == '.':
                root = data_type.get_property_value(root, nodes[idx + 1])
                idx += 2
            else:
                root = root[self.try_convert_to_number(nodes[idx + 1])]
                idx += 3
        return root


class ExpressionToken():
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return 'EToken(' + self.data + ')'

    def __eq__(self, other):
        return isinstance(other, ExpressionToken) and self.data == other.data


def extend_list(l, items):
    if isinstance(items, list):
        l.extend(items)
    else:
        l.append(items)


def escape_string(s):
    return '"' + ''.join(escape_char(ch) for ch in s) + '"'


def escape_char(ch):
    if ch == '"' or ch == '\\':
        return '\\' + ch
    elif ch == '\r':
        return '\\r'
    elif ch == '\n':
        return '\\n'
    else:
        return ch


class ExpressionTokenizer(Transformer):
    def __init__(self):
        super().__init__()

    def logical_or(self, nodes):
        result = []
        for node in nodes:
            if len(result) > 0:
                result.append(ExpressionToken("||"))
            extend_list(result, node)
        return result

    def logical_and(self, nodes):
        result = []
        for node in nodes:
            if len(result) > 0:
                result.append(ExpressionToken("&&"))
            extend_list(result, node)
        return result

    def equality(self, nodes):
        return self.calc(nodes[0], nodes[1].data, nodes[2])

    def primary_expression(self, nodes):
        result = [ExpressionToken(nodes[0])]
        extend_list(result, nodes[1])
        result.append(ExpressionToken(nodes[2]))
        return result

    def calc(self, operand1, op, operand2):
        result = []
        extend_list(result, operand1)
        # 有三种情况：number+number number+obj obj+obj
        if op == 'equals':
            result.append(ExpressionToken("="))
        elif op == 'not_equals':
            result.append(ExpressionToken("!="))
        elif op == 'gt':
            result.append(ExpressionToken(">"))
        elif op == 'ge':
            result.append(ExpressionToken(">="))
        elif op == 'lt':
            result.append(ExpressionToken("<"))
        elif op == 'le':
            result.append(ExpressionToken("<="))
        elif op == 'add':
            result.append(ExpressionToken("+"))
        elif op == 'subtract':
            result.append(ExpressionToken("-"))
        elif op == 'multiply':
            result.append(ExpressionToken("*"))
        elif op == 'divide':
            result.append(ExpressionToken("/"))
        elif op == 'mod':
            result.append(ExpressionToken("%"))
        elif op == 'power':
            result.append(ExpressionToken("**"))
        elif op == 'divide_whole':
            result.append(ExpressionToken("//"))
        else:
            raise Exception(f'Unknown operator: {op}')
        extend_list(result, operand2)
        return result

    def relational(self, nodes):
        return self.calc(nodes[0], nodes[1].data, nodes[2])

    def additive(self, nodes):
        result = nodes[0]
        for i in range(2, len(nodes), 2):
            result = self.calc(result, nodes[i - 1].data, nodes[i])
        return result

    def multiplicative(self, nodes):
        result = nodes[0]
        for i in range(2, len(nodes), 2):
            result = self.calc(result, nodes[i - 1].data, nodes[i])
        return result

    def unary(self, nodes):
        result = []
        if nodes[0].data == 'negative':
            # 算术取负操作
            result.append(ExpressionToken('-'))
        elif nodes[0].data == 'not':
            # 逻辑取非操作
            result.append(ExpressionToken('!'))
        extend_list(result, nodes[1])
        return result

    def string(self, nodes):
        return ast.literal_eval(nodes[0])

    def number(self, nodes):
        return ExpressionToken(nodes[0])

    def true(self, nodes):
        return ExpressionToken('true')

    def false(self, nodes):
        return ExpressionToken('false')

    def variable(self, nodes):
        result = []
        for node in nodes:
            if isinstance(node, Token):
                result.append(ExpressionToken(node))
            else:
                extend_list(result, node)
        return result


def evaluate(expression: str, variables: dict, type_registry: DataTypeRegistry):
    tree = expr_parser.parse(expression)
    return ExpressionEvaluator(variables, type_registry).transform(tree)


def is_identifier(s):
    return bool(s and re.fullmatch(r'(_|[a-zA-Z]|[\u4e00-\u9fa5])\w*', s))


def validate_expression(expression: str):
    try:
        expr_parser.parse(expression)
        return True
    except Exception as e:
        return False


class Test():
    def __init__(self):
        self.a = 1
        self.b = 'abc'


def get_property_suggestions(expression: str, variable_defs: list[VariableDef], type_registry: DataTypeRegistry):
    try:
        interactive = expr_parser.parse_interactive(expression)
        type_tree = []
        current_data_type = None
        is_after_dot = False
        for t in interactive.exhaust_lexer():
            if t.type == 'DOT':
                is_after_dot = True
                continue
            elif current_data_type is None and t.type == 'IDENTIFIER':
                for variable_def in variable_defs:
                    if variable_def.name == t.value:
                        current_data_type = (type_registry.get_data_type(variable_def.type),
                                             type_registry.get_data_type(
                                                 variable_def.elementType) if variable_def.elementType else None)
                        break
                if current_data_type is None:
                    return []
            elif t.type == 'LSB':
                type_tree.append(current_data_type)
                current_data_type = None
            elif t.type == 'RSB':
                current_data_type = type_tree.pop()
                current_data_type = (current_data_type[1], None)
            elif t.type == 'IDENTIFIER' and is_after_dot:
                property_def: DataTypeProperty = current_data_type[0].get_property(t.value)
                current_data_type = (type_registry.get_data_type(property_def.data_type),
                                     type_registry.get_data_type(
                                         property_def.element_type) if property_def.element_type else None)
            else:
                current_data_type = None
            is_after_dot = False
        if is_after_dot:
            return current_data_type[0].properties
        else:
            return []
    except:
        return []


def tokenize_expression(expression: str):
    """
    将表达式转换为token列表，方便后续处理
    :param expression: 表达式字符串
    :return: token列表
    """
    tokens = ExpressionTokenizer().transform(expr_parser.parse(expression))
    if not isinstance(tokens, list):
        tokens = [tokens]
    return tokens


if __name__ == '__main__':
    for i in ['', '1', ' ', '_1', 'ab', '变量']:
        print(i, is_identifier(i))
    text = 'a+arr1["0"]+arr2[1].arr1[2]+t.a+9//2+10**2'
    # text = '收入 > "6000 " && 收入 < "10000"'
    print(text)
    tree = expr_parser.parse(text)
    variables = {
        "收入": "10000",
        "a": 3,
        "b": 1,
        "c00": 3,
        "d": 2,
        "e": 1,
        "f": 1,
        "t": Test(),
        "arr1": [1, 2, 3],
        "arr2": [
            {},
            {
                "arr1": [1, 2, 3]
            }
        ],
        "s1": 'hello'
    }
    print("tree: ", tree)
    print("pretty tree:\n", tree.pretty())
    all_tokens = tree.scan_values(lambda v: isinstance(v, Token))
    print("all_tokens: ", list(all_tokens))
    result = ExpressionEvaluator(variables, builtin_data_type_registry).transform(tree)
    print("eval result: ", type(result), result)
    print("token result: ", ExpressionTokenizer().transform(tree))

    interactive = expr_parser.parse_interactive('a.')
    for t in interactive.exhaust_lexer():
        print(t.type, t.value, t.start_pos)
    print(interactive.accepts())
    for t in expr_parser.terminals:
        print(t)

    print(get_property_suggestions("v1+v2[0].lower.", [
        VariableDef("v1", "text"),
        VariableDef("v2", "list", element_type='text')
    ], builtin_data_type_registry))
