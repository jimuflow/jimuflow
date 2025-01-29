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

import os.path

import pytest

from jimuflow.components.table import ImportExcelAsTableComponent
from jimuflow.datatypes import Table
from jimuflow.runtime.execution_engine import ControlFlow
from jimuflow.runtime.expression import escape_string
from tests.utils import create_component

xls_file = os.path.join(os.path.dirname(__file__), "table.xls")
xlsx_file = os.path.join(os.path.dirname(__file__), "table.xlsx")


@pytest.mark.asyncio
@pytest.mark.parametrize("filePath,sheetSelectType,sheetIndex,sheetName,useFirstRowAsHeader", [
    (xlsx_file, 'by_index', 2, None, True),
    (xlsx_file, 'by_name', None, '测试', False),
    (xls_file, 'by_index', 2, None, True),
    (xls_file, 'by_name', None, '测试', False),
])
async def test_execute(filePath, sheetSelectType, sheetIndex, sheetName, useFirstRowAsHeader):
    component = create_component(ImportExcelAsTableComponent)
    component.node.inputs = {
        "filePath": escape_string(filePath),
        "sheetSelectType": sheetSelectType,
        "useFirstRowAsHeader": useFirstRowAsHeader
    }
    if sheetSelectType == 'by_index':
        component.node.inputs["sheetIndex"] = f'{sheetIndex}'
    elif sheetSelectType == 'by_name':
        component.node.inputs["sheetName"] = escape_string(sheetName)
    component.node.outputs = {
        "table": 'r'
    }
    assert (await component.execute()) == ControlFlow.NEXT
    table = component.process.get_variable('r')
    assert isinstance(table, Table)
    if useFirstRowAsHeader:
        assert table.columnNames == ['列1', '列2']
        assert table.numberOfRows == 3
        assert table.rows == [[4, 'e'], [5, 'f'], [6, 'g']]
    else:
        assert table.columnNames == ['column1', 'column2']
        assert table.numberOfRows == 4
        assert table.rows == [['列1', '列2'], [4, 'e'], [5, 'f'], [6, 'g']]
