from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models


class Task(models.Model):
    class Source(models.TextChoices):
        LOCAL = 'local', 'Local'
        S3 = 's3', 'S3'

    class Status(models.TextChoices):
        NEW = 'new', 'New'
        IN_PROGRESS = 'in progress', 'In progress'
        FINISHED = 'finished', 'Finished'
        FAILED = 'failed', 'Failed'

    created_by = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    filename = models.CharField(max_length=50)
    source = models.CharField(choices=Source.choices, default=Source.LOCAL, max_length=10)
    status = models.CharField(choices=Status.choices, default=Status.NEW, max_length=20)
    result = ArrayField(models.DecimalField(decimal_places=10, max_digits=20), default=list)
    fail_reason = models.TextField(blank=True)

    def __str__(self):
        return f'Task for {self.filename}'
