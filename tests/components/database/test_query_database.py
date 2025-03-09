import sqlite3
import tempfile

import pytest

from jimuflow.components.database import QueryDatabaseComponent
from jimuflow.datatypes import Table
from jimuflow.runtime.execution_engine import ControlFlow
from jimuflow.runtime.expression import escape_string
from tests.utils import create_component_context


@pytest.mark.asyncio
async def test_execute():
    async with create_component_context(QueryDatabaseComponent) as component:
        with tempfile.NamedTemporaryFile(suffix=".db", delete_on_close=False) as db_file:
            conn = sqlite3.connect(db_file.name)
            try:
                await component.process.update_variable('conn', conn)
                cursor = conn.cursor()
                cursor.execute('CREATE TABLE movie(title, year, score)')
                cursor.execute("""
                INSERT INTO movie VALUES 
                    ('Monty Python and the Holy Grail', 1975, 8.2),
                    ('And Now for Something Completely Different', 1971, 7.5)
                """)
                conn.commit()
                cursor.close()
                component.node.inputs = {
                    "dbConnection": 'conn',
                    "sql": escape_string("select title, year, score from movie"),
                }
                component.node.outputs = {
                    "table": 'r',
                }
                assert (await component.execute()) == ControlFlow.NEXT
                r: Table = component.process.get_variable('r')
                assert r.numberOfRows == 2
                assert r.columnNames == ['title', 'year', 'score']
                assert r.rows[0] == ('Monty Python and the Holy Grail', 1975, 8.2)
                assert r.rows[1] == ('And Now for Something Completely Different', 1971, 7.5)
            finally:
                conn.close()
