import sqlite3
import tempfile

import pytest

from jimuflow.components.database import ExecuteSQLComponent
from jimuflow.runtime.execution_engine import ControlFlow
from jimuflow.runtime.expression import escape_string
from tests.utils import create_component_context


@pytest.mark.asyncio
async def test_execute_create_table_sql():
    async with create_component_context(ExecuteSQLComponent) as component:
        with tempfile.NamedTemporaryFile(suffix=".db", delete_on_close=False) as db_file:
            conn = sqlite3.connect(db_file.name)
            try:
                await component.process.update_variable('conn', conn)
                component.node.inputs = {
                    "dbConnection": 'conn',
                    "sql": escape_string('CREATE TABLE movie(title, year, score)'),
                }
                component.node.outputs = {
                    "rowCount": 'r',
                }
                assert (await component.execute()) == ControlFlow.NEXT
                r = component.process.get_variable('r')
                assert r == -1
                cursor = conn.cursor()
                assert cursor.execute('SELECT count(*) FROM movie').fetchone()[0] == 0
                cursor.close()
            finally:
                conn.close()


@pytest.mark.asyncio
async def test_execute_insert_sql():
    async with create_component_context(ExecuteSQLComponent) as component:
        with tempfile.NamedTemporaryFile(suffix=".db", delete_on_close=False) as db_file:
            conn = sqlite3.connect(db_file.name)
            try:
                await component.process.update_variable('conn', conn)
                cursor = conn.cursor()
                cursor.execute('CREATE TABLE movie(title, year, score)')
                conn.commit()
                cursor.close()
                component.node.inputs = {
                    "dbConnection": 'conn',
                    "sql": escape_string("""
                    INSERT INTO movie VALUES 
                        ('Monty Python and the Holy Grail', 1975, 8.2),
                        ('And Now for Something Completely Different', 1971, 7.5)
                    """),
                }
                component.node.outputs = {
                    "rowCount": 'r',
                }
                assert (await component.execute()) == ControlFlow.NEXT
                r = component.process.get_variable('r')
                assert r == 2
                cursor = conn.cursor()
                assert cursor.execute('SELECT count(*) FROM movie').fetchone()[0] == 2
            finally:
                conn.close()
