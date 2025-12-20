from celery import Celery
from kombu import Queue

from source.settings import settings

celery_app = Celery("picko", broker=settings.redis_url)
celery_app.conf.broker_transport_options = {
    "visibility_timeout": settings.celery_visibility_timeout_seconds,
}

celery_app.conf.task_queues = (Queue("default"),)
celery_app.conf.task_default_queue = "default"
celery_app.conf.task_default_routing_key = "default"

celery_app.conf.worker_concurrency = settings.default_worker_concurrency

celery_app.autodiscover_tasks(["source"], related_name="tasks")
