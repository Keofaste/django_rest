import logging
from pathlib import Path

import pandas as pd

from django.conf import settings

from .models import Task

logger = logging.getLogger('tasks')


class UnknownStorageException(Exception):
    pass


def get_csv_filepath(filename: str, storage: Task.Storage):
    match storage:
        case Task.Storage.LOCAL:
            return settings.CSV_PATH / filename
        case Task.Storage.S3:
            raise NotImplementedError()
        case _:
            raise UnknownStorageException()


def _sum_csv_columns(filepath: Path) -> pd.Series:
    df = pd.read_csv(filepath, chunksize=1000, sep=',')

    chunks_sum = None

    for file in df:
        if chunks_sum is None:
            chunks_sum = file[list(file)[9::10]].sum()
        else:
            chunks_sum += file[list(file)[9::10]].sum()

    return chunks_sum


def _save_calculations(task: Task, calculations: pd.Series):
    if calculations is None:
        task.status = Task.Status.FAILED
        task.fail_reason = 'no columns to sum'
    else:
        task.result = calculations.tolist()
        task.status = Task.Status.FINISHED

    task.save()


def make_task_calculations(task_id: int):
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        logger.error(f'Task #{task_id} calculation failed: task does not exists')
        return

    if task.status != Task.Status.NEW:
        logger.error(f'Task #{task_id} calculation failed: incorrect status "{task.status}"')
        return

    try:
        filepath = get_csv_filepath(task.filename, task.storage)
    except (UnknownStorageException, NotImplementedError):
        logger.error(f'Task #{task_id} calculation failed: unknown storage "{task.storage}"')
        task.status = Task.Status.FAILED
        task.fail_reason = 'Unknown storage'
        task.save()
        return

    if not filepath.exists():
        logger.error(f'Task #{task_id} calculation failed: file "{filepath}" does not exists')
        task.status = Task.Status.FAILED
        task.fail_reason = 'File not found'
        task.save()
        return

    calculations = _sum_csv_columns(filepath)
    _save_calculations(task, calculations)
