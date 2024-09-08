from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.contrib import messages


class CustomLoginRequiredMixin(LoginRequiredMixin):
    login_message = _("Вы не авторизованы! Пожалуйста, выполните вход.")
    login_url = 'login'

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            messages.error(
                self.request,
                self.login_message,
                extra_tags='danger'
            )
            return redirect(self.login_url)
        return super().handle_no_permission()


class CheckUserMixin(UserPassesTestMixin):
    permission_denied_message = _("У вас нет прав для изменения другого пользователя.")

    def test_func(self):
        return self.request.user.pk == self.get_object().pk

    def handle_no_permission(self):
        messages.error(
            self.request,
            self.permission_denied_message,
            extra_tags='danger'
        )
        return redirect(reverse_lazy('users_index'))


class CheckAuthorMixin(UserPassesTestMixin):
    permission_denied_message = _("Задачу может удалить только ее автор")

    def test_func(self):
        task = self.get_object()
        return self.request.user.pk == task.author.pk

    def handle_no_permission(self):
        messages.error(
            self.request,
            self.permission_denied_message,
            extra_tags='danger'
        )
        return redirect(reverse_lazy('tasks_index'))


class ProtectedErrorMixin:
    error_message = _("Невозможно удалить пользователя, потому что он используется")
    redirect_url = 'users_index'

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(
                request,
                self.error_message,
                extra_tags='danger'
            )
            return redirect(self.redirect_url)
