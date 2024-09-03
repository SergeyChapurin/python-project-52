from django.test import TestCase, Client
from django.urls import reverse
from django.utils.translation import gettext as _
from urllib.parse import urlencode

from task_manager.tasks.models import Task
from task_manager.users.models import User
from task_manager.statuses.models import Status
from task_manager.labels.models import Label


class TaskTestCase(TestCase):
    fixtures = [
        "fixtures/tasks.json",
        "fixtures/users.json",
        "fixtures/statuses.json",
        "fixtures/labels.json"
    ]

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.get(pk=7)
        self.user2 = User.objects.get(pk=8)
        self.task1 = Task.objects.get(pk=5)

        self.create_data = {
            'name': 'Новая задача',
            'description': 'Новое опсиание',
            'status': 1,
            'executor': 1,
            'label': '',
        }

        self.update_data = {
            'name': 'Обновленная задача',
            'description': 'Обновленное описание',
            'status': 5,
            'executor': 6,
            'label': '',
        }

    def test_task_detail_view(self):
        # Авторизация пользователя
        self.client.force_login(self.user1)
        detail_url = reverse('task_detail', args=[self.task1.pk])
        # Отправка GET-запроса на получение страницы задачи
        response = self.client.get(detail_url)
        # Проверка, что статус ответа 200 (OK)
        self.assertEqual(response.status_code, 200)
        # Проверка, что данные задачи отображаются на странице
        self.assertContains(response, self.task1.name)
        self.assertContains(response, self.task1.description)
        self.assertContains(response, self.task1.author)
        self.assertContains(response, self.task1.executor)
        self.assertContains(response, self.task1.status.name)
        # Проверка меток
        if self.task1.labels.exists():
            for label in self.task1.labels.all():
                self.assertContains(response, label.name)
        else:
            # Проверка, что список меток полностью отсутствует
            self.assertNotContains(response, '<ul></ul>')

        # Проверка наличия ссылок для изменения и удаления задачи
        self.assertContains(response, reverse('task_update', args=[self.task1.pk]))
        self.assertContains(response, reverse('task_delete', args=[self.task1.pk]))

    def test_create_task_logged_in_user(self):
        self.client.force_login(self.user1)
        create_url = reverse('task_create')
        response = self.client.post(create_url, self.create_data, follow=True)
        self.assertRedirects(response, reverse('tasks_index'))
        self.assertTrue(Task.objects.filter(name='Новая задача').exists())
        self.assertContains(response, _("Задача успешно создана"))

    def test_update_task_logged_in_user(self):
        self.client.force_login(self.user1)
        update_url = reverse('task_update', args=[self.task1.pk])
        response = self.client.post(update_url, self.update_data, follow=True)
        self.assertRedirects(response, reverse('tasks_index'))
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.name, 'Обновленная задача')
        self.assertContains(response, _("Задача успешно изменена"))

    def test_delete_task_only_author(self):
        # Проверяем, что автор может удалить задачу
        self.client.force_login(self.user1)
        delete_url = reverse('task_delete', args=[self.task1.pk])
        response = self.client.post(delete_url, follow=True)
        self.assertRedirects(response, reverse('tasks_index'))
        self.assertFalse(Task.objects.filter(pk=self.task1.pk).exists())
        self.assertContains(response, _("Задача успешно удалена"))

        # Проверяем, что другой пользователь не может удалить задачу
        self.client.force_login(self.user2)
        self.task2 = Task.objects.create(
            name='Тест удаления',
            description='тест',
            status_id=1,
            author=self.user1
        )
        delete_url = reverse('task_delete', args=[self.task2.pk])
        response = self.client.post(delete_url, follow=True)
        self.assertRedirects(response, reverse('tasks_index'))
        self.assertTrue(Task.objects.filter(pk=self.task2.pk).exists())
        self.assertContains(response, _("Задачу может удалить только ее автор"))


class TaskFilterTestCase(TestCase):
    fixtures = [
        "fixtures/tasks.json",
        "fixtures/users.json",
        "fixtures/statuses.json",
        "fixtures/labels.json"
    ]

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.get(pk=7)
        self.user2 = User.objects.get(pk=8)
        self.tasks_list_url = reverse('tasks_index')

    def test_filter_by_status(self):
        self.client.force_login(self.user1)
        status = Status.objects.get(pk=1)
        response = self.client.get(f'{self.tasks_list_url}?status={status.pk}')
        filtered_tasks = response.context['filtered_tasks']

        # Проверяем, что все отфильтрованные задачи имеют нужный статус
        for task in filtered_tasks:
            self.assertEqual(task.status, status)

    def test_filter_by_executor(self):
        self.client.force_login(self.user1)
        executor = self.user2
        response = self.client.get(f'{self.tasks_list_url}?executor={executor.pk}')
        filtered_tasks = response.context['filtered_tasks']

        # Проверяем, что все отфильтрованные задачи назначены нужному исполнителю
        for task in filtered_tasks:
            self.assertEqual(task.executor, executor)

    def test_filter_by_label(self):
        self.client.force_login(self.user1)
        label = Label.objects.get(pk=1)
        response = self.client.get(f'{self.tasks_list_url}?labels={label.pk}')
        filtered_tasks = response.context['filtered_tasks']

        # Проверяем, что все отфильтрованные задачи имеют нужную метку
        for task in filtered_tasks:
            self.assertIn(label, task.labels.all())

    def test_filter_by_self_tasks(self):
        self.client.force_login(self.user1)
        response = self.client.get(f'{self.tasks_list_url}?self_tasks=on')
        filtered_tasks = response.context['filtered_tasks']

        # Проверяем, что все отфильтрованные задачи принадлежат текущему пользователю
        # (автором является user1)
        for task in filtered_tasks:
            self.assertEqual(task.author, self.user1)

    def test_combined_filters(self):
        self.client.force_login(self.user1)
        status = Status.objects.get(pk=1)
        executor = self.user2
        label = Label.objects.get(pk=1)
        query_params = {
            'status': status.pk,
            'executor': executor.pk,
            'labels': label.pk,
            'self_tasks': 'on'
        }
        response = self.client.get(f'{self.tasks_list_url}?{urlencode(query_params)}')
        filtered_tasks = response.context['filtered_tasks']

        # Проверяем, что все отфильтрованные задачи соответствуют всем критериям фильтрации
        for task in filtered_tasks:
            self.assertEqual(task.status, status)
            self.assertEqual(task.executor, executor)
            self.assertIn(label, task.labels.all())
            self.assertEqual(task.author, self.user1)
