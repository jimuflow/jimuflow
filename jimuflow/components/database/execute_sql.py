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

from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class ExecuteSQLComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext(
            'Execute ##{sql}## on ##{dbConnection}##, and save the row count to ##{rowCount}##').format(
            sql=flow_node.input('sql'), dbConnection=flow_node.input('dbConnection'),
            rowCount=flow_node.output('rowCount'))

    async def execute(self) -> ControlFlow:
        db_conn = self.read_input('dbConnection')
        sql = self.read_input('sql')
        cursor = None
        try:
            cursor = db_conn.cursor()
            cursor.execute(sql)
            db_conn.commit()
            await self.write_output('rowCount', cursor.rowcount)
        except:
            db_conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
        return ControlFlow.NEXT
