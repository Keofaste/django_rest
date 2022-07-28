from rest_framework import serializers

from .models import Task
from .tasks import make_task_calculations_task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'id',
            'created_by_id',
            'created_at',
            'filename',
            'storage',
            'status',
            'result',
            'fail_reason',
        ]

    def save(self, **kwargs) -> Task:
        task = super(TaskSerializer, self).save(**kwargs)
        make_task_calculations_task.delay(task.id)
        return task
