from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from orders.models import Customer, Driver, Vehicle, Order, ShippingDocument
from finance.models import Invoice, Payment
from django.contrib.auth.models import User
from common.decorators import role_required, admin_only, manager_only, accountant_only
import json

# ==================== مشتریان ====================

@login_required
@role_required('can_manage_customers')
def customer_list(request):
    customers = Customer.objects.all().order_by('-created_at')
    return render(request, 'admin/customers/list.html', {'customers': customers})

@login_required
@role_required('can_manage_customers')
def customer_create(request):
    if request.method == 'POST':
        customer = Customer.objects.create(
            name=request.POST.get('name'),
            phone=request.POST.get('phone'),
            mobile=request.POST.get('mobile'),
            address=request.POST.get('address'),
            national_id=request.POST.get('national_id'),
            credit_limit=request.POST.get('credit_limit', 0)
        )
        messages.success(request, f'مشتری {customer.name} با موفقیت ایجاد شد.')
        return redirect('customer_list')
    return render(request, 'admin/customers/form.html')

@login_required
@role_required('can_manage_customers')
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.name = request.POST.get('name')
        customer.phone = request.POST.get('phone')
        customer.mobile = request.POST.get('mobile')
        customer.address = request.POST.get('address')
        customer.national_id = request.POST.get('national_id')
        customer.credit_limit = request.POST.get('credit_limit', 0)
        customer.save()
        messages.success(request, f'مشتری {customer.name} با موفقیت ویرایش شد.')
        return redirect('customer_list')
    return render(request, 'admin/customers/form.html', {'customer': customer})

@login_required
@role_required('can_manage_customers')
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    name = customer.name
    customer.delete()
    messages.success(request, f'مشتری {name} با موفقیت حذف شد.')
    return redirect('customer_list')

# ==================== رانندگان ====================

@login_required
@role_required('can_manage_drivers')
def driver_list(request):
    drivers = Driver.objects.all().order_by('-id')
    return render(request, 'admin/drivers/list.html', {'drivers': drivers})

@login_required
@role_required('can_manage_drivers')
def driver_create(request):
    if request.method == 'POST':
        driver = Driver.objects.create(
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            national_code=request.POST.get('national_code'),
            license_number=request.POST.get('license_number'),
            phone=request.POST.get('phone'),
            is_active=request.POST.get('is_active') == 'on'
        )
        messages.success(request, f'راننده {driver.first_name} {driver.last_name} با موفقیت ایجاد شد.')
        return redirect('driver_list')
    return render(request, 'admin/drivers/form.html')

@login_required
@role_required('can_manage_drivers')
def driver_edit(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    if request.method == 'POST':
        driver.first_name = request.POST.get('first_name')
        driver.last_name = request.POST.get('last_name')
        driver.national_code = request.POST.get('national_code')
        driver.license_number = request.POST.get('license_number')
        driver.phone = request.POST.get('phone')
        driver.is_active = request.POST.get('is_active') == 'on'
        driver.save()
        messages.success(request, f'راننده {driver.first_name} {driver.last_name} با موفقیت ویرایش شد.')
        return redirect('driver_list')
    return render(request, 'admin/drivers/form.html', {'driver': driver})

@login_required
@role_required('can_manage_drivers')
def driver_delete(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    name = f"{driver.first_name} {driver.last_name}"
    driver.delete()
    messages.success(request, f'راننده {name} با موفقیت حذف شد.')
    return redirect('driver_list')

# ==================== خودروها ====================

@login_required
@role_required('can_manage_vehicles')
def vehicle_list(request):
    vehicles = Vehicle.objects.all().order_by('-id')
    return render(request, 'admin/vehicles/list.html', {'vehicles': vehicles})

@login_required
@role_required('can_manage_vehicles')
def vehicle_create(request):
    drivers = Driver.objects.filter(is_active=True)
    if request.method == 'POST':
        vehicle = Vehicle.objects.create(
            plate_number=request.POST.get('plate_number'),
            model=request.POST.get('model'),
            capacity=request.POST.get('capacity', 0),
            current_driver_id=request.POST.get('current_driver') or None,
            is_available=request.POST.get('is_available') == 'on'
        )
        messages.success(request, f'خودرو {vehicle.plate_number} با موفقیت ایجاد شد.')
        return redirect('vehicle_list')
    return render(request, 'admin/vehicles/form.html', {'drivers': drivers})

@login_required
@role_required('can_manage_vehicles')
def vehicle_edit(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    drivers = Driver.objects.filter(is_active=True)
    if request.method == 'POST':
        vehicle.plate_number = request.POST.get('plate_number')
        vehicle.model = request.POST.get('model')
        vehicle.capacity = request.POST.get('capacity', 0)
        vehicle.current_driver_id = request.POST.get('current_driver') or None
        vehicle.is_available = request.POST.get('is_available') == 'on'
        vehicle.save()
        messages.success(request, f'خودرو {vehicle.plate_number} با موفقیت ویرایش شد.')
        return redirect('vehicle_list')
    return render(request, 'admin/vehicles/form.html', {'vehicle': vehicle, 'drivers': drivers})

@login_required
@role_required('can_manage_vehicles')
def vehicle_delete(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    plate = vehicle.plate_number
    vehicle.delete()
    messages.success(request, f'خودرو {plate} با موفقیت حذف شد.')
    return redirect('vehicle_list')
    # ==================== سفارشات ====================

@login_required
@role_required('can_manage_orders')
def order_list(request):
    orders = Order.objects.all().select_related('customer', 'driver', 'vehicle').order_by('-created_at')
    return render(request, 'admin/orders/list.html', {'orders': orders})

@login_required
@role_required('can_manage_orders')
def order_create(request):
    customers = Customer.objects.all()
    drivers = Driver.objects.filter(is_active=True)
    vehicles = Vehicle.objects.filter(is_available=True)
    
    if request.method == 'POST':
        order = Order.objects.create(
            order_number=request.POST.get('order_number'),
            customer_id=request.POST.get('customer'),
            origin=request.POST.get('origin'),
            destination=request.POST.get('destination'),
            cargo_type=request.POST.get('cargo_type'),
            weight=request.POST.get('weight', 0),
            price=request.POST.get('price', 0),
            advance_payment=request.POST.get('advance_payment', 0),
            status=request.POST.get('status', 'pending'),
            pickup_date=request.POST.get('pickup_date'),
            driver_id=request.POST.get('driver') or None,
            vehicle_id=request.POST.get('vehicle') or None,
        )
        messages.success(request, f'سفارش {order.order_number} با موفقیت ایجاد شد.')
        return redirect('order_list')
    
    context = {
        'customers': customers,
        'drivers': drivers,
        'vehicles': vehicles,
    }
    return render(request, 'admin/orders/form.html', context)

@login_required
@role_required('can_manage_orders')
def order_edit(request, pk):
    order = get_object_or_404(Order, pk=pk)
    customers = Customer.objects.all()
    drivers = Driver.objects.filter(is_active=True)
    vehicles = Vehicle.objects.filter(is_available=True)
    
    if request.method == 'POST':
        order.order_number = request.POST.get('order_number')
        order.customer_id = request.POST.get('customer')
        order.origin = request.POST.get('origin')
        order.destination = request.POST.get('destination')
        order.cargo_type = request.POST.get('cargo_type')
        order.weight = request.POST.get('weight', 0)
        order.price = request.POST.get('price', 0)
        order.advance_payment = request.POST.get('advance_payment', 0)
        order.status = request.POST.get('status')
        order.pickup_date = request.POST.get('pickup_date')
        order.driver_id = request.POST.get('driver') or None
        order.vehicle_id = request.POST.get('vehicle') or None
        order.save()
        messages.success(request, f'سفارش {order.order_number} با موفقیت ویرایش شد.')
        return redirect('order_list')
    
    context = {
        'order': order,
        'customers': customers,
        'drivers': drivers,
        'vehicles': vehicles,
    }
    return render(request, 'admin/orders/form.html', context)

@login_required
@role_required('can_manage_orders')
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    number = order.order_number
    order.delete()
    messages.success(request, f'سفارش {number} با موفقیت حذف شد.')
    return redirect('order_list')

# ==================== اسناد ====================

@login_required
@role_required('can_manage_orders')
def document_list(request):
    documents = ShippingDocument.objects.all().select_related('order', 'uploaded_by').order_by('-uploaded_at')
    return render(request, 'admin/documents/list.html', {'documents': documents})

@login_required
@role_required('can_manage_orders')
def document_create(request):
    orders = Order.objects.all()
    users = User.objects.filter(is_superuser=True)
    
    if request.method == 'POST':
        document = ShippingDocument.objects.create(
            order_id=request.POST.get('order'),
            document_type=request.POST.get('document_type'),
            title=request.POST.get('title'),
            file=request.FILES.get('file'),
            uploaded_by_id=request.POST.get('uploaded_by'),
            notes=request.POST.get('notes', '')
        )
        messages.success(request, f'سند {document.title} با موفقیت ایجاد شد.')
        return redirect('document_list')
    
    context = {
        'orders': orders,
        'users': users,
    }
    return render(request, 'admin/documents/form.html', context)

@login_required
@role_required('can_manage_orders')
def document_edit(request, pk):
    document = get_object_or_404(ShippingDocument, pk=pk)
    orders = Order.objects.all()
    users = User.objects.filter(is_superuser=True)
    
    if request.method == 'POST':
        document.order_id = request.POST.get('order')
        document.document_type = request.POST.get('document_type')
        document.title = request.POST.get('title')
        if request.FILES.get('file'):
            document.file = request.FILES.get('file')
        document.uploaded_by_id = request.POST.get('uploaded_by')
        document.notes = request.POST.get('notes', '')
        document.save()
        messages.success(request, f'سند {document.title} با موفقیت ویرایش شد.')
        return redirect('document_list')
    
    context = {
        'document': document,
        'orders': orders,
        'users': users,
    }
    return render(request, 'admin/documents/form.html', context)

@login_required
@role_required('can_manage_orders')
def document_delete(request, pk):
    document = get_object_or_404(ShippingDocument, pk=pk)
    title = document.title
    document.delete()
    messages.success(request, f'سند {title} با موفقیت حذف شد.')
    return redirect('document_list')

# ==================== مدیریت کاربران ====================

@login_required
@role_required('can_manage_users')
def user_list(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'admin/users/list.html', {'users': users})

@login_required
@role_required('can_manage_users')
def user_create(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        is_staff = request.POST.get('is_staff') == 'on'
        is_superuser = request.POST.get('is_superuser') == 'on'
        is_active = request.POST.get('is_active') == 'on'
        
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.is_active = is_active
        user.save()
        messages.success(request, f'کاربر {username} با موفقیت ایجاد شد.')
        return redirect('user_list')
    
    return render(request, 'admin/users/form.html')

@login_required
@role_required('can_manage_users')
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.is_staff = request.POST.get('is_staff') == 'on'
        user.is_superuser = request.POST.get('is_superuser') == 'on'
        user.is_active = request.POST.get('is_active') == 'on'
        
        new_password = request.POST.get('password')
        if new_password:
            user.set_password(new_password)
        
        user.save()
        messages.success(request, f'کاربر {user.username} با موفقیت ویرایش شد.')
        return redirect('user_list')
    
    return render(request, 'admin/users/form.html', {'user': user})

@login_required
@role_required('can_manage_users')
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    username = user.username
    user.delete()
    messages.success(request, f'کاربر {username} با موفقیت حذف شد.')
    return redirect('user_list')
    # ==================== مدیریت فاکتورها ====================

@login_required
@role_required('can_manage_finance')
def invoice_list(request):
    invoices = Invoice.objects.all().select_related('customer', 'order').order_by('-issue_date')
    return render(request, 'admin/finance/invoices/list.html', {'invoices': invoices})

@login_required
@role_required('can_manage_finance')
def invoice_create(request):
    customers = Customer.objects.all()
    orders = Order.objects.all()
    
    if request.method == 'POST':
        invoice = Invoice.objects.create(
            invoice_number=request.POST.get('invoice_number'),
            order_id=request.POST.get('order'),
            customer_id=request.POST.get('customer'),
            subtotal=request.POST.get('subtotal', 0),
            discount=request.POST.get('discount', 0),
            status=request.POST.get('status', 'sent'),
            due_date=request.POST.get('due_date'),
            description=request.POST.get('description', ''),
            created_by=request.user
        )
        messages.success(request, f'فاکتور {invoice.invoice_number} با موفقیت ایجاد شد.')
        return redirect('invoice_list')
    
    context = {
        'customers': customers,
        'orders': orders,
    }
    return render(request, 'admin/finance/invoices/form.html', context)

@login_required
@role_required('can_manage_finance')
def invoice_edit(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    customers = Customer.objects.all()
    orders = Order.objects.all()
    
    if request.method == 'POST':
        invoice.invoice_number = request.POST.get('invoice_number')
        invoice.order_id = request.POST.get('order')
        invoice.customer_id = request.POST.get('customer')
        invoice.subtotal = request.POST.get('subtotal', 0)
        invoice.discount = request.POST.get('discount', 0)
        invoice.status = request.POST.get('status')
        invoice.due_date = request.POST.get('due_date')
        invoice.description = request.POST.get('description', '')
        invoice.save()
        messages.success(request, f'فاکتور {invoice.invoice_number} با موفقیت ویرایش شد.')
        return redirect('invoice_list')
    
    context = {
        'invoice': invoice,
        'customers': customers,
        'orders': orders,
    }
    return render(request, 'admin/finance/invoices/form.html', context)

@login_required
@role_required('can_manage_finance')
def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    number = invoice.invoice_number
    invoice.delete()
    messages.success(request, f'فاکتور {number} با موفقیت حذف شد.')
    return redirect('invoice_list')

# ==================== مدیریت پرداخت‌ها ====================

@login_required
@role_required('can_manage_finance')
def payment_list(request):
    payments = Payment.objects.all().select_related('customer', 'order', 'invoice').order_by('-payment_date')
    return render(request, 'admin/finance/payments/list.html', {'payments': payments})

@login_required
@role_required('can_manage_finance')
def payment_create(request):
    customers = Customer.objects.all()
    orders = Order.objects.all()
    invoices = Invoice.objects.all()
    
    if request.method == 'POST':
        payment = Payment.objects.create(
            invoice_id=request.POST.get('invoice') or None,
            order_id=request.POST.get('order') or None,
            customer_id=request.POST.get('customer') or None,
            direction=request.POST.get('direction'),
            amount=request.POST.get('amount', 0),
            payment_type=request.POST.get('payment_type'),
            reference_number=request.POST.get('reference_number', ''),
            payment_date=request.POST.get('payment_date'),
            description=request.POST.get('description', ''),
            recorded_by=request.user
        )
        messages.success(request, f'پرداخت با مبلغ {payment.amount} با موفقیت ثبت شد.')
        return redirect('payment_list')
    
    context = {
        'customers': customers,
        'orders': orders,
        'invoices': invoices,
    }
    return render(request, 'admin/finance/payments/form.html', context)

@login_required
@role_required('can_manage_finance')
def payment_edit(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    customers = Customer.objects.all()
    orders = Order.objects.all()
    invoices = Invoice.objects.all()
    
    if request.method == 'POST':
        payment.invoice_id = request.POST.get('invoice') or None
        payment.order_id = request.POST.get('order') or None
        payment.customer_id = request.POST.get('customer') or None
        payment.direction = request.POST.get('direction')
        payment.amount = request.POST.get('amount', 0)
        payment.payment_type = request.POST.get('payment_type')
        payment.reference_number = request.POST.get('reference_number', '')
        payment.payment_date = request.POST.get('payment_date')
        payment.description = request.POST.get('description', '')
        payment.save()
        messages.success(request, 'پرداخت با موفقیت ویرایش شد.')
        return redirect('payment_list')
    
    context = {
        'payment': payment,
        'customers': customers,
        'orders': orders,
        'invoices': invoices,
    }
    return render(request, 'admin/finance/payments/form.html', context)

@login_required
@role_required('can_manage_finance')
def payment_delete(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    payment.delete()
    messages.success(request, 'پرداخت با موفقیت حذف شد.')
    return redirect('payment_list')