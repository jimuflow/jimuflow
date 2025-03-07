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
import re

from jimuflow.datatypes import Table
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class BatchUpdateDatabaseComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext(
            'Use ##{sql}## and ##{table}## to batch update the database ##{dbConnection}##, and save the row count to ##{rowCount}##').format(
            sql=flow_node.input('sql'), table=flow_node.input('table'), dbConnection=flow_node.input('dbConnection'),
            rowCount=flow_node.output('rowCount'))

    async def execute(self) -> ControlFlow:
        db_conn = self.read_input('dbConnection')
        paramstyle = self._get_paramstyle(db_conn)
        sql = self.read_input('sql')
        table: Table = self.read_input('table')
        param_names = []
        transformed_sql = ''
        prev_end = 0
        for match in re.finditer(r'@([^@]*)@', sql):
            transformed_sql += sql[prev_end:match.start()]
            if match.group(1):
                param_names.append(match.group(1))
                column_idx = len(param_names)
                if paramstyle == 'qmark':
                    transformed_sql += '?'
                elif paramstyle == 'numeric':
                    transformed_sql += ':' + str(column_idx)
                elif paramstyle == 'named':
                    transformed_sql += ':c' + str(column_idx)
                elif paramstyle == 'format':
                    transformed_sql += '%s'
                elif paramstyle == 'pyformat':
                    transformed_sql += f'%(c{column_idx})s'
                else:
                    raise ValueError('Unsupported paramstyle: %s' % paramstyle)
            else:
                transformed_sql += '@'
            prev_end = match.end()
        if prev_end < len(sql):
            transformed_sql += sql[prev_end:]
        transformed_data = []
        for row in table.rows:
            if paramstyle == 'qmark' or paramstyle == 'numeric' or paramstyle == 'format':
                transformed_data.append(tuple(row[table.columnNames.index(name)] for name in param_names))
            else:
                transformed_data.append(
                    {'c' + str(i + 1): row[table.columnNames.index(name)] for i, name in enumerate(param_names)})
        cursor = None
        try:
            cursor = db_conn.cursor()
            cursor.executemany(transformed_sql, transformed_data)
            db_conn.commit()
            await self.write_output('rowCount', cursor.rowcount)
        except:
            db_conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
        return ControlFlow.NEXT

    def _get_paramstyle(self, db_conn):
        driver_module = type(db_conn).__module__
        if 'sqlite3' in driver_module:
            return 'qmark'
        else:
            return 'pyformat'
