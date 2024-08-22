from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView, LogoutView
# from django.urls import reverse_lazy
from django.contrib import messages
from .users.models import User
from django.utils.translation import gettext_lazy as _


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label=_('Имя пользователя'), widget=forms.TextInput)
    password = forms.CharField(label=_('Пароль'), widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password']


class IndexView(TemplateView):
    template_name = 'index.html'


class LoginView(SuccessMessageMixin, LoginView):
    template_name = 'login.html'
    success_message = _('Вы залогинены')


class LogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, _('Вы разлогинены'))
        return super().dispatch(request, *args, **kwargs)
