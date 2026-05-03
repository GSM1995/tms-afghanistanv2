from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from orders.models import Order, Customer, Driver, Vehicle
from finance.models import Invoice
from tracking.models import VehicleLocation
from common.decorators import role_required


@login_required
@role_required('can_view_reports')  # فقط کاربرانی که دسترسی گزارش دارند
def admin_dashboard(request):
    """داشبورد ادمین با آمار و اطلاعات"""
    
    # بررسی کن که کاربر ادمین است یا فقط گزارش‌بین
    is_admin = request.user.is_superuser or request.user.is_staff
    
    # آمار کلی
    total_orders = Order.objects.count()
    total_customers = Customer.objects.count()
    total_drivers = Driver.objects.count()
    total_vehicles = Vehicle.objects.count()
    
    # آمار مالی
    total_invoices = Invoice.objects.aggregate(total=Sum('total'))['total'] or 0
    
    # خودروهای فعال (با موقعیت اخیر)
    active_vehicles = VehicleLocation.objects.values('vehicle').distinct().count()
    
    # آخرین 10 سفارش
    recent_orders = Order.objects.all().select_related('customer')[:10]
    
    # آخرین 10 فاکتور
    recent_invoices = Invoice.objects.all().select_related('customer')[:10]
    
    context = {
        'total_orders': total_orders,
        'total_customers': total_customers,
        'total_drivers': total_drivers,
        'total_vehicles': total_vehicles,
        'total_invoices': total_invoices,
        'active_vehicles': active_vehicles,
        'recent_orders': recent_orders,
        'recent_invoices': recent_invoices,
        'is_admin': is_admin,  # برای نمایش یا عدم نمایش بعضی گزینه‌ها
    }
    
    return render(request, 'admin_dashboard.html', context)