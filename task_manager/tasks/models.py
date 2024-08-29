from django.db import models
from django.utils.translation import gettext as _

from task_manager.labels.models import Label
from task_manager.users.models import User
from task_manager.statuses.models import Status


class Task(models.Model):

    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name=_('Имя')
    )

    description = models.TextField(
        blank=True,
        verbose_name=_('Описание')
    )

    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='author',
        verbose_name=_('Автор')
    )

    executor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        blank=True, null=True,
        related_name='executor',
        verbose_name=_('Исполнитель')
    )

    status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        related_name='status',
        verbose_name=_('Статус')
    )

    labels = models.ManyToManyField(
        Label,
        through='IntermediateLabelForTask',
        related_name='labels',
        verbose_name=_('Метки'),
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name


class IntermediateLabelForTask(models.Model):
    label = models.ForeignKey(
        Label,
        on_delete=models.PROTECT
    )

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE
    )
