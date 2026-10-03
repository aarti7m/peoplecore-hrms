from django.urls import path
from . import views

urlpatterns = [
    path('<int:pk>/edit/', views.announcement_edit, name='announcement_edit'),
    path('', views.announcement_list, name='announcements'),
    path('<int:pk>/delete/', views.announcement_delete, name='announcement_delete'),
]
