import sqlite3
import tempfile

import pytest

from jimuflow.components.database import BatchUpdateDatabaseComponent
from jimuflow.datatypes import Table
from jimuflow.runtime.execution_engine import ControlFlow
from jimuflow.runtime.expression import escape_string
from tests.utils import create_component_context


@pytest.mark.asyncio
async def test_execute():
    async with create_component_context(BatchUpdateDatabaseComponent) as component:
        with tempfile.NamedTemporaryFile(suffix=".db") as db_file:
            with sqlite3.connect(db_file.name) as conn:
                await component.process.update_variable('conn', conn)
                table = Table(['col1', 'col2', 'col3'])
                table.rows = [('Monty Python and the Holy Grail', 1975, 8.2),
                              ('And Now for Something Completely Different', 1971, 7.5)]
                await component.process.update_variable('table', table)
                cursor = conn.cursor()
                cursor.execute('CREATE TABLE movie(title, year, score)')
                conn.commit()
                cursor.close()
                component.node.inputs = {
                    "dbConnection": 'conn',
                    "table": 'table',
                    "sql": escape_string("insert into movie (title, year, score) values (@col1@,@col2@,@col3@)"),
                }
                component.node.outputs = {
                    "rowCount": 'r',
                }
                assert (await component.execute()) == ControlFlow.NEXT
                r = component.process.get_variable('r')
                assert r == 2
                cursor = conn.cursor()
                cursor.execute('select * from movie')
                result = cursor.fetchall()
                assert result == table.rows
                cursor.close()
