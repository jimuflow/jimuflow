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

import uuid
from pathlib import Path

from jimuflow.common.uri_utils import describe_element_uri
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class ScreenshotWindowElementComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext(
            'Screenshot ##{element}##, and save to ##{snapshotFilename}##').format(
            element=describe_element_uri(flow_node.process_def.package, flow_node.input('elementUri')),
            snapshotFilename=flow_node.output("snapshotFilename"))

    async def execute(self) -> ControlFlow:
        from jimuflow.components.windows_automation.pywinauto_utill import get_element_by_uri

        element_uri = self.read_input("elementUri")
        wait_time = float(self.read_input("waitTime"))
        control_object = get_element_by_uri(self, element_uri, wait_time)
        save_folder = self.read_input("saveFolder")
        file_format = self.read_input("fileFormat")
        file_naming_type = self.read_input("fileNamingType")
        if file_naming_type == "random":
            # 使用uuid生成随机文件名
            file_name = "screenshot_" + str(uuid.uuid4()) + "." + file_format
        else:
            file_name = self.read_input("customFilename") + "." + file_format
        file_path = Path(save_folder).absolute() / file_name
        override_existing_file = self.read_input("overrideExistingFile")
        if file_path.exists() and not override_existing_file:
            raise Exception("File already exists: " + str(file_path))
        control_object.set_focus()
        img = control_object.capture_as_image()
        img.save(str(file_path), format=file_format)

        await self.write_output('snapshotFilename', str(file_path))
        return ControlFlow.NEXT
