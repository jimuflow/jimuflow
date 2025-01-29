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

from jimuflow.runtime.execution_engine import Process, Component, ProcessListener


class Breakpoint:
    def __init__(self, process_def_id: str, line: int, enabled: bool = True):
        self.process_def_id = process_def_id
        self.line = line
        self.enabled = enabled

    def __eq__(self, other):
        if isinstance(other, Breakpoint):
            return self.process_def_id == other.process_def_id and self.line == other.line
        return False

    def match(self, step: Component):
        return self.process_def_id == step.process.process_def.id and self.line == step.node.line_no


class DebugListener:
    def on_debugger_paused(self, step: Component):
        pass

    def on_debugger_ended(self):
        pass

    def on_debugger_resumed(self):
        pass


class ProcessDebugger(ProcessListener):
    def __init__(self, process: Process, listener: DebugListener):
        self.process = process
        self.step: Component | None = None
        self.breakpoints: list[Breakpoint] = []
        self.end = False
        self._stop_predication = lambda step: self.is_breakpoint(step)
        self._resume_event = asyncio.Event()
        self._listener = listener
        process.add_process_listener(self)

    async def before_execute_component(self, component: "Component"):
        if self._stop_predication and self._stop_predication(component):
            self.step = component
            self._resume_event.clear()
            self._listener.on_debugger_paused(component)
            await self._resume_event.wait()

    async def after_execute_component(self, component: "Component"):
        self.end = component == self.process
        if self.end:
            self._listener.on_debugger_ended()

    def add_breakpoint(self, bp: Breakpoint):
        if bp in self.breakpoints:
            return
        self.breakpoints.append(bp)

    def delete_breakpoint(self, bp: Breakpoint):
        try:
            self.breakpoints.remove(bp)
        except ValueError:
            pass

    def enable_breakpoint(self, bp: Breakpoint):
        try:
            self.breakpoints[self.breakpoints.index(bp)].enabled = True
        except ValueError:
            pass

    def disable_breakpoint(self, bp: Breakpoint):
        try:
            self.breakpoints[self.breakpoints.index(bp)].enabled = False
        except ValueError:
            pass

    def step_over(self):
        start_step = self.step
        self._stop_predication = lambda step: self.is_breakpoint(
            step) or step.process.component_def == start_step.process.component_def
        self.resume()

    def step_into(self):
        self._stop_predication = lambda step: True
        self.resume()

    def step_out(self):
        start_step = self.step
        # 如果是主流程的组件，则执行step_over
        if start_step.process.process is None:
            return self.step_over()
        parent_process_def = start_step.process.process.component_def
        self._stop_predication = lambda step: self.is_breakpoint(
            step) or step.process.component_def == parent_process_def
        self.resume()

    def resume(self):
        self._listener.on_debugger_resumed()
        self._resume_event.set()

    def run_to_next_breakpoint(self):
        self._stop_predication = lambda step: self.is_breakpoint(step)
        self.resume()

    def is_breakpoint(self, step: Component):
        return step.node and step.node.breakpoint

    async def run(self):
        await self.process.invoke()

    def stop(self):
        self.process.stop()
        self._stop_predication = lambda step: False
        self.resume()

