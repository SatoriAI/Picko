from random import shuffle

from source.database.models import Participant


def generate_derangement(
    participants: list[Participant],
) -> list[tuple[Participant, Participant]]:
    n = len(participants)
    if n < 2:
        return []

    indices = list(range(n))
    is_valid = False

    while not is_valid:
        shuffled = indices.copy()
        shuffle(shuffled)
        is_valid = all(i != shuffled[i] for i in range(n))

    return [(participants[i], participants[shuffled[i]]) for i in range(n)]
