from django.urls import path
from . import views

urlpatterns = [
    path('', views.department_list, name='departments'),
    path('add/', views.department_add, name='department_add'),
    path('<int:pk>/edit/', views.department_edit, name='department_edit'),
    path('<int:pk>/delete/', views.department_delete, name='department_delete'),
]
