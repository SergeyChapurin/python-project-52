from django.contrib.auth.models import AbstractUser
from django.urls import reverse


class User(AbstractUser):

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.get_full_name()

    def get_absolute_url(self):
        return reverse('users_index')
