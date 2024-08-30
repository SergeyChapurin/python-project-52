from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from django.utils.translation import gettext as _
from django_filters.views import FilterView

from task_manager.mixins import CustomLoginRequiredMixin, CheckAuthorMixin
from task_manager.tasks.filter import FilterTasks
from task_manager.tasks.forms import TaskForm
from task_manager.tasks.models import Task


class TasksIndexView(CustomLoginRequiredMixin, FilterView):
    model = Task
    template_name = 'tasks/tasks_index.html'
    filterset_class = FilterTasks
    context_object_name = 'filtered_tasks'


class TaskDetailView(DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'


class TaskCreateView(CustomLoginRequiredMixin,
                     SuccessMessageMixin,
                     CreateView):

    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_create.html'
    success_url = reverse_lazy('tasks_index')
    success_message = _('Задача успешно создана')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class TaskUpdateView(CustomLoginRequiredMixin,
                     SuccessMessageMixin,
                     UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_update.html'
    success_url = reverse_lazy('tasks_index')
    success_message = _('Задача успешно изменена')


class TaskDeleteView(CustomLoginRequiredMixin,
                     CheckAuthorMixin,
                     SuccessMessageMixin,
                     DeleteView):
    model = Task
    template_name = 'tasks/task_delete.html'
    success_url = reverse_lazy('tasks_index')
    success_message = _('Задача успешно удалена')
