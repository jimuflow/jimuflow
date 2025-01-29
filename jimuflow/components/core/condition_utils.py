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

from jimuflow.locales.i18n import gettext

op_i18n = {
    '==': gettext('equal to'),
    '!=': gettext('not equal to'),
    '>': gettext('greater than'),
    '<': gettext('less than'),
    '>=': gettext('greater than or equal to'),
    '<=': gettext('less than or equal to'),
    'contains': gettext('contains'),
    'not_contains': gettext('not contains'),
    'is_empty': gettext('is empty'),
    'not_empty': gettext('is not empty'),
    'starts_with': gettext('starts with'),
    'not_starts_with': gettext('not starts with'),
    'ends_with': gettext('ends with'),
    'not_ends_with': gettext('not ends with'),
}


def is_binary_op(op: str):
    return op not in ["is_empty", "not_empty"]


def convert_to_best_type(value):
    if isinstance(value, str):
        try:
            return int(value)
        except:
            pass
        try:
            return float(value)
        except:
            pass
    return value


def convert_to_save_type(operand1, operand2):
    best_operand1 = convert_to_best_type(operand1)
    best_operand2 = convert_to_best_type(operand2)
    if isinstance(best_operand1, (int, float)) and isinstance(best_operand2, (int, float)):
        return best_operand1, best_operand2
    else:
        return operand1, operand2


def evaluate_condition(operand1, op, operand2) -> bool:
    operand1, operand2 = convert_to_save_type(operand1, operand2)
    if op == '==':
        return operand1 == operand2
    elif op == '!=':
        return operand1 != operand2
    elif op == '>':
        return operand1 > operand2
    elif op == '<':
        return operand1 < operand2
    elif op == '>=':
        return operand1 >= operand2
    elif op == '<=':
        return operand1 <= operand2
    elif op == 'contains':
        return operand2 in operand1
    elif op == 'not_contains':
        return operand2 not in operand1
    elif op == 'is_empty':
        return operand1 is None or (isinstance(operand1, str) and len(operand1) == 0)
    elif op == 'not_empty':
        return isinstance(operand1, str) and len(operand1) > 0
    elif op == 'starts_with':
        return operand1 is not None and operand2 is not None and len(operand1) > 0 and len(
            operand2) > 0 and operand1.startswith(operand2)
    elif op == 'not_starts_with':
        return not (operand1 and operand2 and operand1.startswith(operand2))
    elif op == 'ends_with':
        return operand1 is not None and operand2 is not None and len(operand1) > 0 and len(
            operand2) > 0 and operand1.endswith(operand2)
    elif op == 'not_ends_with':
        return not (operand1 and operand2 and operand1.endswith(operand2))
    else:
        raise Exception(gettext('Unsupported operator: {op}').format(op=op_i18n[op]))
