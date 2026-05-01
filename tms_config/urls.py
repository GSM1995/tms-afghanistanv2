from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from .views import admin_dashboard
from django.urls import path, include
import json

@csrf_exempt
def simple_login(request):
    """یک لاگین ساده بدون CSRF برای تست"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({'success': True, 'message': 'ورود موفق', 'redirect': '/'})
            else:
                return JsonResponse({'success': False, 'message': 'نام کاربری یا رمز عبور اشتباه است'}, status=400)
        except:
            return JsonResponse({'success': False, 'message': 'خطا در داده‌ها'}, status=400)
    
    return JsonResponse({'message': 'درخواست GET - برای ورود از POST استفاده کنید'})

@login_required
@csrf_exempt
def dashboard(request):
    """داشبورد ساده بعد از لاگین"""
    from orders.models import Customer, Driver, Vehicle, Order
    
    data = {
        'user': request.user.username,
        'customers_count': Customer.objects.count(),
        'drivers_count': Driver.objects.count(),
        'vehicles_count': Vehicle.objects.count(),
        'orders_count': Order.objects.count(),
    }
    return JsonResponse(data)

# صفحه لاگین HTML ساده
@csrf_exempt
def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponse('''
                <!DOCTYPE html>
                <html>
                <head>
                    <script>
                        window.location.href = '/';
                    </script>
                </head>
                <body>
                    <p>در حال انتقال به داشبورد...</p>
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
                h2 {
                    color: #2c3e50;
                    margin-bottom: 10px;
                }
                h3 {
                    color: #666;
                    margin-bottom: 30px;
                    font-size: 14px;
                }
                input {
                    width: 100%;
                    padding: 12px;
                    margin: 8px 0 20px;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    box-sizing: border-box;
                    font-size: 14px;
                    direction: ltr;
                }
                input:focus {
                    border-color: #27ae60;
                    outline: none;
                    box-shadow: 0 0 0 3px rgba(39,174,96,0.1);
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
                    font-weight: bold;
                    transition: all 0.3s;
                }
                button:hover {
                    background: #1a472a;
                    transform: translateY(-2px);
                }
                .info {
                    margin-top: 20px;
                    font-size: 12px;
                    color: #7f8c8d;
                }
            </style>
        </head>
        <body>
            <div class="login-box">
                <div style="font-size: 48px; margin-bottom: 10px;">🚚</div>
                <h2>سیستم مدیریت حمل و نقل</h2>
                <h3>افغانستان</h3>
                <form method="post">
                    <input type="text" name="username" placeholder="نام کاربری" required autofocus>
                    <input type="password" name="password" placeholder="رمز عبور" required>
                    <button type="submit">ورود به سیستم</button>
                </form>
                <div class="info">
                    سیستم مدیریت حمل و نقل (TMS) | افغانستان
                </div>
            </div>
        </body>
        </html>
    ''')

urlpatterns = [
    path('', admin_dashboard, name='admin_dashboard'),
    path('login/', login_page, name='login_page'),
    path('admin/', admin.site.urls),
    path('admin/logout/', LogoutView.as_view(next_page='/login/'), name='admin_logout'),
    path('api/simple-login/', simple_login, name='simple_login'),
    path('api/dashboard/', dashboard, name='dashboard'),
    path('tracking/', include('tracking.urls')),
    path('finance/', include('finance.urls')),
    path('customer/', include('customer_panel.urls')),
    path('driver/', include('driver_panel.urls')),
]