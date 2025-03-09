import sqlite3
import tempfile

import pytest

from jimuflow.components.database import CloseDatabaseConnectionComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component_context


@pytest.mark.asyncio
async def test_execute():
    async with create_component_context(CloseDatabaseConnectionComponent) as component:
        with tempfile.NamedTemporaryFile(suffix=".db", delete_on_close=False) as db_file:
            conn = sqlite3.connect(db_file.name)
            await component.process.update_variable('conn', conn)
            component.node.inputs = {
                "dbConnection": 'conn',
            }
            assert (await component.execute()) == ControlFlow.NEXT
            with pytest.raises(sqlite3.ProgrammingError):
                conn.cursor()
