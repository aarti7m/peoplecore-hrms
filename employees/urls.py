
from django.urls import path
from . import views

urlpatterns = [
    path('', views.employee_list, name='employees'),
    path('add/', views.employee_add, name='employee_add'),
    path('<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('<int:pk>/', views.employee_profile, name='employee_profile'),
    path('<int:pk>/toggle-status/', views.employee_toggle_status, name='employee_toggle_status'),
]
