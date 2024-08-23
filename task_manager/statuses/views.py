from django.utils.translation import gettext as _
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from task_manager.mixins import CustomLoginRequiredMixin
from task_manager.statuses.forms import StatusForm
from task_manager.statuses.models import Status


class StatusesIndexView(CustomLoginRequiredMixin, ListView):
    model = Status
    template_name = 'statuses/statuses_index.html'
    context_object_name = 'statuses'


class StatusCreateView(CustomLoginRequiredMixin,
                       SuccessMessageMixin,
                       CreateView):
    model = Status
    form_class = StatusForm
    template_name = 'statuses/status_create.html'
    success_url = reverse_lazy('statuses_index')
    success_message = _("Статус успешно создан")


class StatusUpdateView(CustomLoginRequiredMixin,
                       SuccessMessageMixin,
                       UpdateView):
    model = Status
    form_class = StatusForm
    template_name = 'statuses/status_update.html'
    success_url = reverse_lazy('statuses_index')
    success_message = _('Статус успешно изменен')


class StatusDeleteView(CustomLoginRequiredMixin,
                       SuccessMessageMixin,
                       DeleteView):
    model = Status
    template_name = 'statuses/status_delete.html'
    success_url = reverse_lazy('statuses_index')
    success_message = _('Статус успешно удален')
