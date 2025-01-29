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

def escape_xpath_string(value: str):
    has_single_quote = value.find("'") != -1
    has_double_quote = value.find('"') != -1
    if not has_single_quote:
        return '\'' + value + '\''
    elif has_single_quote and not has_double_quote:
        return '"' + value + '"'
    result = []
    state = 'normal'
    part = []
    for i in range(len(value)):
        ch = value[i]
        if state == 'normal':
            if ch == '\'':
                part.append(ch)
                state = 'single_quote'
            elif ch == '"':
                part.append(ch)
                state = 'double_quote'
            else:
                part.append(ch)
        elif state == 'single_quote':
            if ch == '"':
                if part:
                    result.append('"' + ''.join(part) + '"')
                    part.clear()
                part.append(ch)
                state = 'double_quote'
            else:
                part.append(ch)
        elif state == 'double_quote':
            if ch == '\'':
                if part:
                    result.append('\'' + ''.join(part) + '\'')
                    part.clear()
                part.append(ch)
                state = 'single_quote'
            else:
                part.append(ch)
    if part:
        if state == 'single_quote':
            result.append('"' + ''.join(part) + '"')
        else:
            result.append('\'' + ''.join(part) + '\'')
    return 'concat(' + ','.join(result) + ')'


def build_node_xpath(node):
    enabled_predicates = [pred for pred in node['predicates'] if pred[3]]
    if len(enabled_predicates) == 0:
        return node['element']
    elif len(enabled_predicates) == 1 and enabled_predicates[0][0] == 'position()' and enabled_predicates[0][1] == '=':
        return node['element'] + '[' + enabled_predicates[0][2] + ']'
    else:
        xpath = node['element'] + '['
        for i in range(len(enabled_predicates)):
            if i > 0:
                xpath = xpath + ' and '
            left_operand = enabled_predicates[i][0]
            if not left_operand.endswith(')'):
                left_operand = '@' + left_operand
            right_operand = escape_xpath_string(enabled_predicates[i][2])
            op = enabled_predicates[i][1]
            if op == 'contains':
                xpath = xpath + 'contains(' + left_operand + ', ' + right_operand + ')'
            elif op == 'not_contains':
                xpath = xpath + 'not(contains(' + left_operand + ', ' + right_operand + '))'
            elif op == 'starts_with':
                xpath = xpath + 'starts-with(' + left_operand + ', ' + right_operand + ')'
            elif op == 'not_starts_with':
                xpath = xpath + 'not(starts-with(' + left_operand + ', ' + right_operand + '))'
            elif op == 'ends_with':
                xpath = xpath + 'ends-with(' + left_operand + ', ' + right_operand + ')'
            elif op == 'not_ends_with':
                xpath = xpath + 'not(ends-with(' + left_operand + ', ' + right_operand + '))'
            elif op == 'matches':
                xpath = xpath + 'matches(' + left_operand + ', ' + right_operand + ')'
            else:
                xpath = xpath + left_operand + op + right_operand
        xpath = xpath + ']'
        return xpath


def build_xpath(path):
    xpath = ''
    for i in range(len(path)):
        node = path[i]
        if not node['enabled']:
            continue
        prev_node = path[i - 1] if i > 0 else None
        if i == 0 or prev_node['enabled']:
            xpath = xpath + '/'
        else:
            xpath = xpath + '//'
        xpath = xpath + build_node_xpath(node)
    return xpath


def parse_xpath(xpath: str):
    steps = []
    state = 'normal'
    step = []
    for i in range(len(xpath)):
        char = xpath[i]
        if state == 'normal':
            if char == '/':
                if step:
                    step_str = ''.join(step).strip()
                    if step_str:
                        steps.append(step_str)
                    step.clear()
                step.append(char)
                state = 'delimiter'
            elif char == '\'':
                step.append(char)
                state = 'single_quote'
            elif char == '"':
                step.append(char)
                state = 'double_quote'
            else:
                step.append(char)
        elif state == 'delimiter':
            if char == '\'':
                step.append(char)
                state = 'single_quote'
            elif char == '"':
                step.append(char)
                state = 'double_quote'
            else:
                step.append(char)
                state = 'normal'
        elif state == 'single_quote':
            if char == '\'':
                step.append(char)
                state = 'normal'
            else:
                step.append(char)
        elif state == 'double_quote':
            if char == '"':
                step.append(char)
                state = 'normal'
            else:
                step.append(char)
    if step:
        step_str = ''.join(step).strip()
        if step_str:
            steps.append(step_str)
    return steps


def get_relative_xpath(source_xpath, target_xpath):
    # example 1
    # source_xpath: /body/div[1]/div[1]
    # target_xpath: /body/div[1]/div[1]/div/span
    # result: div/span
    # example 2
    # source_xpath: /body/div[1]/div[2]
    # target_xpath: /body/div[1]/div[1]/div/span
    # result: ../div[1]/div/span
    if not source_xpath or not target_xpath:
        return ''
    if source_xpath == target_xpath:
        return '.'
    source_xpath_steps = source_xpath.split('/')
    target_xpath_steps = target_xpath.split('/')
    common_prefix_length = 0
    for i in range(min(len(source_xpath_steps), len(target_xpath_steps))):
        if source_xpath_steps[i] != target_xpath_steps[i]:
            break
        else:
            common_prefix_length += 1
    return '../' * (len(source_xpath_steps) - common_prefix_length) + '/'.join(
        target_xpath_steps[common_prefix_length:])


def get_full_element_xpath(element_path: list):
    full_xpath = []
    for node in element_path:
        full_xpath.append('/')
        full_xpath.append(node['element'])
        position_pred = next((pred for pred in node['predicates'] if pred[0] == 'position()'), None)
        if position_pred:
            full_xpath.append('[' + position_pred[2] + ']')
    return ''.join(full_xpath)
