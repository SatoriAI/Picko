import subprocess
import sys
from pathlib import Path

import pytest
from celery.exceptions import MaxRetriesExceededError

from source.tasks.draw import draw

BACKEND_DIR = Path(__file__).resolve().parent.parent

# A Celery worker process runs many tasks, each in its own event loop. Calling the task function directly is the
# same code path the worker takes; a separate interpreter keeps this suite's own loop out of the engine's pool.
RUN_TASK_THREE_TIMES = """
from source.tasks.draw import draw

for _ in range(3):
    assert draw(999999)["status"] == "event_not_found"
"""


def test_the_draw_task_runs_repeatedly_in_one_worker_process():
    result = subprocess.run(
        [sys.executable, "-c", RUN_TASK_THREE_TIMES],
        cwd=BACKEND_DIR,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )

    assert result.returncode == 0, result.stderr[-2000:]


@pytest.mark.parametrize(
    "outcome",
    [
        pytest.param({"status": "emails_failed", "sent": 0, "failed": 1}, id="a send failed"),
        pytest.param({"status": "emails_in_progress_elsewhere", "sent": 0, "failed": 0}, id="someone was locked"),
    ],
)
def test_the_draw_task_retries_while_someone_is_left_unemailed_and_then_gives_up(monkeypatch, outcome):
    runs: list[int] = []

    async def never_finishes(event_id: int) -> dict:
        runs.append(event_id)
        return {"event_id": event_id} | outcome

    monkeypatch.setattr(sys.modules["source.tasks.draw"], "_run", never_finishes)

    # apply() runs the task in this process and follows its retries without waiting out the countdown.
    result = draw.apply(args=[7])

    assert result.failed()
    assert isinstance(result.result, MaxRetriesExceededError)
    assert runs == [7] * (draw.max_retries + 1)


def test_the_draw_task_retries_after_an_unexpected_error(monkeypatch):
    runs: list[int] = []

    async def database_is_gone(event_id: int) -> dict:
        runs.append(event_id)
        raise RuntimeError("connection lost")

    monkeypatch.setattr(sys.modules["source.tasks.draw"], "_run", database_is_gone)

    result = draw.apply(args=[7])

    assert result.failed()
    assert isinstance(result.result, RuntimeError)
    assert runs == [7] * (draw.max_retries + 1)


@pytest.mark.parametrize("status", ["emails_sent", "already_notified", "draw_not_complete", "event_not_found"])
def test_the_draw_task_does_not_retry_a_finished_outcome(monkeypatch, status):
    runs: list[int] = []

    async def finished(event_id: int) -> dict:
        runs.append(event_id)
        return {"status": status, "event_id": event_id}

    monkeypatch.setattr(sys.modules["source.tasks.draw"], "_run", finished)

    result = draw.apply(args=[7])

    assert result.successful()
    assert runs == [7]
