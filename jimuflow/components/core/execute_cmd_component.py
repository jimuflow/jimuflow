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
import locale

from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class ExecuteCmdComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext('Execute command ##{cmd}##, and save the command output to ##{result}##').format(
            cmd=flow_node.input('cmd'), result=flow_node.output('result'))

    async def execute(self) -> ControlFlow:
        cmd: str = self.read_input('cmd')
        work_dir = self.read_input('workDir')
        process = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE,
                                                        stderr=asyncio.subprocess.PIPE, cwd=work_dir)
        wait_timeout = self.read_input('waitTimeout')
        if wait_timeout:
            async with asyncio.timeout(float(wait_timeout)):
                stdout, stderr = await process.communicate()
        else:
            stdout, stderr = await process.communicate()
        encoding = self.read_input('encoding')
        if encoding == 'system_default':
            encoding = locale.getpreferredencoding()
        if process.returncode != 0:
            raise Exception(gettext('Command failed with exit code {code}: {error}'
                                    .format(code=process.returncode, error=stderr.decode(encoding=encoding))))
        result = stdout.decode(encoding=encoding)
        await self.write_output('result', result)
        return ControlFlow.NEXT
