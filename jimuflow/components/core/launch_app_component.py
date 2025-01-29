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

from jimuflow.components.core.os_utils import launch_app
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class LaunchAppComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext('Launch application ##{appPath}##, and save the pid to ##{pid}##').format(
            appPath=flow_node.input('appPath'), pid=flow_node.output('pid'))

    async def execute(self) -> ControlFlow:
        app_path: str = self.read_input('appPath')
        work_dir = self.read_input('workDir')
        args = self.read_input('args')
        action_after_launch = self.read_input('actionAfterLaunch')
        process = await launch_app(app_path, work_dir, args)
        pid = process.pid
        await self.write_output('pid', pid)
        if action_after_launch == 'wait_complete':
            wait_timeout = self.read_input('waitTimeout')
            if wait_timeout:
                async with asyncio.timeout(float(wait_timeout)):
                    await process.wait()
            else:
                await process.wait()
        return ControlFlow.NEXT
