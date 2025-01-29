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

from jimuflow.locales.i18n import gettext
from .core import DataTypeDef, DataTypeProperty


class Table:
    def __init__(self, column_names):
        self.columnNames = column_names
        self.rows = []

    @property
    def numberOfColumns(self):
        return len(self.columnNames)

    @property
    def numberOfRows(self):
        return len(self.rows)

    def resolve_row_no(self, row_no, check_out_of_range=True):
        if isinstance(row_no, str):
            row_no = int(row_no)
        if row_no < 0:
            row_no = self.numberOfRows + row_no + 1
        if check_out_of_range and (row_no <= 0 or row_no > self.numberOfRows):
            raise Exception(gettext('Row no is out of range: {row_no}').format(row_no=row_no))
        return row_no

    def resolve_column_no(self, column_name_or_no, check_out_of_range=True):
        if isinstance(column_name_or_no, str):
            try:
                column_no = int(column_name_or_no)
            except:
                column_no = self.columnNames.index(column_name_or_no) + 1
        else:
            column_no = column_name_or_no
        if column_no < 0:
            column_no = self.numberOfColumns + column_no + 1
        if check_out_of_range and (column_no <= 0 or column_no > self.numberOfColumns):
            raise Exception(gettext('Column no is out of range: {column_no}').format(column_no=column_no))
        return column_no


table_data_type = DataTypeDef("table", gettext('Table'), [
    DataTypeProperty("numberOfRows", "number", gettext("Number of rows")),
    DataTypeProperty("numberOfColumns", "number", gettext("Number of columns")),
    DataTypeProperty("columnNames", "list", gettext("List of column names"), element_type="text"),
    DataTypeProperty("rows", "list", gettext("List of rows"))
], types=(Table,))
