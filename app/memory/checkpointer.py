from contextlib import asynccontextmanager
from pathlib import Path

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from app.config import settings


@asynccontextmanager
async def get_checkpointer():
    Path(settings.database_path).parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    async with AsyncSqliteSaver.from_conn_string(
        settings.database_path
    ) as checkpointer:
        await checkpointer.setup()
        yield checkpointer
