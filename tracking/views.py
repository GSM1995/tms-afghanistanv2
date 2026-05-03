from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import VehicleLocation, VehicleAlert
from orders.models import Vehicle, Order, Driver
import json
from django.utils import timezone


def check_alerts(vehicle, order, latitude, longitude, speed):
    """بررسی شرایط هشدار و ایجاد هشدار در صورت لزوم"""
    alerts = []
    
    # بررسی سرعت غیرمجاز (بیش از 80 کیلومتر)
    if speed and float(speed) > 80:
        alert = VehicleAlert.objects.create(
            vehicle=vehicle,
            order=order,
            alert_type='speeding',
            message=f'سرعت غیرمجاز: {speed} km/h',
            location=f'{latitude}, {longitude}',
            is_resolved=False
        )
        alerts.append({'type': 'speeding', 'message': alert.message})
    
    return alerts


@csrf_exempt
@require_http_methods(["POST"])
def update_location(request):
    """API برای دریافت موقعیت از راننده (موبایل)"""
    try:
        data = json.loads(request.body)
        
        vehicle_id = data.get('vehicle_id')
        driver_id = data.get('driver_id')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        speed = data.get('speed')
        
        if not all([vehicle_id, latitude, longitude]):
            return JsonResponse({'error': 'اطلاعات ناقص'}, status=400)
        
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
        except Vehicle.DoesNotExist:
            return JsonResponse({'error': 'خودرو یافت نشد'}, status=404)
        
        current_order = None
        if driver_id:
            try:
                driver = Driver.objects.get(id=driver_id)
                current_order = Order.objects.filter(
                    driver=driver,
                    status__in=['assigned', 'loading', 'in_transit']
                ).first()
            except Driver.DoesNotExist:
                pass
        
        location = VehicleLocation.objects.create(
            vehicle=vehicle,
            driver_id=driver_id,
            order=current_order,
            latitude=latitude,
            longitude=longitude,
            speed=speed,
            location_time=timezone.now()
        )
        
        alerts = check_alerts(vehicle, current_order, latitude, longitude, speed)
        
        return JsonResponse({
            'status': 'success',
            'location_id': location.id,
            'alerts': alerts
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'فرمت JSON نامعتبر'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def vehicle_latest_locations(request):
    """دریافت آخرین موقعیت همه خودروها (برای نقشه)"""
    locations = []
    vehicles_with_locations = Vehicle.objects.filter(is_available=True)
    
    for vehicle in vehicles_with_locations:
        latest = VehicleLocation.objects.filter(vehicle=vehicle).first()
        if latest:
            locations.append({
                'vehicle_id': vehicle.id,
                'plate_number': vehicle.plate_number,
                'latitude': str(latest.latitude),
                'longitude': str(latest.longitude),
                'speed': str(latest.speed) if latest.speed else None,
                'last_update': latest.location_time.isoformat(),
            })
    
    return JsonResponse({'locations': locations, 'count': len(locations)})


@login_required
def vehicle_tracking(request):
    """صفحه نقشه برای ردیابی خودروها"""
    return render(request, 'tracking/map.html')


@login_required
def vehicle_history(request, vehicle_id):
    """تاریخچه موقعیت یک خودرو"""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    locations = VehicleLocation.objects.filter(vehicle_id=vehicle_id)
    
    if start_date:
        locations = locations.filter(location_time__gte=start_date)
    if end_date:
        locations = locations.filter(location_time__lte=end_date)
    
    locations = locations[:100]
    
    history = [{
        'latitude': str(loc.latitude),
        'longitude': str(loc.longitude),
        'time': loc.location_time.isoformat(),
        'speed': str(loc.speed) if loc.speed else None,
    } for loc in locations]
    
    return JsonResponse({'history': history, 'count': len(history)})