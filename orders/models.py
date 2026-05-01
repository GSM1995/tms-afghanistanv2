from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    """مشتریان شرکت بارچالانی"""
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="کاربر مرتبط")
    name = models.CharField(max_length=200, verbose_name="نام شرکت/شخص")
    phone = models.CharField(max_length=15, verbose_name="تلفن")
    mobile = models.CharField(max_length=11, verbose_name="موبایل")
    address = models.TextField(verbose_name="آدرس")
    national_id = models.CharField(max_length=10, blank=True, verbose_name="کد ملی/اقتصادی")
    credit_limit = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="سقف اعتبار")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "مشتری"
        verbose_name_plural = "مشتریان"

class Driver(models.Model):
    """اطلاعات رانندگان"""
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="کاربر مرتبط")
    first_name = models.CharField(max_length=50, verbose_name="نام")
    last_name = models.CharField(max_length=50, verbose_name="نام خانوادگی")
    national_code = models.CharField(max_length=10, unique=True, verbose_name="کد ملی")
    license_number = models.CharField(max_length=20, verbose_name="شماره گواهینامه")
    phone = models.CharField(max_length=11, verbose_name="موبایل")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        verbose_name = "راننده"
        verbose_name_plural = "رانندگان"

class Vehicle(models.Model):
    """اطلاعات خودروها"""
    plate_number = models.CharField(max_length=20, unique=True, verbose_name="شماره پلاک")
    model = models.CharField(max_length=50, verbose_name="مدل")
    capacity = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="ظرفیت (تن)")
    current_driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="راننده فعلی")
    is_available = models.BooleanField(default=True, verbose_name="در دسترس")
    
    def __str__(self):
        return f"{self.plate_number} - {self.model}"
    
    class Meta:
        verbose_name = "خودرو"
        verbose_name_plural = "خودروها"

class Order(models.Model):
    """سفارش حمل بار"""
    
    STATUS_CHOICES = [
        ('pending', 'در انتظار تخصیص'),
        ('assigned', 'تخصیص داده شده'),
        ('loading', 'در حال بارگیری'),
        ('in_transit', 'در مسیر'),
        ('delivered', 'تحویل شده'),
        ('cancelled', 'لغو شده'),
    ]
    
    order_number = models.CharField(max_length=20, unique=True, verbose_name="شماره سفارش")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, verbose_name="مشتری")
    origin = models.CharField(max_length=300, verbose_name="مبدا")
    destination = models.CharField(max_length=300, verbose_name="مقصد")
    origin_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    origin_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    dest_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    dest_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    cargo_type = models.CharField(max_length=100, verbose_name="نوع بار")
    weight = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="وزن (تن)")
    volume = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="حجم (مترمکعب)")
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="مبلغ کرایه (تومان)")
    advance_payment = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="پیش پرداخت")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="وضعیت")
    pickup_date = models.DateTimeField(verbose_name="زمان بارگیری")
    expected_delivery = models.DateTimeField(null=True, blank=True, verbose_name="زمان تخمینی تحویل")
    actual_delivery = models.DateTimeField(null=True, blank=True, verbose_name="زمان واقعی تحویل")
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="راننده")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="خودرو")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.order_number} - {self.customer.name}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "سفارش"
        verbose_name_plural = "سفارشات"

class ShippingDocument(models.Model):
    """اسناد و مدارک هر سفارش"""
    
    DOCUMENT_TYPES = [
        ('waybill', 'بارنامه'),
        ('insurance', 'بیمه نامه'),
        ('customs', 'مدارک گمرکی'),
        ('invoice', 'فاکتور'),
        ('other', 'سایر'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='documents', verbose_name="سفارش")
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, verbose_name="نوع سند")
    title = models.CharField(max_length=200, verbose_name="عنوان سند")
    file = models.FileField(upload_to='documents/%Y/%m/', verbose_name="فایل سند")
    uploaded_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="ثبت کننده")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, verbose_name="توضیحات")
    
    def __str__(self):
        return f"{self.get_document_type_display()} - {self.order.order_number}"
    
    class Meta:
        verbose_name = "سند"
        verbose_name_plural = "اسناد"