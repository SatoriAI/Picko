import httpx
import pytest

from source.app import app
from tests.support import create_event, in_one_day, register


@pytest.mark.parametrize(
    "overrides",
    [
        pytest.param({"name": "   "}, id="whitespace-only name"),
        pytest.param({"registration_deadline": "2020-01-01T10:00:00Z"}, id="deadline in the past"),
        pytest.param({"registration_deadline": "2999-01-01T10:00:00"}, id="deadline without a timezone"),
    ],
)
async def test_event_creation_rejects_invalid_input(client, overrides):
    payload = {"name": "Office party", "registration_deadline": in_one_day(), "currency": None} | overrides

    response = await client.post("/event", json=payload)

    assert response.status_code == httpx.codes.UNPROCESSABLE_ENTITY


async def test_event_creation_accepts_a_missing_currency(client):
    response = await client.post("/event", json={"name": "Office party", "registration_deadline": in_one_day()})

    assert response.status_code == httpx.codes.CREATED
    assert response.json()["currency"] is None


async def test_names_are_stored_without_surrounding_whitespace(client):
    event = await create_event(client, name="  Office party  ")
    participant = await register(client, event["registration_token"], "  Ann  ")

    assert event["name"] == "Office party"
    assert participant.json()["name"] == "Ann"


async def test_registration_rejects_a_whitespace_only_name(client):
    event = await create_event(client)

    response = await register(client, event["registration_token"], "   ")

    assert response.status_code == httpx.codes.UNPROCESSABLE_ENTITY


def test_the_api_schema_is_titled_after_the_app():
    assert app.title == "Picko"
