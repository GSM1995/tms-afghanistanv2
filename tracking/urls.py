from django.urls import path
from . import views

urlpatterns = [
    path('api/update-location/', views.update_location, name='update_location'),
    path('api/locations/', views.vehicle_latest_locations, name='latest_locations'),
    path('api/vehicle-history/<int:vehicle_id>/', views.vehicle_history, name='vehicle_history'),
    path('map/', views.vehicle_tracking, name='tracking_map'),
]