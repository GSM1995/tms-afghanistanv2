from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from orders.models import Order, Customer, Driver, Vehicle
from finance.models import Invoice
from tracking.models import VehicleLocation

@staff_member_required
def admin_dashboard(request):
    """داشبورد ادمین با آمار و اطلاعات"""
    
    # آمار کلی
    total_orders = Order.objects.count()
    total_customers = Customer.objects.count()
    total_drivers = Driver.objects.count()
    total_vehicles = Vehicle.objects.count()
    
    # آمار مالی
    total_invoices = Invoice.objects.aggregate(total=Sum('total'))['total'] or 0
    
    # خودروهای فعال (با موقعیت اخیر)
    active_vehicles = VehicleLocation.objects.values('vehicle').distinct().count()
    
    # آخرین 5 سفارش
    recent_orders = Order.objects.all().select_related('customer')[:5]
    
    # آخرین 5 فاکتور
    recent_invoices = Invoice.objects.all().select_related('customer')[:5]
    
    context = {
        'total_orders': total_orders,
        'total_customers': total_customers,
        'total_drivers': total_drivers,
        'total_vehicles': total_vehicles,
        'total_invoices': total_invoices,
        'active_vehicles': active_vehicles,
        'recent_orders': recent_orders,
        'recent_invoices': recent_invoices,
    }
    
    return render(request, 'admin_dashboard.html', context)