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
import json

from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class ConnectToDatabaseComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        db_type = flow_node.input('dbType')
        if db_type == 'SQLite':
            db_desc = flow_node.input('dbFile')
        else:
            db_desc = flow_node.input('host')
            port = flow_node.input('port')
            if port:
                db_desc += ':' + port
            database = flow_node.input('database')
            if database:
                db_desc += '/' + database
        return gettext(
            'Connect ##{db_type}## database ##{db_desc}##, and save the created connection object to ##{connection}##').format(
            db_type=db_type, db_desc=db_desc, connection=flow_node.output('connection'))

    async def execute(self) -> ControlFlow:
        db_type = self.read_input('dbType')
        if db_type == 'SQLite':
            conn = self._connect_to_sqllite()
        elif db_type == 'MySQL':
            conn = self._connect_to_mysql()
        elif db_type == 'SQLServer':
            conn = self._connect_to_sqlserver()
        elif db_type == 'PostgreSQL':
            conn = self._connect_to_postgresql()
        else:
            raise NotImplementedError(gettext('Database type {db_type} is not supported.').format(db_type=db_type))
        await self.write_output('connection', conn, lambda v: v.close())
        return ControlFlow.NEXT

    def _connect_to_sqllite(self):
        db_file = self.read_input('dbFile')
        connect_kwargs = {
            'autocommit': False
        }
        connect_kwargs.update(self._get_extra_config())
        import sqlite3
        conn = sqlite3.connect(db_file, **connect_kwargs)
        return conn

    def _get_extra_config(self):
        extra_config = self.read_input('extraConfig')
        if extra_config:
            if isinstance(extra_config, str):
                extra_config = json.loads(extra_config)
            return extra_config
        return {}

    def _connect_to_mysql(self):
        connect_kwargs = {
            'host': self.read_input('host'),
        }
        port = self.read_input('port')
        if port:
            connect_kwargs['port'] = int(port)
        user = self.read_input('user')
        if user:
            connect_kwargs['user'] = user
        password = self.read_input('password')
        if password:
            connect_kwargs['password'] = password
        database = self.read_input('database')
        if database:
            connect_kwargs['database'] = database
        connect_kwargs.update(self._get_extra_config())
        import mysql.connector
        conn = mysql.connector.connect(**connect_kwargs)
        return conn

    def _connect_to_postgresql(self):
        connect_kwargs = {
            'host': self.read_input('host'),
        }
        port = self.read_input('port')
        if port:
            connect_kwargs['port'] = int(port)
        user = self.read_input('user')
        if user:
            connect_kwargs['user'] = user
        password = self.read_input('password')
        if password:
            connect_kwargs['password'] = password
        database = self.read_input('database')
        if database:
            connect_kwargs['dbname'] = database
        connect_kwargs.update(self._get_extra_config())
        import psycopg2
        conn = psycopg2.connect(**connect_kwargs)
        return conn

    def _connect_to_sqlserver(self):
        connect_kwargs = {
            'server': self.read_input('host'),
        }
        port = self.read_input('port')
        if port:
            connect_kwargs['port'] = int(port)
        user = self.read_input('user')
        if user:
            connect_kwargs['user'] = user
        password = self.read_input('password')
        if password:
            connect_kwargs['password'] = password
        database = self.read_input('database')
        if database:
            connect_kwargs['database'] = database
        connect_kwargs.update(self._get_extra_config())
        connect_kwargs.update({'as_dict': False})
        import pymssql
        conn = pymssql.connect(**connect_kwargs)
        return conn
