from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LogoutView
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.shortcuts import redirect, render
from .views import admin_dashboard
from .admin_views import (
    customer_list, customer_create, customer_edit, customer_delete,
    driver_list, driver_create, driver_edit, driver_delete,
    vehicle_list, vehicle_create, vehicle_edit, vehicle_delete,
    order_list, order_create, order_edit, order_delete,
    document_list, document_create, document_edit, document_delete,
    user_list, user_create, user_edit, user_delete,
    invoice_list, invoice_create, invoice_edit, invoice_delete,
    payment_list, payment_create, payment_edit, payment_delete
)


def redirect_to_login(request):
    """ریدایرکت /admin/login/ به /login/"""
    return redirect('/login/')


def custom_logout_view(request):
    """نمایش صفحه لاگ‌اوت سفارشی"""
    from django.contrib.auth import logout as auth_logout
    auth_logout(request)
    return render(request, 'logout.html')


@csrf_exempt
def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponse('<script>window.location.href = "/";</script>')
        else:
            return HttpResponse('''
                <!DOCTYPE html>
                <html dir="rtl">
                <head><meta charset="UTF-8"><title>خطا در ورود</title>
                <style>
                    body{font-family:Tahoma;background:linear-gradient(135deg,#1a472a,#2c3e50);margin:0;padding:0;display:flex;justify-content:center;align-items:center;min-height:100vh;}
                    .box{background:white;padding:40px;border-radius:15px;width:380px;text-align:center;}
                    .error{background:#fee;color:#c0392b;padding:10px;border-radius:8px;margin-bottom:20px;}
                    input{width:100%;padding:12px;margin:8px 0 20px;border:1px solid #ddd;border-radius:8px;}
                    button{width:100%;padding:12px;background:#27ae60;color:white;border:none;border-radius:8px;cursor:pointer;}
                </style>
                </head>
                <body>
                <div class="box">
                    <div style="font-size:48px;">🚚</div>
                    <div class="error">❌ نام کاربری یا رمز عبور اشتباه است</div>
                    <form method="post">
                        <input type="text" name="username" placeholder="نام کاربری" required>
                        <input type="password" name="password" placeholder="رمز عبور" required>
                        <button type="submit">ورود مجدد</button>
                    </form>
                    <hr><div><a href="/customer/login/">🚛 ورود مشتریان</a> | <a href="/driver/login/">🚚 ورود رانندگان</a></div>
                </div>
                </body>
                </html>
            ''')
    
    return HttpResponse('''
        <!DOCTYPE html>
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>ورود به سیستم TMS - افغانستان</title>
            <style>
                body {
                    font-family: Tahoma, Arial;
                    background: linear-gradient(135deg, #1a472a 0%, #2c3e50 100%);
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                }
                .login-box {
                    background: white;
                    padding: 40px;
                    border-radius: 15px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    width: 380px;
                    text-align: center;
                }
                h2 { color: #2c3e50; margin-bottom: 10px; }
                h3 { color: #666; margin-bottom: 30px; font-size: 14px; }
                input {
                    width: 100%;
                    padding: 12px;
                    margin: 8px 0 20px;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    box-sizing: border-box;
                    font-size: 14px;
                }
                button {
                    width: 100%;
                    padding: 12px;
                    background: #27ae60;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                    cursor: pointer;
                }
                button:hover { background: #1a472a; }
                hr { margin: 20px 0; }
                .links a { color: #27ae60; text-decoration: none; margin: 0 5px; }
            </style>
        </head>
        <body>
            <div class="login-box">
                <div style="font-size: 48px;">🚚</div>
                <h2>سیستم مدیریت حمل و نقل</h2>
                <h3>افغانستان</h3>
                <form method="post">
                    <input type="text" name="username" placeholder="نام کاربری" required>
                    <input type="password" name="password" placeholder="رمز عبور" required>
                    <button type="submit">ورود به سیستم</button>
                </form>
                <hr>
                <div class="links">
                    <a href="/customer/login/">🚛 ورود مشتریان</a> | 
                    <a href="/driver/login/">🚚 ورود رانندگان</a>
                </div>
            </div>
        </body>
        </html>
    ''')


urlpatterns = [
    # ریدایرکت /admin/login/ به /login/
    path('admin/login/', redirect_to_login),
    
    # لاگ‌اوت با صفحه سفارشی
    path('logout/', custom_logout_view, name='logout'),
    path('admin/logout/', custom_logout_view, name='admin_logout'),
    
    path('', admin_dashboard, name='admin_dashboard'),
    path('login/', login_page, name='login_page'),
    
    # مدیریت مشتریان
    path('admin/customers/', customer_list, name='customer_list'),
    path('admin/customers/create/', customer_create, name='customer_create'),
    path('admin/customers/edit/<int:pk>/', customer_edit, name='customer_edit'),
    path('admin/customers/delete/<int:pk>/', customer_delete, name='customer_delete'),
    
    # مدیریت رانندگان
    path('admin/drivers/', driver_list, name='driver_list'),
    path('admin/drivers/create/', driver_create, name='driver_create'),
    path('admin/drivers/edit/<int:pk>/', driver_edit, name='driver_edit'),
    path('admin/drivers/delete/<int:pk>/', driver_delete, name='driver_delete'),
    
    # مدیریت خودروها
    path('admin/vehicles/', vehicle_list, name='vehicle_list'),
    path('admin/vehicles/create/', vehicle_create, name='vehicle_create'),
    path('admin/vehicles/edit/<int:pk>/', vehicle_edit, name='vehicle_edit'),
    path('admin/vehicles/delete/<int:pk>/', vehicle_delete, name='vehicle_delete'),
    
    # مدیریت سفارشات
    path('admin/orders/', order_list, name='order_list'),
    path('admin/orders/create/', order_create, name='order_create'),
    path('admin/orders/edit/<int:pk>/', order_edit, name='order_edit'),
    path('admin/orders/delete/<int:pk>/', order_delete, name='order_delete'),
    
    # مدیریت اسناد
    path('admin/documents/', document_list, name='document_list'),
    path('admin/documents/create/', document_create, name='document_create'),
    path('admin/documents/edit/<int:pk>/', document_edit, name='document_edit'),
    path('admin/documents/delete/<int:pk>/', document_delete, name='document_delete'),
    
    # مدیریت کاربران
    path('admin/users/', user_list, name='user_list'),
    path('admin/users/create/', user_create, name='user_create'),
    path('admin/users/edit/<int:pk>/', user_edit, name='user_edit'),
    path('admin/users/delete/<int:pk>/', user_delete, name='user_delete'),
    
    # مدیریت فاکتورها
    path('admin/finance/invoices/', invoice_list, name='invoice_list'),
    path('admin/finance/invoices/create/', invoice_create, name='invoice_create'),
    path('admin/finance/invoices/edit/<int:pk>/', invoice_edit, name='invoice_edit'),
    path('admin/finance/invoices/delete/<int:pk>/', invoice_delete, name='invoice_delete'),
    
    # مدیریت پرداخت‌ها
    path('admin/finance/payments/', payment_list, name='payment_list'),
    path('admin/finance/payments/create/', payment_create, name='payment_create'),
    path('admin/finance/payments/edit/<int:pk>/', payment_edit, name='payment_edit'),
    path('admin/finance/payments/delete/<int:pk>/', payment_delete, name='payment_delete'),
    
    # اپلیکیشن‌های دیگر
    path('tracking/', include('tracking.urls')),
    path('finance/', include('finance.urls')),
    path('customer/', include('customer_panel.urls')),
    path('driver/', include('driver_panel.urls')),
    path('common/', include('common.urls')),
]