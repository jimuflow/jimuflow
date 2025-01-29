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

import asyncio
import importlib
import json
import logging
import traceback
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Any

from jimuflow.common import app_base_path
from jimuflow.datatypes import DataTypeRegistry, builtin_data_type_registry
from jimuflow.definition import Package, VariableDirection, VariableDef, ComponentDef, PrimitiveComponentDef, \
    ControlFlowType, VariableUiInputType, ProcessDef, FlowNode, ErrorHandlingType
from jimuflow.definition.component_def import Platform, current_platform
from jimuflow.definition.variable_def import VariableUiInputValueType
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.common import ProcessVarScope, ProcessVar, is_empty
from jimuflow.runtime.expression import evaluate, validate_expression, is_identifier
from jimuflow.runtime.log import ConsoleLogger, Logger, LogLevel

logger = logging.getLogger(__name__)


class ControlFlow(Enum):
    NEXT = 0
    SKIP_ELSE_IF = 1
    BREAK = 2
    CONTINUE = 3
    RETURN = 4
    EXIT = 5


class ProcessListener(ABC):

    async def before_execute_component(self, component: "Component"):
        pass

    async def after_execute_component(self, component: "Component"):
        pass


class Component(ABC):
    """代表一个流程组件，是所有指令和流程的基类"""

    def __init__(self, engine: "ExecutionEngine", process: "Process", component_def: ComponentDef, parent: "Component",
                 flow_process: "Process", flow: list[FlowNode], node: FlowNode):
        """
        :param engine: 执行引擎
        :param process: 组件所在的流程
        :param component_def: 组件定义
        :param parent: 父组件
        :param flow_process: flow所在的流程，普通组件的flow_process就是定义组件的流程，流程组件的flow_process为当前流程
        :param flow: 指令包含的子流程节点
        """
        self.engine = engine
        self.process = process
        self.component_def = component_def
        self.parent = parent
        self.node = node
        self.flow: list["Component"] = []
        for node in flow:
            node_component_def = engine.get_component_def(node.process_def.package, node.component)
            node.component_def = node_component_def
            if isinstance(node_component_def, PrimitiveComponentDef):
                component_class = engine.load_component_class(node_component_def)
                component = component_class(flow_process, node_component_def, node, self)
                self.flow.append(component)
            elif isinstance(node_component_def, ProcessDef):
                sub_process = engine.create_sub_process(flow_process, node_component_def, node, self)
                self.flow.append(sub_process)
            else:
                raise Exception(gettext('Instruction or process {name} not found').format(name=node.component))

    def get_name(self):
        """获取组件名称"""
        return self.component_def.name

    async def execute_flow(self) -> ControlFlow:
        """执行组件包含的子流程节点"""
        skip_else_if = False
        for component in self.flow:
            if skip_else_if and (
                    component.component_def.control_flow_type == ControlFlowType.ELSE_IF
                    or component.component_def.control_flow_type == ControlFlowType.ELSE):
                continue
            skip_else_if = False
            control_flow = await component.invoke()
            if control_flow == ControlFlow.SKIP_ELSE_IF:
                skip_else_if = True
            elif (control_flow == ControlFlow.BREAK or control_flow == ControlFlow.CONTINUE
                  or control_flow == ControlFlow.RETURN or control_flow == ControlFlow.EXIT):
                return control_flow
        return ControlFlow.NEXT

    def top_process(self) -> "Process":
        """获取组件所属的顶级流程实例"""
        if self.process is None:
            return self
        top_process = self.process
        while top_process.process:
            top_process = top_process.process
        return top_process

    def owner_process_id(self):
        """获取组件所属的流程ID"""
        if self.process is None:
            return self.component_def.id(self.component_def.package)
        return self.process.component_def.id(self.top_process().component_def.package)

    def component_id(self):
        """获取组件ID"""
        return self.component_def.id(self.top_process().component_def.package)

    def log(self, message: str, *args, level: LogLevel = LogLevel.INFO, exception: Exception = None, **kwargs):
        """
        记录流程日志
        :param message: 日志格式化字符串
        :param args: 格式化字符串参数
        :param level: 日志级别
        :param exception: 异常信息
        :param kwargs: 格式化字符串关键字参数
        """
        if self.engine.logger.is_level_enabled(level):
            self.engine.logger.log(message.format(*args, **kwargs), level, self.owner_process_id(),
                                   self.component_id(), self.node.line_no if self.node else None, exception)

    def log_raw(self, message: str, level: LogLevel = LogLevel.INFO, exception: Exception = None):
        """
        记录流程日志
        :param message: 日志内容
        :param level: 日志级别
        :param exception: 异常信息
        """
        if self.engine.logger.is_level_enabled(level):
            self.engine.logger.log(message, level, self.owner_process_id(),
                                   self.component_id(), self.node.line_no if self.node else None, exception)

    def log_info(self, message: str, *args, exception: Exception = None, **kwargs):
        self.log(message, *args, level=LogLevel.INFO, exception=exception, **kwargs)

    def log_error(self, message: str, *args, exception: Exception = None, **kwargs):
        self.log(message, *args, level=LogLevel.ERROR, exception=exception, **kwargs)

    def log_warn(self, message: str, *args, exception: Exception = None, **kwargs):
        self.log(message, *args, level=LogLevel.WARN, exception=exception, **kwargs)

    def log_debug(self, message: str, *args, exception: Exception = None, **kwargs):
        self.log(message, *args, level=LogLevel.DEBUG, exception=exception, **kwargs)

    def evaluate_expression_in_process(self, expression: str):
        """
        使用当前流程的变量来计算表达式
        :param expression: 表达式
        :return: 表达式计算结果
        """
        return self.process.evaluate_expression(expression)

    def read_input(self, input_name: str):
        """
        读取输入变量
        :param input_name: 变量名称
        """
        value = self.node.input(input_name)
        if value == '' or value is None:
            return None
        var_def = self.component_def.get_input_variable(input_name)
        if var_def.ui_config.input_type == VariableUiInputType.EXPRESSION or var_def.ui_config.input_value_type == VariableUiInputValueType.EXPRESSION:
            return self.evaluate_expression_in_process(value)
        else:
            return value

    async def write_output(self, output_name: str, value: Any, value_destroyer=None):
        """
        保存输出变量
        :param output_name: 输出变量名称
        :param value: 变量值
        :param value_destroyer: 变量清理函数，接收变量值作为参数，删除变量时将调用该函数释放变量相关的资源
        """
        out_var_name = self.node.output(output_name)
        await self.process.update_variable(out_var_name, value, value_destroyer)
        if self.engine.logger.is_level_enabled(LogLevel.DEBUG):
            value_str = str(value)
            if len(value_str) > 100:
                value_str = value_str[:100] + '...'
            self.log_debug(gettext('Write output {out_var_name}: {out_var_value}'), out_var_name=out_var_name,
                           out_var_value=value_str)

    @abstractmethod
    async def execute(self) -> ControlFlow:
        pass

    async def invoke(self) -> ControlFlow:
        try:
            retries = 0
            while True:
                try:
                    await self.before_execute()
                    result = await self.execute()
                    self.log_debug(gettext("Execution successful"))
                    return result
                except ProcessStoppedException:
                    return ControlFlow.EXIT
                except Exception as e:
                    logger.exception("An error occurred while executing component %s", self.component_id())
                    self.log_error(gettext("Execution error"), exception=e)
                    if self.component_def.supports_error_handling and self.node:
                        if self.node.error_handling_type == ErrorHandlingType.IGNORE:
                            for k, v in self.node.outputs_on_error.items():
                                await self.write_output(k, self.evaluate_expression_in_process(v))
                            self.log_error(gettext('Ignore error and continue execution'), exception=e)
                            return ControlFlow.NEXT
                        elif self.node.error_handling_type == ErrorHandlingType.RETRY:
                            if retries < self.node.max_retries:
                                retries += 1
                                self.log_error(gettext('Wait for {} seconds and retry for the {} time'),
                                               self.node.retry_interval, retries, exception=e)
                                await asyncio.sleep(self.node.retry_interval)
                                continue
                    raise
        finally:
            await self.after_execute()

    @abstractmethod
    async def before_execute(self):
        pass

    @abstractmethod
    async def after_execute(self):
        pass

    @classmethod
    def validate(cls, engine: "ExecutionEngine", component_def: ComponentDef, flow_node: FlowNode | None) -> list[str]:
        return []

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        pass


class PrimitiveComponent(Component):
    """所有原子指令的基类"""

    def __init__(self, process: "Process", component_def: PrimitiveComponentDef, node: FlowNode, parent: Component):
        super().__init__(process.engine, process, component_def, parent, process, node.flow, node)
        self.on_init()

    def on_init(self):
        pass

    def get_output_variable(self, output_name: str):
        return self.process.get_variable(self.node.output(output_name))

    @classmethod
    def validate(cls, engine: "ExecutionEngine", component_def: ComponentDef, flow_node: FlowNode | None) -> list[str]:
        errors = []
        comp_name = gettext(component_def.display_name)
        for v in component_def.variables:
            if not cls._is_variable_dependency_satisfied(component_def, flow_node, v):
                continue
            if v.direction == VariableDirection.IN:
                if v.ui_config.required and is_empty(flow_node.input(v.name)):
                    errors.append(gettext('The input parameter {var_name} of {comp_name} is not specified.').format(
                        var_name=v.name, comp_name=comp_name))
                elif not is_empty(flow_node.input(
                        v.name)) and v.ui_config.input_type == VariableUiInputType.EXPRESSION and not validate_expression(
                    flow_node.input(v.name)):
                    errors.append(gettext(
                        'The expression format of the input parameter {var_name} of {comp_name} is incorrect.').format(
                        var_name=v.name, comp_name=comp_name))
            elif v.direction == VariableDirection.OUT:
                if v.ui_config.required and is_empty(v.name):
                    errors.append(gettext('The output parameter {var_name} of {comp_name} is not specified.').format(
                        var_name=v.name, comp_name=comp_name))
                elif not is_empty(flow_node.output(v.name)) and not is_identifier(flow_node.output(v.name)):
                    errors.append(gettext(
                        "The format of the output parameter {var_name} of {comp_name} is incorrect.").format(
                        var_name=v.name, comp_name=comp_name))
        return errors

    @classmethod
    def _is_variable_dependency_satisfied(cls, component_def: ComponentDef, flow_node: FlowNode,
                                          var_def: VariableDef) -> bool:
        if not var_def.ui_config.depends_on.is_valid():
            return True
        dependency_var_def = component_def.get_variable(var_def.ui_config.depends_on.variable_name)
        # 检查上级依赖是否满足
        if not cls._is_variable_dependency_satisfied(component_def, flow_node, dependency_var_def):
            return False
        # 检查当前依赖是否满足
        dependency_var_value = flow_node.input(
            dependency_var_def.name) if dependency_var_def.direction == VariableDirection.IN else flow_node.output(
            dependency_var_def.name)
        return var_def.ui_config.depends_on.is_satisfied(dependency_var_value)

    async def execute(self) -> ControlFlow:
        return await self.execute_flow()

    async def before_execute(self):
        await self.process.before_execute_component(self)

    async def after_execute(self):
        await self.process.after_execute_component(self)

    def get_resource_path(self, name):
        return self.process.component_def.package.path / "resources" / name


class ProcessStoppedException(Exception):
    pass


class Process(Component):
    def __init__(self, engine: "ExecutionEngine", process: "Process", process_def: ProcessDef,
                 parent: "Component" = None, inputs: dict = None, node: FlowNode = None):
        """
        :param engine: 执行引擎
        :param process: 父流程，主流程为None
        :param process_def: 当前流程定义
        :param parent: 调用该流程的父组件，主流程为None
        :param inputs: 输入变量
        :param node: 调用该流程的节点，主流程为None
        """
        super().__init__(engine, process, process_def, parent, self, process_def.flow, node)
        self.inputs = inputs or {}
        self._variables = {}
        self._variable_destroyers = {}
        self.stopped = False
        self._process_vars = {}
        self._process_var_cleaners = {}
        self._process_listeners: list[ProcessListener] = []

    @property
    def variables(self):
        return self._variables

    async def _init_variables(self, inputs: dict):
        await self.clear_variables()
        for var_def in self.component_def.variables:
            self._variables[var_def.name] = inputs.get(var_def.name) if inputs else None

    def evaluate_expression(self, expression: str):
        return evaluate(expression, self._variables, self.engine.type_registry)

    async def clear_variables(self):
        for name in list(self._variables.keys()):
            await self.remove_variable(name)
        self._variables.clear()
        self._variable_destroyers.clear()

    async def remove_variable(self, name: str, destroy=True):
        var_def = self.component_def.get_variable(name)
        value = self._variables.pop(name, None)
        destroyer = self._variable_destroyers.pop(name, None)
        try:
            if destroy and value and destroyer and var_def.direction != VariableDirection.IN:
                destroyer_result = destroyer(value)
                if asyncio.iscoroutine(destroyer_result):
                    await destroyer_result
        except Exception as e:
            self.log_warn(gettext('Error clearing user variable {name}'), name=name, exception=e)
            traceback.print_exc()
        if not destroy:
            return value, destroyer

    async def remove_variable_by_value(self, value: Any):
        if value is None:
            return
        for k, v in self._variables.items():
            if v is value:
                return await self.remove_variable(k, True)

    async def update_variable(self, name: str, value: Any, value_destroyer=None):
        await self.remove_variable(name)
        self._variables[name] = value
        if value_destroyer:
            self._variable_destroyers[name] = value_destroyer

    def get_variable(self, name: str):
        return self._variables.get(name, None)

    def get_variable_destroyer(self, name: str):
        return self._variable_destroyers.get(name, None)

    def get_outputs(self):
        return {k.name: self.get_variable(k.name) for k in self.component_def.variables if
                k.direction == VariableDirection.OUT}

    async def before_execute(self):
        await self.before_execute_component(self)

    async def after_execute(self):
        await self.after_execute_component(self)

    async def execute(self) -> ControlFlow:
        try:
            # 初始化流程的所有变量
            if self.process is None:
                await self._init_variables(self.inputs)
            else:
                await self._init_variables(
                    {k: self.read_input(k) for k, v in self.node.inputs.items()})
            # 执行流程步骤
            control_flow = await self.execute_flow()
            # 保存子流程的输出变量
            if self.process is not None:
                for v in self.component_def.variables:
                    if v.direction == VariableDirection.OUT:
                        value, destroyer = await self.remove_variable(v.name, False)
                        await self.write_output(v.name, value, destroyer)
        finally:
            # 清理用户变量
            await self.clear_variables()
            # 清理流程本地变量
            await self.clear_process_vars()
        return control_flow

    async def invoke(self) -> ControlFlow:
        if self.process is None:
            self.log_info(gettext('Start execution'))
        result = await super().invoke()
        if self.process is None:
            self.log_info(gettext('Execution completed'))
        return result

    def stop(self):
        self.stopped = True

    def is_stopped(self):
        if self.stopped:
            return True
        if self.process and self.process.is_stopped():
            return True
        return False

    @classmethod
    def validate(cls, engine: "ExecutionEngine", component_def: ComponentDef, flow_node: FlowNode | None) -> list[str]:
        if flow_node is not None:
            # 子流程只需要校验输入输出变量
            errors = []
            for v in component_def.variables:
                if v.direction == VariableDirection.IN:
                    if not flow_node.inputs.get(v.name):
                        var_display_name = gettext(v.ui_config.label or v.name)
                        errors.append(gettext(
                            'The input parameter {var_name} for subprocess {process_name} is not specified').format(
                            process_name=component_def.name, var_name=var_display_name))
                elif v.direction == VariableDirection.OUT:
                    if not flow_node.outputs.get(v.name):
                        var_display_name = gettext(v.ui_config.label or v.name)
                        errors.append(gettext(
                            'The output parameter {var_name} for subprocess {process_name} is not specified').format(
                            process_name=component_def.name, var_name=var_display_name))
            return errors
        else:
            # 主流程只需要校验flow节点
            return Process.validate_flow(engine, component_def, component_def.flow, 0)[0]

    @staticmethod
    def validate_flow(engine: "ExecutionEngine", process_def: ProcessDef, flow: list[FlowNode], prev_line_no: int) -> (
            list[tuple[int, list[str]]], int):
        errors = []
        line_no = prev_line_no
        for i in range(len(flow)):
            flow_node = flow[i]
            flow_node.errors.clear()
            line_no = line_no + 1
            component_def = engine.get_component_def(process_def.package, flow_node.component)
            if component_def is None:
                flow_node.errors.append(
                    gettext('Instruction or process {name} not found').format(name=flow_node.component))
            else:
                flow_node.component_def = component_def
                prev_flow_node = flow[i - 1] if i > 0 else None
                prev_component_def = engine.get_component_def(process_def.package,
                                                              prev_flow_node.component) if prev_flow_node else None
                if isinstance(component_def, ProcessDef):
                    comp_name = gettext('Process {name}').format(name=component_def.name)
                else:
                    comp_name = gettext(component_def.display_name)
                # 检查语句顺序
                if (component_def.control_flow_type == ControlFlowType.ELSE_IF
                        or component_def.control_flow_type == ControlFlowType.ELSE):
                    if prev_flow_node is None or prev_component_def is None or (
                            prev_component_def.control_flow_type != ControlFlowType.IF
                            and prev_component_def.control_flow_type != ControlFlowType.ELSE_IF):
                        flow_node.errors.append(
                            gettext('{name} must immediately follow the If or Else If instruction').format(
                                name=comp_name))
                elif (prev_flow_node is not None and prev_component_def is not None and
                      (prev_component_def.control_flow_type == ControlFlowType.BREAK
                       or prev_component_def.control_flow_type == ControlFlowType.CONTINUE
                       or prev_component_def.control_flow_type == ControlFlowType.RETURN
                       or prev_component_def.control_flow_type == ControlFlowType.EXIT)):
                    flow_node.errors.append(
                        gettext('{name} cannot follow a Break, Continue, Return, or Exit instruction').format(
                            name=comp_name))
                # 检查语句嵌套关系
                if (component_def.control_flow_type == ControlFlowType.IF
                        or component_def.control_flow_type == ControlFlowType.ELSE_IF
                        or component_def.control_flow_type == ControlFlowType.ELSE
                        or component_def.control_flow_type == ControlFlowType.LOOP):
                    if len(flow_node.flow) == 0:
                        flow_node.errors.append(gettext('{name} has no sub instructions').format(name=comp_name))
                elif component_def.control_flow_type != ControlFlowType.INVOKE:
                    if len(flow_node.flow) > 0:
                        flow_node.errors.append(
                            gettext('{name} should not have any sub instructions').format(name=comp_name))
                if component_def.control_flow_type == ControlFlowType.BREAK or component_def.control_flow_type == ControlFlowType.CONTINUE:
                    parent_node = flow_node.parent
                    while parent_node:
                        parent_component_def = engine.get_component_def(process_def.package, parent_node.component)
                        if parent_component_def.control_flow_type == ControlFlowType.LOOP:
                            break
                        parent_node = parent_node.parent
                    else:
                        flow_node.errors.append(
                            gettext('{name} must be used in conjunction with Loop instruction').format(name=comp_name))
                # 检查组件自身配置
                if isinstance(component_def, ProcessDef):
                    flow_node.errors.extend(Process.validate(engine, component_def, flow_node))
                else:
                    component_class = engine.load_component_class(component_def)
                    flow_node.errors.extend(component_class.validate(engine, component_def, flow_node))
            if len(flow_node.errors) > 0:
                errors.append((line_no, flow_node.errors))
            if len(flow_node.flow) > 0:
                sub_flow_errors, line_no = Process.validate_flow(engine, process_def, flow_node.flow, line_no)
                errors.extend(sub_flow_errors)
        return errors, line_no

    def get_process_var(self, var: ProcessVar, scope: ProcessVarScope = ProcessVarScope.LOCAL):
        if scope == ProcessVarScope.LOCAL or self.process is None:
            return self._process_vars.get(var, None)
        else:
            return self.process.get_process_var(var, scope)

    async def set_process_var(self, var: ProcessVar, value, cleaner, scope: ProcessVarScope = ProcessVarScope.LOCAL):
        if scope == ProcessVarScope.LOCAL or self.process is None:
            await self.remove_process_var(var)
            self._process_vars[var] = value
            if cleaner:
                self._process_var_cleaners[var] = cleaner
        else:
            await self.process.set_process_var(var, value, cleaner, scope)

    async def remove_process_var(self, var: ProcessVar, scope: ProcessVarScope = ProcessVarScope.LOCAL):
        if scope == ProcessVarScope.LOCAL or self.process is None:
            value = self._process_vars.pop(var, None)
            cleaner = self._process_var_cleaners.pop(var, None)
            try:
                if value and cleaner:
                    result = cleaner(value)
                    if asyncio.iscoroutine(result):
                        await result
            except Exception as e:
                self.log_warn(gettext('Error clearing process local variable {}'), var.name, exception=e)
                traceback.print_exc()
        else:
            await self.process.remove_process_var(var, scope)

    async def clear_process_vars(self):
        for var in list(self._process_vars.keys()):
            await self.remove_process_var(var)

    def add_process_listener(self, listener: ProcessListener):
        self._process_listeners.append(listener)

    def remove_process_listener(self, listener: ProcessListener):
        self._process_listeners.remove(listener)

    async def before_execute_component(self, component: Component):
        if self.is_stopped():
            raise ProcessStoppedException()
        if self.process:
            await self.process.before_execute_component(component)
        else:
            for listener in self._process_listeners:
                await listener.before_execute_component(component)
        if self.is_stopped():
            raise ProcessStoppedException()

    async def after_execute_component(self, component: Component):
        if self.is_stopped():
            raise ProcessStoppedException()
        if self.process:
            await self.process.after_execute_component(component)
        else:
            for listener in self._process_listeners:
                await listener.after_execute_component(component)
        if self.is_stopped():
            raise ProcessStoppedException()


class ExecutionEngine:
    def __init__(self, package_paths: list[str]):
        self.logger = ConsoleLogger()
        self.packages: list[Package] = []
        self.package_paths = []
        self.package_paths.append(str(app_base_path / "packages"))
        self.package_paths.extend(package_paths)
        self.type_registry = DataTypeRegistry()
        self.type_registry.copy_from_registry(builtin_data_type_registry)
        self.scan_packages(self.package_paths)

    def scan_packages(self, package_paths: list[str]):
        for p in package_paths:
            scan_path = Path(p)
            for package_path in scan_path.iterdir():
                if package_path.is_dir():
                    package_json_file = package_path / 'jimuflow.json'
                    if package_json_file.exists():
                        package = self.load_package(package_path)
                        self.packages.append(package)

    def load_package(self, package_path: Path) -> Package:
        package = Package()
        package.load(package_path)
        for file in package_path.rglob('*.comp.json'):
            component_def = PrimitiveComponentDef(package)
            component_def.load_from_file(file)
            package.components.append(component_def)
        for file in package_path.rglob('*.process.json'):
            process_def = ProcessDef(package)
            process_def.load_from_file(file)
            package.components.append(process_def)
        for file in package_path.rglob('*.type.json'):
            self.register_type_from_file(file)
        return package

    def register_type_from_file(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            registrar = json_data['registrar']
            idx = registrar.rindex('.')
            registrar_module_name = registrar[:idx]
            registrar_class_name = registrar[idx + 1:]
            registrar_module = __import__(registrar_module_name, fromlist=[registrar_class_name])
            registrar_class = getattr(registrar_module, registrar_class_name)
            registrar_class.register(self.type_registry)

    def get_available_component_defs(self, source_package: Package) -> list[ComponentDef]:
        if source_package and source_package not in self.packages:
            packages = []
            packages.extend(self.packages)
            packages.append(source_package)
        else:
            packages = self.packages
        return [component for package in packages for component in package.components]

    def get_component_def(self, source_package: Package, component_def_id: str) -> ComponentDef:
        if ':' in component_def_id:
            package_namespace, package_name, component_name = component_def_id.split(':')
        else:
            package_namespace = source_package.namespace
            package_name = source_package.name
            component_name = component_def_id
        if source_package and source_package not in self.packages:
            packages = []
            packages.extend(self.packages)
            packages.append(source_package)
        else:
            packages = self.packages
        for package in packages:
            if package.namespace == package_namespace and package.name == package_name:
                for component in package.components:
                    if component.name == component_name:
                        return component

    def get_component_by_class(self, component_class) -> ComponentDef:
        for package in self.packages:
            for component in package.components:
                module_name = component_class.__module__
                class_name = component_class.__name__
                if component.class_name == class_name and (
                        component.module_name == module_name or module_name.startswith(component.module_name + ".")):
                    return component

    def create_process(self, process_def: ProcessDef, inputs: dict):
        return Process(self, None, process_def, None, inputs)

    def create_sub_process(self, process: "Process", process_def: ProcessDef, node: FlowNode, parent: "Component"):
        return Process(self, process, process_def, parent, node=node)

    async def run_app(self, app_path: Path, process_name: str = None, inputs: dict = None):
        if inputs is None:
            inputs = {}
        app_package = self.load_package(app_path)
        if not process_name:
            process_name = app_package.main_process
        if not process_name:
            raise Exception("No main process defined in app package")
        process_def = self.get_component_def(app_package, process_name)
        if not process_def:
            raise Exception("No process named {} defined in app package".format(process_name))
        process = self.create_process(process_def, inputs)
        await process.execute()

    def set_logger(self, logger: Logger):
        self.logger = logger

    def load_component_class(self, component_def: ComponentDef) -> type[Component]:
        component_module = importlib.import_module(component_def.module_name)
        component_class = getattr(component_module, component_def.class_name)
        return component_class

    def get_process_platforms(self, process_def: ProcessDef):
        supported_platforms = {Platform.windows, Platform.linux, Platform.macos}
        flow_nodes = []
        flow_nodes.extend(process_def.flow)
        while supported_platforms and flow_nodes:
            flow_node = flow_nodes.pop(0)
            if not flow_node.component_def:
                flow_node.component_def = self.get_component_def(process_def.package, flow_node.component)
            if isinstance(flow_node.component_def, PrimitiveComponentDef):
                if flow_node.component_def.platforms:
                    supported_platforms = supported_platforms & flow_node.component_def.platforms
            elif isinstance(flow_node.component_def, ProcessDef):
                supported_platforms = supported_platforms & self.get_process_platforms(flow_node.component_def)
            else:
                return set()
            flow_nodes.extend(flow_node.flow)
        return supported_platforms

    def is_process_platform_supported(self, process_def: ProcessDef) -> bool:
        supported_platforms = self.get_process_platforms(process_def)
        return current_platform in supported_platforms, supported_platforms
