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

import os
import random
import shutil
import tempfile
from pathlib import Path

from jimuflow.common.uri_utils import WEB_ELEMENT_URI_PREFIX, WINDOW_ELEMENT_URI_PREFIX
from jimuflow.components.core.os_utils import is_macos, is_windows, is_linux
from jimuflow.definition import ProcessDef, FlowNode, Package, PrimitiveComponentDef, VariableDef
from jimuflow.runtime.execution_engine import Process, ExecutionEngine, PrimitiveComponent, Component, ControlFlow

engine = ExecutionEngine([])


def create_component(comp_class, result_var_name='r', result_var_type='any') -> PrimitiveComponent:
    package = Package()
    package.name = "test"
    package.namespace = "test"
    package.version = "1.0.0"
    package.path = Path(tempfile.mkdtemp(suffix="jimuflow_test_package"))
    process_def = ProcessDef(package)
    process = Process(engine, None, process_def, None, {})
    process.component_def.variables.append(VariableDef(result_var_name, result_var_type))
    flow_node = FlowNode(process_def)
    comp_def = engine.get_component_by_class(comp_class)
    flow_node.component_def = comp_def
    return comp_class(process, comp_def, flow_node, None)


def create_component_context(comp_class, result_var_name='r', result_var_type='any'):
    class ComponentContextManager:
        def __init__(self):
            self._component = create_component(comp_class, result_var_name, result_var_type)

        async def __aenter__(self):
            return self._component

        async def __aexit__(self, exc_type, exc_value, traceback):
            await self._component.process.clear_variables()
            await self._component.process.clear_process_vars()
            shutil.rmtree(self._component.process.component_def.package.path)

    return ComponentContextManager()


class MockComponent(PrimitiveComponent):
    def __init__(self, process: "Process", component_def: PrimitiveComponentDef, node: FlowNode, parent: Component):
        super().__init__(process, component_def, node, parent)
        self.mock_func = None

    @classmethod
    def display_name(cls):
        return "Mock Component"

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return "Mock Component"

    async def execute(self) -> ControlFlow:
        return await self.mock_func(self)


def add_mock_component(parent: PrimitiveComponent, mock_func) -> MockComponent:
    flow_node = FlowNode(parent.process.component_def)
    mock_comp_def = PrimitiveComponentDef(parent.component_def.package)
    flow_node.component_def = mock_comp_def
    mock_comp = MockComponent(parent.process, mock_comp_def, flow_node, parent)
    mock_comp.mock_func = mock_func
    parent.flow.append(mock_comp)
    return mock_comp


def random_string(prefix="random_string:", chars="abcdefghijklmnopqrstuvwxyz", length=5, suffix=""):
    return prefix + ''.join(random.choice(chars) for _ in range(length)) + suffix


def get_test_app_path():
    if is_macos():
        return "FindMy", "/System/Applications/FindMy.app"
    elif is_windows():
        system_root = os.environ['SYSTEMROOT']
        return "notepad.exe", os.path.join(system_root, 'System32', 'notepad.exe')
    elif is_linux():
        return "gnome-calculator", "/usr/bin/gnome-calculator"
    else:
        raise Exception("Unsupported OS")


def add_test_web_element(component: PrimitiveComponent, element_xpath, iframe_xpath=None, name=None):
    element_info = {"name": name or random_string(prefix="测试网页元素"),
                    "iframeXPath": iframe_xpath,
                    "elementXPath": element_xpath,
                    "inIframe": bool(iframe_xpath),
                    "webPageUrl": "",
                    "useCustomIframeXPath": True,
                    "iframePath": [],
                    "customIframeXPath": iframe_xpath,
                    "useCustomElementXPath": True,
                    "elementPath": [],
                    "customElementXPath": element_xpath}
    component.process.component_def.package.add_web_element_group("test", None)
    element_id = component.process.component_def.package.add_web_element("test", element_info,
                                                                         None)
    return f"{WEB_ELEMENT_URI_PREFIX}{element_id}"


def add_test_window_element(component: PrimitiveComponent, element_xpath, window_xpath=None, name=None):
    element_info = {"name": name or random_string(prefix="测试窗口元素"),
                    "windowXPath": window_xpath,
                    "elementXPath": element_xpath,
                    "useCustomWindowXPath": True,
                    "windowPath": [],
                    "customWindowXPath": window_xpath,
                    "useCustomElementXPath": True,
                    "elementPath": [],
                    "customElementXPath": element_xpath}
    component.process.component_def.package.add_window_element_group("test", None)
    element_id = component.process.component_def.package.add_window_element("test", element_info,
                                                                            None)
    return f"{WINDOW_ELEMENT_URI_PREFIX}{element_id}"
