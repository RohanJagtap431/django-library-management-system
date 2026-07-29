import os
from django.apps import AppConfig
from django.conf import settings


class TransactionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transactions'

    def ready(self):

        if settings.DEBUG and os.environ.get("RUN_MAIN") != "true":
            return

        from .scheduler import start_scheduler

        start_scheduler()

        print("Transactions App Ready")