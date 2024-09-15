from celery import Celery
from core.config import settings

# Create a Celery instance
celery_app = Celery(
    "crawler_app",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Automatically discover tasks in the crawling module
# celery_app.autodiscover_tasks(["crawling"])

# Example task (you can remove this when you no longer need it for testing)
@celery_app.task
def example_task():
    return "Task executed successfully"
