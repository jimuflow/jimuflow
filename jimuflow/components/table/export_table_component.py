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

import csv
import uuid
from pathlib import Path

import xlwt
from openpyxl import Workbook

from jimuflow.datatypes import Table
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class ExportTableComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        file_naming_type = flow_node.input("fileNamingType")
        if file_naming_type == 'random':
            return gettext(
                "Export table ##{table}## to ##{fileFormat}## file in ##{saveFolder}## with random file name").format(
                table=flow_node.input('table'), fileFormat=flow_node.input('fileFormat'),
                saveFolder=flow_node.input('saveFolder'))
        else:
            return gettext(
                "Export table ##{table}## to ##{fileFormat}## file in ##{saveFolder}## with file name ##{customFilename}##").format(
                table=flow_node.input('table'), fileFormat=flow_node.input('fileFormat'),
                saveFolder=flow_node.input('saveFolder'), customFilename=flow_node.input('customFilename'))

    async def execute(self) -> ControlFlow:
        table: Table = self.read_input("table")
        save_folder = self.read_input("saveFolder")
        file_format = self.read_input("fileFormat")
        file_naming_type = self.read_input("fileNamingType")
        if file_naming_type == "random":
            # 使用uuid生成随机文件名
            file_name = "table_" + str(uuid.uuid4()) + "." + file_format
        else:
            file_name = self.read_input("customFilename") + "." + file_format
        file_path = Path(save_folder).absolute() / file_name
        override_existing_file = self.read_input("overrideExistingFile")
        if file_path.exists() and not override_existing_file:
            raise Exception(gettext("File already exists: {file_path}").format(file_path=str(file_path)))
        export_header = self.read_input("exportHeader")
        if file_format == "xlsx":
            wb = Workbook()
            ws = wb.active
            ws.title = self.read_input('sheetName')
            if export_header:
                ws.append(table.columnNames)
            for row in table.rows:
                ws.append(row)
            wb.save(file_path)
        elif file_format == "xls":
            wb = xlwt.Workbook()
            ws = wb.add_sheet(self.read_input('sheetName'))
            if export_header:
                for i, column_name in enumerate(table.columnNames):
                    ws.write(0, i, column_name)
            for i, row in enumerate(table.rows):
                for j, cell in enumerate(row):
                    ws.write(i + 1, j, cell)
            wb.save(file_path)
        elif file_format == "csv":
            file_encoding = self.read_input('fileEncoding')
            if file_encoding == 'system_default':
                encoding = None
            else:
                encoding = file_encoding
            use_custom_delimiter = self.read_input('useCustomDelimiter')
            if use_custom_delimiter:
                delimiter = self.read_input('customDelimiter')
            else:
                delimiter = ','
            with open(file_path, 'w', newline='', encoding=encoding) as f:
                writer = csv.writer(f, delimiter=delimiter)
                if export_header:
                    writer.writerow(table.columnNames)
                for row in table.rows:
                    writer.writerow(row)
        else:
            raise Exception(gettext("Unsupported file format: {file_format}").format(file_format=file_format))

        await self.write_output('filePath', str(file_path))
        return ControlFlow.NEXT
