import os

import pytest

# The suite drops and recreates every table, so it only ever runs against a database named explicitly for it.
if "TEST_DATABASE_URL" not in os.environ:
    pytest.exit("Set TEST_DATABASE_URL to a disposable Postgres database; the suite drops its tables.", returncode=4)

os.environ.update(
    DATABASE_URL=os.environ["TEST_DATABASE_URL"],
    REDIS_URL="redis://127.0.0.1:1/0",
    CORS_ORIGINS="https://picko.test,https://www.picko.test",
    FRONTEND_URL="https://picko.test",
    EMAIL_FROM="noreply@picko.test",
    RESEND_API_KEY="re_test",
)

import httpx  # noqa: E402
from sqlalchemy import text  # noqa: E402

from source.app import app  # noqa: E402
from source.database.connection import ENGINE  # noqa: E402
from source.database.models import Base  # noqa: E402
from source.tasks.draw import draw  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
async def schema():
    async with ENGINE.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    yield
    await ENGINE.dispose()


@pytest.fixture(autouse=True)
async def clean_tables(schema):
    yield
    async with ENGINE.begin() as connection:
        await connection.execute(text("TRUNCATE event RESTART IDENTITY CASCADE"))


@pytest.fixture(autouse=True)
def scheduled_draws(monkeypatch) -> list[dict]:
    """There is no broker in tests; record what the API would have scheduled instead."""
    calls: list[dict] = []
    monkeypatch.setattr(draw, "apply_async", lambda *args, **kwargs: calls.append(kwargs))
    return calls


@pytest.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as http_client:
        yield http_client
