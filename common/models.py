from django.db import models
from django.contrib.auth.models import User, Group, Permission

class UserRole(models.Model):
    """نقش‌های کاربری در سیستم"""
    
    ROLE_CHOICES = [
        ('admin', 'مدیر کل'),
        ('manager', 'مدیر'),
        ('accountant', 'حسابدار'),
        ('dispatcher', 'مسئول تخصیص بار'),
        ('viewer', 'بازدیدکننده'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='role_profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    can_manage_customers = models.BooleanField(default=False, verbose_name="مدیریت مشتریان")
    can_manage_drivers = models.BooleanField(default=False, verbose_name="مدیریت رانندگان")
    can_manage_vehicles = models.BooleanField(default=False, verbose_name="مدیریت خودروها")
    can_manage_orders = models.BooleanField(default=False, verbose_name="مدیریت سفارشات")
    can_manage_finance = models.BooleanField(default=False, verbose_name="مدیریت مالی")
    can_view_reports = models.BooleanField(default=False, verbose_name="مشاهده گزارشات")
    can_manage_users = models.BooleanField(default=False, verbose_name="مدیریت کاربران")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    class Meta:
        verbose_name = "نقش کاربری"
        verbose_name_plural = "نقش‌های کاربری"

class AccessLog(models.Model):
    """لاگ دسترسی‌های کاربران"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_logs')
    action = models.CharField(max_length=200, verbose_name="عملیات")
    page = models.CharField(max_length=200, verbose_name="صفحه")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.created_at}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "لاگ دسترسی"
        verbose_name_plural = "لاگ‌های دسترسی"