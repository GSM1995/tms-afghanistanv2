from django.db import models
from orders.models import Order, Driver
from django.utils import timezone

class DriverOrderRequest(models.Model):
    """درخواست قبول/رد سفارش توسط راننده"""
    
    STATUS_CHOICES = [
        ('pending', 'در انتظار پاسخ'),
        ('accepted', 'قبول شده'),
        ('rejected', 'رد شده'),
        ('expired', 'منقضی شده'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='driver_requests')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='order_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    def accept(self):
        self.status = 'accepted'
        self.responded_at = timezone.now()
        self.save()
        # تخصیص سفارش به این راننده
        self.order.driver = self.driver
        self.order.status = 'assigned'
        self.order.save()
    
    def reject(self):
        self.status = 'rejected'
        self.responded_at = timezone.now()
        self.save()
    
    def __str__(self):
        return f"{self.order.order_number} - {self.driver} - {self.status}"

class DriverLocation(models.Model):
    """موقعیت لحظه‌ای راننده (ارسال شده از موبایل)"""
    
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='locations')
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    speed = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name="در دسترس برای بار")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.driver} - {self.timestamp}"
    
    class Meta:
        ordering = ['-timestamp']