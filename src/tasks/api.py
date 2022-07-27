from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.shortcuts import get_object_or_404

from tasks.models import Task
from tasks.serializers import TaskSerializer


class TasksViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def perform_create(self, serializer: TaskSerializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, url_path='active_tasks_count')
    def get_active_tasks_count(self, request):
        qs = self.filter_queryset(self.get_queryset())
        qs = qs.filter(
            status__in=[Task.Status.NEW, Task.Status.IN_PROGRESS],
        )
        active_tasks_count = qs.count()
        return Response(active_tasks_count)

    @action(detail=True, url_path='results')
    def get_results(self, request, pk: int = None):
        qs = self.filter_queryset(self.get_queryset())
        task = get_object_or_404(qs, pk=pk)

        match task.status:
            case Task.Status.NEW | Task.Status.IN_PROGRESS:
                return Response(
                    data={'error': 'Task still in progress'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            case Task.Status.FAILED:
                return Response(
                    data={'error': task.fail_reason},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(task.result)
