from django.urls import path
from .views import StatusesIndexView, StatusCreateView, StatusUpdateView, StatusDeleteView

urlpatterns = [
    path('', StatusesIndexView.as_view(), name='statuses_index'),
    path('<int:pk>/update/', StatusUpdateView.as_view(), name='status_update'),
    path('<int:pk>/delete/', StatusDeleteView.as_view(), name='status_delete'),
    path('create/', StatusCreateView.as_view(), name='status_create')
]
