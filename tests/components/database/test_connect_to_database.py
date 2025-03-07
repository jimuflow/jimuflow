import tempfile

import pytest

from jimuflow.components.database import ConnectToDatabaseComponent
from jimuflow.runtime.execution_engine import ControlFlow
from jimuflow.runtime.expression import escape_string
from tests.utils import create_component_context


@pytest.mark.asyncio
async def test_connect_to_sqlite():
    async with create_component_context(ConnectToDatabaseComponent) as component:
        with tempfile.NamedTemporaryFile(suffix=".db") as db_file:
            component.node.inputs = {
                "dbType": 'SQLite',
                "dbFile": escape_string(db_file.name),
            }
            component.node.outputs = {
                "connection": 'r',
            }
            assert (await component.execute()) == ControlFlow.NEXT
            conn = component.process.get_variable('r')
            assert conn is not None
            conn.close()
