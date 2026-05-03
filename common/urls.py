from django.urls import path
from . import views

app_name = 'common'

urlpatterns = [
    path('roles/', views.role_list, name='role_list'),
    path('roles/create/', views.role_create, name='role_create'),
    path('roles/edit/<int:pk>/', views.role_edit, name='role_edit'),
    path('roles/delete/<int:pk>/', views.role_delete, name='role_delete'),
    path('logs/', views.access_logs, name='access_logs'),
]