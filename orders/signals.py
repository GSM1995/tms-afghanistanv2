from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from driver_panel.models import DriverOrderRequest
from orders.models import Driver

@receiver(post_save, sender=Order)
def send_order_to_drivers(sender, instance, created, **kwargs):
    """وقتی سفارش جدید ثبت شد، برای همه رانندگان فعال درخواست بفرست"""
    if created and instance.status == 'pending':
        # پیدا کردن همه رانندگان فعال
        active_drivers = Driver.objects.filter(is_active=True)
        
        for driver in active_drivers:
            DriverOrderRequest.objects.create(
                order=instance,
                driver=driver,
                status='pending'
            )
        print(f"✅ درخواست سفارش {instance.order_number} برای {active_drivers.count()} راننده ارسال شد")