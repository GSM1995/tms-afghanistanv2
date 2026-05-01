from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order, Customer
from finance.models import Invoice, Payment
from tracking.models import VehicleLocation
from django.db.models import Sum
from django.utils import timezone
import json

def customer_login_view(request):
    """صفحه ورود مشتری"""
    if request.user.is_authenticated:
        return redirect('customer_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            try:
                customer = Customer.objects.get(user=user)
                login(request, user)
                return redirect('customer_dashboard')
            except Customer.DoesNotExist:
                return render(request, 'customer_panel/login.html', {'error': 'این کاربر دسترسی مشتری ندارد'})
        else:
            return render(request, 'customer_panel/login.html', {'error': 'نام کاربری یا رمز عبور اشتباه است'})
    
    return render(request, 'customer_panel/login.html')

@login_required
def customer_dashboard(request):
    """داشبورد مشتری"""
    try:
        customer = Customer.objects.get(user=request.user)
    except Customer.DoesNotExist:
        return redirect('customer_login')
    
    orders = Order.objects.filter(customer=customer).order_by('-created_at')
    
    total_orders = orders.count()
    total_invoices = Invoice.objects.filter(customer=customer).aggregate(total=Sum('total'))['total'] or 0
    pending_invoices = Invoice.objects.filter(customer=customer, status='sent').aggregate(total=Sum('total'))['total'] or 0
    delivered_orders = orders.filter(status='delivered').count()
    in_transit_orders = orders.filter(status='in_transit').count()
    
    context = {
        'customer': customer,
        'total_orders': total_orders,
        'total_invoices': total_invoices,
        'pending_invoices': pending_invoices,
        'delivered_orders': delivered_orders,
        'in_transit_orders': in_transit_orders,
        'recent_orders': orders[:5],
    }
    return render(request, 'customer_panel/dashboard.html', context)

@login_required
def customer_orders(request):
    """لیست سفارشات مشتری"""
    try:
        customer = Customer.objects.get(user=request.user)
    except Customer.DoesNotExist:
        return redirect('customer_login')
    
    orders = Order.objects.filter(customer=customer).order_by('-created_at')
    return render(request, 'customer_panel/orders.html', {'orders': orders})

@login_required
def customer_order_detail(request, order_id):
    """جزئیات یک سفارش"""
    try:
        customer = Customer.objects.get(user=request.user)
        order = Order.objects.get(id=order_id, customer=customer)
    except (Customer.DoesNotExist, Order.DoesNotExist):
        return redirect('customer_orders')
    
    current_location = None
    if order.vehicle and order.status == 'in_transit':
        current_location = VehicleLocation.objects.filter(vehicle=order.vehicle).first()
    
    invoices = Invoice.objects.filter(order=order)
    
    context = {
        'order': order,
        'current_location': current_location,
        'invoices': invoices,
    }
    return render(request, 'customer_panel/order_detail.html', context)

@login_required
def customer_invoices(request):
    """لیست فاکتورهای مشتری"""
    try:
        customer = Customer.objects.get(user=request.user)
    except Customer.DoesNotExist:
        return redirect('customer_login')
    
    invoices = Invoice.objects.filter(customer=customer).order_by('-issue_date')
    return render(request, 'customer_panel/invoices.html', {'invoices': invoices})

@login_required
def customer_logout_view(request):
    """خروج مشتری"""
    logout(request)
    return redirect('customer_login')

@login_required
def track_order(request, order_id):
    """ردیابی سفارش روی نقشه (API)"""
    try:
        customer = Customer.objects.get(user=request.user)
        order = Order.objects.get(id=order_id, customer=customer)
    except (Customer.DoesNotExist, Order.DoesNotExist):
        return JsonResponse({'error': 'دسترسی غیرمجاز'}, status=403)
    
    if order.vehicle and order.status == 'in_transit':
        location = VehicleLocation.objects.filter(vehicle=order.vehicle).first()
        if location:
            return JsonResponse({
                'latitude': str(location.latitude),
                'longitude': str(location.longitude),
                'speed': str(location.speed),
                'last_update': location.location_time.isoformat(),
            })
    
    return JsonResponse({'error': 'موقعیتی یافت نشد'}, status=404)