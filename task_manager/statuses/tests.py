from django.test import TestCase, Client
from django.urls import reverse
from django.utils.translation import gettext as _

from task_manager.tasks.models import Task
from task_manager.users.models import User
from task_manager.statuses.models import Status


class StatusTestCase(TestCase):
    fixtures = [
        "fixtures/tasks.json",
        "fixtures/users.json",
        "fixtures/statuses.json",
    ]

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.get(pk=7)
        self.task1 = Task.objects.get(pk=5)
        self.status1 = Status.objects.get(pk=1)
        self.create_data = {'name': 'Новый статус'}
        self.update_data = {'name': 'Обновленный статус'}
        self.status_no_tasks = Status.objects.create(name='Статус без задач')
        self.task = Task.objects.create(
            name='Тестовая задача',
            description='Описание тестовой задачи',
            status=self.status1,
            executor=self.user1,
            author=self.user1
        )

    def test_create_status_logged_in_user(self):
        self.client.force_login(self.user1)
        create_url = reverse('status_create')
        response = self.client.post(create_url, self.create_data, follow=True)
        self.assertRedirects(response, reverse('statuses_index'))
        self.assertTrue(Status.objects.filter(name='Новый статус').exists())
        self.assertContains(response, _("Статус успешно создан"))

    def test_update_status_logged_in_user(self):
        self.client.force_login(self.user1)
        update_url = reverse('status_update', args=[self.status1.pk])
        response = self.client.post(update_url, self.update_data, follow=True)
        self.assertRedirects(response, reverse('statuses_index'))
        self.status1.refresh_from_db()
        self.assertEqual(self.status1.name, 'Обновленный статус')
        self.assertContains(response, _("Статус успешно изменен"))

    def test_delete_status_not_related_to_tasks(self):
        self.client.force_login(self.user1)
        delete_url = reverse('status_delete', args=[self.status_no_tasks.pk])
        response = self.client.post(delete_url, follow=True)
        self.assertRedirects(response, reverse('statuses_index'))
        self.assertFalse(Status.objects.filter(pk=self.status_no_tasks.pk).exists())
        self.assertContains(response, _("Статус успешно удален"))

    def test_delete_status_related_to_tasks(self):
        self.client.force_login(self.user1)
        delete_url = reverse('status_delete', args=[self.status1.pk])
        response = self.client.post(delete_url, follow=True)
        self.assertRedirects(response, reverse('statuses_index'))
        self.assertTrue(Status.objects.filter(pk=self.status1.pk).exists())
        self.assertContains(
            response,
            _("Невозможно удалить статус, потому что он используется")
        )
