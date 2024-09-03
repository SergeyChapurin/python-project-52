from django.test import TestCase, Client
from django.urls import reverse
from task_manager.users.models import User
from django.utils.translation import gettext as _
from django.contrib.messages import get_messages


class HomeTest(TestCase):

    def test_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn(_('Менеджер задач'), content)
        self.assertIn(_('Пользователи'), content)
        self.assertIn(_('Практические курсы по программированию'), content)


class UsersIndexViewTest(TestCase):
    fixtures = ['fixtures/users.json']

    def setUp(self):
        self.url = reverse('users_index')

    def test_users_index_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/users_index.html')
        content = response.content.decode()
        self.assertIn('Гудвин', content)
        self.assertIn('Фил', content)
        self.assertIn('Родри', content)
        self.assertIn('Гюндо', content)
        self.assertIn('Рубен', content)
        self.assertIn('Кевин', content)
        self.assertIn('Ден', content)


class CreateUserTest(TestCase):
    fixtures = ['fixtures/users.json']

    def setUp(self):
        self.register_url = reverse('user_create')
        self.empty_form = {
            'first_name': '',
            'last_name': '',
            'username': '',
            'password1': '',
            'password2': '',
        }
        self.user = {
            'first_name': 'Имя1',
            'last_name': 'Фамилия1',
            'username': 'Пользователь1',
            'password1': '123',
            'password2': '123',
        }
        self.user_with_short_password = {
            'first_name': 'Имя2',
            'last_name': 'Фамилия2',
            'username': 'Пользователь2',
            'password1': '12',
            'password2': '12',
        }
        self.user_with_invalid_username = {
            'first_name': 'Имя3',
            'last_name': 'Фамилия3',
            'username': 'Пользователь$',
            'password1': '123',
            'password2': '123',
        }

    def test_can_view_page_correctly(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/user_create.html')

    def test_empty_form(self):
        response = self.client.post(self.register_url, self.empty_form)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn(_('Обязательное поле.'), form.errors.get('username', []))

    def test_can_register_user(self):
        response = self.client.post(self.register_url, self.user)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='Пользователь1').exists())

    def test_cant_register_user_with_short_password(self):
        response = self.client.post(self.register_url, self.user_with_short_password)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn(
            _('Введённый пароль слишком короткий. '
              'Он должен содержать как минимум 3 символа.'),
            form.errors.get('password2', []))

    def test_cant_register_user_with_invalid_username(self):
        response = self.client.post(self.register_url, self.user_with_invalid_username)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn(
            _('Введите правильное имя пользователя. '
              'Оно может содержать только буквы, цифры и знаки @/./+/-/_.'),
            form.errors.get('username', []))

    def test_cant_register_user_with_taken_username(self):
        self.client.post(self.register_url, self.user)
        response = self.client.post(self.register_url, self.user)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn(
            _('Пользователь с таким именем уже существует.'),
            form.errors.get('username', []))

    def test_create_user(self):
        response = self.client.post(self.register_url, self.user, follow=True)
        self.assertRedirects(response, reverse('login'))
        new_user = User.objects.last()
        self.assertEqual(self.user['username'], new_user.username)


class UpdateUserTest(TestCase):
    fixtures = ['fixtures/users.json']

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.get(pk=4)
        self.user2 = User.objects.get(pk=5)
        self.valid_data = {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'username': 'Иванушка',
            'password1': '123',
            'password2': '123',
        }
        self.invalid_data = {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'username': 'Иванушка',
            'password1': '123',
            'password2': '456',
        }

    def test_update_user_successfully(self):
        self.client.force_login(self.user1)
        update_url = reverse('user_update', args=[self.user1.pk])
        post_response = self.client.post(update_url, self.valid_data, follow=True)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.username, 'Иванушка')
        self.assertRedirects(post_response, reverse('users_index'))
        messages = list(get_messages(post_response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), _("Пользователь успешно изменен"))

    def test_update_user_without_permissions(self):
        self.client.force_login(self.user2)
        update_url = reverse('user_update', args=[self.user1.pk])
        get_response = self.client.get(update_url)
        self.assertRedirects(get_response, reverse('users_index'))
        messages = list(get_messages(get_response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            _("У вас нет прав для изменения другого пользователя.")
        )

    def test_update_user_with_invalid_data(self):
        self.client.force_login(self.user1)
        update_url = reverse('user_update', args=[self.user1.pk])
        post_response = self.client.post(update_url, self.invalid_data, follow=True)
        self.user1.refresh_from_db()
        self.assertNotEqual(self.user1.username, '')
        self.assertContains(post_response, "Введенные пароли не совпадают.")


class DeleteUserTest(TestCase):
    fixtures = ['fixtures/users.json']

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.get(pk=4)
        self.user2 = User.objects.get(pk=5)

    def test_delete_user_successfully(self):
        self.client.force_login(self.user1)
        delete_url = reverse('user_delete', args=[self.user1.pk])
        post_response = self.client.post(delete_url, follow=True)
        self.assertRedirects(post_response, reverse('users_index'))
        messages = list(get_messages(post_response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), _("Пользователь успешно удален"))

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(pk=self.user1.pk)

    def test_delete_user_without_permissions(self):
        self.client.force_login(self.user2)
        delete_url = reverse('user_delete', args=[self.user1.pk])
        get_response = self.client.get(delete_url)

        # Проверка, что пользователь без прав
        # не может удалить другого пользователя
        self.assertRedirects(get_response, reverse('users_index'))
        messages = list(get_messages(get_response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            _("У вас нет прав для изменения другого пользователя.")
        )
