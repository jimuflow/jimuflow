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
from jimuflow.datatypes import Table
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class QueryDatabaseComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext(
            'Query ##{dbConnection}## with ##{sql}##, and save the result set to ##{table}##').format(
            sql=flow_node.input('sql'), dbConnection=flow_node.input('dbConnection'),
            table=flow_node.output('table'))

    async def execute(self) -> ControlFlow:
        db_conn = self.read_input('dbConnection')
        sql = self.read_input('sql')
        cursor = None
        try:
            cursor = db_conn.cursor()
            cursor.execute(sql)
            column_names = [description[0] for description in cursor.description]
            table = Table(column_names)
            for row in cursor.fetchall():
                table.rows.append(row)
            db_conn.commit()
        except:
            db_conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
        await self.write_output('table', table)
        return ControlFlow.NEXT
