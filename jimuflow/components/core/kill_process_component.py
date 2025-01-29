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

import psutil

from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class KillProcessComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        process_prop = flow_node.input('processProp')
        if process_prop == 'pid':
            return gettext(
                'Kill process with pid ##{pid}##').format(
                pid=flow_node.input('pid')
            )
        else:
            return gettext(
                'Kill process with name ##{name}##').format(
                name=flow_node.input('name')
            )

    async def execute(self) -> ControlFlow:
        process_prop = self.read_input('processProp')
        if process_prop == 'pid':
            pid = int(self.read_input('pid'))
            try:
                process = psutil.Process(pid)
                process.kill()
            except psutil.NoSuchProcess:
                self.log_warn(gettext('Process not found'))
                pass
        else:
            name = self.read_input('name')
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == name:
                    try:
                        process = psutil.Process(proc.info['pid'])
                        process.kill()
                    except psutil.NoSuchProcess:
                        self.log_warn(gettext('Process not found'))
                    break
            else:
                self.log_warn(gettext('Process not found'))
        return ControlFlow.NEXT
