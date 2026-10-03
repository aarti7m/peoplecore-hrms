from django.urls import path
from . import views

urlpatterns = [
    path('', views.salary_list, name='salary'),
    path('add/', views.salary_add, name='salary_add'),
    path('<int:pk>/edit/', views.salary_edit, name='salary_edit'),
    path('my/', views.my_salary, name='my_salary'),
]
