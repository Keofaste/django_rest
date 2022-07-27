import secrets

from django.contrib.auth import get_user_model
from django.test import Client
from django.test import TestCase

from .models import Task


class TasksCreationTestCase(TestCase):
    create_task_path = '/tasks/'

    user = None
    client: Client = None

    def setUp(self):
        self._setup_user()
        self._setup_client()

    def _setup_client(self):
        self.client = Client()
        self.client.force_login(self.user)

    def _setup_user(self):
        username = 'test_user'
        password = secrets.token_urlsafe(10)

        self.user = get_user_model()(username=username)
        self.user.set_password(password)
        self.user.save()

    def test_unauthenticated(self):
        response = Client().post(
            path=self.create_task_path,
            data={},
        )
        self.assertEqual(response.status_code, 403)

    def test_incorrect_create(self):
        response = self.client.post(
            path=self.create_task_path,
            data={
                'filename': '',
                'source': 'invalid source',
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_create_local(self):
        filename = 'test.csv'

        response = self.client.post(
            path=self.create_task_path,
            data={
                'filename': filename,
                'source': Task.Source.LOCAL,
            }
        )
        self.assertEqual(response.status_code, 201)

        response_data = response.json()
        self.assertIn('id', response_data)

        task_id = response_data['id']
        task = Task.objects.get(id=task_id)

        self.assertEqual(task.filename, filename)
        self.assertEqual(task.source, Task.Source.LOCAL)
        self.assertEqual(task.status, Task.Status.NEW)
        self.assertEqual(task.created_by, self.user)


class ActiveTasksCountTestCase(TestCase):
    tasks_list_path = '/tasks/active_tasks_count/'

    user = None
    client: Client = None
    tasks_count = 15
    active_tasks: list[Task] = []

    def setUp(self):
        self._setup_user()
        self._setup_client()
        self._create_tasks()

    def _setup_client(self):
        self.client = Client()
        self.client.force_login(self.user)

    def _setup_user(self):
        username = 'test_user'
        password = secrets.token_urlsafe(10)

        self.user = get_user_model()(username=username)
        self.user.set_password(password)
        self.user.save()

    def _create_tasks(self):
        for idx in range(self.tasks_count):
            match idx % 3:
                case 0:
                    status = Task.Status.NEW
                case 1:
                    status = Task.Status.IN_PROGRESS
                case 2:
                    status = Task.Status.FINISHED
                case _:
                    status = Task.Status.NEW

            task = Task(
                created_by=self.user,
                filename=f'test_{idx}.csv',
                source=Task.Source.LOCAL,
                status=status,
            )
            task.save()
            if status in (Task.Status.NEW, Task.Status.IN_PROGRESS):
                self.active_tasks.append(task)

    def test_unauthenticated(self):
        response = Client().get(self.tasks_list_path)
        self.assertEqual(response.status_code, 403)

    def test_retrieve_active_tasks(self):
        response = self.client.get(self.tasks_list_path)
        self.assertEqual(response.status_code, 200)

        tasks_count = response.json()
        self.assertIsInstance(tasks_count, int)
        self.assertEqual(tasks_count, len(self.active_tasks))


class TaskResultsTestCase(TestCase):
    task_results_path = '/tasks/{task_id}/results/'

    user = None
    client: Client = None
    task: Task = None

    def setUp(self):
        self._setup_user()
        self._setup_client()

    def _setup_client(self):
        self.client = Client()
        self.client.force_login(self.user)

    def _setup_user(self):
        username = 'test_user'
        password = secrets.token_urlsafe(10)

        self.user = get_user_model()(username=username)
        self.user.set_password(password)
        self.user.save()

    def _create_task(self) -> Task:
        task = Task(
            created_by=self.user,
            filename='test.csv',
            source=Task.Source.LOCAL,
        )
        task.save()
        return task

    def test_unfinished_task(self):
        task = self._create_task()
        response = self.client.get(self.task_results_path.format(task_id=task.id))
        self.assertEqual(response.status_code, 400)

        response_data = response.json()
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'Task still in progress')

    def test_not_existing_task(self):
        response = self.client.get(self.task_results_path.format(task_id=1))
        self.assertEqual(response.status_code, 404)

    def test_failed_task(self):
        fail_reason = 'file not found'

        task = self._create_task()
        task.status = Task.Status.FAILED
        task.fail_reason = fail_reason
        task.save()

        response = self.client.get(self.task_results_path.format(task_id=task.id))
        self.assertEqual(response.status_code, 400)

        response_data = response.json()
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], fail_reason)
