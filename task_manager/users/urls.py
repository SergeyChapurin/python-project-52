from django.urls import path
from .views import UsersIndexView, UserCreateView, UserUpdateView, UserDeleteView


urlpatterns = [
    path('', UsersIndexView.as_view(), name='users_index'),
    path('<int:pk>/update/', UserUpdateView.as_view(), name='user_update'),
    path('<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
    path('create/', UserCreateView.as_view(), name='user_create'),
]
