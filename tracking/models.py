from django.db import models
from orders.models import Vehicle, Order, Driver

class VehicleLocation(models.Model):
    """موقعیت لحظه‌ای خودرو"""
    
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='locations', verbose_name="خودرو")
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="راننده")
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="سفارش جاری")
    
    # موقعیت جغرافیایی
    latitude = models.DecimalField(max_digits=10, decimal_places=7, verbose_name="عرض جغرافیایی")
    longitude = models.DecimalField(max_digits=10, decimal_places=7, verbose_name="طول جغرافیایی")
    
    # اطلاعات اضافی
    speed = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="سرعت (km/h)")
    direction = models.IntegerField(null=True, blank=True, verbose_name="جهت (درجه)")
    accuracy = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="دقت (متر)")
    
    # زمان
    location_time = models.DateTimeField(verbose_name="زمان موقعیت")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="ثبت در سیستم")
    
    def __str__(self):
        return f"{self.vehicle.plate_number} - {self.latitude}, {self.longitude}"
    
    class Meta:
        verbose_name = "موقعیت خودرو"
        verbose_name_plural = "موقعیت خودروها"
        ordering = ['-location_time']
        indexes = [
            models.Index(fields=['vehicle', '-location_time']),
            models.Index(fields=['order']),
        ]

class TripHistory(models.Model):
    """تاریخچه مسیر هر سفارش"""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='trip_history', verbose_name="سفارش")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, verbose_name="خودرو")
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, verbose_name="راننده")
    
    start_time = models.DateTimeField(verbose_name="زمان شروع")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="زمان پایان")
    start_location = models.CharField(max_length=500, verbose_name="موقعیت شروع")
    end_location = models.CharField(max_length=500, null=True, blank=True, verbose_name="موقعیت پایان")
    
    total_distance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="مسافت کل (km)")
    total_duration = models.IntegerField(null=True, blank=True, verbose_name="مدت زمان (دقیقه)")
    
    def __str__(self):
        return f"{self.order.order_number} - {self.vehicle.plate_number}"
    
    class Meta:
        verbose_name = "تاریخچه سفر"
        verbose_name_plural = "تاریخچه سفرها"

class Geofence(models.Model):
    """منطقه جغرافیایی (محوطه گمرک، انبارها)"""
    
    name = models.CharField(max_length=100, verbose_name="نام منطقه")
    address = models.TextField(verbose_name="آدرس")
    
    # مرکز منطقه
    center_lat = models.DecimalField(max_digits=10, decimal_places=7, verbose_name="عرض مرکز")
    center_lng = models.DecimalField(max_digits=10, decimal_places=7, verbose_name="طول مرکز")
    
    # شعاع (متر)
    radius = models.IntegerField(default=100, verbose_name="شعاع (متر)")
    
    # یا مختصات چند ضلعی
    polygon_coords = models.TextField(blank=True, help_text="JSON format: [[lat,lng], [lat,lng], ...]", verbose_name="مختصات چند ضلعی")
    
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "منطقه جغرافیایی"
        verbose_name_plural = "مناطق جغرافیایی"

class VehicleAlert(models.Model):
    """هشدارهای خودرو (خروج از مسیر، ورود به منطقه)"""
    
    ALERT_TYPES = [
        ('speeding', 'سرعت غیرمجاز'),
        ('off_route', 'خروج از مسیر'),
        ('geofence_enter', 'ورود به منطقه'),
        ('geofence_exit', 'خروج از منطقه'),
        ('idle', 'توقف طولانی'),
        ('emergency', 'وضعیت اضطراری'),
    ]
    
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='alerts', verbose_name="خودرو")
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="سفارش مرتبط")
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES, verbose_name="نوع هشدار")
    message = models.TextField(verbose_name="پیام هشدار")
    location = models.CharField(max_length=500, verbose_name="موقعیت")
    is_resolved = models.BooleanField(default=False, verbose_name="برطرف شده")
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان برطرف شدن")
    
    def __str__(self):
        return f"{self.vehicle.plate_number} - {self.get_alert_type_display()}"
    
    class Meta:
        verbose_name = "هشدار خودرو"
        verbose_name_plural = "هشدارهای خودرو"