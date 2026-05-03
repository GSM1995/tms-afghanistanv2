from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserRole, AccessLog
from .decorators import admin_only

@staff_member_required
@admin_only
def role_list(request):
    roles = UserRole.objects.all().select_related('user')
    return render(request, 'common/roles/list.html', {'roles': roles})

@staff_member_required
@admin_only
def role_create(request):
    users_without_role = User.objects.exclude(id__in=UserRole.objects.values('user_id'))
    
    if request.method == 'POST':
        user_id = request.POST.get('user')
        role = request.POST.get('role')
        
        user = get_object_or_404(User, id=user_id)
        
        user_role = UserRole.objects.create(
            user=user,
            role=role,
            can_manage_customers=request.POST.get('can_manage_customers') == 'on',
            can_manage_drivers=request.POST.get('can_manage_drivers') == 'on',
            can_manage_vehicles=request.POST.get('can_manage_vehicles') == 'on',
            can_manage_orders=request.POST.get('can_manage_orders') == 'on',
            can_manage_finance=request.POST.get('can_manage_finance') == 'on',
            can_view_reports=request.POST.get('can_view_reports') == 'on',
            can_manage_users=request.POST.get('can_manage_users') == 'on',
        )
        
        AccessLog.objects.create(
            user=request.user,
            action=f"ایجاد نقش کاربری برای {user.username}",
            page="مدیریت نقش‌ها",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, f'نقش کاربری برای {user.username} با موفقیت ایجاد شد.')
        return redirect('common:role_list')
    
    context = {
        'users': users_without_role,
        'role_choices': UserRole.ROLE_CHOICES,
    }
    return render(request, 'common/roles/form.html', context)

@staff_member_required
@admin_only
def role_edit(request, pk):
    user_role = get_object_or_404(UserRole, pk=pk)
    
    if request.method == 'POST':
        user_role.role = request.POST.get('role')
        user_role.can_manage_customers = request.POST.get('can_manage_customers') == 'on'
        user_role.can_manage_drivers = request.POST.get('can_manage_drivers') == 'on'
        user_role.can_manage_vehicles = request.POST.get('can_manage_vehicles') == 'on'
        user_role.can_manage_orders = request.POST.get('can_manage_orders') == 'on'
        user_role.can_manage_finance = request.POST.get('can_manage_finance') == 'on'
        user_role.can_view_reports = request.POST.get('can_view_reports') == 'on'
        user_role.can_manage_users = request.POST.get('can_manage_users') == 'on'
        user_role.save()
        
        AccessLog.objects.create(
            user=request.user,
            action=f"ویرایش نقش کاربری {user_role.user.username}",
            page="مدیریت نقش‌ها",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, f'نقش کاربری {user_role.user.username} با موفقیت ویرایش شد.')
        return redirect('common:role_list')
    
    context = {
        'user_role': user_role,
        'role_choices': UserRole.ROLE_CHOICES,
    }
    return render(request, 'common/roles/form.html', context)

@staff_member_required
@admin_only
def role_delete(request, pk):
    user_role = get_object_or_404(UserRole, pk=pk)
    username = user_role.user.username
    user_role.delete()
    
    AccessLog.objects.create(
        user=request.user,
        action=f"حذف نقش کاربری {username}",
        page="مدیریت نقش‌ها",
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    messages.success(request, f'نقش کاربری {username} با موفقیت حذف شد.')
    return redirect('common:role_list')

@staff_member_required
@admin_only
def access_logs(request):
    logs = AccessLog.objects.all().select_related('user')[:100]
    return render(request, 'common/logs/list.html', {'logs': logs})