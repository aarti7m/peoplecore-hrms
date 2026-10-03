from django.urls import path
from . import views

urlpatterns = [
    path('', views.leave_list, name='leaves'),
    path('apply/', views.apply_leave, name='apply_leave'),
    path('<int:pk>/approve/', views.approve_leave, name='approve_leave'),
    path('<int:pk>/reject/', views.reject_leave, name='reject_leave'),
]
