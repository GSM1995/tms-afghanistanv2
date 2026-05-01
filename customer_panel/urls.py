from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.customer_login_view, name='customer_login'),
    path('dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('orders/', views.customer_orders, name='customer_orders'),
    path('order/<int:order_id>/', views.customer_order_detail, name='customer_order_detail'),
    path('invoices/', views.customer_invoices, name='customer_invoices'),
    path('logout/', views.customer_logout_view, name='customer_logout'),
    path('track/<int:order_id>/', views.track_order, name='track_order'),
]