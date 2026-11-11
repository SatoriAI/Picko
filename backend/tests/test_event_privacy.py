from tests.support import close_registration, create_event_with_participants, fetch_all


async def test_public_event_responses_expose_no_reveal_tokens_or_emails(client):
    event = await create_event_with_participants(client, ["Ann", "Bob", "Cid"])
    await close_registration(event["id"])

    by_id = (await client.get(f"/event/{event['id']}")).json()
    by_token = (await client.get(f"/event/register/{event['registration_token']}")).json()

    # The draw has run, so there are tokens that could leak.
    assert by_id["is_draw_complete"] is True
    reveal_tokens = {row.reveal_token for row in await fetch_all("SELECT reveal_token FROM assignment")}
    assert len(reveal_tokens) == 3

    for body in (by_id, by_token):
        assert len(body["participants"]) == 3
        for participant in body["participants"]:
            assert "reveal_token" not in participant
            assert "email" not in participant
        assert not any(token in str(body) for token in reveal_tokens)
