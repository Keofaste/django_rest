from rest_framework import serializers

from .models import Task


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
