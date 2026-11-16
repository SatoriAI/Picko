from tests.support import close_registration, create_event, create_event_with_participants, fetch_all, register


async def test_public_event_responses_expose_no_reveal_tokens_or_emails(client):
    event = await create_event_with_participants(client, ["Ann", "Bob", "Cid"])
    await close_registration(event["id"])

    by_view_token = (await client.get(f"/event/{event['view_token']}")).json()
    by_token = (await client.get(f"/event/register/{event['registration_token']}")).json()

    # The draw has run, so there are tokens that could leak.
    assert by_view_token["is_draw_complete"] is True
    reveal_tokens = {row.reveal_token for row in await fetch_all("SELECT reveal_token FROM assignment")}
    assert len(reveal_tokens) == 3

    for body in (by_view_token, by_token):
        assert len(body["participants"]) == 3
        for participant in body["participants"]:
            assert "reveal_token" not in participant
            assert "email" not in participant
        assert not any(token in str(body) for token in reveal_tokens)


async def test_an_event_page_opens_by_its_token_and_not_by_its_id(client):
    first = await create_event_with_participants(client, ["Ann", "Bob"])
    second = await create_event_with_participants(client, ["Cid", "Dee"])

    assert first["view_token"] != second["view_token"]
    assert (await client.get(f"/event/{first['view_token']}")).json()["id"] == first["id"]
    # The ids are 1 and 2; counting through them must find nothing.
    for event in (first, second):
        assert (await client.get(f"/event/{event['id']}")).status_code == 404


async def test_the_pages_that_link_to_the_event_page_carry_its_token(client):
    event = await create_event(client)
    registered = (await register(client, event["registration_token"], "Ann")).json()

    by_registration = (await client.get(f"/event/register/{event['registration_token']}")).json()
    status = (await client.get(f"/participant/me/{registered['access_token']}")).json()

    assert by_registration["view_token"] == event["view_token"]
    assert status["event"]["view_token"] == event["view_token"]
