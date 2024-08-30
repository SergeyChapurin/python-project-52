import django_filters
from django import forms
from django.utils.translation import gettext as _
from .models import Task
from ..labels.models import Label
from ..statuses.models import Status
from ..users.models import User


class FilterTasks(django_filters.FilterSet):
    status = django_filters.ModelChoiceFilter(queryset=Status.objects.all(),
                                              label=_('Статус'))
    executor = django_filters.ModelChoiceFilter(queryset=User.objects.all(),
                                                label=_('Исполнитель'))
    labels = django_filters.ModelChoiceFilter(queryset=Label.objects.all(),
                                              label=_('Метка'))
    self_tasks = django_filters.BooleanFilter(method='filter_self_tasks',
                                              widget=forms.CheckboxInput,
                                              label=_('Только свои задачи'))

    class Meta:
        model = Task
        fields = ['status', 'executor', 'labels']

    def filter_self_tasks(self, queryset, arg, value):
        if value:
            return queryset.filter(author=self.request.user)
        return queryset
