from django.test import TestCase, Client
from django.urls import reverse
from django.utils.translation import gettext as _

from task_manager.statuses.models import Status
from task_manager.tasks.models import Task
from task_manager.users.models import User
from task_manager.labels.models import Label


class LabelTestCase(TestCase):
    fixtures = [
        "fixtures/tasks.json",
        "fixtures/users.json",
        "fixtures/statuses.json",
        "fixtures/labels.json",
    ]

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.get(pk=7)
        self.task1 = Task.objects.get(pk=5)
        self.status1 = Status.objects.get(pk=1)
        self.label1 = Label.objects.get(pk=1)
        self.create_data = {'name': 'Новая метка'}
        self.update_data = {'name': 'Обновленная метка'}
        self.label_no_tasks = Label.objects.create(name='Метка без задач')
        self.task = Task.objects.create(
            name='Тестовая задача',
            description='Описание тестовой задачи',
            status=self.status1,
            executor=self.user1,
            author=self.user1
        )
        self.task.labels.add(self.label1)
        # Добавляем метку к задаче методом add из-за связи ManyToManyField

    def test_create_label_logged_in_user(self):
        self.client.force_login(self.user1)
        create_url = reverse('label_create')
        response = self.client.post(create_url, self.create_data, follow=True)
        self.assertRedirects(response, reverse('labels_index'))
        self.assertTrue(Label.objects.filter(name='Новая метка').exists())
        self.assertContains(response, _("Метка успешно создана"))

    def test_update_label_logged_in_user(self):
        self.client.force_login(self.user1)
        update_url = reverse('label_update', args=[self.label1.pk])
        response = self.client.post(update_url, self.update_data, follow=True)
        self.assertRedirects(response, reverse('labels_index'))
        self.label1.refresh_from_db()
        self.assertEqual(self.label1.name, 'Обновленная метка')
        self.assertContains(response, _("Метка успешно изменена"))

    def test_delete_label_not_related_to_tasks(self):
        self.client.force_login(self.user1)
        delete_url = reverse('label_delete', args=[self.label_no_tasks.pk])
        response = self.client.post(delete_url, follow=True)
        self.assertRedirects(response, reverse('labels_index'))
        self.assertFalse(Label.objects.filter(pk=self.label_no_tasks.pk).exists())
        self.assertContains(response, _("Метка успешно удалена"))

    def test_delete_label_related_to_tasks(self):
        self.client.force_login(self.user1)
        delete_url = reverse('label_delete', args=[self.label1.pk])
        response = self.client.post(delete_url, follow=True)
        self.assertRedirects(response, reverse('labels_index'))
        self.assertTrue(Label.objects.filter(pk=self.label1.pk).exists())
        self.assertContains(
            response,
            _("Невозможно удалить метку, потому что она используется")
        )
