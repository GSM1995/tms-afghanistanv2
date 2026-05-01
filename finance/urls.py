from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_report, name='finance_dashboard'),
    path('export/orders/excel/', views.export_orders_excel, name='export_orders_excel'),
    path('export/invoices/excel/', views.export_invoices_excel, name='export_invoices_excel'),
]