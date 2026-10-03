from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.attendance_add, name='attendance_add'),
    path('', views.attendance_list, name='attendance'),
    path('my/', views.my_attendance, name='my_attendance'),
]
