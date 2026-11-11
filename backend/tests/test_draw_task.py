import subprocess
import sys
from pathlib import Path

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


def test_the_draw_task_retries_while_emails_fail_and_then_gives_up(monkeypatch):
    runs: list[int] = []

    async def always_one_failed_email(event_id: int) -> dict:
        runs.append(event_id)
        return {"status": "emails_failed", "event_id": event_id, "sent": 0, "failed": 1}

    monkeypatch.setattr(sys.modules["source.tasks.draw"], "_run", always_one_failed_email)

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
