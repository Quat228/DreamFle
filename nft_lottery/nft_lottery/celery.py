import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nft_lottery.settings")

app = Celery("nft_lottery")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
