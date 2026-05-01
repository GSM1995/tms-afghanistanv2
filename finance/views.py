from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.db.models import Sum
from .models import Invoice
from orders.models import Order, Customer, Driver, Vehicle
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter

# تنظیمات ارزی افغانستان
CURRENCY_SYMBOL = '؋'
CURRENCY_NAME = 'افغانی'

@staff_member_required
def export_orders_excel(request):
    """خروجی اکسل سفارشات"""
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="orders_report.xlsx"'
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "سفارشات"
    
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="2C3E50", end_color="2C3E50", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")
    
    headers = ['شماره سفارش', 'مشتری', 'مبدا', 'مقصد', 'نوع بار', 'وزن (تن)', f'مبلغ ({CURRENCY_SYMBOL})', 'وضعیت', 'تاریخ']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
    
    orders = Order.objects.all().select_related('customer')
    for row, order in enumerate(orders, 2):
        ws.cell(row=row, column=1, value=order.order_number)
        ws.cell(row=row, column=2, value=order.customer.name)
        ws.cell(row=row, column=3, value=order.origin)
        ws.cell(row=row, column=4, value=order.destination)
        ws.cell(row=row, column=5, value=order.cargo_type)
        ws.cell(row=row, column=6, value=float(order.weight))
        ws.cell(row=row, column=7, value=float(order.price))
        ws.cell(row=row, column=8, value=order.get_status_display())
        ws.cell(row=row, column=9, value=order.pickup_date.strftime('%Y/%m/%d') if order.pickup_date else '')
    
    for col in range(1, 10):
        ws.column_dimensions[get_column_letter(col)].width = 20
    
    wb.save(response)
    return response

@staff_member_required
def export_invoices_excel(request):
    """خروجی اکسل فاکتورها"""
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="invoices_report.xlsx"'
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "فاکتورها"
    
    headers = ['شماره فاکتور', 'مشتری', f'مبلغ کل ({CURRENCY_SYMBOL})', f'مالیات ({CURRENCY_SYMBOL})', 
               f'تخفیف ({CURRENCY_SYMBOL})', f'قابل پرداخت ({CURRENCY_SYMBOL})', 'وضعیت', 'تاریخ صدور', 'سررسید']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="27AE60", end_color="27AE60", fill_type="solid")
        cell.alignment = Alignment(horizontal="center")
    
    invoices = Invoice.objects.all().select_related('customer')
    for row, inv in enumerate(invoices, 2):
        ws.cell(row=row, column=1, value=inv.invoice_number)
        ws.cell(row=row, column=2, value=inv.customer.name)
        ws.cell(row=row, column=3, value=float(inv.subtotal))
        ws.cell(row=row, column=4, value=float(inv.tax))
        ws.cell(row=row, column=5, value=float(inv.discount))
        ws.cell(row=row, column=6, value=float(inv.total))
        ws.cell(row=row, column=7, value=inv.get_status_display())
        ws.cell(row=row, column=8, value=inv.issue_date.strftime('%Y/%m/%d'))
        ws.cell(row=row, column=9, value=inv.due_date.strftime('%Y/%m/%d'))
    
    wb.save(response)
    return response

@staff_member_required
def dashboard_report(request):
    """داشبورد گزارشات - صفحه اصلی گزارشات"""
    total_orders = Order.objects.count()
    total_customers = Customer.objects.count()
    total_drivers = Driver.objects.count()
    total_vehicles = Vehicle.objects.count()
    
    total_invoices = Invoice.objects.aggregate(total=Sum('total'))['total'] or 0
    paid_invoices = Invoice.objects.filter(status='paid').aggregate(total=Sum('total'))['total'] or 0
    pending_invoices = Invoice.objects.filter(status='sent').aggregate(total=Sum('total'))['total'] or 0
    
    now = timezone.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0)
    monthly_orders = Order.objects.filter(created_at__gte=start_of_month).count()
    
    context = {
        'currency_symbol': CURRENCY_SYMBOL,
        'currency_name': CURRENCY_NAME,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'total_drivers': total_drivers,
        'total_vehicles': total_vehicles,
        'total_invoices': total_invoices,
        'paid_invoices': paid_invoices,
        'pending_invoices': pending_invoices,
        'monthly_orders': monthly_orders,
    }
    return render(request, 'finance/dashboard_report.html', context)