import secrets

from django.contrib.auth import get_user_model
from django.test import Client
from django.test import TestCase

from django_rest import settings

from .models import Task
from .services import make_task_calculations


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
                'storage': 'invalid storage',
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_create_local(self):
        filename = 'test.csv'

        response = self.client.post(
            path=self.create_task_path,
            data={
                'filename': filename,
                'storage': Task.Storage.LOCAL,
            },
        )
        self.assertEqual(response.status_code, 201)

        response_data = response.json()
        self.assertIn('id', response_data)

        task_id = response_data['id']
        task = Task.objects.get(id=task_id)

        self.assertEqual(task.filename, filename)
        self.assertEqual(task.storage, Task.Storage.LOCAL)
        self.assertEqual(task.status, Task.Status.NEW)
        self.assertEqual(task.created_by, self.user)


class ActiveTasksCountTestCase(TestCase):
    TASKS_COUNT = 15
    TASKS_LIST_PATH = '/tasks/active_tasks_count/'

    user = None
    client: Client = None
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
        for idx in range(self.TASKS_COUNT):
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
                storage=Task.Storage.LOCAL,
                status=status,
            )
            task.save()
            if status in (Task.Status.NEW, Task.Status.IN_PROGRESS):
                self.active_tasks.append(task)

    def test_unauthenticated(self):
        response = Client().get(self.TASKS_LIST_PATH)
        self.assertEqual(response.status_code, 403)

    def test_retrieve_active_tasks(self):
        response = self.client.get(self.TASKS_LIST_PATH)
        self.assertEqual(response.status_code, 200)

        tasks_count = response.json()
        self.assertIsInstance(tasks_count, int)
        self.assertEqual(tasks_count, len(self.active_tasks))


class TaskResultsTestCase(TestCase):
    TEST_FILENAME = 'test.csv'
    TEST_FILEPATH = settings.CSV_PATH / TEST_FILENAME
    TEST_FILE_COLUMNS_COUNT = 21
    TEST_FILE_ROWS_COUNT = 5_000
    TASK_RESULTS_PATH_TEMPLATE = '/tasks/{task_id}/results/'

    user = None
    client: Client = None

    def setUp(self):
        self._setup_user()
        self._setup_client()

    def tearDown(self):
        if self.TEST_FILEPATH.exists():
            self.TEST_FILEPATH.unlink()

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
            filename=self.TEST_FILENAME,
            storage=Task.Storage.LOCAL,
        )

        task.save()
        return task

    def _create_test_file(self):
        line = ','.join([str(idx + 1) for idx in range(self.TEST_FILE_COLUMNS_COUNT)])
        line = f'{line}\n'
        lines = [line] * self.TEST_FILE_ROWS_COUNT

        headers = ','.join([f'col{idx}' for idx in range(self.TEST_FILE_COLUMNS_COUNT)])
        lines.insert(0, f'{headers}\n')

        with open(settings.CSV_PATH / self.TEST_FILENAME, 'w') as csv_file:
            csv_file.writelines(lines)

    def test_unfinished_task(self):
        task = self._create_task()
        response = self.client.get(self.TASK_RESULTS_PATH_TEMPLATE.format(task_id=task.id))
        self.assertEqual(response.status_code, 400)

        response_data = response.json()
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'Task still in progress')

    def test_not_existing_task(self):
        response = self.client.get(self.TASK_RESULTS_PATH_TEMPLATE.format(task_id=1))
        self.assertEqual(response.status_code, 404)

    def test_failed_task(self):
        fail_reason = 'file not found'

        task = self._create_task()
        task.status = Task.Status.FAILED
        task.fail_reason = fail_reason
        task.save()

        response = self.client.get(self.TASK_RESULTS_PATH_TEMPLATE.format(task_id=task.id))
        self.assertEqual(response.status_code, 400)

        response_data = response.json()
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], fail_reason)

    def test_finished_task(self):
        columns_count = self.TEST_FILE_COLUMNS_COUNT // 10
        expected_calculations_result = [
            idx * 10 * self.TEST_FILE_ROWS_COUNT
            for idx in range(1, columns_count + 1)
        ]

        task = self._create_task()
        self._create_test_file()
        make_task_calculations(task_id=task.id)

        task.refresh_from_db()
        self.assertEqual(task.status, Task.Status.FINISHED)

        response = self.client.get(self.TASK_RESULTS_PATH_TEMPLATE.format(task_id=task.id))
        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        self.assertIsInstance(response_data, list)
        self.assertEqual(len(response_data), columns_count)
        self.assertEqual(response_data, expected_calculations_result)
