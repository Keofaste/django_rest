import logging

from celery import shared_task

from .services import make_task_calculations

logger = logging.getLogger('tasks')


@shared_task
def make_task_calculations_task(task_id: int):
    make_task_calculations(task_id)
