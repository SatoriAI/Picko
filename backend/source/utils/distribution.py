from random import shuffle

from source.database.models import Participant


def generate_derangement(
    participants: list[Participant],
) -> list[tuple[Participant, Participant]]:
    if (n := len(participants)) < 2:
        return []

    indices = list(range(n))

    while True:
        shuffled = indices.copy()
        shuffle(shuffled)
        if all(i != shuffled[i] for i in range(n)):
            break

    return [(participants[i], participants[shuffled[i]]) for i in range(n)]
