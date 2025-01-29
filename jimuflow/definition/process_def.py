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

import json
from enum import Enum

from .component_def import ComponentDef, ControlFlowType
from .package import Package


class ErrorHandlingType(Enum):
    """错误处理类型"""
    IGNORE = "IGNORE"
    RETRY = "RETRY"
    STOP = "STOP"


next_flow_node_id = 0


def get_next_flow_node_id():
    global next_flow_node_id
    next_flow_node_id += 1
    return next_flow_node_id


class FlowNode:
    def __init__(self, process_def: "ProcessDef", parent: "FlowNode" = None):
        self.process_def = process_def
        self.parent = parent
        self.component = ""
        self.component_def: ComponentDef | None = None
        self.inputs = {}
        self.outputs = {}
        self.flow = []
        self.breakpoint = False
        self.errors = []
        self.error_handling_type = ErrorHandlingType.STOP
        self.max_retries = 0
        self.retry_interval = 0
        self.outputs_on_error = {}
        self.line_no = 0
        self._id = get_next_flow_node_id()

    @property
    def id(self):
        return self._id

    def load(self, json_data: dict):
        self.component = json_data['component']
        if 'inputs' in json_data:
            self.inputs = json_data['inputs']
        if 'outputs' in json_data:
            self.outputs = json_data['outputs']
        if 'flow' in json_data:
            for item in json_data['flow']:
                child_node = FlowNode(self.process_def, self)
                child_node.load(item)
                self.flow.append(child_node)
        if 'errorHandlingType' in json_data:
            self.error_handling_type = ErrorHandlingType(json_data['errorHandlingType'])
        if 'maxRetries' in json_data:
            self.max_retries = json_data['maxRetries']
        if 'retryInterval' in json_data:
            self.retry_interval = json_data['retryInterval']
        if 'outputsOnError' in json_data:
            self.outputs_on_error = json_data['outputsOnError']
        if 'lineNo' in json_data:
            self.line_no = json_data['lineNo']

    def to_json(self, with_flow=True) -> dict:
        result = {
            "component": self.component,
        }
        if len(self.inputs) > 0:
            result['inputs'] = self.inputs
        if len(self.outputs) > 0:
            result['outputs'] = self.outputs
        if self.error_handling_type == ErrorHandlingType.RETRY:
            result['errorHandlingType'] = self.error_handling_type.value
            result['maxRetries'] = self.max_retries
            result['retryInterval'] = self.retry_interval
        elif self.error_handling_type == ErrorHandlingType.IGNORE:
            result['errorHandlingType'] = self.error_handling_type.value
            result['outputsOnError'] = self.outputs_on_error
        if self.line_no > 0:
            result['lineNo'] = self.line_no
        if with_flow and len(self.flow) > 0:
            result['flow'] = [child_node.to_json() for child_node in self.flow]
        return result

    def input(self, name):
        var_def = self.component_def.get_input_variable(name)
        if not var_def:
            raise Exception(f"{name} is not defined in {self.component_def.name}")
        value = self.inputs.get(name)
        return var_def.defaultValue if value == '' or value is None else value

    def output(self, name):
        var_def = self.component_def.get_output_variable(name)
        if not var_def:
            raise Exception(f"{name} is not defined in {self.component_def.name}")
        return self.outputs.get(name)


def snapshot_flow_node(flow_node: FlowNode) -> dict:
    result = {
        "component": flow_node.component,
        "inputs": flow_node.inputs,
        "outputs": flow_node.outputs
    }
    if flow_node.error_handling_type == ErrorHandlingType.RETRY:
        result['error_handling_type'] = flow_node.error_handling_type.value
        result['max_retries'] = flow_node.max_retries
        result['retry_interval'] = flow_node.retry_interval
    elif flow_node.error_handling_type == ErrorHandlingType.IGNORE:
        result['error_handling_type'] = flow_node.error_handling_type.value
        result['outputs_on_error'] = flow_node.outputs_on_error
    return result


def snapshot_flow_node_tree(flow_node: FlowNode) -> dict:
    result = snapshot_flow_node(flow_node)
    if flow_node.flow:
        result['flow'] = [snapshot_flow_node_tree(node) for node in flow_node.flow]
    return result


class ProcessDef(ComponentDef):
    def __init__(self, package: Package):
        super().__init__(package)
        self.control_flow_type = ControlFlowType.INVOKE
        self.flow: list[FlowNode] = []
        self.supports_error_handling = True

    def load(self, json_data: dict):
        super().load(json_data)
        self.flow = []
        if 'flow' in json_data:
            for item in json_data['flow']:
                child_node = FlowNode(self)
                child_node.load(item)
                self.flow.append(child_node)

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "variables": [var_def.to_json() for var_def in self.variables],
            "flow": [child_node.to_json() for child_node in self.flow]
        }

    def save_to_file(self, file):
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(self.to_json(), f, ensure_ascii=False, indent=2)

    def reload(self):
        with open(self.path, 'r', encoding='utf-8') as f:
            self.load(json.load(f))

    def get_node_by_line_no(self, line_no: int) -> FlowNode:
        """根据行号获取节点"""
        stack = []
        stack.extend(self.flow)
        while len(stack) > 0:
            node = stack.pop()
            if node.line_no == line_no:
                return node
            stack.extend(node.flow)
        return None

    def clone(self):
        json_def = self.to_json()
        cloned = ProcessDef(self.package)
        cloned.load(json_def)
        return cloned

    def __eq__(self, other):
        if not super().__eq__(other):
            return False
        return self._is_flow_equal(self.flow, other.flow)

    def _is_flow_equal(self, flow1: list[FlowNode], flow2: list[FlowNode]):
        if len(flow1) != len(flow2):
            return False
        for i in range(len(flow1)):
            node1 = flow1[i]
            node2 = flow2[i]
            if (node1.component != node2.component or node1.error_handling_type != node2.error_handling_type
                    or node1.max_retries != node2.max_retries or node1.retry_interval != node2.retry_interval
                    or node1.inputs != node2.inputs or node1.outputs != node2.outputs
                    or node1.outputs_on_error != node2.outputs_on_error
                    or not self._is_flow_equal(node1.flow, node2.flow)):
                return False
        return True
