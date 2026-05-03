from .models import AccessLog


class AccessLogMiddleware:
    """ثبت خودکار لاگ دسترسی کاربران"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if request.user.is_authenticated:
            should_log = False
            action_type = ""
            
            if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
                should_log = True
                action_type = f"{request.method}"
            
            if '/login/' in request.path:
                should_log = True
                action_type = "ورود به سیستم"
            elif '/logout/' in request.path:
                should_log = True
                action_type = "خروج از سیستم"
            
            important_pages = ['/admin/customers/', '/admin/orders/', '/admin/finance/']
            for page in important_pages:
                if page in request.path:
                    should_log = True
                    if not action_type:
                        action_type = "مشاهده"
                    break
            
            if should_log:
                AccessLog.objects.create(
                    user=request.user,
                    action=f"{action_type} - {request.path}",
                    page=request.path,
                    ip_address=self.get_client_ip(request)
                )
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip