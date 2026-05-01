from django.db import models
from django.contrib.auth.models import User
from orders.models import Order, Customer, Driver

class Invoice(models.Model):
    """فاکتور صادر شده برای مشتری"""
    
    INVOICE_STATUS = [
        ('draft', 'پیش‌نویس'),
        ('sent', 'ارسال شده'),
        ('paid', 'پرداخت شده'),
        ('overdue', 'سررسید گذشته'),
        ('cancelled', 'لغو شده'),
    ]
    
    invoice_number = models.CharField(max_length=50, unique=True, verbose_name="شماره فاکتور")
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='invoices', verbose_name="سفارش")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, verbose_name="مشتری")
    
    # مبالغ
    subtotal = models.DecimalField(max_digits=15, decimal_places=0, verbose_name="جمع کرایه")
    tax = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="مالیات (9%)")
    discount = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="تخفیف")
    total = models.DecimalField(max_digits=15, decimal_places=0, verbose_name="قابل پرداخت")
    
    # وضعیت
    status = models.CharField(max_length=20, choices=INVOICE_STATUS, default='draft', verbose_name="وضعیت")
    issue_date = models.DateField(auto_now_add=True, verbose_name="تاریخ صدور")
    due_date = models.DateField(verbose_name="تاریخ سررسید")
    paid_date = models.DateField(null=True, blank=True, verbose_name="تاریخ پرداخت")
    
    # توضیحات
    description = models.TextField(blank=True, verbose_name="توضیحات")
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="ایجاد کننده")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.invoice_number} - {self.customer.name}"
    
    def save(self, *args, **kwargs):
        # محاسبه خودکار مالیات و جمع کل
        self.tax = int(self.subtotal * 0.09)  # 9% مالیات
        self.total = self.subtotal + self.tax - self.discount
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "فاکتور"
        verbose_name_plural = "فاکتورها"
        ordering = ['-issue_date']

class Payment(models.Model):
    """ثبت دریافت و پرداخت"""
    
    PAYMENT_TYPES = [
        ('cash', 'نقدی'),
        ('check', 'چک'),
        ('card', 'کارتخوان'),
        ('transfer', 'انتقال بانکی'),
    ]
    
    PAYMENT_DIRECTION = [
        ('income', 'دریافت'),
        ('expense', 'پرداخت'),
    ]
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments', null=True, blank=True, verbose_name="فاکتور مربوطه")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments', null=True, blank=True, verbose_name="سفارش")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True, verbose_name="مشتری")
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, null=True, blank=True, verbose_name="راننده")
    
    direction = models.CharField(max_length=10, choices=PAYMENT_DIRECTION, verbose_name="نوع")
    amount = models.DecimalField(max_digits=15, decimal_places=0, verbose_name="مبلغ")
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES, verbose_name="نوع پرداخت")
    
    reference_number = models.CharField(max_length=100, blank=True, verbose_name="شماره مرجع (شماره چک/رسید)")
    payment_date = models.DateField(verbose_name="تاریخ پرداخت")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    
    recorded_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="ثبت کننده")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        direction_fa = "دریافت" if self.direction == 'income' else "پرداخت"
        return f"{direction_fa} - {self.amount:,} تومان"
    
    class Meta:
        verbose_name = "تراکنش مالی"
        verbose_name_plural = "تراکنش‌های مالی"
        ordering = ['-payment_date']

class DriverSalary(models.Model):
    """حقوق و دستمزد رانندگان"""
    
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='salaries', verbose_name="راننده")
    month = models.IntegerField(verbose_name="ماه", help_text="عدد 1 تا 12")
    year = models.IntegerField(verbose_name="سال")
    
    base_salary = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="حقوق پایه")
    trip_count = models.IntegerField(default=0, verbose_name="تعداد سفر")
    total_amount = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="کل مبلغ کرایه‌ها")
    driver_share = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="سهم راننده (30%)")
    bonuses = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="پاداش")
    deductions = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="کسورات")
    net_payable = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="قابل پرداخت")
    
    is_paid = models.BooleanField(default=False, verbose_name="پرداخت شده")
    paid_date = models.DateField(null=True, blank=True, verbose_name="تاریخ پرداخت")
    
    def save(self, *args, **kwargs):
        self.driver_share = int(self.total_amount * 0.30)  # 30% سهم راننده
        self.net_payable = self.base_salary + self.driver_share + self.bonuses - self.deductions
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.driver} - {self.year}/{self.month}"
    
    class Meta:
        verbose_name = "حقوق راننده"
        verbose_name_plural = "حقوق رانندگان"
        unique_together = ['driver', 'month', 'year']