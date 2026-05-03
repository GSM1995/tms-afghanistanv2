from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.http import JsonResponse
from django.contrib import messages
from orders.models import Order, Customer
from finance.models import Invoice, Payment
from tracking.models import VehicleLocation
from django.db.models import Sum
from django.utils import timezone
import json


def customer_login_view(request):
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
                messages.success(request, f'خوش آمدید {customer.name}')
                return redirect('customer_dashboard')
            except Customer.DoesNotExist:
                messages.error(request, 'شما دسترسی مشتری ندارید')
                return render(request, 'customer_panel/login.html')
        else:
            messages.error(request, 'نام کاربری یا رمز عبور اشتباه است')
            return render(request, 'customer_panel/login.html')
    
    return render(request, 'customer_panel/login.html')


@login_required
def customer_dashboard(request):
    try:
        customer = Customer.objects.get(user=request.user)
    except Customer.DoesNotExist:
        messages.error(request, 'شما دسترسی مشتری ندارید')
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
    try:
        customer = Customer.objects.get(user=request.user)
    except Customer.DoesNotExist:
        return redirect('customer_login')
    
    orders = Order.objects.filter(customer=customer).order_by('-created_at')
    return render(request, 'customer_panel/orders.html', {'orders': orders})


@login_required
def customer_order_detail(request, order_id):
    try:
        customer = Customer.objects.get(user=request.user)
        order = Order.objects.get(id=order_id, customer=customer)
    except (Customer.DoesNotExist, Order.DoesNotExist):
        messages.error(request, 'سفارش مورد نظر یافت نشد.')
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
def customer_order_create(request):
    """ثبت سفارش جدید توسط مشتری"""
    try:
        customer = Customer.objects.get(user=request.user)
    except Customer.DoesNotExist:
        messages.error(request, 'شما دسترسی مشتری ندارید')
        return redirect('customer_login')
    
    if request.method == 'POST':
        # دریافت اطلاعات از فرم
        order_number = request.POST.get('order_number')
        origin = request.POST.get('origin')
        destination = request.POST.get('destination')
        cargo_type = request.POST.get('cargo_type')
        weight = request.POST.get('weight', 0)
        price = request.POST.get('price', 0)
        pickup_date = request.POST.get('pickup_date')
        description = request.POST.get('description', '')
        
        # اعتبارسنجی
        if not all([order_number, origin, destination, cargo_type, pickup_date]):
            messages.error(request, 'لطفاً تمام فیلدهای ضروری را پر کنید.')
            return render(request, 'customer_panel/order_form.html', {'customer': customer})
        
        # ایجاد سفارش جدید
        order = Order.objects.create(
            order_number=order_number,
            customer=customer,
            origin=origin,
            destination=destination,
            cargo_type=cargo_type,
            weight=weight,
            price=price,
            advance_payment=0,
            status='pending',
            pickup_date=timezone.datetime.strptime(pickup_date, '%Y-%m-%dT%H:%M'),
            created_at=timezone.now()
        )
        
        messages.success(request, f'سفارش {order.order_number} با موفقیت ثبت شد. در انتظار تایید مدیریت.')
        return redirect('customer_orders')
    
    # نمایش فرم خالی
    return render(request, 'customer_panel/order_form.html', {'customer': customer})


@login_required
def customer_invoices(request):
    try:
        customer = Customer.objects.get(user=request.user)
    except Customer.DoesNotExist:
        return redirect('customer_login')
    
    invoices = Invoice.objects.filter(customer=customer).order_by('-issue_date')
    return render(request, 'customer_panel/invoices.html', {'invoices': invoices})


def customer_logout_view(request):
    auth_logout(request)
    messages.info(request, 'شما از پنل مشتری خارج شدید.')
    return redirect('/logout/')


@login_required
def track_order(request, order_id):
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