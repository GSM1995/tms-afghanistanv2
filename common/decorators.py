from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from .models import UserRole


def role_required(permission):
    """دکوراتور برای بررسی دسترسی کاربر"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('/login/')
            
            # سوپریوزرها همه دسترسی‌ها را دارند
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            try:
                user_role = UserRole.objects.get(user=request.user)
                if getattr(user_role, permission, False):
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(request, 'شما دسترسی لازم برای این بخش را ندارید.')
                    return redirect('/')
            except UserRole.DoesNotExist:
                messages.error(request, 'نقش کاربری شما تعریف نشده است.')
                return redirect('/')
        return wrapper
    return decorator


def admin_only(view_func):
    """فقط ادمین‌ها (سوپریوزر)"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/login/')
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        messages.error(request, 'این بخش فقط برای مدیران سیستم قابل دسترسی است.')
        return redirect('/')
    return wrapper


def manager_only(view_func):
    """مدیران و ادمین‌ها"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/login/')
        
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        try:
            user_role = UserRole.objects.get(user=request.user)
            if user_role.role in ['admin', 'manager']:
                return view_func(request, *args, **kwargs)
        except UserRole.DoesNotExist:
            pass
        
        messages.error(request, 'دسترسی محدود به مدیران')
        return redirect('/')
    return wrapper


def accountant_only(view_func):
    """فقط حسابداران و ادمین‌ها"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/login/')
        
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        try:
            user_role = UserRole.objects.get(user=request.user)
            if user_role.role in ['admin', 'accountant'] or user_role.can_manage_finance:
                return view_func(request, *args, **kwargs)
        except UserRole.DoesNotExist:
            pass
        
        messages.error(request, 'این بخش فقط برای حسابداران قابل دسترسی است.')
        return redirect('/')
    return wrapper