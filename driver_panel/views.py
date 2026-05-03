from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from orders.models import Driver, Order, Vehicle
from .models import DriverOrderRequest, DriverLocation
from django.utils import timezone
import json


def driver_login_view(request):
    if request.user.is_authenticated:
        return redirect('driver_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            try:
                driver = Driver.objects.get(user=user)
                login(request, user)
                messages.success(request, f'خوش آمدید {driver.first_name} {driver.last_name}')
                return redirect('driver_dashboard')
            except Driver.DoesNotExist:
                messages.error(request, 'شما دسترسی راننده ندارید')
                return render(request, 'driver_panel/login.html')
        else:
            messages.error(request, 'نام کاربری یا رمز عبور صحیح نیست')
            return render(request, 'driver_panel/login.html')
    
    return render(request, 'driver_panel/login.html')


@login_required
def driver_dashboard(request):
    try:
        driver = Driver.objects.get(user=request.user)
    except Driver.DoesNotExist:
        messages.error(request, 'شما دسترسی راننده ندارید')
        return redirect('driver_login')
    
    context = {
        'driver': driver,
        'total_trips': Order.objects.filter(driver=driver).count(),
        'delivered_orders': Order.objects.filter(driver=driver, status='delivered').count(),
        'current_order': Order.objects.filter(driver=driver, status__in=['assigned', 'loading', 'in_transit']).first(),
        'pending_requests': DriverOrderRequest.objects.filter(driver=driver, status='pending'),
        'vehicle': Vehicle.objects.filter(current_driver=driver).first(),
    }
    return render(request, 'driver_panel/dashboard.html', context)


@login_required
def accept_order(request, request_id):
    try:
        driver = Driver.objects.get(user=request.user)
        order_request = get_object_or_404(DriverOrderRequest, id=request_id, driver=driver, status='pending')
    except Driver.DoesNotExist:
        return redirect('driver_login')
    
    order_request.accept()
    messages.success(request, f'سفارش {order_request.order.order_number} با موفقیت قبول شد.')
    return redirect('driver_dashboard')


@login_required
def reject_order(request, request_id):
    try:
        driver = Driver.objects.get(user=request.user)
        order_request = get_object_or_404(DriverOrderRequest, id=request_id, driver=driver, status='pending')
    except Driver.DoesNotExist:
        return redirect('driver_login')
    
    order_request.reject()
    messages.info(request, f'سفارش {order_request.order.order_number} رد شد.')
    return redirect('driver_dashboard')


@login_required
def update_order_status(request, order_id):
    if request.method == 'POST':
        try:
            driver = Driver.objects.get(user=request.user)
            order = get_object_or_404(Order, id=order_id, driver=driver)
            new_status = request.POST.get('status')
            
            if new_status in ['loading', 'in_transit', 'delivered']:
                order.status = new_status
                if new_status == 'delivered':
                    order.actual_delivery = timezone.now()
                    messages.success(request, 'سفارش با موفقیت تحویل داده شد.')
                else:
                    messages.success(request, f'وضعیت سفارش به {order.get_status_display()} تغییر یافت.')
                order.save()
                return JsonResponse({'success': True, 'status': order.get_status_display()})
        except:
            pass
    
    return JsonResponse({'error': 'درخواست نامعتبر'}, status=400)


def driver_logout_view(request):
    """خروج راننده و هدایت به صفحه لاگ‌اوت"""
    auth_logout(request)
    messages.info(request, 'شما از پنل راننده خارج شدید.')
    return redirect('/logout/')


@csrf_exempt
@require_http_methods(["POST"])
def update_location_api(request):
    try:
        data = json.loads(request.body)
        driver_id = data.get('driver_id')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        speed = data.get('speed')
        
        if not all([driver_id, latitude, longitude]):
            return JsonResponse({'error': 'اطلاعات ناقص'}, status=400)
        
        try:
            driver = Driver.objects.get(id=driver_id)
        except Driver.DoesNotExist:
            return JsonResponse({'error': 'راننده یافت نشد'}, status=404)
        
        location = DriverLocation.objects.create(
            driver=driver,
            latitude=latitude,
            longitude=longitude,
            speed=speed,
            is_active=True
        )
        
        return JsonResponse({
            'status': 'success',
            'location_id': location.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'فرمت JSON نامعتبر'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def driver_locations(request):
    locations = []
    for driver in Driver.objects.filter(is_active=True):
        latest = DriverLocation.objects.filter(driver=driver).first()
        if latest:
            locations.append({
                'driver_id': driver.id,
                'driver_name': f"{driver.first_name} {driver.last_name}",
                'latitude': str(latest.latitude),
                'longitude': str(latest.longitude),
                'speed': str(latest.speed) if latest.speed else None,
                'last_update': latest.timestamp.isoformat(),
            })
    
    return JsonResponse({'locations': locations, 'count': len(locations)})