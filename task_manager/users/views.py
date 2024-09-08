from django.utils.translation import gettext as _
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)
from task_manager.users.forms import UsersForm
from task_manager.users.models import User
from task_manager.mixins import (
    CustomLoginRequiredMixin,
    CheckUserMixin,
    ProtectedErrorMixin
)


class UsersIndexView(ListView):
    model = User
    template_name = 'users/users_index.html'
    context_object_name = 'users'


class UserCreateView(SuccessMessageMixin, CreateView):
    model = User
    form_class = UsersForm
    template_name = 'users/user_create.html'
    success_url = reverse_lazy('login')
    success_message = _("Пользователь успешно зарегистрирован")


class UserUpdateView(CustomLoginRequiredMixin,
                     CheckUserMixin,
                     SuccessMessageMixin,
                     UpdateView):
    model = User
    form_class = UsersForm
    template_name = 'users/user_update.html'
    success_url = reverse_lazy('users_index')
    success_message = _('Пользователь успешно изменен')


class UserDeleteView(CustomLoginRequiredMixin,
                     CheckUserMixin,
                     SuccessMessageMixin,
                     ProtectedErrorMixin,
                     DeleteView):
    model = User
    template_name = 'users/user_delete.html'
    success_url = reverse_lazy('users_index')
    success_message = _('Пользователь успешно удален')
