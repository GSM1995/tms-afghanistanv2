from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.driver_login_view, name='driver_login'),
    path('dashboard/', views.driver_dashboard, name='driver_dashboard'),
    path('accept/<int:request_id>/', views.accept_order, name='accept_order'),
    path('reject/<int:request_id>/', views.reject_order, name='reject_order'),
    path('update-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('logout/', views.driver_logout_view, name='driver_logout'),
    path('api/update-location/', views.update_location_api, name='update_location_api'),
    path('api/locations/', views.driver_locations, name='driver_locations'),
]