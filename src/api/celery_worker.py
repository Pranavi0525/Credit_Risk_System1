from celery import Celery

celery_app = Celery(
    "credit_risk",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]

# Register tasks
celery_app.autodiscover_tasks(["src.api"])
