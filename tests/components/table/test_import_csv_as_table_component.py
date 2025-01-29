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

from jimuflow.components.table import ImportCsvAsTableComponent
from jimuflow.datatypes import Table
from jimuflow.runtime.execution_engine import ControlFlow
from jimuflow.runtime.expression import escape_string
from tests.utils import create_component

csv_file = os.path.join(os.path.dirname(__file__), "table.csv")
tsv_file = os.path.join(os.path.dirname(__file__), "table.tsv")


@pytest.mark.asyncio
@pytest.mark.parametrize("filePath,fileEncoding,useCustomDelimiter,customDelimiter,useFirstRowAsHeader", [
    (csv_file, 'utf-8-sig', False, None, True),
    (csv_file, 'utf-8-sig', False, None, False),
    (tsv_file, 'utf-8-sig', True, '\t', True),
    (tsv_file, 'utf-8-sig', True, '\t', False),
])
async def test_execute(filePath, fileEncoding, useCustomDelimiter, customDelimiter, useFirstRowAsHeader):
    component = create_component(ImportCsvAsTableComponent)
    component.node.inputs = {
        "filePath": escape_string(filePath),
        "fileEncoding": fileEncoding,
        "useCustomDelimiter": useCustomDelimiter,
        "useFirstRowAsHeader": useFirstRowAsHeader
    }
    if useCustomDelimiter:
        component.node.inputs['customDelimiter'] = escape_string(customDelimiter)
    component.node.outputs = {
        "table": 'r'
    }
    assert (await component.execute()) == ControlFlow.NEXT
    table = component.process.get_variable('r')
    assert isinstance(table, Table)
    if useFirstRowAsHeader:
        assert table.columnNames == ['ID', '名称']
        assert table.numberOfRows == 3
        assert table.rows == [['1', 'a'], ['2', 'b'], ['3', 'c']]
    else:
        assert table.columnNames == ['column1', 'column2']
        assert table.numberOfRows == 4
        assert table.rows == [['ID', '名称'], ['1', 'a'], ['2', 'b'], ['3', 'c']]
