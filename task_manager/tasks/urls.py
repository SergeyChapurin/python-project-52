from django.urls import path
from .views import (TasksIndexView,
                    TaskDetailView,
                    TaskCreateView,
                    TaskUpdateView,
                    TaskDeleteView
                    )


urlpatterns = [
    path('', TasksIndexView.as_view(), name='tasks_index'),
    path('<int:pk>/update/', TaskUpdateView.as_view(), name='task_update'),
    path('<int:pk>/delete/', TaskDeleteView.as_view(), name='task_delete'),
    path('<int:pk>/', TaskDetailView.as_view(), name='task_detail'),
    path('create/', TaskCreateView.as_view(), name='task_create')
]
